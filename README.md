

---

# Public Health Data Analysis Insight Tool

A modular, testable data analysis tool for importing, cleaning, storing, analysing, and visualising public health datasets.
Designed with layered architecture, clear separation of concerns, and full unit/integration test coverage.

---

## 📌 Features

### Data Import (ETL)

* Load data from CSV (extensible to JSON / API / DB)
* Clean and validate raw data
* Store into SQLite (extensible to cloud databases)
* Transaction-safe import pipeline

### Data Analysis

* **Filter Service**: flexible conditional filtering and date range queries
* **Summary Service**: table-wide or filtered data summaries
* **Trend Service**: time-series aggregation for visualisation
* **Analysis Orchestration** via `AnalyseService`

### Visualisation

* Console preview tables
* Trend preview figures
* Deferred export (CSV / image)

### CLI Interface

* One-off import commands
* Interactive analysis session (REPL-style)
* Export on demand

### Engineering Quality

* Layered architecture (Application / Service / Infrastructure)
* Repository & Factory patterns
* Fully testable (FakeRepository + SQLite)
* Centralised logging

---

## 🏗 Architecture Overview

### High-Level Layers

```
┌──────────────┐
│     CLI      │
└──────┬───────┘
       ↓
┌─────────────────────┐
│ Application Layer   │
│  - ImportPipeline   │
│  - AnalyseService   │
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│ Service Layer       │
│  - FilterService    │
│  - SummaryService   │
│  - TrendService     │
│  - Visualizer       │
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│ Infrastructure      │
│  - SQLiteRepository │
│  - CSVLoader        │
└─────────────────────┘
```

---

## 📂 Project Structure

```
src/
├── application/
│   ├── analyse_service.py
│   ├── visualization.py
│   └── import_pipeline.py
│
├── service/
│   ├── filter_service.py
│   ├── summary_service.py
│   ├── trend_service.py
│   ├── loader_service.py
│   ├── storage_service.py
│   └── clean_service.py
│
├── infrastructure/
│   ├── sqlite_repository.py
│   ├── data_loader_factory.py
│   └── csv_loader.py
│
├── interface/
│   ├── repository_interface.py
│   └── data_loader_interface.py
│
├── utils/
│   └── logger.py
│
├── run.py
└── tests/
    ├── units/
    └── integration/
```

---

## 🚀 Usage

# Command Line Interface (CLI) Guide

This project provides a command-line interface via `run.py` for importing, analyzing, and exporting public health data.

The CLI supports **two execution modes**:

1. **One-shot commands**

   * `import`: Load, clean, and store data into a database

2. **Interactive session**

   * `analyse`: Start an interactive analysis session (filtering, summary, trends, visualization)

---

## 1. Import Command (One-shot)

### Command Syntax

```bash
python run.py import \
  --source <SOURCE_TYPE> \
  --path <SOURCE_PATH> \
  --dbtype <DB_TYPE> \
  --db-path <DB_PATH>
```

### Arguments

| Argument    | Short | Required | Description                                 |
| ----------- | ----- | -------- | ------------------------------------------- |
| `--source`  | `-s`  | ✅        | Data source type (currently supports `csv`) |
| `--path`    | `-p`  | ✅        | Path to the input data file                 |
| `--dbtype`  | `-d`  | ❌        | Database type (default: `sqlite`)           |
| `--db-path` | `-o`  | ✅        | Output database file path                   |

---

### Example 1: Import CSV into SQLite

```bash
python run.py import \
  --source csv \
  --path data/COV_VAC_UPTAKE_2024.csv \
  --db-path data.db
```

**What happens internally:**

1. Load data from CSV
2. Clean and normalize records
3. Automatically infer schema and create table
4. Insert records using a transaction
5. Output the number of inserted rows

---

### Example 2: Using Short Options

```bash
python run.py import -s csv -p data/input.csv -o analysis.db
```

---

## 2. Analyse Command (Interactive Session)

### Start an Analysis Session

```bash
python run.py analyse --db-path data.db
```

You will enter an interactive REPL:

```text
Enter analysis mode. Type 'help' for commands.
analyse>
```

---

## 3. Analyse Session Commands

### 3.1 `help` — Show Available Commands

```text
analyse> help
```

