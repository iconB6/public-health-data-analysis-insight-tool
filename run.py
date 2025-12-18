# run.py
import argparse
from src.application.import_pipeline import import_data
from src.application.analyse_service import AnalyseService
from src.infrastructure.sqlite_repository import SQLiteRepository
from src.application.visualization import Visualizer
from src.utils.logger import get_logger
import os

logger = get_logger("CLI")


# ========== ARGUMENT PARSING ==========

def parse_args():
    parser = argparse.ArgumentParser(description="Data Analysis CLI")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # import command (one-shot)
    import_parser = subparsers.add_parser("import", help="Import data into database")
    import_parser.add_argument("--source", "-s", required=True)
    import_parser.add_argument("--path", "-p", required=True)
    import_parser.add_argument("--dbtype", "-d", default="sqlite")
    import_parser.add_argument("--db-path", "-o", required=True)

    # analyse command (interactive)
    analyse_parser = subparsers.add_parser("analyse", help="Start analysis session")
    analyse_parser.add_argument("--dbtype", "-d", default="sqlite")
    analyse_parser.add_argument("--db-path", "-o", required=True,
                                help="Path to SQLite DB file or cloud DB URL when using -d cloud")

    return parser.parse_args()


# ========== IMPORT COMMAND ==========

def handle_import(args):
    logger.info("Starting import pipeline")
    if args.dbtype == "sqlite":
        repository = SQLiteRepository(args.db_path)
    elif args.dbtype == "cloud":
        # when using cloud, existing --db-path is treated as the cloud URL
        cloud_url = args.db_path or os.getenv("CLOUD_DB_URL")
        if not cloud_url:
            raise ValueError("Cloud DB selected but no URL provided via --db-path or CLOUD_DB_URL")
        from src.infrastructure.cloud_repository import CloudRepository
        repository = CloudRepository(cloud_url)
    else:
        raise ValueError(f"Unsupported db type: {args.dbtype}")
    
    inserted = import_data(
        source_type=args.source,
        source_path=args.path,
        repository=repository,
    )
    logger.info("Import completed successfully")
    logger.info(f"Inserted {inserted} records")


# ========== ANALYSE COMMAND ==========

def handle_analyse(args):
    logger.info("Starting analysis session")

    if args.dbtype == "sqlite":
        if not os.path.exists(args.db_path):
            raise FileNotFoundError(
                f"Database file not found: {args.db_path}. "
                f"Please run the import command first."
            )
        repository = SQLiteRepository(args.db_path)
    elif args.dbtype == "cloud":
        cloud_url = args.db_path or os.getenv("CLOUD_DB_URL")
        if not cloud_url:
            raise FileNotFoundError(
                "Cloud DB selected but no CLOUD_DB_URL set and --db-path not provided."
            )
        from src.infrastructure.cloud_repository import CloudRepository
        repository = CloudRepository(cloud_url)
    else:
        raise ValueError(f"Unsupported db type: {args.dbtype}")
    
    visualizer = Visualizer()

    service = AnalyseService(
        repository=repository,
        visualizer=visualizer,
    )

    try:
        analyse_repl(service)
    finally:
        service.close()


# ========== ANALYSE REPL ==========

def analyse_repl(service: AnalyseService):
    print("Enter analysis mode. Type 'help' for commands.")

    while True:
        try:
            cmd = input("analyse> ").strip()
            if not cmd:
                continue

            parts = cmd.split()
            command = parts[0]

            if command == "help":
                print_help()

            elif command == "filter":
                # filter COUNTRY eq AND
                from datetime import datetime

                date_from = None
                date_to = None
                conditions = {}

                i = 1
                while i < len(parts):
                    if parts[i] == "--from":
                        date_from = datetime.strptime(parts[i + 1], "%Y-%m-%d").date()
                        i += 2
                    elif parts[i] == "--to":
                        date_to = datetime.strptime(parts[i + 1], "%Y-%m-%d").date()
                        i += 2
                    else:
                        # parse condition: COLUMN OP VALUE
                        if i + 2 >= len(parts):
                            raise ValueError("Invalid filter condition format")

                        col = parts[i]
                        op = parts[i + 1]
                        val = parts[i + 2]

                        conditions.setdefault(col, {})[op] = val
                        i += 3

                service.run_filter(
                    date_from=date_from,
                    date_to=date_to,
                    conditions=conditions if conditions else None,
                )

            elif command == "summary":
                service.run_filter()

            elif command == "trend":
                """
                trend DATE VALUE
                    [agg=mean]
                    [from=YYYY-MM-DD]
                    [to=YYYY-MM-DD]
                    [where COL OP VAL ...]
                """

                date_field = parts[1]
                metric_field = parts[2]

                agg = "count"
                date_from = None
                date_to = None
                conditions = {}

                i = 3
                while i < len(parts):
                    token = parts[i]

                    if token.startswith("agg="):
                        agg = token.split("=", 1)[1]

                    elif token.startswith("from="):
                        date_from = token.split("=", 1)[1]

                    elif token.startswith("to="):
                        date_to = token.split("=", 1)[1]

                    elif token == "where":
                        i += 1
                        while i + 2 < len(parts):
                            col = parts[i]
                            op = parts[i + 1]
                            val = parts[i + 2]
                            conditions.setdefault(col, {})[op] = val
                            i += 3
                        break

                    else:
                        raise ValueError(f"Unknown trend option: {token}")

                    i += 1

                service.run_trend(
                    date_field=date_field,
                    metric_field=metric_field,
                    agg=agg,
                    date_from=date_from,
                    date_to=date_to,
                    conditions=conditions or None,
                )

            elif command == "export_summary":
                path = parts[1]
                service.export_summary(path)
            
            elif command == "export_trend":
                path = parts[1] 
                service.export_trend(path)

            elif command == "exit":
                print("Bye.")
                break

            else:
                print(f"Unknown command: {command}")

        except Exception as e:
            print(f"Error: {e}")
            logger.exception("CLI error")


# ========== HELP ==========

def print_help():
    print("""
Available commands:
  filter [--from YYYY-MM-DD] [--to YYYY-MM-DD] COLUMN OP VALUE [COLUMN OP VALUE ...]
  summary
  trend DATE VALUE  [agg=mean]
                    [from=YYYY-MM-DD]
                    [to=YYYY-MM-DD]
                    [where COL OP VAL ...]
  export_summary <PATH>
  export_trend <PATH>
  exit
""")


# ========== MAIN ==========

def main():
    args = parse_args()

    if args.command == "import":
        handle_import(args)
    elif args.command == "analyse":
        handle_analyse(args)


if __name__ == "__main__":
    main()
