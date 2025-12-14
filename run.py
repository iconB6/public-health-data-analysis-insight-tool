# run.py
import argparse
from src.application.import_pipeline import import_data
from src.application.analyse_service import AnalyseService
from src.infrastructure.sqlite_repository import SQLiteRepository
from src.application.visualization import Visualizer
from src.utils.logger import get_logger

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
    analyse_parser.add_argument("--db-path", "-o", required=True)

    return parser.parse_args()


# ========== IMPORT COMMAND ==========

def handle_import(args):
    logger.info("Starting import pipeline")
    if args.dbtype == "sqlite":
        repository = SQLiteRepository(args.db_path)
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
        repository = SQLiteRepository(args.db_path)
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
                # filter COUNTRY eq USA
                col, op, val = parts[1], parts[2], parts[3]
                service.run_filter(conditions={col: {op: val}})

            elif command == "summary":
                service.run_filter()

            elif command == "trend":
                # trend DATE VALUE mean
                date_field, metric_field = parts[1], parts[2]
                agg = parts[3] if len(parts) > 3 else "count"
                service.run_trend(
                    date_field=date_field,
                    metric_field=metric_field,
                    agg=agg,
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
  filter <COLUMN> <OP> <VALUE>
  summary
  trend <DATE_FIELD> <METRIC_FIELD> [AGG]
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
