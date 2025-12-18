

---

# Public Health Data Analysis Insight Tool

A modular, testable data analysis tool for importing, cleaning, storing, analysing, and visualising public health datasets.
Designed with layered architecture, clear separation of concerns, and full unit/integration test coverage.

---

## 📌 Features

### Data Import (ETL)

* Load data from CSV (extensible to JSON / API / DB)
* Clean and validate raw data
* Store into SQLite or cloud databases
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
* Fully testable (FakeRepository + SQLite + cloud)
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
│  - CloudRepository  │
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
│   ├── cloud_repository.py
│   └── loaders/
│       ├── data_loader_factory.py
│       └── csv_loader.py
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
  --db-path analysis.db

python run.py import -s csv -p data/COV_VAC_UPTAKE_2024.csv -o analysis.db # Using Short Options
```

**What happens internally:**

1. Load data from CSV
2. Clean and normalize records
3. Automatically infer schema and create table
4. Insert records using a transaction
5. Output the number of inserted rows

---

### Example 2: Import CSV into Cloud Database (Postgres)

Warning: you should a Postgres DB on localhost first.

Start a local Postgres with Docker Compose (project includes `docker-compose.yml`):

```bash
docker-compose up -d
```
then you can:

```bash
python run.py import \
  --source csv \
  --path data/COV_VAC_UPTAKE_2024.csv \
  --dbtype cloud \
  --db-path "postgresql://test:pass@localhost:5432/testdb"

python run.py import -s csv -p data/COV_VAC_UPTAKE_2024.csv -d cloud -o postgresql://test:pass@localhost:5432/testdb # Using Short Options
```
---

## 2. Analyse Command (Interactive Session)

### Start an Analysis Session

```bash
python run.py analyse --db-path analysis.db

python run.py analyse -d cloud -o "postgresql://test:pass@localhost:5432/testdb" # cloud option
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
```

---

### 3.2 `filter` — Filter Records

#### Syntax

```text
filter [--from YYYY-MM-DD] [--to YYYY-MM-DD] COLUMN OP VALUE [COLUMN OP VALUE ...]
```

#### Supported Operators

* **TEXT fields**

  * `eq` (equals)
  * `ne` (not equals)

* **INTEGER / REAL fields**

  * `eq`, `ne`
  * `lt`, `lte` (<, <=)
  * `gt`, `gte` (>, >=)

---

#### Example 3: Filter by CATEGORICAL KEYWORDS

```text
analyse> filter COUNTRY eq AND
analyse> filter --from 2021-10-11 --to 2024-7-30 COUNTRY eq AND
analyse> filter COUNTRY eq AND GROUP eq old
```

Effect:

* Query database with condition
* Cache filtered rows in memory
* Automatically generate and display a **summary preview**

---

#### Example 4: Numeric Filtering

```text
analyse> filter POPULATION gt 10000
analyse> filter POPULATION gt 1000 POPULATION lt 10000
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
  trend DATE VALUE  [agg=mean]
                    [from=YYYY-MM-DD]
                    [to=YYYY-MM-DD]
                    [where COL OP VAL ...]
```

* `AGG` is optional (default: `count`)
* Supported aggregations:

  * `count`
  * `sum`
  * `mean`

---

#### Example 5: Count Trend Over Time

```text
analyse> trend DATE COVID_VACCINE_ADM_1D
```

Equivalent to:

```text
analyse> trend DATE COVID_VACCINE_ADM_1D agg=count
```

---

#### Example 6: Other Command

```text
analyse> trend DATE POPULATION agg=mean
analyse> trend DATE COVID_VACCINE_ADM_1D from=2023-01-01 to=2024-10-30
analyse> trend DATE COVID_VACCINE_ADM_1D where GROUP eq hcw
analyse> trend DATE COVID_VACCINE_ADM_1D where POPULATION lt 100000
```

Effect:

* Fetch data from the database (filtered or full)
* Compute trend values
* Display trend plot preview
* Cache the **latest trend preview**

---

### 3.5 `export_summary` — Export Summary as CSV

```text
analyse> export_summary results/summary.csv
```

Notes:

* Exports the **most recent summary preview**
* If the file extension is missing, the file is still written in CSV format

---

### 3.6 `export_trend` — Export Trend Figure

```text
analyse> export_trend results/trend.png
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
$ python run.py analyse -o analysis.db

analyse> filter COUNTRY eq AND
# summary preview displayed

analyse> trend DATE POPULATION agg=mean
# trend figure preview displayed

analyse> export_summary results/and_summary.csv
analyse> export_trend results/population_trend.png

analyse> exit
```

when using cloud database(on docker):

```text
$ docker-compose up -d
$ python run.py import -s csv -p data/COV_VAC_UPTAKE_2024.csv -d cloud -o postgresql://test:pass@localhost:5432/testdb
$ python run.py analyse -d cloud -o "postgresql://test:pass@localhost:5432/testdb"

analyse> filter COUNTRY eq AND
# summary preview displayed

analyse> trend DATE POPULATION agg=mean
# trend figure preview displayed

analyse> export_summary results/and_summary.csv
analyse> export_trend results/population_trend.png

analyse> exit

$ docker-compose down
```

---

---

## 🧪 Testing

### Unit Tests

* Service-level logic
* FakeRepository for IO-free testing
* Type validation & edge cases

### Integration Tests

* Full import → analyse → export flows
* Real SQLiteRepository/CloudRepository
* CLI-driven behaviour

Run all tests:

```bash
pytest
```
Note: Make sure you are maintaining a connection with the cloud database; 
      otherwise, test_cloud_repository.py will fail.
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
* REST API / Frontend dashboard
* Streaming data sources
* Advanced analytics (forecasting, anomaly detection)

---

