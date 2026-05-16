import pandas as pd
import datetime

from database import connect_db

from telegram_utils import (
    send_telegram_message
)


def check_reminders():

    conn = connect_db()

    df = pd.read_sql(
        "SELECT * FROM tasks WHERE status='Pending'",
        conn
    )

    conn.close()

    now = datetime.datetime.now()

    for _, row in df.iterrows():

        if (
            "reminder_time" not in row
            or pd.isna(row["reminder_time"])
            or not row["reminder_time"]
        ):
        
            continue

        reminder_time = datetime.datetime.fromisoformat(
            str(row["reminder_time"])
        )

        time_diff = abs(
            (now - reminder_time)
            .total_seconds()
        )

        # Trigger within 60 seconds
        if time_diff <= 60:

            send_telegram_message(

                f"🚨 FocusFlow Reminder\n\n"

                f"Task: {row['task']}\n"

                f"Priority: {row['priority']}\n"

                f"Deadline: {row['deadline']}\n\n"

                f"You should start NOW ✅"
            )
