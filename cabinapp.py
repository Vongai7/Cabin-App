from flask import Flask, request, jsonify, render_template
from googletrans import Translator
from sklearn.cluster import KMeans
import sqlite3
import requests
import json

app = Flask(__name__)
translator = Translator()

# Database initialization
conn = sqlite3.connect('calls.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS calls (
    id INTEGER PRIMARY KEY,
    seat TEXT,
    request_type TEXT,
    status TEXT,
    cluster INTEGER
)
''')

# Send SMS using Sinch
def send_sms(seat, request_type):
    url = "https://sms.api.sinch.com/xms/v1/your_service_plan_id/batches"
    headers = {
        "Authorization": "Bearer your_api_key",
        "Content-Type": "application/json"
    }
    payload = {
        "from": "YourNumber",
        "to": ["AttendantNumber"],
        "body": f"Passenger at seat {seat} requested: {request_type}"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code

@app.route('/')
def home():
    return render_template('frontend.html')

@app.route('/call', methods=['POST'])
def handle_call():
    data = request.json
    seat = data.get('seat')
    request_type = data.get('request_type')
    lang = data.get('language', 'en')
    
    # Save to database
    cursor.execute('''
    INSERT INTO calls (seat, request_type, status) 
    VALUES (?, ?, ?)
    ''', (seat, request_type, 'pending'))
    conn.commit()
    
    # Multilingual feedback
    translated_message = translator.translate(
        f"Your {request_type} request has been received.", dest=lang
    ).text
    
    # Send SMS notification
    send_sms(seat, request_type)
    
    return jsonify({'message': translated_message})

@app.route('/diagnostics', methods=['GET'])
def diagnostics():
    # Example: Check database connection
    try:
        cursor.execute('SELECT 1')
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)



from flask import Flask, render_template

app = Flask(__name__)

# Route for the homepage
@app.route('/')
def index():
    return render_template('frontend.html')  # Serves the index.html file from /templates

if __name__ == '__main__':
    app.run(debug=True)



import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px

df = pd.read_sql_query("SELECT * FROM calls", conn)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Call System Dashboard"),
    dcc.Graph(
        figure=px.bar(df, x='request_type', y='id', color='status', title="Requests Overview")
    ),
    dcc.Graph(
        figure=px.pie(df, names='request_type', title="Request Distribution")
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)