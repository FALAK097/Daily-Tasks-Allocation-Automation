from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import main

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ! Remove this below line after testing
    main.main()  # Run once at startup
    # Startup: Schedule daily email at 9 PM
    scheduler.add_job(
        main.main,
        trigger=CronTrigger(hour=21, minute=0),  
        id="daily_allocation",
        max_instances=1
    )
    scheduler.start()
    yield
    # Shutdown: Clean up scheduler
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.post("/send-update/{message_id}")
async def send_update(message_id: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(main.main, in_reply_to=message_id)
    return {"message": "Update scheduled"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
