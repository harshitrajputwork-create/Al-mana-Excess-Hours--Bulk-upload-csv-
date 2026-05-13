import json
import logging
import pandas as pd
import io
import re

class AlignmentEngine:
    def __init__(self, csv_data, manual_objective=None, form_json_path=None):
        """
        :param csv_data: Raw CSV string from API.
        :param manual_objective: Optional user-provided objective.
        :param form_json_path: Optional path to form JSON.
        """
        self.csv_df = pd.read_csv(io.StringIO(csv_data))
        self.manual_objective = manual_objective
        
        # Load form JSON if exists
        self.form_json = None
        if form_json_path:
            try:
                with open(form_json_path, 'r', encoding='utf-8') as f:
                    self.form_json = json.load(f)
            except Exception as e:
                logging.error(f"Error loading form JSON: {e}")

        # Extract Questions (Headers)
        self.questions = self._extract_questions()
        
        # Pillars & Keyword Mapping
        self.pillar_keywords = {
            "Financial Integrity": ["cash", "money", "safe", "wallet", "sale", "deposit", "petty", "invoice", "receipt", "variance"],
            "Inventory & Stock": ["stock", "inventory", "waste", "expired", "chiller", "freezer", "fifo", "count", "transfer"],
            "Facility & Safety": ["maintenance", "it", "facility", "cctv", "camera", "clean", "hygiene", "staff", "attendance"],
            "Operational Compliance": ["policy", "procedure", "audit", "schedule", "manager", "timing", "daily", "operation"]
        }
        
    def _extract_questions(self):
        """
        Extracts question-like headers from the CSV.
        """
        # Exclude common metadata columns
        exclude = ["submission id", "submitted for", "store", "entity", "date", "created", "status", "percentage", "compliance"]
        questions = []
        for col in self.csv_df.columns:
            if not any(ex in col.lower() for ex in exclude):
                questions.append(col)
        return questions

    def _infer_objective(self):
        """
        Infers the objective based on the mix of questions.
        """
        if self.manual_objective:
            return self.manual_objective
            
        # Count keyword hits
        scores = {p: 0 for p in self.pillar_keywords}
        all_text = " ".join(self.questions).lower()
        
        for pillar, keywords in self.pillar_keywords.items():
            for kw in keywords:
                scores[pillar] += all_text.count(kw)
        
        # Sorted pillars by hits
        sorted_pillars = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_pillar = sorted_pillars[0][0] if sorted_pillars[0][1] > 0 else "General Operational Excellence"
        
        return f"Focus on {top_pillar} and Process Governance"

    def analyze_fidelity(self):
        """
        Checks data depth and identifying 'Pencil Whipping' or gaps.
        """
        fidelity = {}
        for col in self.questions:
            series = self.csv_df[col].dropna()
            fill_rate = len(series) / len(self.csv_df) if len(self.csv_df) > 0 else 0
            
            # Check for variance (are they always saying 'Yes'?)
            unique_vals = series.nunique()
            is_static = unique_vals <= 1 and len(series) > 1
            
            fidelity[col] = {
                "fill_rate": round(fill_rate * 100, 1),
                "is_static": is_static,
                "values": series.unique().tolist()
            }
        return fidelity

    def generate_recommendations(self, fidelity, objective):
        """
        Generate actionable tips based on analysis.
        """
        tips = []
        gaps = []
        
        # Check for sparse columns
        sparse_cols = [col for col, data in fidelity.items() if data['fill_rate'] < 50]
        if sparse_cols:
            gaps.append(f"Data Gaps: {len(sparse_cols)} columns are under-reported (<50% fill rate).")
            tips.append(f"Improve field compliance for: {', '.join(sparse_cols[:3])}...")

        # Check for 'Pencil Whipping' (Static answers)
        static_cols = [col for col, data in fidelity.items() if data['is_static']]
        if static_cols:
            tips.append(f"High risk of 'Pencil Whipping' in {len(static_cols)} columns. Consider adding Mandatory Photo/Comment requirements for: {', '.join(static_cols[:2])}.")

        # Store Diversification Tip
        store_col = next((c for c in self.csv_df.columns if "Store" in c or "Entity" in c or "Submission For" in c), 'Store')
        if store_col in self.csv_df.columns:
            if self.csv_df[store_col].nunique() < 5:
                tips.append("Lower data diversity. Encourage submissions from more store clusters to identify regional variances.")
        else:
            tips.append("Could not identify store clusters. Ensure 'Store' or 'Entity' column exists for diversification analysis.")
            
        return tips, gaps

    def analyze_alignment(self):
        objective = self._infer_objective()
        fidelity = self.analyze_fidelity()
        
        # Pillar Score Calculation
        pillar_scores = {p: 0 for p in self.pillar_keywords}
        all_text = " ".join(self.questions).lower()
        for pillar, keywords in self.pillar_keywords.items():
            hits = sum(1 for kw in keywords if kw in all_text)
            pillar_scores[pillar] = round((hits / len(keywords)) * 100, 1) if keywords else 0
            
        # Overall Alignment Score
        avg_fullness = sum(f['fill_rate'] for f in fidelity.values()) / len(fidelity) if fidelity else 0
        alignment_score = (avg_fullness * 0.4) + (sum(pillar_scores.values()) / len(pillar_scores) * 0.6)
        
        tips, gaps = self.generate_recommendations(fidelity, objective)
        
        rationale = f"Score of {round(alignment_score, 1)}% is based on 60% Pillar Coverage (Form Design) and 40% Data Fidelity (Actual Submissions)."
        
        return {
            "objective": objective,
            "alignment_score": round(alignment_score, 1),
            "pillar_coverage": pillar_scores,
            "fidelity": fidelity,
            "summary": rationale,
            "recommendations": tips,
            "gaps": gaps,
            "column_warnings": [col for col, d in fidelity.items() if d['is_static'] or d['fill_rate'] < 30]
        }
