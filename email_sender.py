import os
import smtplib
from typing import List, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.username = os.getenv("EMAIL_USERNAME")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.recipients = os.getenv("RECIPIENTS", "").split(',')
        self.cc_recipient = os.getenv("CC_RECIPIENT")

    def format_tasks_for_email(self, data: List[List[str]]) -> str:
        if not data:
            return "No tasks available"
        
        projects = {}
        current_project = None
        
        for row in data:
            if len(row) >= 4:
                if row[0] == '' and row[1] == '' and row[2] == '' and row[3] in [
                    'Projects', 'ISB', 'Operations', 'OutCaller AI', 'Claypot Website', 
                    'Hiranandani School', 'Calton EMS', 'OutRiskAI', 'Adhoc'
                ]:
                    current_project = row[3]
                    projects[current_project] = []
                elif current_project and len(row) > 1:
                    projects[current_project].append(row)

        formatted = []
        for project, tasks in projects.items():
            if tasks:
                formatted.append(f"\n{project}:")
                for task in tasks:
                    if len(task) >= 8:
                        status = task[8] if len(task) > 8 else "No Status"
                        formatted.append(f"- {task[3]} ({status})")
        
        return "\n".join(formatted)

    def send_allocation_email(
        self, 
        current_day_data: List[List[str]], 
        next_day_data: List[List[str]], 
        date_today: datetime.date,
        next_working_day: datetime.date,
        in_reply_to: Optional[str] = None
    ) -> None:
        msg = MIMEMultipart()
        msg['From'] = f"Falak <{self.username}>"
        msg['To'] = ', '.join(self.recipients)
        msg['Cc'] = self.cc_recipient
        
        today_str = date_today.strftime('%d %B %Y')
        next_day_str = next_working_day.strftime('%d %B %Y')
        
        current_tasks = self.format_tasks_for_email(current_day_data)
        next_day_tasks = self.format_tasks_for_email(next_day_data)
        
        if in_reply_to:
            msg['In-Reply-To'] = in_reply_to
            msg['References'] = in_reply_to
            msg['Subject'] = f"Re: Daily Task Allocation - {today_str}"
            body = self._create_reply_body(today_str, current_tasks)
        else:
            msg['Subject'] = f"Daily Task Allocation - {today_str}"
            body = self._create_new_email_body(today_str, next_day_str, current_tasks, next_day_tasks)
        
        msg.attach(MIMEText(body, 'plain'))
        self._send_email(msg)

    def _create_reply_body(self, today_str: str, current_tasks: str) -> str:
        return f"""Dear Team,

Please find below the updated Daily Allocation for {today_str}:

{current_tasks}

Best Regards,
Falak"""

    def _create_new_email_body(self, today_str: str, next_day_str: str, current_tasks: str, next_day_tasks: str) -> str:
        return f"""Dear Team,

Please find below the Daily Allocation for {today_str}:

{current_tasks}

Please find below the Allocation for {next_day_str}:

{next_day_tasks}

Best Regards,
Falak"""

    def _send_email(self, msg: MIMEMultipart) -> None:
        all_recipients = self.recipients + [self.cc_recipient]
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                # Set to 1 to enable debug logs
                server.set_debuglevel(0)  
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.username, self.password)
                server.sendmail(self.username, all_recipients, msg.as_string())
                print("✓ Email sent successfully!")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            raise
