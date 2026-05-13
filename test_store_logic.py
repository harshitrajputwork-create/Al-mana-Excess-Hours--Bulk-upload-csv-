import pandas as pd
from csv_processor import CSVProcessor
from health_engine import HealthEngine
import io

def test_store_wise_logic():
    print("--- Testing Store-wise Processing Logic ---")
    
    # Mock CSV data with two different stores
    csv_content = """Submission Id,Submitted For,Store,Percentage compliance
1,2026-01-01 10:00:00,Store A,80
2,2026-01-02 10:00:00,Store A,85
3,2026-01-01 12:00:00,Store B,50
4,2026-01-05 12:00:00,Store B,55
"""
    
    # Initialize processor
    processor = CSVProcessor(csv_content, store_entity_ids=["Store A", "Store B"], form_ids=["F1"])
    metrics = processor.process()
    
    # Verify overall metrics
    print(f"Overall Submissions: {metrics['total_submissions']} (Expected: 4)")
    print(f"Overall Compliance: {metrics['avg_compliance']:.1f}% (Expected: 67.5%)")
    
    # Verify store breakdown
    breakdown = metrics['store_breakdown']
    print(f"Stores found: {list(breakdown.keys())}")
    
    for s_id, s_metrics in breakdown.items():
        print(f" {s_id}: {s_metrics['submissions']} subs, {s_metrics['avg_compliance']:.1f}% comp")
        
    # Verify health evaluation
    health_engine = HealthEngine(metrics, {
        "completion_critical": 60,
        "compliance_critical": 75,
        "recency_days": 7
    })
    health_data = health_engine.evaluate()
    
    print(f"Overall Health: {health_data['status']} ({health_data['label']})")
    for s_id, s_status in health_data['store_health'].items():
        print(f" {s_id} Health: {s_status['status']} ({s_status['label']})")

if __name__ == "__main__":
    test_store_wise_logic()
