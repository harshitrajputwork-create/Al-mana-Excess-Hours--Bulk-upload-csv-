import json

class DashboardDataFormatter:
    def __init__(self, account_name, metrics, health_data):
        self.account_name = account_name
        self.metrics = metrics
        self.health_data = health_data

    def to_json(self):
        """
        Formats metrics and health data into a structured JSON for dashboard consumption.
        """
        output = {
            "account_metadata": {
                "name": self.account_name,
                "generated_at": self.metrics.get("generated_at", "")
            },
            "summary_metrics": {
                "total_submissions": self.metrics.get("total_submissions"),
                "avg_compliance": round(self.metrics.get("avg_compliance", 0), 2),
                "store_coverage": round(self.metrics.get("store_coverage", 0), 2),
                "last_submission": self.metrics.get("last_submission_date")
            },
            "health_assessment": {
                "status": self.health_data.get("status"),
                "label": self.health_data.get("label"),
                "health_score": round(self.health_data.get("health_score", 0), 2),
                "risks": self.health_data.get("risks", [])
            },
            "time_series": [
                {
                    "week": w["week"],
                    "date": w["end_date"],
                    "submissions": w["cumulative_submissions"],
                    "coverage": round(w["store_coverage"], 2),
                    "compliance": round(w["avg_compliance"], 2)
                }
                for w in self.metrics.get("weekly_metrics", [])
            ]
        }
        return json.dumps(output, indent=4)
