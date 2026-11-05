# Automated Analytics Reporting Pipeline

A Python-based analytics pipeline for automated data extraction, validation, KPI calculation, visualization, and report generation.

The project simulates an analytics workflow for a lending business and demonstrates practical skills in Python, Google BigQuery, pandas, data visualization, reporting automation, and optional AI-assisted analysis.

## Features

- **Data extraction:** Load application data from Google BigQuery, with a fallback to local Excel files.
- **Data validation:** Check required columns, numeric values, dates, and application statuses.
- **Data processing:** Clean and aggregate records using pandas and NumPy.
- **KPI calculation:** Analyze applications, issued loans, issuance amounts, average issuance amounts, and conversion rates.
- **Month-over-month analysis:** Compare monthly results and identify traffic sources contributing to performance changes.
- **Data visualization:** Generate analytical charts using Matplotlib.
- **Automated reporting:** Export results to Excel and PDF.
- **AI-assisted insights:** Optional OpenAI API integration for analytical summaries.
- **Fallback analysis:** Generate rule-based insights when AI is disabled or unavailable.
- **Scheduling:** Support daily execution at 09:00 using macOS `launchd`.

## Tech Stack

- Python
- pandas and NumPy
- Google BigQuery
- Matplotlib
- openpyxl
- ReportLab
- OpenAI API (optional)
- python-dotenv
- Git

## Project Structure

```text
report_automation/
├── main.py
├── ai_analysis.py
├── generate_data.py
├── tests/
│   ├── __init__.py
│   ├── test_ai_module.py
│   └── test_ukrainian_pdf.py
├── requirements.txt
├── .env.example
├── .gitignore
├── com.reportautomation.daily.example.plist
└── README.md
```

The `data/` and `output/` directories are used locally and excluded from version control.

## Installation

Clone the repository and navigate to the project directory.

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a local environment configuration:

```bash
cp .env.example .env
```

Update the `.env` file with your own configuration.

## Environment Configuration

The project uses environment variables to configure BigQuery and optional AI integration.

Example `.env`:

```dotenv
# Google BigQuery configuration
BIGQUERY_PROJECT_ID=your-google-cloud-project-id
BIGQUERY_DATASET=report_automation
BIGQUERY_TABLE=applications

# Optional OpenAI integration
USE_AI=false
OPENAI_API_KEY=
```

By default, AI-generated insights are disabled, so no OpenAI API calls are made.

**Never commit real API keys, credentials, or private data to GitHub.**

## Data Sources

### Google BigQuery

The pipeline can load data directly from a Google BigQuery table.

BigQuery connection settings are configured through environment variables:

- `BIGQUERY_PROJECT_ID`
- `BIGQUERY_DATASET`
- `BIGQUERY_TABLE`

Google Cloud credentials with permission to query the configured dataset are required.

The current pipeline attempts to load data from BigQuery first and switches to Excel if the BigQuery request fails.

### Local Excel Files

To use local Excel files directly, change the source setting in `main.py`:

```python
source = 'excel'
```

Place compatible `.xlsx` files in the local `data/` directory.

### Expected Input Schema

| Column | Description |
|---|---|
| `user_id` | User identifier |
| `source` | Acquisition or traffic source |
| `status` | Application status (`issued` or `rejected`) |
| `amount` | Application amount |
| `created_at` | Application creation date |

The pipeline validates the required columns and checks numeric values, dates, and application statuses before processing.

## Analytics and KPIs

The pipeline calculates:

- Total applications
- Issued applications
- Issuance conversion rate
- Total issued amount
- Average issued amount
- Monthly changes in issued amounts
- Performance differences across traffic sources

Monthly comparisons help identify positive and negative contributions to overall performance.

## Data Visualizations

Three charts are generated automatically:

1. **Monthly Issued Amount** — total issued amount over time.
2. **Conversion by Source** — issuance conversion rate across traffic sources.
3. **Applications vs Issued** — comparison of application and issuance counts by source.

Charts are saved as PNG files and included in the PDF report.

## Running the Pipeline

Execute:

```bash
python main.py
```

The pipeline performs the following steps:

1. Loads data from BigQuery or Excel.
2. Validates and prepares the dataset.
3. Calculates KPIs and monthly comparisons.
4. Generates charts.
5. Exports an Excel report.
6. Produces analytical insights.
7. Generates a PDF report.

### Output Files

Generated files are stored in the `output/` directory:

```text
output/
├── report.xlsx
├── test_report.pdf
├── monthly_amount.png
├── conversion_by_source.png
└── applications_vs_issued.png
```

## AI-Assisted Analysis

The project includes an optional OpenAI integration implemented in `ai_analysis.py`.

When enabled, the module prepares structured analytical data and sends it to the OpenAI API to generate a written summary.

To enable the integration, configure:

```dotenv
USE_AI=true
OPENAI_API_KEY=your_api_key_here
```

When AI is disabled or an API request fails, the pipeline uses rule-based analytical insights instead.

The AI integration has been tested using a simulated API client. Live OpenAI API execution has not yet been verified.

OpenAI API usage may incur additional charges.

## Testing

The project includes tests for the AI analysis module and Ukrainian PDF rendering.

Run:

```bash
python -m tests.test_ai_module
python -m tests.test_ukrainian_pdf
```

The AI tests use a simulated client and do not require paid API requests.

## Scheduling and Automation

The pipeline supports automated daily execution using macOS `launchd`.

A scheduling template is provided:

```text
com.reportautomation.daily.example.plist
```

The template is configured for daily execution at **09:00**.

To configure scheduling:

1. Copy the example `.plist` file.
2. Replace the placeholder paths with absolute paths to your project and Python interpreter.
3. Ensure the `output/` directory exists.
4. Install and load the configuration using macOS `launchctl`.

The machine-specific scheduling configuration is excluded from version control.

## Limitations and Future Improvements

- Make PDF font handling cross-platform.
- Handle datasets containing fewer than two reporting periods.
- Add more comprehensive data validation and automated tests.
- Add continuous integration with GitHub Actions.
- Verify live OpenAI API execution.
- Improve configuration of data-source selection.

## Project Purpose

This portfolio project demonstrates an end-to-end analytics automation workflow, including data extraction, validation, transformation, KPI calculation, visualization, report generation, and integration with external services.

It reflects practical skills relevant to Data Analyst, Product Analyst, Marketing Analyst, and BI Analyst roles.