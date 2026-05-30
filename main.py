#!/usr/bin/env python3
# cli. give email by --text / --file / stdin, or --demo for samples

from __future__ import annotations

import argparse
import json
import logging
import os
import sys

# so we can import src without install
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from support_assistant import build_orchestrator  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from examples.sample_emails import ALL_SAMPLES  # noqa: E402


# get the email from wherever
def _read_email(args: argparse.Namespace) -> str | None:
    if args.text:
        return args.text
    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            return fh.read()
    if not sys.stdin.isatty():
        data = sys.stdin.read().strip()
        if data:
            return data
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Intelligent customer-support email assistant.",
    )
    parser.add_argument("--text", help="The raw customer email as a string.")
    parser.add_argument("--file", help="Path to a file containing the email.")
    parser.add_argument("--demo", action="store_true",
                        help="Process all bundled sample emails.")
    parser.add_argument("--debug", action="store_true",
                        help="Include the internal plan and tool results.")
    parser.add_argument("--verbose", action="store_true",
                        help="Log which reasoning strategy is used.")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    orchestrator = build_orchestrator()

    # demo mode: run all samples
    if args.demo:
        results = {
            name: orchestrator.process(email).to_dict(include_debug=args.debug)
            for name, email in ALL_SAMPLES.items()
        }
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    email = _read_email(args)
    if not email:
        parser.error("Provide an email via --text, --file, stdin, or use --demo.")

    result = orchestrator.process(email)
    print(json.dumps(result.to_dict(include_debug=args.debug),
                      indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
