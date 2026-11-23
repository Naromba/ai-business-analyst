# AI Business Analyst Agent

An autonomous AI agent that analyzes business data, detects anomalies, generates visualizations, and produces business reports using Python, Ollama, and Qwen3.

## Overview

AI Business Analyst demonstrates how a local language model can autonomously select and execute Python tools to complete business analysis tasks.

Instead of following predefined steps, the agent interprets a user's request, selects relevant tools, evaluates their results, and generates a report.

## Features

- Autonomous AI-powered tool selection
- Revenue analysis by region, product, and year
- Year-over-year revenue comparison
- Data quality and anomaly detection
- Automatic chart generation
- AI-generated business reports
- Duplicate tool execution prevention
- Local AI execution with Ollama

## Tech Stack

- **Python** — Agent orchestration and data processing
- **Ollama** — Local LLM execution
- **Qwen3:4b** — AI reasoning and tool selection
- **Pandas** — Data analysis
- **Matplotlib** — Data visualization

## Available Tools

| Tool | Description |
|---|---|
| `explore_data` | Explores available datasets |
| `analyze_sales` | Analyzes sales by region, product, or year |
| `compare_years` | Compares revenue across equivalent periods |
| `check_data_quality` | Detects missing values, duplicates, and inconsistencies |
| `create_chart` | Generates revenue charts |

## Installation

**Prerequisites:** Python 3 and Ollama.

1. Clone the repository:

   `git clone https://github.com/Naromba/ai-business-analyst.git`

2. Navigate to the project:

   `cd ai-business-analyst`

3. Create and activate a virtual environment:

   `python3 -m venv .venv`

   `source .venv/bin/activate`

4. Install dependencies:

   `pip install -r requirements.txt`

5. Download the local AI model:

   `ollama pull qwen3:4b`

## Usage

Run the agent:

`python agent.py`

Example mission:

> Compare les revenus de 2025 et 2026 sur des périodes équivalentes, détecte les anomalies dans les données et génère un graphique des revenus par année. Présente ensuite tes conclusions et recommandations dans un rapport détaillé.

The agent selects the appropriate tools and generates its analysis without requiring step-by-step guidance.

Generated reports and charts are saved in the `reports/` directory.

## Limitations

- The local language model may occasionally repeat tool requests.
- Execution speed depends on the machine and model.
- AI-generated conclusions should be reviewed.
- All business datasets are synthetic and used for demonstration purposes.

## Future Improvements

- More robust decision-making
- Automated unit and integration tests
- Interactive dashboard
- Support for additional business datasets

## Author

Naromba Conde 