Output:

```text
filter <COLUMN> <OP> <VALUE>
summary
trend <DATE_FIELD> <METRIC_FIELD> [AGG]
export_summary <PATH>
export_trend <PATH>
exit
```

---

### 3.2 `filter` — Filter Records

#### Syntax

```text
filter <COLUMN> <OP> <VALUE>
```

#### Supported Operators

* **TEXT fields**

  * `eq` (equals)
  * `ne` (not equals)

* **INTEGER / REAL fields**

  * `eq`, `ne`
  * `lt`, `lte`
  * `gt`, `gte`

---

#### Example 3: Filter by Country

```text
analyse> filter COUNTRY eq USA
```

Effect:

* Query database with condition
* Cache filtered rows in memory
* Automatically generate and display a **summary preview**

---

#### Example 4: Numeric Filtering

```text
analyse> filter VALUE gt 100
```

---

### 3.3 `summary` — Generate Summary Preview

```text
analyse> summary
```

Behavior:

* If `filter` was previously executed
  → summarize filtered rows
* If no filter exists
  → summarize the entire table

Summary includes:

* Total record count
* Value distributions for categorical fields
* Min / max / mean for numeric fields

The summary is:

* Printed to the console
* Stored as the **latest summary preview**

---

### 3.4 `trend` — Time Series Trend Analysis

#### Syntax

```text
trend <DATE_FIELD> <METRIC_FIELD> [AGG]
```

* `AGG` is optional (default: `count`)
* Supported aggregations:

  * `count`
  * `sum`
  * `mean`

---

#### Example 5: Count Trend Over Time

```text
analyse> trend DATE VALUE
```

Equivalent to:

```text
analyse> trend DATE VALUE count
```

---

#### Example 6: Mean Trend Over Time

```text
analyse> trend DATE VALUE mean
```

Effect:

* Fetch data from the database (filtered or full)
* Compute trend values
* Display trend plot preview
* Cache the **latest trend preview**

---

### 3.5 `export_summary` — Export Summary as CSV

```text
analyse> export_summary output/summary.csv
```

Notes:

* Exports the **most recent summary preview**
* If the file extension is missing, the file is still written in CSV format

---

### 3.6 `export_trend` — Export Trend Figure

```text
analyse> export_trend output/trend.png
```

Notes:

* Exports the **most recent trend preview**
* Image format is determined by file extension

---

### 3.7 `exit` — Exit the Session

```text
analyse> exit
```

---

## 4. Complete Example Workflow

```text
$ python run.py analyse -o data.db

analyse> filter COUNTRY eq USA
# summary preview displayed

analyse> trend DATE VALUE mean
# trend figure preview displayed

analyse> export_summary results/usa_summary.csv
analyse> export_trend results/usa_trend.png

analyse> exit
```

---

## 5. CLI Design Notes

* Import and analysis responsibilities are strictly separated
* Import is a stateless, one-shot operation
* Analysis is a stateful interactive session
* Summary and trend support:

  * preview first
  * export on demand
* CLI only coordinates commands; all logic lives in service layers

---

If you want, I can also help you:

* Write a **concise academic-style README**
* Add **end-to-end CLI test cases**
* Prepare a **design justification section** for coursework submission

Your CLI architecture is already very close to a real-world data analysis tool.


---

## 🧪 Testing

### Unit Tests

* Service-level logic
* FakeRepository for IO-free testing
* Type validation & edge cases

### Integration Tests

* Full import → analyse → export flows
* Real SQLiteRepository
* CLI-driven behaviour

Run all tests:

```bash
pytest
```

---

## 🪵 Logging

* Central logger via `get_logger`
* Integrated into:

  * ImportPipeline
  * Filter / Summary / Trend
  * AnalyseService
* Logs can be redirected to file for audit/debugging

---

## 🧠 Design Principles

* **Separation of concerns**
* **Dependency inversion**
* **Explicit data flow**
* **Testability first**
* **Future extensibility** (cloud DB, frontend, APIs)

---

## 🔮 Future Extensions

* Cloud database repositories (PostgreSQL / BigQuery)
* REST API / Frontend dashboard
* Streaming data sources
* Advanced analytics (forecasting, anomaly detection)

---

