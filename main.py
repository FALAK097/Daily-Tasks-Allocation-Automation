import datetime
import signal
import time
import os

from dotenv import load_dotenv
from email_sender import EmailSender
from sheets_client import SheetsClient
from mail_scheduler import EmailScheduler

class DailyAllocationService:
    def __init__(self):
        self.email_sender = EmailSender()
        self.sheets_client = SheetsClient()
        self.scheduler = EmailScheduler()

    def is_weekend(self, date: datetime.date) -> bool:
        return date.weekday() in [5, 6]

    def get_next_working_day(self, date_today: datetime.date) -> datetime.date:
        next_day = date_today + datetime.timedelta(days=1)
        while self.is_weekend(next_day):
            next_day += datetime.timedelta(days=1)
        return next_day

    def process_allocation(self) -> None:
        date_today = datetime.date.today()
        print(f"Processing allocation for date: {date_today.strftime('%d %B %Y')}")
        
        if self.is_weekend(date_today):
            print("Weekend - No tasks to send")
            return
            
        next_working_day = self.get_next_working_day(date_today)
        
        current_day_data = self.sheets_client.get_sheet_data(date_today)
        if not current_day_data:
            print(f"❌ No data found for current day ({date_today.strftime('%d %B %Y')})")
            return

        next_day_data = self.sheets_client.get_sheet_data(next_working_day)
        if not next_day_data:
            print(f"⚠️ No data found for next day ({next_working_day.strftime('%d %B %Y')})")
            next_day_data = []
        
        print(f"📧 Sending reply email for {date_today.strftime('%d %B %Y')}")
        self.email_sender.send_allocation_email(
            current_day_data, 
            None,
            date_today, 
            next_working_day, 
            "reply"
        )
        
        if next_day_data:
            print(f"📧 Sending new email for {next_working_day.strftime('%d %B %Y')}")
            self.email_sender.send_allocation_email(
                None,
                next_day_data, 
                date_today, 
                next_working_day, 
                "new"
            )
        else:
            print("⏭️ Skipping new email due to missing next day data")

def handle_shutdown(signum=None, frame=None):
    """Handle graceful shutdown with optional signal parameters"""
    print("\nShutting down gracefully...")
    if hasattr(handle_shutdown, 'service'):
        handle_shutdown.service.scheduler.stop()
    exit(0)

def main():
    print("Starting Daily Allocation Task Service...")
    
    load_dotenv()
    
    required_vars = ["SHEET_URL", "SERVICE_ACCOUNT_FILE", "EMAIL_USERNAME", "EMAIL_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        return
    
    service = DailyAllocationService()
    handle_shutdown.service = service
    
    #! Remove this line after testing
    service.process_allocation()
    
    service.scheduler.start(service.process_allocation)
    
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    print("Service running. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handle_shutdown()  

if __name__ == "__main__":
    main()
