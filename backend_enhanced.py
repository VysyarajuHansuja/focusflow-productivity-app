from database import connect_db
import pandas as pd
from datetime import datetime, timedelta

class TaskManager:

    def add_task(self, user_id, task, description, priority, category, time, deadline,reminder_time,attachment="",
             is_daily=False, start_time=None, end_time=None):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO tasks(user_id, task, description, priority, category, estimated_time,
        deadline,reminder_time,attachment, status, is_daily, start_time, end_time)
        VALUES(?,?,?,?,?,?,?,?,?,'Pending',?,?,?)
        """, (user_id, task, description, priority, category, time, deadline,reminder_time,
            attachment, is_daily, start_time, end_time))
        conn.commit()
        conn.close()

    def get_tasks(self,user_id):
        conn = connect_db()
        df = pd.read_sql(
            "SELECT * FROM tasks WHERE user_id=?",
            conn,
            params=(user_id,)
        )
        conn.close()
        return df

    def complete_task(self,task_id):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE tasks SET status='Completed' WHERE id=?",
            (task_id,)
        )
        conn.commit()
        conn.close()
        
    def delete_task(self, task_id):
        """Delete a task"""
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        conn.close()
        
    def update_task(self, task_id, task=None, priority=None, estimated_time=None, deadline=None):
        """Update task details"""
        conn = connect_db()
        cur = conn.cursor()
        
        updates = []
        values = []
        
        if task:
            updates.append("task=?")
            values.append(task)
        if priority:
            updates.append("priority=?")
            values.append(priority)
        if estimated_time:
            updates.append("estimated_time=?")
            values.append(estimated_time)
        if deadline:
            updates.append("deadline=?")
            values.append(deadline)
            
        if updates:
            values.append(task_id)
            query = f"UPDATE tasks SET {', '.join(updates)} WHERE id=?"
            cur.execute(query, tuple(values))
            conn.commit()
        
        conn.close()
    
    def update_deadline(self,task_id,new_date):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE tasks SET deadline=? WHERE id=?",
            (new_date,task_id)
        )
        conn.commit()
        conn.close()

    # DAA algorithm - Greedy approach for task scheduling
    def generate_daily_schedule(self,df,hours):
        df = df[df["status"]=="Pending"]
        df = df.sort_values("deadline")
        schedule=[]
        total=0
        for _,row in df.iterrows():
            t=row["estimated_time"]
            if total+t<=hours:
                schedule.append(row)
                total+=t
        return schedule
    
    # AI Question Generator Scoring
    def save_score(self, user_id, score):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO scores(user_id, score, date) VALUES(?,?,Date('now'))",
            (user_id, score)
        )
        conn.commit()
        conn.close()

    #Track of no. of questions attempted by user
    def get_today_count(self, user_id):
        conn = connect_db()
        df = pd.read_sql(
            "SELECT * FROM scores WHERE user_id=? AND date=Date('now')",
            conn,
            params=(user_id,)
        )
        conn.close()
        return len(df)
    
    def get_weekly_scores(self, user_id):
        """Get scores for the past week"""
        conn = connect_db()
        df = pd.read_sql("""
            SELECT date, SUM(score) as total_score, COUNT(*) as attempts
            FROM scores 
            WHERE user_id=? AND date >= Date('now', '-7 days')
            GROUP BY date
            ORDER BY date
        """, conn, params=(user_id,))
        conn.close()
        return df
    
    def add_event(self, user_id, title, event_date, category):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO events(user_id, title, event_date, category) VALUES(?,?,?,?)",
            (user_id, title, event_date, category)
        )
        conn.commit()
        conn.close()
        
    def get_events(self, user_id):
        conn = connect_db()
        import pandas as pd
        df = pd.read_sql(
            "SELECT * FROM events WHERE user_id=?",
            conn,
            params=(user_id,)
        )
        conn.close()
        return df
    
    def delete_event(self, event_id):
        """Delete an event"""
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM events WHERE id=?", (event_id,))
        conn.commit()
        conn.close()
    
    def update_event_date(self, event_id, new_date):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE events SET event_date=? WHERE id=?",
            (new_date, event_id)
        )
        conn.commit()
        conn.close()
        
    def get_overdue_tasks(self, user_id):
        """Get tasks that are overdue"""
        conn = connect_db()
        df = pd.read_sql("""
            SELECT * FROM tasks 
            WHERE user_id=? AND status='Pending' AND date(deadline) < date('now')
            ORDER BY deadline
        """, conn, params=(user_id,))
        conn.close()
        return df
    
    def get_upcoming_tasks(self, user_id, days=7):
        """Get tasks due in the next N days"""
        conn = connect_db()
        df = pd.read_sql("""
            SELECT * FROM tasks 
            WHERE user_id=? AND status='Pending' 
            AND date(deadline) BETWEEN date('now') AND date('now', '+' || ? || ' days')
            ORDER BY deadline
        """, conn, params=(user_id, days))
        conn.close()
        return df
    
    def add_subtask(self, task_id, subtask):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO subtasks(task_id, subtask, status)
            VALUES(?,?,?)
            """,
            (task_id, subtask, "Pending")
        )
        conn.commit()
        conn.close()
    
    def get_subtasks(self, task_id):
        conn = connect_db()
        df = pd.read_sql(
            "SELECT * FROM subtasks WHERE task_id=?",
            conn,
            params=(task_id,)
        )
        conn.close()
        return df
    
    def complete_subtask(self, subtask_id):
        conn = connect_db()
        cur = conn.cursor()
        # Complete subtask
        cur.execute(
            """
            UPDATE subtasks
            SET status='Completed'
            WHERE id=?
            """,
            (subtask_id,)
        )
        # Get parent task
        cur.execute(
            """
            SELECT task_id
            FROM subtasks
            WHERE id=?
            """,
            (subtask_id,)
        )
        task_id = cur.fetchone()[0]
        # Check if all subtasks completed
        cur.execute(
            """
            SELECT COUNT(*)
            FROM subtasks
            WHERE task_id=? AND status='Pending'
            """,
            (task_id,)
        )
        pending = cur.fetchone()[0]
        # Auto-complete main task
        if pending == 0:
            cur.execute(
                """
                UPDATE tasks
                SET status='Completed'
                WHERE id=?
                """,
                (task_id,)
            )
        conn.commit()
        conn.close()
    
    def get_task_progress(self, task_id):
        subtasks = self.get_subtasks(task_id)
        if subtasks.empty:
            return 0
        completed = len(
            subtasks[subtasks["status"] == "Completed"]
        )
        total = len(subtasks)
        return int((completed / total) * 100)
