# Taqtics Implementation Reporting Engine (POC)

## Objective
Build a semi-automated reporting system that:

1. Authenticates using Taqtics External API
2. Pulls monthly CSV export for selected forms
3. Filters data by specific store entityIds
4. Computes cumulative weekly implementation metrics
5. Generates:
   - Executive HTML email summary
   - Dashboard JSON data
6. Allows manual email sending via preview screen

---

## POC Account
Subdomain: impl4.taqtics.co  
Account: SHAWARMER  

Forms:
- IMPFORM115
- IMPFORM127

---

## Weekly Definition
Cumulative model:
Week 1 = first submission date + 7 days  
Week 2 = first submission date + 14 days  
And so on.

---

## Risk Logic
- Completion < 60% → Critical
- Compliance < 75% → Critical
- No submission in last 7 days → Risk

---

## Architecture
main.py
  → api_client
  → csv_processor
  → health_engine
  → email_generator
  → dashboard_data
