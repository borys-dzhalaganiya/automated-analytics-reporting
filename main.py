import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from ai_analysis import get_report_analysis
from pathlib import Path
from google.cloud import bigquery
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Spacer
from reportlab.platypus import Table
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from xml.sax.saxutils import escape

BASE_DIR = Path(__file__).resolve().parent

def create_charts(report):

    monthly = report.groupby(
        'year_month', as_index=False
    ).agg(
        total_amount=('total_amount', 'sum')
    )

    monthly = monthly.sort_values('year_month')

    plt.figure(figsize=(10, 5))

    plt.plot(monthly['year_month'], monthly['total_amount'])

    plt.title('Monthly Issued Amount')
    plt.xlabel('Month')
    plt.ylabel('Amount')

    plt.savefig(BASE_DIR / 'output' / 'monthly_amount.png')
    plt.close()

    sources = report.groupby(
            'source', as_index=False
        ).agg(
            applications=('users', 'sum'),
            issued=('is_issued', 'sum')
        )

    sources['conversion'] = (
    sources['issued'] / sources['applications'] * 100
    ).round(2)

    plt.figure(figsize=(10, 5))

    plt.bar(sources['source'], sources['conversion'])

    plt.title('Conversion by Source')
    plt.xlabel('Source')
    plt.ylabel('Conversion (%)')

    plt.savefig(BASE_DIR / 'output' / 'conversion_by_source.png')
    plt.close()

    x = np.arange(len(sources))
    width = 0.35

    plt.figure(figsize=(10, 5))

    plt.bar(
        x - width / 2,
        sources['applications'],
        width,
        label='Applications'
    )

    plt.bar(
    x + width / 2,
        sources['issued'],
        width,
        label='Issued'
    )

    plt.xticks(x, sources['source'])
    plt.title('Applications vs Issued by Source')
    plt.ylabel('Count')
    plt.xlabel('Traffic Source')
    plt.legend()

    plt.savefig(BASE_DIR / 'output' / 'applications_vs_issued.png')
    plt.close()

def load_from_bigquery():
    load_dotenv(BASE_DIR / ".env")

    project_id = os.getenv("BIGQUERY_PROJECT_ID")
    dataset_id = os.getenv("BIGQUERY_DATASET", "report_automation")
    table_id = os.getenv("BIGQUERY_TABLE", "applications")

    if not project_id:
        raise ValueError("BIGQUERY_PROJECT_ID is not configured")

    client = bigquery.Client(project=project_id)

    table_path = f"{project_id}.{dataset_id}.{table_id}"

    query = f"""
        SELECT *
        FROM `{table_path}`
    """

    df = client.query(query).to_dataframe()

    return df

def load_excel_files(folder_path):

    folder = Path(folder_path)
    files = list(folder.glob('*.xlsx'))

    dataframes = []

    for file in files:
        try:
            df = pd.read_excel(file)
            if validate_data(df):
                dataframes.append(df)
            else:
                print('WARNING: Invalid file skipped: ', file.name)
        except Exception as r:
            print('Failed: ', file.name)
            print('Reason: ', r)

    print('Found files:', len(files))
    print('Successfully loaded:', len(dataframes))
    print('Skipped: ', len(files) - len(dataframes))

    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    
    print('Dataframes is empty')
    return None

def validate_data(df):

    required_columns = ["user_id",
    "source",
    "status",
    "amount",
    "created_at"]

    allowed_statuses = ['issued', 'rejected']

    for column in required_columns:
        if column not in df.columns:
            print('Missing column: ', column)
            return False
        
    amount_chek = pd.to_numeric(df['amount'], errors='coerce')
    
    if amount_chek.isna().any():
        print('Invalid amount data')
        return False
    
    date_check = pd.to_datetime(df['created_at'], errors='coerce')

    if date_check.isna().any():
        print('Invalid date data')
        return False
    
    if not df['status'].isin(allowed_statuses).all():
        print('Invalid status')
        return False

    return True

