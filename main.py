import datetime
import signal
import time
import os
from typing import Optional
from email_sender import EmailSender
from sheets_client import SheetsClient
from mail_scheduler import EmailScheduler
from dotenv import load_dotenv

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

    def process_allocation(self, in_reply_to: Optional[str] = None) -> None:
        date_today = datetime.date.today()
        
        if self.is_weekend(date_today):
            print("Weekend - No tasks to send")
            return
            
        next_working_day = self.get_next_working_day(date_today)

        current_day_data = self.sheets_client.get_sheet_data(date_today)
        next_day_data = self.sheets_client.get_sheet_data(next_working_day)

        self.email_sender.send_allocation_email(
            current_day_data, 
            next_day_data, 
            date_today, 
            next_working_day, 
            in_reply_to
        )

def handle_shutdown(signum, frame):
    print("\nShutting down gracefully...")
    if hasattr(handle_shutdown, 'service'):
        handle_shutdown.service.scheduler.stop()
    exit(0)

def main():
    print("Starting Daily Allocation Task Service...")
    
    # Load environment variables
    load_dotenv()
    
    # Validate required environment variables
    required_vars = ["SHEET_URL", "SERVICE_ACCOUNT_FILE", "EMAIL_USERNAME", "EMAIL_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        return
    
    service = DailyAllocationService()
    handle_shutdown.service = service
    
    #! Remove this line after testing
    # Run once immediately
    service.process_allocation()
    
    # Setup scheduler
    service.scheduler.start(service.process_allocation)
    
    # Setup graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    print("Service running. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handle_shutdown(None, None)

if __name__ == "__main__":
    main()
