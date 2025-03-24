import os
import smtplib
import datetime
from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load environment variables
SHEET_URL = os.getenv("SHEET_URL")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENTS = os.getenv("RECIPIENTS").split(',')
CC_RECIPIENT = os.getenv("CC_RECIPIENT")

def get_gid_for_date(service, sheet_id, target_date):
    try:
        sheets_metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        for sheet in sheets_metadata['sheets']:
            if target_date in sheet['properties']['title']:
                return sheet['properties']['sheetId'], sheet['properties']['title']
        return None, None
    except Exception as e:
        print(f"Error fetching sheet metadata: {e}")
        return None, None

def get_sheet_data(date: datetime.date):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build('sheets', 'v4', credentials=creds)
    sheet_id = SHEET_URL.split('/d/')[1].split('/')[0]

    # Convert date to matching sheet name format
    target_date = date.strftime("%d %B")
    gid, sheet_name = get_gid_for_date(service, sheet_id, target_date)
    
    if not gid or not sheet_name:
        print(f"No sheet found for date: {target_date}")
        return []

    try:
        range_name = f"'{sheet_name}'!A1:Z1000"
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
        return result.get('values', [])
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def format_tasks(data):
    if not data:
        return "No tasks available"
    formatted_rows = []
    for row in data:
        formatted_rows.append('\t'.join(row))
    return '\n'.join(formatted_rows)

def format_tasks_for_email(data):
    if not data:
        return "No tasks available"
    
    # Group tasks by project
    projects = {}
    current_project = None
    
    for row in data:
        if len(row) >= 4:  
            if row[0] == '' and row[1] == '' and row[2] == '' and row[3] in ['Projects', 'ISB', 'Operations', 'OutCaller AI', 'Claypot Website', 'Hiranandani School', 'Calton EMS', 'OutRiskAI', 'Adhoc']:
                current_project = row[3]
                projects[current_project] = []
            elif current_project and len(row) > 1:
                projects[current_project].append(row)

    # Format the output
    formatted = []
    for project, tasks in projects.items():
        if tasks:  # Only include projects with tasks
            formatted.append(f"\n{project}:")
            for task in tasks:
                if len(task) >= 8:  # Assuming standard task format
                    status = task[8] if len(task) > 8 else "No Status"
                    formatted.append(f"- {task[3]} ({status})")
    
    return "\n".join(formatted)

def send_email(current_day_data: str, next_day_data: str, date_today: datetime.date, 
              next_working_day: datetime.date, in_reply_to: Optional[str] = None):
    msg = MIMEMultipart()
    msg['From'] = f"Falak <{EMAIL_USERNAME}>"  # Add display name
    msg['To'] = ', '.join(RECIPIENTS)
    msg['Cc'] = CC_RECIPIENT
    
    # Format the dates nicely
    today_str = date_today.strftime('%d %B %Y')
    next_day_str = next_working_day.strftime('%d %B %Y')
    
    # Format the tasks
    current_tasks = format_tasks_for_email(current_day_data)
    next_day_tasks = format_tasks_for_email(next_day_data)
    
    if in_reply_to:
        msg['In-Reply-To'] = in_reply_to
        msg['References'] = in_reply_to
        msg['Subject'] = f"Re: Daily Task Allocation - {today_str}"
        body = f"""Dear Team,

Please find below the updated Daily Allocation for {today_str}:

{current_tasks}

Best Regards,
Falak"""
    else:
        msg['Subject'] = f"Daily Task Allocation - {today_str}"
        body = f"""Dear Team,

Please find below the Daily Allocation for {today_str}:

{current_tasks}

Please find below the Allocation for {next_day_str}:

{next_day_tasks}

Best Regards,
Falak"""
    
    msg.attach(MIMEText(body, 'plain'))
    all_recipients = RECIPIENTS + [CC_RECIPIENT]

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:  
            server.set_debuglevel(1)  # Enable debug output
            server.ehlo()  # Say hello to the server
            server.starttls()  # Enable TLS
            server.ehlo()  # Say hello again after TLS
            print("Attempting login with:", EMAIL_USERNAME)
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            print("Login successful")
            server.sendmail(EMAIL_USERNAME, all_recipients, msg.as_string())
            print(f"Email {'reply' if in_reply_to else 'sent'} successfully!")
    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication failed: {e}")
        raise
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        raise

def is_weekend(date: datetime.date) -> bool:
    return date.weekday() in [5, 6]

def get_next_working_day(date_today: datetime.date) -> datetime.date:
    next_day = date_today + datetime.timedelta(days=1)
    while is_weekend(next_day):
        next_day += datetime.timedelta(days=1)
    return next_day

def main(in_reply_to: Optional[str] = None):
    date_today = datetime.date.today()
    
    # Skip weekends
    if is_weekend(date_today):
        print("Weekend - No tasks to send")
        return
        
    next_working_day = get_next_working_day(date_today)

    current_day_data = format_tasks(get_sheet_data(date_today))
    next_day_data = format_tasks(get_sheet_data(next_working_day))

    # Send Email
    send_email(current_day_data, next_day_data, date_today, next_working_day, in_reply_to)

if __name__ == "__main__":
    main()
