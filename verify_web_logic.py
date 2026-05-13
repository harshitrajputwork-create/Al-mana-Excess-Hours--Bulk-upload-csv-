from api_client import TaqticsAPIClient
from csv_processor import CSVProcessor
from health_engine import HealthEngine
import json

# Simulation script to verify store-wise logic
def verify_web_logic():
    print("--- Verifying Web Logic (Store-wise) ---")
    
    # Use real credentials for a quick test of the data fetching and processing flow
    subdomain = "impl4.taqtics.co"
    email = "harshit.rajput@taqtics.co"
    password = "Sahkir12345@"
    form_ids = ["IMPFORM115", "IMPFORM127"]
    month = "01-2026"
    
    client = TaqticsAPIClient(subdomain, email, password)
    client.authenticate()
    print("[✔] Auth Success")
    
    csv_data = client.get_monthly_csv(form_ids, month)
    print(f"[✔] CSV Fetch Success ({len(csv_data)} chars)")
    
    # Test with strict filtering (optional)
    store_ids = [] # Let it auto-detect for verification
    processor = CSVProcessor(csv_data, store_entity_ids=store_ids, form_ids=form_ids)
    metrics = processor.process()
    
    print("\n[✔] Processing Success")
    print(f"Total Submissions: {metrics['total_submissions']}")
    print(f"Store Breakdown (Count: {len(metrics['store_breakdown'])}):")
    
    for s_id, s_metrics in list(metrics['store_breakdown'].items())[:3]:
        print(f"  - {s_id}: {s_metrics['submissions']} subs, {s_metrics['avg_compliance']:.1f}% comp")
        
    health_engine = HealthEngine(metrics, {
        "completion_critical": 60,
        "compliance_critical": 75,
        "recency_days": 7
    })
    health_data = health_engine.evaluate()
    
    print(f"\n[✔] Health Assessment: {health_data['status']}")
    print(f"Store Health Sample: {list(health_data['store_health'].items())[:3]}")

if __name__ == "__main__":
    verify_web_logic()
