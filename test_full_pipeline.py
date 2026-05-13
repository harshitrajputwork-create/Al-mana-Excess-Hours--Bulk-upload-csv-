import pandas as pd
from csv_processor import CSVProcessor
from health_engine import HealthEngine
from alignment_engine import AlignmentEngine
import io

def test_full_pipeline():
    print("--- Testing Full Reporting Pipeline ---")
    
    # Mock CSV data
    csv_content = """Submission Id,Submitted For,Store,Percentage compliance,Cash policy signed,Petty cash variance
1,2026-01-01 10:00:00,Store A,80,Yes,0
2,2026-01-02 10:00:00,Store A,85,Yes,0
3,2026-01-01 12:00:00,Store B,50,No,10
"""
    
    # 1. Processing
    processor = CSVProcessor(csv_content, store_entity_ids=["Store A", "Store B"], form_ids=["F1"])
    metrics = processor.process()
    print("[✔] CSVProcessor Success")
    
    # 2. Health
    health_engine = HealthEngine(metrics, {"completion_critical": 60, "compliance_critical": 75, "recency_days": 7})
    health_data = health_engine.evaluate()
    print(f"[✔] HealthEngine Success: {health_data['status']}")
    
    # 3. Alignment
    alignment_engine = AlignmentEngine(csv_content, manual_objective="Test Objective")
    alignment_data = alignment_engine.analyze_alignment()
    print(f"[✔] AlignmentEngine Success: {alignment_data['alignment_score']}%")
    print(f"    Inferred Objective: {alignment_data['objective']}")
    
    if alignment_data['recommendations']:
        print(f"    Top Tip: {alignment_data['recommendations'][0]}")

if __name__ == "__main__":
    test_full_pipeline()
