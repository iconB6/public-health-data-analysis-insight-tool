# public-health-data-analysis-insight-tool
This is a Python-based data insights tool for a team of researchers analysing public health data (e.g., vaccination rates, disease outbreaks, or mental health reports).The goal is to support data access, filtering, cleaning, summarisation, and presentation


# 📦 Command-Line Interface (CLI)

This project includes a command-line interface for interacting with the full data pipeline:

**load → clean → store → filter → summarize → visualize**

The CLI entry point is:

```
src/cli.py
```

Run any CLI command using:

```
python src/cli.py <command> [options]
```

---

# 🚀 Available CLI Commands

---

## **1. `load` — Load raw data**

Load data from a specified source type (e.g., CSV).

### **Usage**

```bash
python src/cli.py load --type csv --path data/sample.csv
```

### **Arguments**

| Flag     | Description                 |
| -------- | --------------------------- |
| `--type` | Loader type (`csv`, `json`) |
| `--path` | Path to the raw data file   |

---

## **2. `clean` — Clean a dataset**

Applies the project’s data cleaning rules.

### **Usage**

```bash
python src/cli.py clean --input data/sample.csv --output data/cleaned.json
```

### **Arguments**

| Flag       | Description                  |
| ---------- | ---------------------------- |
| `--input`  | Raw dataset path             |
| `--output` | Output path for cleaned data |

---

## **3. `store` — Save cleaned data into storage**

Stores cleaned data using the configured storage backend.

### **Usage**

```bash
python src/cli.py store --input data/cleaned.json --engine local
```

### **Arguments**

| Flag       | Description                         |
| ---------- | ----------------------------------- |
| `--input`  | Path to cleaned dataset             |
| `--engine` | Storage backend (`local`, `memory`) |

---

## **4. `summarize` — Compute summary statistics**

Calculates count, mean, min, and max for a numeric metric.

### **Usage**

```bash
python src/cli.py summarize --input data/cleaned.json --metric value_1
```

### **Arguments**

| Flag       | Description             |
| ---------- | ----------------------- |
| `--input`  | Path to cleaned dataset |
| `--metric` | Metric to summarize     |

---

## **5. `trend` — Compute time-series trend (optionally visualize)**

Extracts a date-based trend from the dataset.

### **Usage**

```bash
python src/cli.py trend --input data/cleaned.json --date date --metric value_1 --plot
```

### **Arguments**

| Flag       | Description                             |
| ---------- | --------------------------------------- |
| `--input`  | Cleaned dataset path                    |
| `--date`   | Date field in dimensions (`YYYY-MM-DD`) |
| `--metric` | Numeric metric                          |
| `--plot`   | (Optional) Show matplotlib line chart   |

---

## **6. `group` — Group by a dimension**

Groups records by a dimension and computes aggregated statistics.

### **Usage**

```bash
python src/cli.py group --input data/cleaned.json --group country --metric value_1
```

### **Arguments**

| Flag       | Description                     |
| ---------- | ------------------------------- |
| `--input`  | Path to cleaned dataset         |
| `--group`  | Dimension key (`country`, etc.) |
| `--metric` | Numeric metric                  |

---

## **7. `visualize-table` — Display formatted table**

Shows the dataset as a pandas DataFrame.

### **Usage**

```bash
python src/cli.py visualize-table --input data/cleaned.json
```

### **Arguments**

| Flag      | Description       |
| --------- | ----------------- |
| `--input` | Path to data file |

---

# 🧩 Example Full Workflow

```bash
# Load raw CSV
python src/cli.py load --type csv --path data/sample.csv

# Clean it
python src/cli.py clean --input data/sample.csv --output data/cleaned.json

# Store results
python src/cli.py store --input data/cleaned.json --engine local

# Summary statistics
python src/cli.py summarize --input data/cleaned.json --metric value_1

# Time trend (with plotting)
python src/cli.py trend --input data/cleaned.json --date date --metric value_1 --plot

# Group by dimension
python src/cli.py group --input data/cleaned.json --group country --metric value_1

# Show formatted table
python src/cli.py visualize-table --input data/cleaned.json
```
