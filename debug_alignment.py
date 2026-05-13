from alignment_engine import AlignmentEngine
import pandas as pd
import io
import os

def debug_generation():
    print("--- Debugging Generation Logic ---")
    
    # Mock data that might cause issues
    csv_data = "Submission Id,Submitted For,Store,Percentage compliance\n" # Headers only
    manual_objective = "Improve sales"
    form_json_path = r"C:\Users\Harshit Rajput\Downloads\Herfy V\LPD New Audit Checklist for SHAWARMER.json"
    
    try:
        print("Initializing AlignmentEngine...")
        engine = AlignmentEngine(
            csv_data, 
            manual_objective=manual_objective,
            form_json_path=form_json_path if os.path.exists(form_json_path) else None
        )
        print("Analyzing alignment...")
        data = engine.analyze_alignment()
        print(f"Success! Score: {data['alignment_score']}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    debug_generation()
