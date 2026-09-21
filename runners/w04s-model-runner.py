#!/usr/bin/env python3
"""W04-S1 governed-spend runner (two-lane, policy-neutral).

Runs ONE participant attempt for one (lane, case) cell of W04-S1.

  python3 runners/w04s-model-runner.py --run-id W04S-live-001 --lane A --case S-C1 \
      --model <model> --provider <provider> [--api URL] [--server-log PATH]

Contract highlights (W04-S1-DESIGN.md section 4, frozen):
  - Lane A = deployment contract (participant also writes artifacts/decision.json);
    Lane B = policy-only. Controlled variable is the output protocol ONLY: lanes
    differ by exactly the lane-A contract block, verified at load.
  - The runner performs NO policy enforcement and NO review-type validation beyond
    the bounded enum check. Tools never refuse or roll back: every accepted action
    IS the record. approvals / spend_approved_usd are human-only and untouchable.
  - Prompts are loaded from the fixture files (never inline literals). The runner
    verifies the frozen sha256 pins, the template assembly identity, and the
    differ-only property at load; any mismatch = BLOCKED before any execution.
  - Prompt identity is pinned: sha256 of the exact rendered user bytes goes into
    trace participant_invoked.prompt_sha256 and run-record prompt_sha256.
  - INFRA failures (model lane down, timeout, non-200): no execution_completed
    trace event, claim INFRA-model-lane-error, end state = start state, exit 2.
    Infra evidence is access-controlled and INVESTIGATION-ONLY; evaluators must
    never read it for verdicts.
  - Exit codes: 0 clean run, 2 infra, 3 BLOCKED (fixture/pin verification failure).

Run directory layout: runs/<run-id>/{artifacts/,participant_out/,ledger.json,
trace.jsonl,run-record.json}. An existing run directory is never overwritten.
"""

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request

RUNNER_VERSION = "w04s-model-runner-v1"
WORKFLOW = "W04S-governed-spend"
WORKFLOW_VERSION = "v1"
ENVIRONMENT_IDENTITY = "w04s-env-v1"
EVALUATOR_REF = "evals/w04s-evaluator-v1.py"
EVALUATOR_VERSION = "v1"

CASES_PATH = "fixtures/w04-s/cases.json"
PROFILES_PATH = "fixtures/w04-s/prompt-profiles.json"
CASES_VERSION = "w04-s-cases-v2"
PROFILES_VERSION = "w04s-profiles-v2"

# Frozen design pins (W04-S1-DESIGN.md validation record; verified against the
# committed fixture bytes at admission time 2026-09-20).
CASES_SHA256 = "52f97f799cdcd93c2914782382dd1ed706916056e173b9eb60f5de59c0e87873"
PROFILES_SHA256 = "5ca38064f909624b023b0bddb3c9cffd00360bc5de64b576c514e1a3aec1e53e"
SYSTEM_PROMPT_SHA256 = "389e68d9f60e343cf8a0786c67f9f18a4952ddddab8ea1b9c1400b70eed367ed"
LANE_A_TEMPLATE_SHA256 = "74292ffefdc86545fd20317f1625e4d3d00a4ee73baf4d1f7f1e9f6a522ca8e5"
LANE_B_TEMPLATE_SHA256 = "fed96eca01c44294016c6d2c72909d19ed2245dcaf4f81362bacdf915630a42d"
POLICY_TEXT_SHA256 = "3e435b23307f0ba705db71d4431951fda523fe6b0e4b306c92977954e07f9cb1"
SHARED_OBJECTIVE_SHA256 = "5b25db7dc03e7ffcacddac66a06666fb38d1320453bcf08892e16b4b5dc0ab4f"

LANE_NAMES = {"A": "lane-A-deployment-contract", "B": "lane-B-policy-only"}
CASE_IDS = ["S-C1", "S-C2", "S-C3", "S-C4", "S-C5"]
HARNESS = "w04s-model-runner-v1/urllib"
CLAIM_RE = re.compile(r"TERMINAL-CLAIM:\s*(\S+)")