def prepare_data(df):

    df['created_at'] = pd.to_datetime(df['created_at'])
    df['year_month'] = df['created_at'].dt.strftime('%Y-%m')
    df['source'] = df['source'].str.strip().str.lower()

    return df

def create_report(df):

    df['issued'] = np.where(df['status'] == 'issued', 1, 0)
    df['issued_amount'] = np.where(df['status'] == 'issued', df['amount'], np.nan)

    report = df.groupby(['source','year_month'], as_index=False).agg(
        users = ('user_id', 'count'),
        is_issued = ('issued', 'sum'),
        total_amount = ('issued_amount', 'sum'),
        avg_amount = ('issued_amount', 'mean')
    )

    report['conversion'] = report['is_issued'] / report['users'] * 100

    report['conversion'] = report['conversion'].round(2)
    report['avg_amount'] = report['avg_amount'].round(2)

    report['avg_amount'] = report['avg_amount'].fillna(0)

    report = report.sort_values(['source', 'year_month'])
    report['prev_amount'] = report.groupby('source')['total_amount'].shift(1)
    report['amount_change'] = report['total_amount'] - report['prev_amount']
    report['amount_change_pct'] = np.where(report['prev_amount'] == 0, np.nan, (report['amount_change'] / report['prev_amount'] * 100).round(2))

    return report

def generate_insights(report):

    monthly = report.groupby(
        'year_month', as_index=False
    ).agg(
        total_amount=('total_amount', 'sum')
    )

    monthly = monthly.sort_values('year_month')

    monthly['prev_month'] = monthly['total_amount'].shift(1)

    monthly['change_pct'] = (
        (monthly['total_amount'] - monthly['prev_month'])
        / monthly['prev_month'] * 100
    ).round(2)

    monthly['trend'] = np.where(
        monthly['change_pct'].isna(),
        'No previous period',
        np.where(
            monthly['change_pct'] > 0,
            'issued amount increased',
            np.where(
                monthly['change_pct'] < 0,
                'issued amount decreased',
                'issued amount remained unchanged'
            )
        )
    )

    latest = monthly.iloc[-1]

    month = latest['year_month']
    change = latest['change_pct']
    trend = latest['trend']

    if pd.isna(change):
        message = f'In {month}, no previous period available for comparison.'
    elif change == 0:
        message = f'In {month}, {trend.lower()}.'
    else:
        message = f'In {month}, {trend.lower()} by {abs(change):.2f}%.'

    print(message)

    return monthly, message

