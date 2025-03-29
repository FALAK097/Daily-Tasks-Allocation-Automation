import os
import smtplib
import datetime

from typing import List
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_styles import HTML_STYLES

class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.username = os.getenv("EMAIL_USERNAME")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.recipients = os.getenv("RECIPIENTS", "").split(',')
        self.cc_recipient = os.getenv("CC_RECIPIENT")
        self.domain = os.getenv("EMAIL_DOMAIN", "example.com")
        self.html_styles = HTML_STYLES

    def _generate_message_id(self, date: datetime.date) -> str:
        return f"<daily-allocation-{date.strftime('%Y%m%d')}@{self.domain}>"

    def format_tasks_for_email(self, data: List[List[str]]) -> str:
        if not data:
            return "<p>No tasks available</p>"
        
        html = [self.html_styles, "<div>"]
        current_project = None
        in_table = False
        
        def is_project_header(row: List[str]) -> bool:
            if len(row) >= 4:
                return all(cell == '' for cell in row[:3]) and row[3] not in ['', 'Projects']
            return False

        def is_summary_row(row: List[str]) -> bool:
            if len(row) >= 4:
                return all(cell == '' for cell in row[:3]) and row[3] != '' and any(cell.strip().isdigit() for cell in row[4:])
            return False

        summary_data = []
        header_row = None

        for row in data:
            if len(row) >= 4 and 'Projects' in row and ('WIP' in row or 'Done' in row):
                header_row = row
            elif header_row and is_summary_row(row):
                summary_data.append(row)

        if header_row:
            html.append("<h3>Project Summary</h3><table><tr>")
            for cell in header_row:
                html.append(f"<th>{cell}</th>")
            html.append("</tr>")
            
            for row in summary_data:
                html.append("<tr>")
                for cell in row:
                    html.append(f"<td>{cell}</td>")
                html.append("</tr>")
            html.append("</table><br>")

        for row in data:
            if is_project_header(row):
                if in_table:
                    html.append("</table><br>")
                current_project = row[3]
                html.append(f"<h3>{current_project}</h3><table>")
                in_table = True
            elif current_project and len(row) > 1:
                if 'Team Member' in row or 'Sr. No.' in row:
                    html.append("<tr>")
                    for cell in row[1:]:
                        html.append(f"<th>{cell}</th>")
                    html.append("</tr>")
                else:
                    html.append("<tr>")
                    for cell in row[1:]:
                        html.append(f"<td>{cell}</td>")
                    html.append("</tr>")

        if in_table:
            html.append("</table>")
        html.append("</div>")
        
        return "\n".join(html)

    def send_allocation_email(self, current_day_data: List[List[str]], next_day_data: List[List[str]], date_today: datetime.date, next_working_day: datetime.date, email_type: str = "new") -> None:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"Falak <{self.username}>"
        msg['To'] = ', '.join(self.recipients)
        msg['Cc'] = self.cc_recipient

        if email_type == "reply":
            msg['In-Reply-To'] = self._generate_message_id(date_today)
            msg['References'] = self._generate_message_id(date_today)
            msg['Subject'] = f"Re: Daily Task Allocation - {date_today.strftime('%d %B %Y')}"
            plain_body = self._create_reply_body(date_today.strftime('%d %B %Y'), "See HTML version")
            html_body = self._create_reply_body_html(date_today.strftime('%d %B %Y'), self.format_tasks_for_email(current_day_data))
        else:
            msg['Message-ID'] = self._generate_message_id(next_working_day)
            msg['Subject'] = f"Daily Task Allocation - {next_working_day.strftime('%d %B %Y')}"
            plain_body = self._create_new_email_body(next_working_day.strftime('%d %B %Y'), "See HTML version")
            html_body = self._create_new_email_body_html(next_working_day.strftime('%d %B %Y'), self.format_tasks_for_email(next_day_data))

        msg.attach(MIMEText(plain_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        self._send_email(msg)

    def _create_reply_body(self, today_str: str, current_tasks: str) -> str:
        return f"""Dear Team,

Please find below the updated Daily Allocation for {today_str}:

{current_tasks}

Best Regards,
Falak"""

    def _create_new_email_body(self, next_day_str: str, next_day_tasks: str) -> str:
        return f"""Dear Team,

Please find below the Daily Allocation for {next_day_str}:

{next_day_tasks}

Best Regards,
Falak"""

    def _create_reply_body_html(self, today_str: str, tasks_html: str) -> str:
        return f"""
        <html>
        <body>
        <p>Dear Team,</p>
        <p>Please find below the updated Daily Allocation for {today_str}:</p>
        {tasks_html}
        <p>Best Regards,<br>Falak</p>
        </body>
        </html>
        """

    def _create_new_email_body_html(self, next_day_str: str, tasks_html: str) -> str:
        return f"""
        <html>
        <body>
        <p>Dear Team,</p>
        <p>Please find below the Daily Allocation for {next_day_str}:</p>
        {tasks_html}
        <p>Best Regards,<br>Falak</p>
        </body>
        </html>
        """

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