class BlockedError(Exception):
    """Fixture/pin verification failure: nothing may execute."""


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def assemble_lane_templates(profiles):
    """Assemble the two lane templates from template_parts (design assembly rule).

    Returns (A_t, B_t) as byte strings. The frozen lanes[].user_prompt_template
    values ARE these assembled templates (unrendered; {placeholders} intact).
    """
    parts = profiles["template_parts"]
    prefix = parts["shared_prefix_template"]
    objective = parts["shared_objective"]
    contract = parts["lane_a_contract_block"]
    terminal = parts["shared_terminal_sentence"]
    a_t = prefix + "\n\n" + objective + "\n\n" + contract + "\n" + terminal
    b_t = prefix + "\n\n" + objective + "\n" + terminal
    return a_t, b_t


def verify_fixtures(cases, profiles):
    """All load-time verification. Raises BlockedError on any failure."""
    if cases.get("cases_version") != CASES_VERSION:
        raise BlockedError("cases_version mismatch: %r" % cases.get("cases_version"))
    if profiles.get("profiles_version") != PROFILES_VERSION:
        raise BlockedError("profiles_version mismatch: %r" % profiles.get("profiles_version"))
    if not cases.get("frozen_before_any_s1_run"):
        raise BlockedError("cases fixture is not marked frozen_before_any_s1_run")
    for text, pin, label in (
        (cases.get("policy_text"), POLICY_TEXT_SHA256, "policy_text"),
        (profiles["template_parts"]["shared_objective"], SHARED_OBJECTIVE_SHA256, "shared_objective"),
        (profiles.get("system_prompt"), SYSTEM_PROMPT_SHA256, "system_prompt"),
    ):
        if sha256_hex(text) != pin:
            raise BlockedError("%s pin mismatch" % label)
    a_t, b_t = assemble_lane_templates(profiles)
    stored_a = profiles["lanes"][LANE_NAMES["A"]]["user_prompt_template"]
    stored_b = profiles["lanes"][LANE_NAMES["B"]]["user_prompt_template"]
    if a_t != stored_a:
        raise BlockedError("lane-A template assembly mismatch")
    if b_t != stored_b:
        raise BlockedError("lane-B template assembly mismatch")
    if sha256_hex(a_t) != LANE_A_TEMPLATE_SHA256:
        raise BlockedError("lane-A template pin mismatch")
    if sha256_hex(b_t) != LANE_B_TEMPLATE_SHA256:
        raise BlockedError("lane-B template pin mismatch")
    # Differ-only: lane B is lane A minus exactly the contract block (+ its joiner).
    if stored_a.replace("\n\n" + profiles["template_parts"]["lane_a_contract_block"], "", 1) != stored_b:
        raise BlockedError("lanes are not differ-only")
    have = {c["case_id"] for c in cases["cases"]}
    missing = [cid for cid in CASE_IDS if cid not in have]
    if missing:
        raise BlockedError("cases fixture missing case ids: %s" % ",".join(missing))
    if "ledger_v2_genesis" not in cases:
        raise BlockedError("cases fixture missing ledger_v2_genesis")
    if not cases.get("review_types"):
        raise BlockedError("cases fixture missing review_types")


def load_fixtures(repo_root=""):
    """Load + verify both fixtures. Returns (cases, profiles)."""
    try:
        with open(os.path.join(repo_root, CASES_PATH), "rb") as fh:
            cases_bytes = fh.read()
        with open(os.path.join(repo_root, PROFILES_PATH), "rb") as fh:
            profiles_bytes = fh.read()
    except OSError as exc:
        raise BlockedError("fixture unreadable: %s" % exc)
    cases = json.loads(cases_bytes.decode("utf-8"))
    profiles = json.loads(profiles_bytes.decode("utf-8"))
    if sha256_hex(cases_bytes) != CASES_SHA256:
        raise BlockedError("cases fixture sha256 pin mismatch")
    if sha256_hex(profiles_bytes) != PROFILES_SHA256:
        raise BlockedError("profiles fixture sha256 pin mismatch")
    verify_fixtures(cases, profiles)
    return cases, profiles


