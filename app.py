from flask import Flask, request, jsonify, redirect, url_for, send_from_directory
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from datetime import datetime
import pytz
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

#Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar']
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
logging.basicConfig(level=logging.DEBUG)

def get_google_calendar_service():
  """Initialize Google Calendar service."""
  creds = None
  if os.path.exists(os.getenv("TOKEN_PICKLE_FILE")):
    with open(os.getenv("TOKEN_PICKLE_FILE"), 'rb') as token:
      creds = pickle.load(token)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        os.getenv("GOOGLE_CREDENTIALS_FILE"), SCOPES
      )
      creds = flow.run_local_server(port=0)
    with open(os.getenv("TOKEN_PICKLE_FILE"), 'wb') as token:
      pickle.dump(creds, token)
  try: 
    service = build('calendar', 'v3', credentials=creds)
  except Exception as e:
     logging.error(f"Failed to build Google Calendar service: {str(e)}")

  return service

@app.route('/')
def index():
  """Serve the main HTML page."""
  return send_from_directory('public', "index.html")

@app.route('/authorize')
def authorize():
  """Authorize the user and save credentials"""
  flow = InstalledAppFlow.from_client_secrets_file(os.getenv("GOOGLE_CREDENTIALS_FILE"), SCOPES)
  creds = flow.run_local_server(port=0)
  with open(os.getenv("TOKEN_PICKLE_FILE"), 'wb') as token:
    pickle.dump(creds, token)
  return redirect(url_for('index'))

@app.route('/public/<path:filename>')
def serve_static(filename):
   """Server static files."""
   return send_from_directory('public', filename)

@app.route('/chat', methods=['POST'])
def dialogflow_webhook():
    """Handle Dialogflow webhook requests for scheduling events."""
    data = request.get_json()
    intent_name = data['queryResult']['intent']['displayName']

    if intent_name == 'ScheduleEvent':
        parameters = data['queryResult']['parameters']
        event_title = parameters.get('event_title')
        date = parameters.get('date').split('T')[0]
        start_time = parameters.get('start_time').split('T')[1].split('-')[0]
        end_time = parameters.get('end_time').split('T')[1].split('-')[0]

        if date and start_time and end_time:
            start_datetime = f"{date}T{start_time}:00"
            end_datetime = f"{date}T{end_time}:00"
            tz = pytz.timezone('America/New_York')
            start_dt = tz.localize(datetime.fromisoformat(start_datetime))
            end_dt = tz.localize(datetime.fromisoformat(end_datetime))

            try:
                service = get_google_calendar_service()
                event = {
                    'summary': event_title,
                    'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'America/New_York'},
                    'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'America/New_York'},
                }

                event_result = service.events().insert(calendarId='floresjason06@gmail.com', body=event).execute()
                response_text = (f"Scheduled event '{event_title}' on {start_dt.strftime('%B %d, %Y')} "
                                 f"from {start_dt.strftime('%I:%M %p')} to {end_dt.strftime('%I:%M %p')}.")
            except Exception as e:
                logging.error(f"Failed to schedule event: {str(e)}")
                response_text = f"Failed to schedule event: {str(e)}"
        else:
            response_text = "Couldn't understand the event details."
    else:
        response_text = "Please schedule an event."

    return jsonify({'fulfillmentText': response_text})
  


if __name__ == '__main__':
    app.run(debug=True)