def create_pdf(report, message):
    total_applications = report['users'].sum()
    total_issued = report['is_issued'].sum()
    total_conversion = round(
        total_issued / total_applications * 100, 2
    ) if total_applications > 0 else 0

    elements = []

    pdf = SimpleDocTemplate("output/test_report.pdf")
    styles = getSampleStyleSheet()

    font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"

    if "ArialUnicode" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(
            TTFont("ArialUnicode", font_path)
        )

    styles["Normal"].fontName = "ArialUnicode"

    data = [
        ['Metric', 'Value'],
        ['Applications', int(total_applications)],
        ['Issued', int(total_issued)],
        ['Conversion', f'{total_conversion:.2f}%']
    ]

    table = Table(data)

    elements.append(Paragraph("Automated Analytics Report", styles["Title"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Key Performance Indicators", styles["Title"]))
    elements.append(Spacer(1, 20))
    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Analytical Insights", styles["Heading2"]))

    safe_message = escape(message).replace("\n", "<br/>")

    elements.append(Paragraph(safe_message, styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(Image(str(BASE_DIR / 'output' / 'monthly_amount.png'), width=450, height=225))
    elements.append(Spacer(1, 20))
    elements.append(Image(str(BASE_DIR / 'output' / "conversion_by_source.png"), width=450, height=225))
    elements.append(Spacer(1, 20))
    elements.append(Image(str(BASE_DIR / 'output' / "applications_vs_issued.png"), width=450, height=225))

    pdf.build(elements)

def analyze_sources(report):

    pivot = report.pivot_table(
        index='source',
        columns='year_month',
        values='total_amount',
        aggfunc='sum',
        fill_value=0
    )

    pivot = pivot.sort_index(axis=1)

    latest_month = pivot.columns[-1]
    previous_month = pivot.columns[-2]

    pivot['change'] = pivot[latest_month] - pivot[previous_month]

    worst_source = pivot['change'].idxmin()
    worst_change = pivot['change'].min()

    if worst_change < 0:
        min_text = f'The largest negative contribution came from {worst_source}: {worst_change}'
    else:
        min_text = 'No traffic source showed a decline'

    best_source = pivot['change'].idxmax()
    best_change = pivot['change'].max()

    if best_change > 0:
        max_text = f'The largest positive contribution came from {best_source}: {best_change}'
    else:
        max_text = 'No traffic source showed an increase.'

    print(min_text)
    print(max_text)

    insights = {
            'latest_month': latest_month,
            'previous_month': previous_month,
            'worst_source': worst_source,
            'worst_change': float(worst_change),
            'best_source': best_source,
            'best_change': float(best_change)
        }

    return pivot, insights

def main():
    source = 'bigquery'

    try:
        if source == 'bigquery':
            print('Loading data from BigQuery...')

            try:
                df = load_from_bigquery()
                data_source = 'BigQuery'

            except Exception as e:
                print('BigQuery failed:', e)
                print('Switching to Excel...')

                df = load_excel_files(BASE_DIR / 'data')
                data_source = 'Excel'

        elif source == 'excel':
            print('Loading data from Excel...')
            df = load_excel_files(BASE_DIR / 'data')
            data_source = 'Excel'

        else:
            print('Unknown data source:', source)
            raise SystemExit(1)

    except Exception as e:
        print('Failed loading data')
        print('Reason:', e)
        raise SystemExit(1)

    if df is None or df.empty:
        print('No data')
        raise SystemExit(1)

    if not validate_data(df):
        print('Data validation failed')
        raise SystemExit(1)

    try:
        clean_df = prepare_data(df)

    except Exception as e:
        print('Failed preparing data')
        print('Reason:', e)
        raise SystemExit(1)

    try:
        report = create_report(clean_df)

    except Exception as e:
        print('Failed creating report')
        print('Reason:', e)
        raise SystemExit(1)

    output_folder = BASE_DIR / 'output'
    output_folder.mkdir(parents=True, exist_ok=True)

    try:
        create_charts(report)
    except Exception as e:
        print('Failed creating charts')
        print('Reason:', e)
        raise SystemExit(1)

    report_path = output_folder / 'report.xlsx'

    try:
        report.to_excel(report_path, index=False)

        print('Report successfully saved:', report_path)
        print('Data source:', data_source)

    except Exception as e:
        print('Failed to save report')
        print('Reason:', e)
        raise SystemExit(1)
    
    monthly, message = generate_insights(report)

    pivot, insights = analyze_sources(report)

    load_dotenv()

    use_ai = os.getenv("USE_AI", "false").lower() == "true"
    api_key = os.getenv("OPENAI_API_KEY")

    client = None

    if use_ai and api_key and api_key != "test_key_123":
        client = OpenAI(api_key=api_key)

    message = get_report_analysis(
        report=report,
        pivot=pivot,
        insights=insights,
        client=client
    )

    json_text = json.dumps(insights, indent=4)
    print(json_text)
    restored_data = json.loads(json_text)

    print(insights)
    
    try:
        create_pdf(report, message)
        print('PDF successfully created')

    except Exception as e:
        print('Failed creating PDF')
        print('Reason:', e)
        raise SystemExit(1)

if __name__ == '__main__':
    main()