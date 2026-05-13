from datetime import datetime, timedelta

class HealthEngine:
    def __init__(self, metrics, thresholds):
        self.metrics = metrics
        self.thresholds = thresholds

    def evaluate(self):
        """
        Evaluates account health and identifies risks.
        """
        if not self.metrics or self.metrics.get("total_submissions", 0) == 0:
            return {
                "status": "At Risk",
                "label": "No Data",
                "risks": ["No submissions found for the selected account."],
                "store_health": {}
            }

        overall_risks = self._calculate_risks(
            self.metrics.get("store_coverage", 0),
            self.metrics.get("avg_compliance", 0),
            self.metrics.get("last_submission_date")
        )

        # Per-store health
        store_health = {}
        for store_id, store_metrics in self.metrics.get("store_breakdown", {}).items():
            store_risks = self._calculate_risks(
                100, # Individual store coverage is 100% relative to itself
                store_metrics.get("avg_compliance", 0),
                store_metrics.get("last_submission")
            )
            store_health[store_id] = self._get_status_from_risks(store_risks)

        result = self._get_status_from_risks(overall_risks)
        result["store_health"] = store_health
        result["health_score"] = self.calculate_health_score(
            self.metrics.get("store_coverage", 0),
            self.metrics.get("avg_compliance", 0)
        )
        return result

    def _calculate_risks(self, coverage, compliance, last_sub_str):
        risks = []
        if coverage < self.thresholds.get("completion_critical", 60):
            risks.append(f"Low Coverage: {coverage:.1f}%")
        
        if compliance < self.thresholds.get("compliance_critical", 75):
            risks.append(f"Low Compliance: {compliance:.1f}%")

        if last_sub_str:
            last_sub = datetime.strptime(last_sub_str, "%Y-%m-%d %H:%M:%S")
            days_inactive = (datetime.now() - last_sub).days
            if days_inactive > self.thresholds.get("recency_days", 7):
                risks.append(f"Inactive for {days_inactive} days")
        else:
            risks.append("No history")
        return risks

    def _get_status_from_risks(self, risks):
        if len(risks) >= 2:
            status = "At Risk"
            label = "Critical Action Required"
        elif len(risks) == 1:
            status = "Stabilizing"
            label = "Needs Observation"
        else:
            status = "On Track"
            label = "Healthy"
        
        return {
            "status": status,
            "label": label,
            "risks": risks
        }

    def calculate_health_score(self, completion, compliance):
        # Simple weighted score
        return (completion * 0.4) + (compliance * 0.6)
