from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

class EmailScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        
    def start(self, email_func):
        """Schedule emails to be sent at 9 PM daily"""
        self.scheduler.add_job(
            email_func,
            trigger=CronTrigger(hour=21, minute=0),
            id="daily_allocation",
            max_instances=1
        )
        self.scheduler.start()
        
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
