import streamlit as st
import pandas as pd
from datetime import datetime
from github import Github
import json

st.set_page_config(page_title="Support Desk", layout="centered")

# --- GITHUB SYNC LOGIC ---
def get_github_repo():
    g = Github(st.secrets["github"]["token"])
    return g.get_repo(st.secrets["github"]["repo"])

def load_tickets_from_github():
    try:
        repo = get_github_repo()
        file_content = repo.get_contents(st.secrets["github"]["file_path"])
        return json.loads(file_content.decoded_content.decode())
    except:
        # If file doesn't exist yet, return empty list
        return []

def save_tickets_to_github(tickets):
    repo = get_github_repo()
    path = st.secrets["github"]["file_path"]
    content = json.dumps(tickets, indent=4)
    
    try:
        # Update existing file
        contents = repo.get_contents(path)
        repo.update_file(path, "Update tickets", content, contents.sha)
    except:
        # Create new file if it doesn't exist
        repo.create_file(path, "Initial ticket file", content)

# Initialize session state from GitHub if empty
if "tickets" not in st.session_state:
    st.session_state.tickets = load_tickets_from_github()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- ADMIN LOGIN (Same as before) ---
with st.sidebar:
    if not st.session_state.logged_in:
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == st.secrets["admin_credentials"]["username"] and \
               pw == st.secrets["admin_credentials"]["password"]:
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.write(f"Logged in as: **Admin**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

st.title("🎫 Help Ticket Machine")

# --- SUBMISSION ---
with st.expander("Submit a New Ticket", expanded=not st.session_state.logged_in):
    with st.form("ticket_form", clear_on_submit=True):
        subject = st.text_input("Subject")
        description = st.text_area("Issue Description")
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
        if st.form_submit_button("Submit Ticket"):
            if subject and description:
                new_ticket = {
                    "id": len(st.session_state.tickets) + 1,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "subject": subject,
                    "description": description,
                    "priority": priority,
                    "status": "Open"
                }
                st.session_state.tickets.append(new_ticket)
                save_tickets_to_github(st.session_state.tickets) # SAVE TO GITHUB
                st.success("Ticket saved to GitHub!")
            else:
                st.error("Missing info.")

# --- DISPLAY & ADMIN EDITING ---
st.divider()
for i, ticket in enumerate(st.session_state.tickets):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**[{ticket['priority']}] {ticket['subject']}**")
        st.caption(f"Status: {ticket['status']} | Filed: {ticket['timestamp']}")
    with col2:
        if st.session_state.logged_in:
            new_status = st.selectbox("Update", ["Open", "In Progress", "Resolved", "Closed"], 
                                      index=["Open", "In Progress", "Resolved", "Closed"].index(ticket['status']),
                                      key=f"s_{ticket['id']}")
            if new_status != ticket['status']:
                st.session_state.tickets[i]['status'] = new_status
                save_tickets_to_github(st.session_state.tickets) # SAVE TO GITHUB
                st.rerun()
        else:
            st.info(ticket['status'])
    st.divider()