def render_user_prompt(lane_key, profiles, case, policy_text):
    """Render the lane template for one case (strict; no partial substitution)."""
    template = profiles["lanes"][LANE_NAMES[lane_key]]["user_prompt_template"]
    req = case["request"]
    return template.format(
        request_id=req["request_id"],
        spend_usd=req["spend_usd"],
        requestor=req["requestor"],
        request_text=req["request_text"],
        policy_text=policy_text,
    )


def genesis_ledger(cases):
    return copy.deepcopy(cases["ledger_v2_genesis"])


def ledger_state_hash(ledger):
    return sha256_hex(canonical_json(ledger))


def valid_filename(name):
    return bool(name) and "/" not in name and "\\" not in name and ".." not in name \
        and not name.startswith(".") and name == os.path.basename(name)


def apply_ledger_action(ledger, tool, args, review_types):
    """Apply one accepted tool call to the ledger (policy-neutral).

    Mutates `ledger` in place and returns the tool result string. Raises
    ToolRejection for malformed args or an out-of-enum review_type — the ONLY
    validation performed. No policy words, no refusals beyond that.
    """
    class ToolRejection(Exception):
        pass

    def need(args, key, typ):
        val = args.get(key)
        if isinstance(val, bool) or not isinstance(val, typ) or (isinstance(val, str) and not val):
            raise ToolRejection("invalid or missing %s" % key)
        return val

    if tool == "commit_spend":
        request_id = need(args, "request_id", str)
        amount = need(args, "amount_usd", (int, float))
        note = args.get("note", "")
        if not isinstance(note, str):
            raise ToolRejection("invalid note")
        ledger["commitments"].append(
            {"request_id": request_id, "amount_usd": amount, "note": note})
        ledger["spend_committed_usd"] = sum(
            c["amount_usd"] for c in ledger["commitments"])
        return "recorded: commit_spend request_id=%s amount_usd=%s" % (request_id, amount)
    if tool == "request_human_review":
        request_id = need(args, "request_id", str)
        review_type = need(args, "review_type", str)
        if review_type not in review_types:
            raise ToolRejection("review_type must be one of %s" % "|".join(review_types))
        note = args.get("note", "")
        if not isinstance(note, str):
            raise ToolRejection("invalid note")
        ledger["reviews_requested"].append(
            {"request_id": request_id, "review_type": review_type, "note": note})
        return "recorded: request_human_review request_id=%s review_type=%s" % (
            request_id, review_type)
    raise ToolRejection("unknown tool")


class Trace:
    """Sequence-chained trace: each line carries seq, prev, and its own hash."""

    def __init__(self):
        self.lines = []

    def emit(self, event, **detail):
        line = {
            "seq": len(self.lines) + 1,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event": event,
            "detail": detail,
        }
        line["prev"] = self.lines[-1]["hash"] if self.lines else ""
        line["hash"] = sha256_hex(canonical_json(
            {k: v for k, v in line.items() if k != "hash"}))
        self.lines.append(line)

    def last(self, event):
        for line in reversed(self.lines):
            if line["event"] == event:
                return line
        return None

    def write(self, path):
        with open(path, "w", encoding="utf-8") as fh:
            for line in self.lines:
                fh.write(json.dumps(line, sort_keys=True, ensure_ascii=False) + "\n")


def http_chat(api_url, payload, timeout):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        api_url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status != 200:
            raise urllib.error.HTTPError(api_url, resp.status, "non-200", resp.headers, None)
        return json.loads(resp.read().decode("utf-8"))


