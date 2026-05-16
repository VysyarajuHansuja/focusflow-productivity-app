from apscheduler.schedulers.blocking import (
    BlockingScheduler
)

from reminder_service import (
    check_reminders
)

scheduler = BlockingScheduler()

scheduler.add_job(
    check_reminders,
    "interval",
    seconds=60
)

print("🚨 Reminder worker started...")

scheduler.start()