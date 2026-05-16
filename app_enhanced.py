from apscheduler.schedulers.background import (BackgroundScheduler)
from reminder_service import (check_reminders)
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from email_utils import send_email
import datetime
from auth import register_user, login_user
from backend_enhanced import TaskManager
from analytics import BehaviorAnalytics
from database import connect_db
load_dotenv()
from ai_generator import (generate_question,generate_task_suggestions,is_online)
import time
import os
from telegram_utils import (send_telegram_message)
from init_db import init_database
init_database()
if "scheduler_started" not in st.session_state:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        check_reminders,
        "interval",
        seconds=60
    )
    scheduler.start()
    st.session_state.scheduler_started = True
# ✅ Mobile-friendly page config
st.set_page_config(
    page_title="Smart Task Manager",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown("""
<style>
/* Main app padding */
.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
    padding-left:2rem;
    padding-right:2rem;
}
/* Mobile responsiveness */
@media (max-width:768px){
    .block-container{
        padding-left:1rem;
        padding-right:1rem;
    }
    h1{
        font-size:28px !important;
    }
    h2{
        font-size:24px !important;
    }
    h3{
        font-size:20px !important;
    }
    .stButton>button{
        width:100%;
        border-radius:10px;
    }
    .stTextInput>div>div>input{
        font-size:16px;
    }
}
/* Better cards */
[data-testid="stVerticalBlock"]{
    gap:0.8rem;
}
</style>
""", unsafe_allow_html=True)
# Persistent theme state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dark_mode = st.sidebar.toggle(
    "🌙 Dark Mode",
    value=st.session_state.dark_mode
)

st.session_state.dark_mode = dark_mode

# ✅ Custom CSS for mobile responsiveness
if dark_mode:
    st.markdown("""
    <style>

    .stApp {
        background-color: #121212;
        color: white;
    }
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        color: white;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 50px;
        font-size: 16px;
        background-color: #333333;
        color: white;
        border: 1px solid #555;
    }
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div {
        background-color: #222222;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <style>

    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }

    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 50px;
        font-size: 16px;
    }

    </style>
    """, unsafe_allow_html=True)

def get_event_color(category):
    if category == "Exam":
        return "#000000"   # ⚫ black
    elif category == "Personal":
        return "#2ECC71"   # 🟢 green
    elif category == "Meeting":
        return "#3498DB"   # 🔵 blue
    else:
        return "#9B59B6"   # 🟣 purple

# Initialize
manager = TaskManager()
analytics = BehaviorAnalytics()
TASK_TEMPLATES = {
    "📚 Study Routine": [
        "Revise Notes",
        "Solve Practice Questions",
        "Take Mock Test"
    ],
    "💻 Coding Practice": [
        "Solve DSA Problems",
        "Work on Project",
        "Read Documentation"
    ],
    "🏋️ Workout": [
        "Warm Up",
        "Exercise Session",
        "Stretching"
    ],
    "📝 Exam Preparation": [
        "Read Theory",
        "Solve PYQs",
        "Revision"
    ]
}

st.title("📱 Smart Task Manager")

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- LOGIN / REGISTER ----------------
menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

if st.session_state.user is None:
    
    # ✅ Centered login/register form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if menu == "Register":
            st.subheader("🔐 Create Account")
            username = st.text_input("Username", key="reg_user")
            password = st.text_input("Password", type="password", key="reg_pass")
            email = st.text_input("Email", key="reg_email")
            
            if st.button("Create Account", key="reg_btn"):
                if username and password and email:
                    try:
                        register_user(username, password, email)
                        st.success("✅ Account created! Please login.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please fill all fields")
        
        if menu == "Login":
            st.subheader("👋 Welcome Back")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Login", key="login_btn"):
                user = login_user(username, password)
                if user:
                    st.session_state.user = user
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")

