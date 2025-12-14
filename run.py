import click
from application.import_pipeline import *


# ==========================================
# CLI COMMAND: Import Data (One-time)
# ==========================================
@click.group()
def cli():
    """Main CLI group for Data Insights Tool."""
    pass


@cli.command(name="import")
@click.option("--source-type", "-t", type=click.Choice(["csv", "json", "api", "db"]), required=True)
@click.option("--source-path", "-p", required=True)
@click.option("--db-name", "-n", required=False)
def import_data(source_type, source_path, db_name):
    """Import data from a source, clean it, and store into SQLite."""
    click.echo(f"[INFO] Importing from {source_type}: {source_path}")
    import_data_from_source(source_type, source_path, db_name)
    click.echo("[DONE] Data import completed.")

# ==========================================
# CLI COMMAND: Quick Import for CSV 
# ==========================================
@cli.command(name="csv")
@click.argument("path")
@click.option("--db-name", "-d", required=False)
def import_csv(path, db_name):
    """Quick import for CSV files."""
    import_data_from_source("csv", path, db_name)
    click.echo("[DONE] CSV import completed.")


# ==========================================
# Entry point
# ==========================================
if __name__ == "__main__":
    cli()