from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json
from api_client import TaqticsAPIClient
from csv_processor import CSVProcessor
from health_engine import HealthEngine
from dashboard_data import DashboardDataFormatter
from alignment_engine import AlignmentEngine
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure logging
logging.basicConfig(level=logging.INFO)

REPORT_CACHE = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate():
    data = request.json
    subdomain = data.get('subdomain')
    email = data.get('email')
    password = data.get('password')
    
    client = TaqticsAPIClient(subdomain, email, password)
    try:
        success = client.authenticate()
        if success:
            session['subdomain'] = subdomain
            session['email'] = email
            session['password'] = password
            session['token'] = client.token
            return jsonify({"success": True, "message": "✅ Authentication Successful"})
        else:
            return jsonify({"success": False, "message": "❌ Authentication Failed"})
    except Exception as e:
        return jsonify({"success": False, "message": f"❌ Error: {str(e)}"})

@app.route('/setup')
def setup():
    if 'token' not in session:
        return redirect(url_for('index'))
    return render_template('setup.html')

@app.route('/generate', methods=['POST'])
def generate():
    if 'token' not in session:
        return redirect(url_for('index'))
        
    form_ids = request.form.get('form_ids').replace(' ', '').split(',')
    month_year = request.form.get('month_year') # MM-YYYY
    store_ids_raw = request.form.get('store_ids')
    store_ids = store_ids_raw.replace(' ', '').split(',') if store_ids_raw else []
    account_name = request.form.get('account_name', 'Unnamed Account')
    manual_objective = request.form.get('manual_objective')

    # Fetch data
    client = TaqticsAPIClient(session['subdomain'], session['email'], session['password'])
    client.token = session['token']
    client.headers["access-token"] = session['token']
    
    try:
        csv_data = client.get_monthly_csv(form_ids, month_year)
        if not csv_data.strip():
            return render_template('setup.html', error="No data found for the selected criteria.")
            
        processor = CSVProcessor(csv_data, store_entity_ids=store_ids, form_ids=form_ids)
        metrics = processor.process()
        
        if not metrics:
            return render_template('setup.html', error="Filtering resulted in no data.")
            
        health_engine = HealthEngine(metrics, {
            "completion_critical": 60,
            "compliance_critical": 75,
            "recency_days": 7
        })
        health_data = health_engine.evaluate()
        
        # Alignment Analysis
        alignment_data = None
        try:
            form_json_path = r"C:\Users\Harshit Rajput\Downloads\Herfy V\LPD New Audit Checklist for SHAWARMER.json"
            alignment_engine = AlignmentEngine(
                csv_data, 
                manual_objective=manual_objective,
                form_json_path=form_json_path if os.path.exists(form_json_path) else None
            )
            alignment_data = alignment_engine.analyze_alignment()
        except Exception as ae:
            logging.error(f"Alignment Analysis failed: {ae}")

        # Store in global cache for dashboard view (fixes session 4KB limit)
        cache_key = session.get('email', 'guest')
        REPORT_CACHE[cache_key] = {
            "account_name": account_name,
            "metrics": metrics,
            "health_data": health_data,
            "alignment_data": alignment_data,
            "month": month_year
        }
        
        return redirect(url_for('dashboard'))
    except Exception as e:
        logging.exception("Generation error")
        return render_template('setup.html', error=f"Processing Error: {str(e)}")

@app.route('/dashboard')
def dashboard():
    cache_key = session.get('email', 'guest')
    data = REPORT_CACHE.get(cache_key)
    if not data:
        return redirect(url_for('setup'))
    return render_template('dashboard.html', **data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
