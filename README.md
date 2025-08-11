# Database-System-Principles

Welcome to the project portfolio for the NTU SC3020 module. This repository contains summaries and implementation artifacts for two major projects that explore both low-level and high-level aspects of modern database systems.

---

## Project 1: Storage and Indexing System for NBA Statistics

### Objective  
Design and implement core components of a database management system — specifically, on-disk storage management and an indexing mechanism using a B+ tree.

### Features

- **Storage Layer:**  
  - Stores and manages NBA game data from 2003–2022, sourced from a `.txt` dataset.  
  - Efficient block-based on-disk storage with customized block size per machine.  
  - Records are directly stored and retrieved through file I/O operations.

- **Indexing Layer:**  
  - Implements a persistent B+ tree stored on disk.  
  - Indexes records by the `FG_PCT_home` attribute (field goal percentage, home team).  
  - Supports both iterative insertion and bulk loading strategies.

- **Search & Query:**  
  - Efficiently supports range queries (e.g., `FG_PCT_home` between 0.6 and 0.9).  
  - Reports statistics like number of indexed nodes/blocks accessed and compares performance with brute-force scanning.  
  - Calculates aggregate statistics such as average `FG3_PCT_home` for matches.

### Deliverables  
- Clear documentation and illustrations of the storage design and B+ tree architecture.  
- Performance analysis with tabulated results.  
- Full source code and video demonstration.

> See the [Project 1 Report](./project1-report.pdf) for detailed design, results, and contributor information.

---

## Project 2: SQL to Pipe Syntax Converter for PostgreSQL

### Objective  
Create a tool that translates traditional SQL queries into pipe syntax — a more flexible, readable, and operation-focused SQL representation.

### Workflow

- **Dataset Setup:**  
  - Loads standard TPC-H benchmark datasets into a PostgreSQL database.  
  - Preprocessing scripts establish DB connections and run queries.

- **QEP Extraction:**  
  - Uses PostgreSQL’s `EXPLAIN (FORMAT JSON, ANALYZE)` to parse the full query execution plan (QEP).  
  - Extracts step-by-step operations in JSON, revealing the query execution pipeline.

- **Pipe Syntax Generation:**  
  - Recursively traverses the QEP tree to identify and represent popular SQL operations (e.g., WHERE, JOIN, AGGREGATE, ORDER BY, UNION) as sequential pipe operators.  
  - Outputs a clear, indented textual representation illustrating query data flow.

- **User Interface:**  
  - Interactive GUI built with `ttkbootstrap`.  
  - Allows users to enter PostgreSQL connection settings, input SQL queries, and view the translated pipe syntax, full QEP, and a visual QEP graph.

### Limitations  
- Handles the most common SQL operations; exotic operators may default to generic pipe syntax output.

### Deliverables  
- Comprehensive report describing the algorithm and QEP-to-pipe operator mapping.  
- Python scripts for SQL parsing and GUI operation.  
- Installation instructions and requirements included in the project folder.

---

## How to Run

Both projects have dedicated folders with source code and setup instructions.

- Refer to each project's README and installation guide for environment setup, including dependencies such as PostgreSQL, Python libraries, and Graphviz.  
- Demo videos are available via private cloud links illustrating key functionalities.

---

## Credits

Please refer to the individual project reports for detailed group contributions and references.

---

## Important Notes

- All source code is original and adheres to NTU’s academic integrity policy.  
- Do **not** share the code or demo videos outside the course context.  
- For issues or clarifications, please raise an issue in this repository or contact contributors privately via emails listed in the reports.
