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

        reminder_value = row.get(
            "reminder_time",
            None
        )

        if reminder_value is None:

            continue

        reminder_value = str(
            reminder_value
        ).strip()

        if (
            reminder_value == ""
            or reminder_value.lower() == "none"
            or reminder_value.lower() == "nan"
        ):

            continue

        try:

            reminder_time = (
                datetime.datetime.fromisoformat(
                    reminder_value
                )
            )

        except Exception:

            continue

        time_diff = abs(
            (
                now - reminder_time
            ).total_seconds()
        )

        if time_diff <= 60:

            send_telegram_message(

                f"🚨 FocusFlow Reminder\n\n"

                f"Task: {row['task']}\n"

                f"Priority: {row['priority']}\n"

                f"Deadline: {row['deadline']}\n\n"

                f"You should start NOW ✅"
            )