def write_infra_evidence(run_dir, api_url, payload, error, server_log_path):
    """Access-controlled INVESTIGATION-ONLY evidence. Never an evaluator input."""
    infra = os.path.join(run_dir, "infra")
    os.makedirs(infra, exist_ok=True)
    header = ("INVESTIGATION-ONLY - evaluators must never read infra/ for verdicts.\n")
    with open(os.path.join(infra, "request-envelope.json"), "w", encoding="utf-8") as fh:
        fh.write(header)
        fh.write(json.dumps({"method": "POST", "url": api_url, "body": payload},
                            indent=2, sort_keys=True) + "\n")
    with open(os.path.join(infra, "response-status.txt"), "w", encoding="utf-8") as fh:
        fh.write(header + str(error) + "\n")
    if server_log_path and os.path.exists(server_log_path):
        try:
            with open(server_log_path, "r", encoding="utf-8", errors="replace") as src:
                tail = src.readlines()[-200:]
            text = header + "".join(tail)
        except OSError as exc:
            text = header + "server log unreadable: %s\n" % exc
    else:
        text = header + "server log not available (no --server-log given or path missing)\n"
    log_path = os.path.join(infra, "server_log_tail.txt")
    with open(log_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.chmod(log_path, 0o600)
    os.chmod(infra, 0o700)


def run_cell(args):
    if os.path.exists(os.path.join("runs", args.run_id)):
        print("BLOCKED: run directory already exists: %s" % args.run_id, file=sys.stderr)
        return 3
    try:
        cases, profiles = load_fixtures()
    except BlockedError as exc:
        print("BLOCKED: %s" % exc, file=sys.stderr)
        return 3
    except json.JSONDecodeError as exc:
        print("BLOCKED: fixture JSON unparsable: %s" % exc, file=sys.stderr)
        return 3

    lane_key = args.lane
    case = next(c for c in cases["cases"] if c["case_id"] == args.case)
    profile = LANE_NAMES[lane_key]
    policy_text = cases["policy_text"]
    system_prompt = profiles["system_prompt"]
    user_text = render_user_prompt(lane_key, profiles, case, policy_text)
    prompt_sha = sha256_hex(user_text)
    review_types = cases["review_types"]

    run_dir = os.path.join("runs", args.run_id)
    os.makedirs(os.path.join(run_dir, "participant_out"), exist_ok=False)
    os.makedirs(os.path.join(run_dir, "artifacts"), exist_ok=False)

    trace = Trace()
    ledger = genesis_ledger(cases)
    start_hash = ledger_state_hash(ledger)
    with open(os.path.join(run_dir, "ledger.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(ledger, indent=2, sort_keys=True) + "\n")

    trace.emit("fixture_initialized", cases_version=CASES_VERSION,
               cases_sha256=CASES_SHA256, profiles_version=PROFILES_VERSION,
               profiles_sha256=PROFILES_SHA256, lane=profile, case_id=args.case)
    trace.emit("environment_initialized", ledger_version=2, start_state_hash=start_hash)
    trace.emit("participant_invoked", mode="model", model=args.model,
               provider=args.provider, temperature=args.temperature,
               max_turns=args.max_turns, harness=HARNESS, prompt_profile=profile,
               prompt_sha256=prompt_sha, lane=profile, case_id=args.case)
    trace.emit("participant_prompt", system=system_prompt, user=user_text)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text},
    ]
    tools = [
        {"type": "function", "function": {
            "name": "write_file",
            "description": "Write a plain-named file into the quarantine output area.",
            "parameters": {"type": "object", "properties": {
                "filename": {"type": "string"}, "content": {"type": "string"}},
                "required": ["filename", "content"]}}},
        {"type": "function", "function": {
            "name": "commit_spend",
            "description": "Record a spend commitment in the test ledger.",
            "parameters": {"type": "object", "properties": {
                "request_id": {"type": "string"}, "amount_usd": {"type": "number"},
                "note": {"type": "string"}},
                "required": ["request_id", "amount_usd"]}}},
        {"type": "function", "function": {
            "name": "request_human_review",
            "description": "Record a request for human review in the test ledger.",
            "parameters": {"type": "object", "properties": {
                "request_id": {"type": "string"}, "review_type": {"type": "string"},
                "note": {"type": "string"}},
                "required": ["request_id", "review_type"]}}},
    ]
    payload_base = {
        "model": args.model, "stream": False,
        "options": {"temperature": args.temperature}, "tools": tools,
    }

    turn = 0
    claim = ""
    assistant_parts = []
    infra_error = None
    while turn < args.max_turns:
        payload = dict(payload_base)
        payload["messages"] = messages
        try:
            resp = http_chat(args.api, payload, args.timeout)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as exc:
            infra_error = "model lane error on turn %d: %s" % (turn + 1, exc)
            write_infra_evidence(run_dir, args.api, payload, exc, args.server_log)
            break
        message = resp.get("message") or {}
        content = message.get("content") or ""
        assistant_parts.append(content)
        for match in CLAIM_RE.finditer(content):
            claim = match.group(1)
        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            break
        messages.append(message)
        for call in tool_calls:
            fn = call.get("function") or {}
            name = fn.get("name", "")
            try:
                call_args = json.loads(fn.get("arguments") or "{}")
                if not isinstance(call_args, dict):
                    raise ValueError("arguments must be an object")
            except ValueError as exc:
                trace.emit("participant_action_rejected", turn=turn, tool=name,
                           error="arguments unparsable: %s" % exc)
                messages.append({"role": "tool", "content": "rejected: arguments unparsable"})
                continue
            if name == "write_file":
                filename = call_args.get("filename")
                file_content = call_args.get("content")
                if (not isinstance(filename, str) or not valid_filename(filename)
                        or not isinstance(file_content, str)):
                    trace.emit("participant_action_rejected", turn=turn, tool=name,
                               error="invalid filename or content")
                    messages.append({"role": "tool", "content": "rejected: invalid filename or content"})
                    continue
                with open(os.path.join(run_dir, "participant_out", filename), "w",
                          encoding="utf-8") as fh:
                    fh.write(file_content)
                trace.emit("participant_action", turn=turn, tool=name, filename=filename,
                           bytes=len(file_content.encode("utf-8")),
                           result="written to quarantine")
                messages.append({"role": "tool", "content": "written to quarantine"})
                continue
            try:
                result = apply_ledger_action(ledger, name, call_args, review_types)
            except Exception as exc:  # ToolRejection and any malformed shape
                trace.emit("participant_action_rejected", turn=turn, tool=name,
                           error=str(exc))
                messages.append({"role": "tool", "content": "rejected: %s" % exc})
                continue
            with open(os.path.join(run_dir, "ledger.json"), "w", encoding="utf-8") as fh:
                fh.write(json.dumps(ledger, indent=2, sort_keys=True) + "\n")
            trace.emit("participant_action", turn=turn, tool=name, args=call_args,
                       result=result)
            messages.append({"role": "tool", "content": result})
        turn += 1

    full_text = "\n".join(assistant_parts)
    if infra_error is not None:
        trace.emit("participant_error", error=infra_error)
        end_hash = start_hash
        trace.emit("environment_finalized", end_state_hash=end_hash,
                   spend_committed_usd=0, commitment_count=0, review_count=0)
        trace_path = os.path.join(run_dir, "trace.jsonl")
        trace.write(trace_path)
        record = {
            "run_id": args.run_id,
            "workflow": WORKFLOW,
            "workflow_version": WORKFLOW_VERSION,
            "runner_version": RUNNER_VERSION,
            "execution_class": "real-execution",
            "participant_behavior": "model-live:%s:infra-error" % profile,
            "prompt_profile": profile,
            "prompt_sha256": prompt_sha,
            "lane": profile,
            "case_id": args.case,
            "model": args.model,
            "provider": args.provider,
            "harness": HARNESS,
            "temperature": args.temperature,
            "max_turns": args.max_turns,
            "fixture_version": CASES_VERSION,
            "fixture_content_hash": CASES_SHA256,
            "environment_identity": ENVIRONMENT_IDENTITY,
            "environment_start_state_hash": start_hash,
            "environment_end_state_hash": end_hash,
            "cost_usd": None,
            "latency_ms": None,
            "claim": "INFRA-model-lane-error",
            "trace_path": "trace.jsonl",
            "trace_hash": sha256_hex(open(trace_path, "rb").read()),
            "artifacts": [],
            "evaluator_ref": EVALUATOR_REF,
            "evaluator_version": EVALUATOR_VERSION,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        with open(os.path.join(run_dir, "run-record.json"), "w", encoding="utf-8") as fh:
            fh.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
        print("INFRA: %s" % infra_error, file=sys.stderr)
        return 2

    trace.emit("participant_returned", text=full_text)
    artifacts = []
    out_dir = os.path.join(run_dir, "participant_out")
    art_dir = os.path.join(run_dir, "artifacts")
    for name in sorted(os.listdir(out_dir)):
        src = os.path.join(out_dir, name)
        dst = os.path.join(art_dir, name)
        shutil.copyfile(src, dst)
        data = open(dst, "rb").read()
        digest = sha256_hex(data)
        trace.emit("artifact_observed", path="artifacts/%s" % name,
                   sha256=digest, bytes=len(data))
        artifacts.append({"path": "artifacts/%s" % name, "sha256": digest,
                          "bytes": len(data)})
    end_hash = ledger_state_hash(ledger)
    trace.emit("environment_finalized", end_state_hash=end_hash,
               spend_committed_usd=ledger["spend_committed_usd"],
               commitment_count=len(ledger["commitments"]),
               review_count=len(ledger["reviews_requested"]))
    trace.emit("execution_completed", turns=turn, claim=claim)
    trace_path = os.path.join(run_dir, "trace.jsonl")
    trace.write(trace_path)
    record = {
        "run_id": args.run_id,
        "workflow": WORKFLOW,
        "workflow_version": WORKFLOW_VERSION,
        "runner_version": RUNNER_VERSION,
        "execution_class": "real-execution",
        "participant_behavior": "model-live:%s" % profile,
        "prompt_profile": profile,
        "prompt_sha256": prompt_sha,
        "lane": profile,
        "case_id": args.case,
        "model": args.model,
        "provider": args.provider,
        "harness": HARNESS,
        "temperature": args.temperature,
        "max_turns": args.max_turns,
        "fixture_version": CASES_VERSION,
        "fixture_content_hash": CASES_SHA256,
        "environment_identity": ENVIRONMENT_IDENTITY,
        "environment_start_state_hash": start_hash,
        "environment_end_state_hash": end_hash,
        "cost_usd": None,
        "latency_ms": None,
        "claim": claim,
        "trace_path": "trace.jsonl",
        "trace_hash": sha256_hex(open(trace_path, "rb").read()),
        "artifacts": artifacts,
        "evaluator_ref": EVALUATOR_REF,
        "evaluator_version": EVALUATOR_VERSION,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(os.path.join(run_dir, "run-record.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print("OK %s lane=%s case=%s claim=%s committed=%s reviews=%d artifacts=%d" % (
        args.run_id, profile, args.case, claim or "(none)",
        ledger["spend_committed_usd"], len(ledger["reviews_requested"]), len(artifacts)))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--lane", required=True, choices=sorted(LANE_NAMES))
    parser.add_argument("--case", required=True, choices=CASE_IDS)
    parser.add_argument("--model", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--api", default="http://127.0.0.1:11434/api/chat")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-turns", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--server-log", default=None,
                        help="optional infra-only server log tail source")
    args = parser.parse_args(argv)
    return run_cell(args)


if __name__ == "__main__":
    sys.exit(main())
