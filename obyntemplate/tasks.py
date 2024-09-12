from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def scheduled_task():
    print("Scheduled task running...")

def setup_tasks(scheduler: AsyncIOScheduler):
    # Schedule a task that runs every 10 minutes
    scheduler.add_job(scheduled_task, 'interval', minutes=10)