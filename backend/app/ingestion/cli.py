"""
Command-Line Interface for Curriculum Ingestion.

Usage:
    python -m app.ingestion.cli --manifest <path_to_manifest.json> --dry-run
    python -m app.ingestion.cli --manifest <path_to_manifest.json> --publish
    python -m app.ingestion.cli --dir <directory_of_manifests> --publish
"""

import argparse
import logging
from pathlib import Path
import sys

# Silence verbose SQLAlchemy echo for cleaner CLI output
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
from app.db.session import engine
engine.echo = False

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("smartlearn.cli")

from app.ingestion.pipeline import CurriculumIngestionPipeline, IngestionError


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SmartLearn.AI Curriculum Ingestion Pipeline CLI"
    )
    parser.add_argument(
        "--manifest",
        type=str,
        help="Path to a single curriculum manifest JSON file",
    )
    parser.add_argument(
        "--dir",
        type=str,
        help="Path to a directory containing curriculum manifest JSON files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Perform schema validation and display change diff without writing to database",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        default=False,
        help="Publish changes to the active PostgreSQL database",
    )
    parser.add_argument(
        "--allow-drafts",
        action="store_true",
        default=False,
        help="Allow ingesting manifests flagged as ai_draft or unreviewed",
    )

    args = parser.parse_args()

    if not args.manifest and not args.dir:
        parser.print_help()
        sys.exit(1)

    # Determine execution mode: default to dry-run if --publish not explicitly provided
    is_dry_run = not args.publish or args.dry_run

    targets = []
    if args.manifest:
        targets.append(Path(args.manifest))
    if args.dir:
        d = Path(args.dir)
        if not d.is_dir():
            print(f"Error: Directory not found: {d}", file=sys.stderr)
            sys.exit(1)
        targets.extend(sorted(d.glob("*.json")))

    if not targets:
        print("No manifest files found to ingest.", file=sys.stderr)
        sys.exit(1)

    mode_str = "DRY-RUN PREVIEW" if is_dry_run else "DATABASE PUBLICATION"
    print(f"\n=== Starting Curriculum Ingestion ({mode_str}) ===")
    print(f"Total manifests to process: {len(targets)}\n")

    has_errors = False
    for target in targets:
        print(f"--> Processing: {target.name}")
        try:
            result = CurriculumIngestionPipeline.run(
                source=target,
                dry_run=is_dry_run,
                allow_drafts=args.allow_drafts,
            )
            print(result["rendered_preview"])
            if result.get("warnings"):
                for w in result["warnings"]:
                    print(f"    WARNING: {w}")
            print(f"[OK] {target.name} - {result['status']}\n")
        except IngestionError as e:
            print(f"[ERROR] Ingestion failed for {target.name}: {e}", file=sys.stderr)
            has_errors = True
        except Exception as e:
            print(f"[CRITICAL] Unexpected error processing {target.name}: {e}", file=sys.stderr)
            has_errors = True

    if has_errors:
        print("\n=== Ingestion Completed with Errors ===", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\n=== Ingestion Completed Successfully ({mode_str}) ===")


if __name__ == "__main__":
    main()
