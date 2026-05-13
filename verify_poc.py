import json
import os
import pandas as pd
from datetime import datetime, timedelta
from csv_processor import CSVProcessor
from health_engine import HealthEngine
from email_generator import EmailGenerator
from dashboard_data import DashboardDataFormatter

def generate_mock_csv():
    """
    Generates a mock CSV string for SHAWARMER account.
    Forms: IMPFORM115, IMPFORM127
    Stores: 101, 102, 103 (3 stores)
    """
    base_date = datetime.now() - timedelta(days=20)
    data = []
    
    # Week 1 entries
    for i in range(5):
        data.append({
            "submission_date": (base_date + timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "entityId": 101 if i % 2 == 0 else 102,
            "form_id": "IMPFORM115",
            "compliance_percentage": 85 - i
        })

    # Week 2 entries
    for i in range(5, 12):
        data.append({
            "submission_date": (base_date + timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "entityId": 103 if i % 3 == 0 else 101,
            "form_id": "IMPFORM127",
            "compliance_percentage": 70 + i
        })

    df = pd.DataFrame(data)
    return df.to_csv(index=False)

def test_poc_flow():
    print("--- Starting POC Verification ---")
    
    # Mock Config
    config = {
        "account": {
            "name": "SHAWARMER (MOCK)",
            "store_entity_ids": [101, 102, 103],
            "form_ids": ["IMPFORM115", "IMPFORM127"]
        },
        "risk_thresholds": {
            "completion_critical": 60,
            "compliance_critical": 75,
            "recency_days": 7
        }
    }

    # 1. Mock Data
    csv_content = generate_mock_csv()
    print("Generated Mock CSV data.")

    # 2. Process
    processor = CSVProcessor(csv_content, config['account']['store_entity_ids'], config['account']['form_ids'])
    metrics = processor.process()
    print(f"Processed Metrics: {metrics['total_submissions']} total submissions found.")
    print(f"Store Coverage: {metrics['store_coverage']:.1f}%")

    # 3. Health
    health_engine = HealthEngine(metrics, config['risk_thresholds'])
    health_data = health_engine.evaluate()
    print(f"Health Status: {health_data['status']} ({health_data['label']})")
    if health_data['risks']:
        print(f"Risks Detected: {health_data['risks']}")

    # 4. Outputs
    print("Generating HTML report...")
    email_gen = EmailGenerator(config['account']['name'], metrics, health_data)
    html_report = email_gen.generate()
    with open('verify_poc_summary.html', 'w') as f:
        f.write(html_report)
    
    print("Generating JSON dashboard data...")
    dashboard_fmt = DashboardDataFormatter(config['account']['name'], metrics, health_data)
    json_output = dashboard_fmt.to_json()
    with open('verify_poc_data.json', 'w') as f:
        f.write(json_output)

    print("--- Verification Complete ---")
    print(f"Check 'verify_poc_summary.html' and 'verify_poc_data.json' for results.")

if __name__ == "__main__":
    test_poc_flow()