# ---------------- AFTER LOGIN ----------------
else:
    user = st.session_state.user
    # Handle quick navigation
    if "goto_page" not in st.session_state:
        st.session_state.goto_page = None
    # ✅ Better mobile navigation
    st.sidebar.markdown(f"""
    <div style="
    padding:20px;
    border-radius:15px;
    background-color:#1E1E1E;
    text-align:center;
    margin-bottom:20px;
    ">

    <h2 style="color:#4CAF50;">
    👤 {user[1]}
    </h2>

    <p>
    FocusFlow Productivity
    </p>

    </div>

    """, unsafe_allow_html=True)
    pages = [
        "🏠 Dashboard",
        "➕ Add Task",
        "⚡ Task Templates",
        "🍅 Pomodoro Timer",
        "📅 Add Event",
        "✅ Task Manager",
        "📆 Calendar",
        "📊 Weekly View",
        "🎯 Daily Planner",
        "🧠 AI Practice"
    ]
    default_index = 0
    if (
        st.session_state.goto_page
        in pages
    ):
        default_index = pages.index(
            st.session_state.goto_page
        )
    global_search = st.sidebar.text_input("🔍 Quick Search",placeholder="Search tasks...")
    st.sidebar.markdown("## 🚀 Navigation")
    from telegram_utils import (
        send_telegram_message
    )

    if st.sidebar.button(
        "📨 Test Telegram Alert"
    ):

        send_telegram_message(

            "🚨 FocusFlow Test Alert!\n\n"

            "Telegram notifications "
            "are working successfully ✅"
        )

        st.sidebar.success(
            "Test alert sent!"
        )
    page = st.sidebar.radio(
        "📍 Navigation",
        options=pages,
        index=default_index,
        label_visibility="collapsed"

    )
    st.session_state.goto_page = page
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout",use_container_width=True):
        st.session_state.user = None
        st.rerun()
    
    # ---------------- DASHBOARD ----------------
    if page == "🏠 Dashboard":
        st.header("📊 Your Dashboard")
        tab1, tab2, tab3= st.tabs([
            "📊 Overview",
            "📈 Analytics",
            "📅 Planner"
        ])
        if not is_online():
            st.warning(
                "📴 Offline Mode Active — "
                "Using local productivity features."
            )
        df = manager.get_tasks(user[0])
        with tab1:
            # Overdue Tasks Alert
            overdue = manager.get_overdue_tasks(
                user[0]
            )
            if not overdue.empty:
                st.error(
                    f"🚨 {len(overdue)} overdue task(s)!"
                )
                with st.expander(
                    "View Overdue Tasks"
                ):
                    for _, row in overdue.iterrows():
                        st.write(
                            f"❌ {row['task']} "
                            f"(Due: {row['deadline']})"
                        )
            # Upcoming Tasks
            upcoming = manager.get_upcoming_tasks(
                user[0]
            )
            if not upcoming.empty:
                st.subheader(
                    "📅 Upcoming Tasks"
                )
                for _, row in upcoming.iterrows():
                    priority = row["priority"]
                    if priority == "High":
                        color = "🔴"
                    elif priority == "Medium":
                        color = "🟡"
                    else:
                        color = "🟢"
                    st.write(
                        f"{color} "
                        f"**{row['task']}** "
                        f"(Due: {row['deadline']})"
                    )
            # ✅ Mobile-friendly metrics
            col1, col2 = st.columns(2)
            completion = analytics.completion_rate(df)
            score = analytics.productivity_score(df)
            badge, message = analytics.motivation_badge(df)
            stress = analytics.stress_level(df)        
            with col1:
                st.metric("✅ Completion", f"{completion}%")
                st.metric("🏆 Badge", badge)
            
            with col2:
                st.metric("⚡ Score", score)
                st.metric("😌 Stress", stress)
            
            st.info(message)
            
            # ✅ Collapsible motivation section
            if "Beginner" in badge:
                with st.expander("💪 Need Motivation?"):
                    problem = st.text_area("What's blocking you?")
                    if st.button("Get AI Advice"):
                        if problem:
                            from ai_generator import generate_motivation
                            advice = generate_motivation(problem)
                            st.success("🤖 AI Coach Says:")
                            st.write(advice)
                        else:
                            st.warning("Please describe your challenge")
            
            # ✅ Quick Actions
            st.subheader("⚡ Quick Actions")
            is_mobile = st.sidebar.checkbox(
                "📱 Mobile Layout",
                value=True
            )
            if is_mobile:
                if st.button(
                    "➕ Add Quick Task",
                    use_container_width=True
                ):
                    st.session_state.goto_page = "➕ Add Task"
                    st.rerun()
                if st.button(
                    "📅 View Calendar",
                    use_container_width=True
                ):
                    st.session_state.goto_page = "📆 Calendar"
                    st.rerun()
            else:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(
                        "➕ Add Quick Task",
                        use_container_width=True
                    ):
                        st.session_state.goto_page = "➕ Add Task"
                        st.rerun()
                with col2:
                    if st.button(
                        "📅 View Calendar",
                        use_container_width=True
                    ):
                        st.session_state.goto_page = "📆 Calendar"
                        st.rerun()
        with tab2:   
            # ✅ Simplified graph
            st.subheader("📈 Your Progress")
            if not df.empty:
                completed = df[df["status"] == "Completed"].copy()
                if not completed.empty:
                    completed["created_at"] = pd.to_datetime(completed["created_at"])
                    daily = completed.groupby(completed["created_at"].dt.date).size()
                    fig, ax = plt.subplots(figsize=(10, 4))
                    ax.plot(daily.index, daily.values, marker="o", color="#2ECC71", linewidth=2)
                    ax.fill_between(daily.index, daily.values, alpha=0.3, color="#2ECC71")
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Tasks Completed")
                    ax.set_title("Daily Productivity Trend")
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
                else:
                    st.info("Complete some tasks to see your progress!")
            
            # Weekly AI Practice Performance
            st.subheader("📊 Performance Analytics")
            weekly_scores = manager.get_weekly_scores(
                user[0]
            )
            if not weekly_scores.empty:
                st.subheader(
                    "🧠 Weekly AI Practice"
                )
                fig, ax = plt.subplots(
                    figsize=(10, 4)
                )
                ax.plot(
                    weekly_scores["date"],
                    weekly_scores["total_score"],
                    marker="o",
                    linewidth=3
                )
                ax.set_xlabel("Date")
                ax.set_ylabel("Score")
                ax.set_title(
                    "Weekly AI Performance"
                )
                plt.xticks(rotation=45)
                st.pyplot(fig)
        with tab3:
            st.subheader("🤖 AI Productivity Assistant")
            if st.button(
                "🧠 Analyze My Tasks",
                use_container_width=True
            ):
                if not df.empty:
                    task_summary = df[
                        ["task", "priority", "deadline", "status"]
                    ].to_string(index=False)
                    with st.spinner("AI analyzing tasks..."):
                        advice = generate_task_suggestions(
                            task_summary
                        )
                    st.success("✅ AI Suggestions")
                    st.write(advice)
                else:
                    st.warning("No tasks available for analysis.")
            # Email reminders section
            st.subheader("📧 Today's Reminders")
            today = datetime.date.today()
            due_tasks = df[
                (pd.to_datetime(df["deadline"]).dt.date == today) &
                (df["status"] == "Pending")
            ]
            
            if not due_tasks.empty:
                st.warning(f"⚠️ You have {len(due_tasks)} task(s) due today!")
                for _, task in due_tasks.iterrows():
                    st.write(f"• {task['task']}")
                
                if st.button("📨 Email Me Reminders"):
                    for _, row in due_tasks.iterrows():
                        success = send_email(
                            user[3],
                            "Task Reminder",
                            f"Task '{row['task']}' is due today!"
                        )

                        if success:
                            st.success("✅ Email sent!")
                        else:
                            st.warning("⚠️ Email could not be sent (offline mode).")
            else:
                st.success("✨ No tasks due today. Great job!")
        
        
        
    
    # ---------------- ADD TASK ----------------
    elif page == "➕ Add Task":
        st.header("➕ Add New Task")
        
        task = st.text_input("📝 Task Name", placeholder="E.g., Complete project report")
        description = st.text_area(
            "📝 Task Description",
            placeholder="Add detailed notes about this task..."
        )
        uploaded_file = st.file_uploader(
            "📎 Attach File",
            type=["pdf", "png", "jpg", "jpeg", "txt", "docx"]
        )
        
        attachment_path = None
        
        if uploaded_file:
        
            os.makedirs(
                "uploads",
                exist_ok=True
            )
        
            attachment_path = (
                f"uploads/{uploaded_file.name}"
            )
        
            with open(
                attachment_path,
                "wb"
            ) as f:
        
                f.write(
                    uploaded_file.getbuffer()
                )
        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox("🎯 Priority", ["High", "Medium", "Low"])
            category = st.selectbox(
                "📂 Category",
                ["Study", "Work", "Personal", "Health", "Meeting", "Other"]
            )
        with col2:
            time = st.number_input("⏱️ Hours Needed", min_value=1, value=2)
        
        deadline = st.date_input("📅 Deadline", min_value=datetime.date.today())
        deadline_time = st.time_input("⏰ Submission Time")
        deadline_datetime = datetime.datetime.combine(deadline,deadline_time)
        reminder_time = (deadline_datetime
                        - datetime.timedelta(hours=time))
        st.info(
            f"🚨 Reminder will trigger at:\n\n"
            f"{reminder_time.strftime('%d %b %Y %I:%M %p')}"
        )
        is_daily = st.checkbox("🔄 Make this a daily task")
        
        start_time = None
        end_time = None
        
        if is_daily:
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.time_input("🌅 Start Time")
            with col2:
                end_time = st.time_input("🌆 End Time")
        
        if st.button("✅ Add Task", use_container_width=True):
            if task:
                attachment_path = ""
                if uploaded_file is not None:
                    attachment_path = os.path.join(
                        "uploads",
                        uploaded_file.name
                    )
                    # with open(attachment_path, "wb") as f:
                    #     f.write(uploaded_file.getbuffer())
                manager.add_task(user[0], task, description, priority, category, time, deadline,str(reminder_time), attachment_path, is_daily, start_time, end_time)
                st.success("✅ Task added successfully!")
                st.balloons()
            else:
                st.warning("⚠️ Please enter a task name")
    
    # ---------------- ADD EVENT ----------------
    elif page == "📅 Add Event":
        st.header("📅 Add Event")
        
        title = st.text_input("📌 Event Name", placeholder="E.g., Team Meeting")
        category = st.selectbox("🏷️ Category", ["Exam", "Personal", "Meeting", "Other"])
        date = st.date_input("📆 Event Date", min_value=datetime.date.today())
        
        if st.button("✅ Add Event", use_container_width=True):
            if title:
                manager.add_event(user[0], title, date, category)
                st.success("✅ Event added!")
            else:
                st.warning("⚠️ Please enter event name")
    
    # ---------------- TASK MANAGER ----------------
    elif page == "✅ Task Manager":
        st.header("✅ Task Manager")
        search = st.text_input(
            "🔍 Search Tasks",
            placeholder="Search by task name..."
        )
        
        df = manager.get_tasks(user[0])
        if global_search:
            df = df[df["task"].str.contains(global_search,case=False,na=False)]
        # Export tasks to CSV
        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Export Tasks to CSV",
            data=csv,
            file_name=f"tasks_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
        if search:
            df = df[
                df["task"].str.contains(search, case=False, na=False)
            ]
        
        # ✅ Tabs for better organization
        tab1, tab2, tab3 = st.tabs(["📋 All Tasks", "🔄 Daily Tasks", "⏰ Pending"])
        
        with tab1:
            if not df.empty:
                for _, task in df.iterrows():
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            status_icon = "✅" if task["status"] == "Completed" else "⏳"
                            priority = task["priority"]
                            if priority == "High":
                                priority_color = "🔴"
                            elif priority == "Medium":
                                priority_color = "🟡"
                            else:
                                priority_color = "🟢"
                            st.markdown(f"""
                            <div style="
                            padding:15px;
                            border-radius:12px;
                            background-color:#1E1E1E;
                            margin-bottom:10px;
                            border-left:6px solid #4CAF50;
                            ">
                            <h4>
                            {status_icon}
                            {task['task']}
                            {priority_color}
                            </h4>
                            <p>📂 {task['category']}
                            <br>📅 Due: {task['deadline']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            progress = manager.get_task_progress(task["id"])
                            if progress > 0:
                                st.progress(progress / 100)
                                st.caption(f"📊 Progress: {progress}%")
                            if task["description"]:
                                st.caption(task["description"])
                            if task["attachment"]:
                                file_path = task["attachment"]
                                file_name = os.path.basename(file_path)
                                try:
                                    with open(file_path, "rb") as file:
                                        st.download_button(
                                            label=f"📎 Open {file_name}",
                                            data=file,
                                            file_name=file_name,
                                            use_container_width=True,
                                            key=f"file_{task['id']}"
                                        )
                                except FileNotFoundError:
                                    st.warning("Attachment file missing")
                            # st.caption(f"📂 {task['category']} | "f"Due: {task['deadline']} | Priority: {task['priority']}")
                            subtask_input = st.text_input(
                                f"Add subtask for {task['task']}",
                                key=f"subtask_{task['id']}"
                            )
                            if st.button(
                                "➕ Add Subtask",
                                key=f"add_sub_{task['id']}"
                            ):
                                if subtask_input:
                                    manager.add_subtask(task["id"], subtask_input)
                                    st.rerun()
                            subtasks = manager.get_subtasks(task["id"])
                            if not subtasks.empty:
                                for _, sub in subtasks.iterrows():
                                    checked = sub["status"] == "Completed"
                                    if st.checkbox(
                                        sub["subtask"],
                                        value=checked,
                                        key=f"sub_{sub['id']}"
                                    ):
                                        if not checked:
                                            manager.complete_subtask(sub["id"])
                                            st.rerun()
                        with col2:
                            if task["status"] == "Pending":
                                if st.button("✔️", key=f"complete_{task['id']}"):
                                    manager.complete_task(task['id'])
                                    st.rerun()
                        with col3:
                            if st.button("🗑️", key=f"delete_{task['id']}"):
                                # You'll need to add delete_task to backend.py
                                if st.button("🗑️", key=f"delete_{task['id']}"):
                                    manager.delete_task(task["id"])
                                    st.success("Task deleted!")
                                    st.rerun()
                        st.divider()
            else:
                st.markdown("""
                <div style="
                padding:30px;
                text-align:center;
                border-radius:15px;
                background-color:#1E1E1E;
                margin-top:20px;
                ">
                <h2>📭 No Tasks Yet</h2>
                <p>Start by adding your first task and
                boost your productivity 🚀
                </p></div>
                """, unsafe_allow_html=True)
        
        with tab2:
            daily_tasks = df[df["is_daily"] == 1]
            if not daily_tasks.empty:
                st.dataframe(daily_tasks[["task", "start_time", "end_time", "status"]], use_container_width=True)
            else:
                st.info("No daily tasks configured")
        
        with tab3:
            pending = df[df["status"] == "Pending"]
            if not pending.empty:
                st.dataframe(pending[["task", "priority", "deadline"]], use_container_width=True)
            else:
                st.success("🎉 No pending tasks!")
    
    # ---------------- CALENDAR ----------------
    elif page == "📆 Calendar":
        st.header("📆 Task Calendar")
        
        try:
            from streamlit_calendar import calendar
            
            events = []
            df = manager.get_tasks(user[0])
            
            if not df.empty:
                for _, row in df.iterrows():
                    if pd.isna(row["deadline"]):
                        continue
                    events.append({
                        "id": str(row["id"]),
                        "title": row["task"],
                        "start": str(row["deadline"]),
                        "color": "#FF4B4B" if row["status"] == "Pending" else "#00C851"
                    })
            
            events_df = manager.get_events(user[0])
            if not events_df.empty:
                for _, row in events_df.iterrows():
                    events.append({
                        "id": f"event_{row['id']}",
                        "title": f"{row['category']} - {row['title']}",
                        "start": str(row["event_date"]),
                        "color": get_event_color(row["category"])
                    })
            
            if events:
                st.markdown("""
                <style>
                .fc{
                    font-size:14px;
                }
                @media (max-width:768px){
                    .fc-toolbar-title{
                        font-size:18px !important;
                    }
                    .fc-button{
                        padding:4px !important;
                        font-size:12px !important;
                    }
                }
                </style>
                """, unsafe_allow_html=True)
                result = calendar(
                    events=events,
                    options={
                        "initialView":"dayGridMonth",
                        "editable":True,
                        "height":600
                    },
                    key="monthly_calendar"
                )
                
                if result and "eventChange" in result:
                    event = result["eventChange"]
                    event_id = event["event"]["id"]
                    new_date = event["event"]["start"]
                    if "event_" in event_id:
                        e_id = event_id.replace("event_", "")
                        manager.update_event_date(e_id, new_date)
                    else:
                        manager.update_deadline(event_id, new_date)
                    st.success("✅ Updated!")
                    st.rerun()
            else:
                st.markdown("""
                <div style="
                padding:25px;
                text-align:center;
                border-radius:15px;
                background-color:#1E1E1E;
                margin-top:20px;
                ">
                <h3>📅 Calendar Empty</h3>
                <p>Add tasks or events to start planning.</p></div>
                """, unsafe_allow_html=True)
        
        except ImportError:
            st.error("Calendar feature requires 'streamlit-calendar' package. Install with: pip install streamlit-calendar")
    
    # ---------------- WEEKLY VIEW ----------------
    elif page == "📊 Weekly View":
        st.header("📊 Weekly Planner")
        
        if "week_offset" not in st.session_state:
            st.session_state.week_offset = 0
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Previous"):
                st.session_state.week_offset -= 1
                st.rerun()
        with col2:
            st.write(f"**Week {st.session_state.week_offset}**")
        with col3:
            if st.button("Next ➡️"):
                st.session_state.week_offset += 1
                st.rerun()
        
        today = datetime.date.today()
        start_week = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(weeks=st.session_state.week_offset)
        days = [start_week + datetime.timedelta(days=i) for i in range(7)]
        
        df = manager.get_tasks(user[0])
        events_df = manager.get_events(user[0])
        
        # ✅ Mobile-friendly columns
        for day in days:
            with st.expander(f"📅 {day.strftime('%A, %b %d')}"):
                if not df.empty:
                    day_tasks = df[pd.to_datetime(df["deadline"]).dt.date == day]
                    if not day_tasks.empty:
                        st.write("**Tasks:**")
                        for _, row in day_tasks.iterrows():
                            priority = row["priority"]
                            if priority == "High":
                                icon = "🔴"
                            elif priority == "Medium":
                                icon = "🟡"
                            else:
                                icon = "🟢"
                            st.markdown(
                                f"{icon} "
                                f"**{row['task']}**"
                            )
                                            
                if not events_df.empty:
                    day_events = events_df[pd.to_datetime(events_df["event_date"]).dt.date == day]
                    if not day_events.empty:
                        st.write("**Events:**")
                        for _, row in day_events.iterrows():
                            st.markdown(
                                f"🎯 "
                                f"**{row['title']}** "
                                f"({row['category']})"
                            )
    
    # ---------------- DAILY PLANNER ----------------
    elif page == "🎯 Daily Planner":
        st.header("🎯 Daily Schedule Generator")
        
        hours = st.slider("⏰ Available Hours Today", 1, 24, 6)
        
        df = manager.get_tasks(user[0])
        
        if st.button("✨ Generate My Schedule", use_container_width=True):
            schedule = manager.generate_daily_schedule(df, hours)
            
            if schedule:
                st.success(f"📋 Optimized schedule for {hours} hours:")
                for i, task in enumerate(schedule, 1):
                    st.write(f"{i}. **{task['task']}** - {task['estimated_time']} hrs (Due: {task['deadline']})")
            else:
                st.info(
                    "✨ No suitable tasks found "
                    "for today's schedule."
                )
    
    # ---------------- AI PRACTICE ----------------
    elif page == "🧠 AI Practice":
        st.header("🧠 AI Question Generator")
        
        today_count = manager.get_today_count(user[0])
        
        # ✅ Better progress visualization
        st.subheader("📊 Daily Progress")
        progress = min(today_count / 5, 1.0)
        st.progress(progress)
        st.write(f"**{today_count}/5** questions completed today")
        
        if today_count >= 5:
            st.success("🎉 Daily target achieved!")
        else:
            st.info(f"💪 {5 - today_count} more to go!")
        
        col1, col2 = st.columns(2)
        with col1:
            topic = st.selectbox(
                "📚 Topic",
                ["Quantitative Aptitude", "Logical Reasoning", "Number Series",
                 "Time and Work", "Probability", "Percentages", "Puzzles"]
            )
        with col2:
            difficulty = st.selectbox("⚡ Difficulty", ["Easy", "Medium", "Hard"])
        
        if "ai_q" not in st.session_state:
            st.session_state.ai_q = None
        
        if st.button("🎲 Generate Question", use_container_width=True):
            with st.spinner("Generating..."):
                q = generate_question(topic, difficulty)
                if q:
                    st.session_state.ai_q = q
                else:
                    st.error("Generation failed. Try again!")
        
        if st.session_state.ai_q:
            q = st.session_state.ai_q
            
            st.markdown("---")
            st.subheader("❓ Question")
            st.write(q["question"])
            
            choice = st.radio("Choose your answer:", q["options"], key="answer_choice")
            
            if st.button("✅ Submit Answer", use_container_width=True):
                if choice == q["answer"]:
                    st.success("🎉 Correct!")
                    st.balloons()
                    score = 1
                else:
                    st.error(f"❌ Wrong! Correct answer: {q['answer']}")
                    score = 0
                
                st.info(f"💡 Explanation: {q['explanation']}")
                manager.save_score(user[0], score)
                
                # Clear question after submission
                st.session_state.ai_q = None
                if st.button("🔄 Try Another Question"):
                    st.rerun()
    # ---------------- POMODORO TIMER ----------------
    elif page == "🍅 Pomodoro Timer":
        st.header("🍅 Pomodoro Focus Timer")
        st.info(
            "25 minutes focus + 5 minutes break"
        )
        if "pomodoro_seconds" not in st.session_state:
            st.session_state.pomodoro_seconds = 25 * 60
        if "pomodoro_running" not in st.session_state:
            st.session_state.pomodoro_running = False
        mins, secs = divmod(
            st.session_state.pomodoro_seconds,
            60
        )
        timer_display = f"{mins:02d}:{secs:02d}"
        st.markdown(
            f"# ⏳ {timer_display}"
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "▶️ Start Focus Session",
                use_container_width=True
            ):
                st.session_state.pomodoro_running = True
        with col2:
            if st.button(
                "🔄 Reset",
                use_container_width=True
            ):
                st.session_state.pomodoro_seconds = 25 * 60
                st.session_state.pomodoro_running = False
        if st.session_state.pomodoro_running:
            time.sleep(1)
            st.session_state.pomodoro_seconds -= 1
            if st.session_state.pomodoro_seconds <= 0:
                st.success("🎉 Focus session completed!")
                st.balloons()
                st.session_state.pomodoro_running = False
                st.session_state.pomodoro_seconds = 25 * 60
            st.rerun()
    
    # ---------------- TASK TEMPLATES ----------------
    elif page == "⚡ Task Templates":
        st.header("⚡ Task Templates")
        st.write(
            "Create multiple productivity tasks instantly."
        )
        selected_template = st.selectbox(
            "Choose Template",
            list(TASK_TEMPLATES.keys())
        )
        st.subheader("Included Tasks")
        for item in TASK_TEMPLATES[selected_template]:
            st.write(f"✅ {item}")
        if st.button(
            "🚀 Create Template Tasks",
            use_container_width=True
        ):
            for task_name in TASK_TEMPLATES[selected_template]:
                manager.add_task(
                    user[0],
                    task_name,
                    "",
                    "Medium",
                    "Personal",
                    1,
                    datetime.date.today(),False, None, None
                )
            st.success("✅ Template tasks created!")
