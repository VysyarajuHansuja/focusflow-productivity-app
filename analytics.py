
import pandas as pd

class BehaviorAnalytics:

    def completion_rate(self, df):

        if len(df) == 0:
            return 0

        completed = len(df[df["status"] == "Completed"])

        return round((completed / len(df)) * 100, 2)


    def productivity_score(self, df):

        completed = len(df[df["status"] == "Completed"])
        pending = len(df[df["status"] == "Pending"])

        return completed * 10 - pending * 2


    def motivation_badge(self, df):

        completed = len(df[df["status"] == "Completed"])

        if completed >= 20:
            return "🏆 Master Performer", "Excellent work! Keep maintaining your productivity."

        elif completed >= 10:
            return "⭐ Productivity Star", "Great progress! You are becoming consistent."

        elif completed >= 5:
            return "🔥 Rising Achiever", "Good start! Keep pushing forward."

        else:
            return "🚀 Beginner", "Start completing tasks regularly to build momentum."


    # -----------------------------
    # NEW OB FUNCTIONS
    # -----------------------------

    def productivity_time(self, df):

        completed = df[df["status"] == "Completed"]

        if completed.empty:
            return "Not enough data"

        completed["created_at"] = pd.to_datetime(completed["created_at"])

        hours = completed["created_at"].dt.hour

        peak_hour = hours.mode()[0]

        if peak_hour < 12:
            return "Morning Productivity"

        elif peak_hour < 18:
            return "Afternoon Productivity"

        else:
            return "Night Productivity"


    def stress_level(self, df):

        pending = len(df[df["status"] == "Pending"])

        if pending >= 10:
            return "High Stress Risk"

        if pending >= 5:
            return "Moderate Stress"

        return "Low Stress"


    def delay_behavior(self, df):

        df["deadline"] = pd.to_datetime(df["deadline"])
        df["created_at"] = pd.to_datetime(df["created_at"])

        delayed = df[
            (df["status"] == "Completed") &
            (df["created_at"] > df["deadline"])
        ]

        return len(delayed)