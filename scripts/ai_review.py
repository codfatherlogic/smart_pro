#!/usr/bin/env python3
"""Post a code review to a GitHub pull request using the crenya-ai OpenAI-compatible gateway.

Deliberately stdlib-only: it runs on the self-hosted arm64 runner with no pip install step.

Usage:
    ai_review.py --pr 101 --base-url https://api.crenya.ai/v1 --model crenya-economy

Environment:
    CRENYA_AI_TOKEN  JWT access token for the crenya-ai gateway (required)
    GH_TOKEN         token used to read the diff and post the review (required)
    GITHUB_REPOSITORY  owner/repo, set automatically by GitHub Actions
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

MAX_DIFF_CHARS = 60_000
MAX_FILES = 40
TIMEOUT = 180

SYSTEM_PROMPT = """You are a senior engineer reviewing a pull request.

Report only defects a reviewer would block on:
- bugs and incorrect logic
- security problems (secrets, injection, authz, unsafe deserialization)
- resource or performance regressions
- broken error handling
- missing or wrong tests for the changed behaviour

Rules:
- Cite the file path and the line or function for every finding.
- Do not restate the diff, do not praise, do not suggest stylistic rewrites.
- If the diff contains no blocking defect, reply with exactly: NO_BLOCKING_ISSUES
- Keep the whole review under 400 words. Prefer omission over padding."""


def _request(url: str, token: str, data: dict | None = None, method: str = "GET",
             accept: str = "application/vnd.github+json") -> dict | list:
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", accept)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        payload = resp.read()
    return json.loads(payload) if payload else {}


def fetch_diff(repo: str, pr: int, token: str) -> str:
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/pulls/{pr}")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github.v3.diff")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", "replace")


def changed_file_count(diff: str) -> int:
    return sum(1 for line in diff.splitlines() if line.startswith("diff --git "))


def truncate(diff: str) -> str:
    if len(diff) <= MAX_DIFF_CHARS:
        return diff
    return diff[:MAX_DIFF_CHARS] + "\n\n[diff truncated by ai_review.py]\n"


def review(base_url: str, model: str, token: str, diff: str) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "temperature": 0,
        "max_tokens": 1200,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Review this diff:\n\n```diff\n{diff}\n```"},
        ],
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", "replace")
        raise SystemExit(f"crenya-ai gateway returned {err.code}: {body[:400]}") from err
    return data["choices"][0]["message"]["content"].strip()


def post_review(repo: str, pr: int, token: str, text: str) -> str:
    url = f"https://api.github.com/repos/{repo}/pulls/{pr}/reviews"
    data = {"body": text, "event": "COMMENT"}
    result = _request(url, token, data=data, method="POST")
    return result.get("html_url", "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--base-url", default=os.environ.get("CRENYA_AI_BASE_URL", "https://api.crenya.ai/v1"))
    parser.add_argument("--model", default=os.environ.get("CRENYA_AI_MODEL", "crenya-economy"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = os.environ.get("GITHUB_REPOSITORY")
    gh_token = os.environ.get("GH_TOKEN")
    ai_token = os.environ.get("CRENYA_AI_TOKEN")
    missing = [n for n, v in (("GITHUB_REPOSITORY", repo), ("GH_TOKEN", gh_token),
                              ("CRENYA_AI_TOKEN", ai_token)) if not v]
    if missing:
        raise SystemExit("missing environment: " + ", ".join(missing))

    diff = fetch_diff(repo, args.pr, gh_token)
    if not diff.strip():
        print("empty diff, nothing to review")
        return 0

    files = changed_file_count(diff)
    if files > MAX_FILES:
        print(f"skipping: {files} changed files exceeds MAX_FILES={MAX_FILES}")
        return 0

    text = review(args.base_url, args.model, ai_token, truncate(diff))
    if text == "NO_BLOCKING_ISSUES":
        print("no blocking issues reported")
        return 0

    body = f"### crenya-ai review (`{args.model}`)\n\n{text}\n\n_Automated review. Advisory only._"
    if args.dry_run:
        print(body)
        return 0

    url = post_review(repo, args.pr, gh_token, body)
    print(f"posted: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
