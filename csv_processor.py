import pandas as pd
import io
from datetime import datetime, timedelta

class CSVProcessor:
    def __init__(self, csv_content, store_entity_ids=None, form_ids=None, store_names=None):
        self.raw_data = pd.read_csv(io.StringIO(csv_content))
        self.store_entity_ids = store_entity_ids or []
        self.form_ids = form_ids or []
        self.store_names = store_names or []
        self.processed_df = None

    def process(self):
        """
        Filters and processes the raw CSV data with dynamic schema detection.
        """
        if self.raw_data.empty:
            return None

        df = self.raw_data.copy()
        df.columns = [c.strip() for c in df.columns]

        # Dynamic Schema Detection
        potential_entity_cols = ['entityId', 'store_entity_id', 'storeId', 'Store', 'Entity Name', 'Store ID']
        potential_name_cols = ['store_name', 'Store', 'Entity Name', 'name']
        potential_form_cols = ['form_id', 'formId', 'Form ID', 'form_name']
        potential_date_cols = ['Submitted For', 'submission_date', 'created_at', 'Submission Date', 'Created At', 'date']
        potential_compliance_cols = ['Percentage compliance', 'percentage_compliance', 'compliance_percentage', 'score', 'Compliance %']

        # Find best matches
        entity_col = next((c for c in potential_entity_cols if c in df.columns), None)
        name_col = next((c for c in potential_name_cols if c in df.columns), None)
        form_col = next((c for c in potential_form_cols if c in df.columns), None)
        date_col = next((c for c in potential_date_cols if c in df.columns), None)
        compliance_col = next((c for c in potential_compliance_cols if c in df.columns), None)

        if not date_col:
            raise ValueError(f"Required column (Date) not found in CSV. Found: {df.columns.tolist()}")

        # 1. Filter by Form IDs (only if column exists)
        if form_col:
            df = df[df[form_col].astype(str).isin(self.form_ids)]

        # 2. Filter by Account (ID or Name)
        if self.store_entity_ids and entity_col:
            df = df[df[entity_col].astype(str).isin([str(x) for x in self.store_entity_ids])]
        elif self.store_names and name_col:
            # Flexible name matching (case-insensitive substring)
            pattern = '|'.join(self.store_names)
            df = df[df[name_col].str.contains(pattern, case=False, na=False)]

        # Since we might not have store_names in __init__, let's assume filtering happened via entityId
        # unless we explicitly add store_names support. Let's add it.
        
        # Note: I'll update __init__ to accept store_names in a moment.

        if df.empty:
            return None

        # Parse dates
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        df = df.sort_values(by=date_col)

        self.processed_df = df
        return self.calculate_metrics(date_col, compliance_col, entity_col or name_col)

    def get_store_breakdown(self, date_col, compliance_col, entity_col):
        """
        Calculates metrics for each individual store.
        """
        if self.processed_df is None or self.processed_df.empty:
            return {}

        store_data = {}
        for entity_id, group in self.processed_df.groupby(entity_col):
            last_sub = group[date_col].max()
            comp_vals = group[compliance_col] if compliance_col and compliance_col in group else pd.Series([0]*len(group))
            
            store_data[str(entity_id)] = {
                "submissions": len(group),
                "avg_compliance": comp_vals.mean(),
                "last_submission": last_sub.strftime("%Y-%m-%d %H:%M:%S")
            }
        return store_data

    def calculate_metrics(self, date_col, compliance_col, entity_col):
        if self.processed_df is None or self.processed_df.empty:
            return None

        first_submission = self.processed_df[date_col].min()
        last_submission = self.processed_df[date_col].max()
        
        # Fallback for compliance if not found
        compliance_values = self.processed_df[compliance_col] if compliance_col and compliance_col in self.processed_df else pd.Series([0]*len(self.processed_df))
        
        metrics = {
            "total_submissions": len(self.processed_df),
            "avg_compliance": compliance_values.mean(),
            "store_coverage": (self.processed_df[entity_col].nunique() / len(self.store_entity_ids)) if (self.store_entity_ids and entity_col) else (100.0 if not self.processed_df.empty else 0),
            "last_submission_date": last_submission.strftime("%Y-%m-%d %H:%M:%S"),
            "weekly_metrics": [],
            "store_breakdown": self.get_store_breakdown(date_col, compliance_col, entity_col)
        }
        
        # Ensure store_coverage doesn't exceed 100 if we have a target list
        if isinstance(metrics["store_coverage"], float) and metrics["store_coverage"] <= 1.0:
            metrics["store_coverage"] *= 100

        # Weekly cumulative calculation
        week_num = 1
        current_now = datetime.now()
        
        while True:
            week_end = first_submission + timedelta(days=7 * week_num)
            
            # Cumulative data up to week_end
            cumulative_df = self.processed_df[self.processed_df[date_col] <= week_end]
            
            if not cumulative_df.empty:
                comp_subset = cumulative_df[compliance_col] if compliance_col and compliance_col in cumulative_df else pd.Series([0]*len(cumulative_df))
                
                coverage = (cumulative_df[entity_col].nunique() / len(self.store_entity_ids)) if (self.store_entity_ids and entity_col) else 1.0
                if coverage <= 1.0: coverage *= 100

                metrics["weekly_metrics"].append({
                    "week": week_num,
                    "end_date": week_end.strftime("%Y-%m-%d"),
                    "cumulative_submissions": len(cumulative_df),
                    "avg_compliance": comp_subset.mean(),
                    "store_coverage": coverage
                })
            
            if week_end > last_submission and week_end > current_now:
                break
            
            if week_num > 52: # Safety break
                break
                
            week_num += 1

        return metrics
