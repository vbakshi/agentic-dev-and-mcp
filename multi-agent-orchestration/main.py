#!/usr/bin/env python3
"""Run the ComplAI sales multi-agent orchestration workflow."""

import argparse
import asyncio
import logging
import os

from src.config import Settings, load_project_env
from src.workflow import DEFAULT_CAMPAIGN_BRIEF, SalesCampaignWorkflow


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the sales manager multi-agent workflow (writers as tools, emailer handoff)",
    )
    parser.add_argument(
        "--request",
        type=str,
        default=DEFAULT_CAMPAIGN_BRIEF,
        help="User request passed to the Sales Manager agent",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip SendGrid delivery (overrides SALES_WORKFLOW_DRY_RUN env)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not write results to the output folder",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Directory for saved workflow JSON (default: output)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


async def _run(args: argparse.Namespace) -> int:
    load_project_env()

    if args.dry_run:
        os.environ["SALES_WORKFLOW_DRY_RUN"] = "true"

    settings = Settings.from_env(
        output_dir=args.output_dir,
        load_env=False,
    )
    workflow = SalesCampaignWorkflow(settings=settings)

    result = await workflow.run(
        user_request=args.request,
        save_output=not args.no_save,
    )

    print("\n" + "=" * 60)
    print("SALES WORKFLOW COMPLETE")
    print("=" * 60)
    print(f"\nDry run: {result.dry_run}")
    print(f"\nFinal output:\n{result.final_output}")
    if result.output_file:
        print(f"\nSaved to: {result.output_file}")
    return 0


def main() -> None:
    args = parse_args()
    _configure_logging(args.verbose)

    try:
        raise SystemExit(asyncio.run(_run(args)))
    except ValueError as exc:
        logging.error("%s", exc)
        raise SystemExit(1) from exc
    except KeyboardInterrupt:
        raise SystemExit(130)


if __name__ == "__main__":
    main()
