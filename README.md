The **SQL Query Generator from Natural Language** is a developer-focused CLI utility that bridges human language and database schemas.

![Summary](https://github.com/user-attachments/assets/4e45a612-2840-472a-96fe-1c67ce00a575 "Note: Ignore vepython, it's just an alias.")

Instead of manually writing complex SQL statements, joining multiple tables, or remembering specific syntax quirks across different database engines, you simply provide your target database schema (`.sql` or inline text) and a plain-English question. The tool uses **Gemini 2.5 Flash** to analyze your schema and translate your request into a precise, syntax-checked SQL query complete with performance warnings, table dependencies, and a human-readable explanation.

---

### Breakdown of Each File

The project consists of three core components:

#### 1. `schemas.py` (The Data Contract & Output Schema)

This file uses **Pydantic V2** to define the strict data structure (`SQLGenerationResponse`) enforced on the Gemini API response. By passing this schema into `response_schema`, it guarantees that the output will return cleanly formatted and typed JSON every single time.

* **Fields Captured:** `sql_query`, `dialect`, `explanation`, `tables_involved`, and `potential_edge_cases`.

---

#### 2. `generator.py` (The Core CLI Engine)

This script manages the application logic, file parsing, API communication, error handling, and terminal presentation.

* **File & Schema Extraction:** Reads the database schema file or accepts inline SQL text string arguments.
* **Gemini API Integration:** Sends the schema and your natural language question to `gemini-2.5-flash` with strict JSON constraints and system prompts tailored for database administration.
* **Stderr Suppression:** Temporarily redirects `sys.stderr` during the API call to eliminate background SDK warnings and keep your terminal pristine.
* **Rich Terminal UI & Syntax Highlighting:** Uses Python's `rich` library to render color-coded metadata tables, explanatory panels, and **built-in SQL syntax highlighting** for the generated query.

---

#### 3. `schema.sql` (Sample Database Schema)

A sample SQL DDL file containing database table definitions (such as `users` and `orders` with foreign keys and constraints) used as input to test and demonstrate the query generator.
