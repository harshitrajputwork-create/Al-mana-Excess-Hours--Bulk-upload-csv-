import json
import os
import logging
import webbrowser
from api_client import TaqticsAPIClient
from csv_processor import CSVProcessor
from health_engine import HealthEngine
from email_generator import EmailGenerator
from email_sender import EmailSender
from dashboard_data import DashboardDataFormatter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_path='config.json'):
    if not os.path.exists(config_path):
        logging.error(f"Config file not found: {config_path}")
        return None
    with open(config_path, 'r') as f:
        return json.load(f)

def run_reporting_engine():
    print("\n--- Taqtics Implementation Intelligence Layer ---")
    config = load_config()
    if not config: return

    # 1. API Fetch
    api_cfg = config['api']
    acc_cfg = config['account']
    client = TaqticsAPIClient(api_cfg['subdomain'], api_cfg['username'], api_cfg['password'])
    
    from datetime import datetime, timedelta
    months_to_try = [
        datetime.now().strftime("%m-%Y"),
        (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%m-%Y")
    ]
    
    csv_data = ""
    selected_month = ""
    
    try:
        logging.info(f"Authenticating for {api_cfg['username']}...")
        client.authenticate()
        print("[✔] Authentication Successful")
        
        for month in months_to_try:
            logging.info(f"Attempting to fetch data for {month}...")
            csv_data = client.get_monthly_csv(acc_cfg['form_ids'], month)
            if csv_data.strip():
                selected_month = month
                break
        
        if not csv_data.strip():
            print("[x] No CSV data found for current or previous month.")
            return

        raw_rows = len(csv_data.splitlines()) - 1
        print(f"[✔] CSV Retrieved for {selected_month}: {raw_rows} total rows across selected forms")
    except Exception as e:
        logging.error(f"API Error: {e}")
        return

    # 2. Processing
    acc_cfg = config['account']
    logging.info(f"Processing data for account: {acc_cfg['name']}...")
    
    processor = CSVProcessor(
        csv_data, 
        store_entity_ids=acc_cfg.get('store_entity_ids'), 
        form_ids=acc_cfg.get('form_ids'),
        store_names=acc_cfg.get('store_names')
    )
    
    metrics = processor.process()
    if not metrics:
        print("[!] No rows matching the account filter were found.")
        return

    filtered_rows = metrics.get('total_submissions', 0)
    print(f"[✔] Filtered Data: {filtered_rows} matching rows found for {acc_cfg['name']}")

    # 3. Health Analysis
    health_engine = HealthEngine(metrics, config['risk_thresholds'])
    health_data = health_engine.evaluate()
    print(f"[✔] Health Classification: {health_data['status']} ({health_data['label']})")

    # 4. Generate Outputs
    logging.info("Generating reports...")
    
    # HTML Email
    email_gen = EmailGenerator(acc_cfg['name'], metrics, health_data)
    html_report = email_gen.generate()
    report_path = os.path.abspath('executive_summary.html')
    with open(report_path, 'w') as f:
        f.write(html_report)
    print(f"[✔] Executive Summary: {report_path}")

    # Dashboard JSON
    dashboard_fmt = DashboardDataFormatter(acc_cfg['name'], metrics, health_data)
    json_output = dashboard_fmt.to_json()
    json_path = os.path.abspath('dashboard_data.json')
    with open(json_path, 'w') as f:
        f.write(json_output)
    print(f"[✔] Dashboard Data: {json_path}")

    # 5. Email Delivery (Optional)
    email_cfg = config.get('email')
    if email_cfg and email_cfg.get('recipient'):
        sender = EmailSender(email_cfg)
        subject = f"Implementation Report: {acc_cfg['name']} | {health_data['status']}"
        success = sender.send(email_cfg['recipient'], subject, html_report)
        if success:
            print(f"[✔] Email Sent to: {email_cfg['recipient']}")
        else:
            print("[x] Email Delivery Skipped (Check SMTP config)")

    # 6. Open Dashboard
    print(f"Opening report in browser...")
    webbrowser.open(f"file://{report_path}")

    print("--------------------------------------------------\n")

if __name__ == "__main__":
    run_reporting_engine()
