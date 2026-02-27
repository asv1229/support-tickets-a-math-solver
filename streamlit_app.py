import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_title("Support Desk")

# Initialize session state for tickets if it doesn't exist
if "tickets" not in st.session_state:
    st.session_state.tickets = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- AUTHENTICATION LOGIC ---
def login():
    with st.sidebar:
        st.title("Admin Portal")
        if not st.session_state.logged_in:
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.button("Login"):
                # Accessing variables from st.secrets
                if user == st.secrets["admin_credentials"]["username"] and \
                   pw == st.secrets["admin_credentials"]["password"]:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        else:
            st.write(f"Logged in as: **{st.secrets['admin_credentials']['username']}**")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.rerun()

login()

# --- USER INTERFACE: TICKET SUBMISSION ---
st.title("🎫 Help Ticket Machine")

with st.expander("Submit a New Ticket", expanded=not st.session_state.logged_in):
    with st.form("ticket_form", clear_on_submit=True):
        subject = st.text_input("Subject")
        description = st.text_area("Issue Description")
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
        submitted = st.form_submit_button("Submit Ticket")
        
        if submitted:
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
                st.success("Ticket submitted successfully!")
            else:
                st.error("Please fill in both the subject and description.")

st.divider()

# --- ADMIN DASHBOARD: VIEW & EDIT ---
st.subheader("Current Tickets")

if not st.session_state.tickets:
    st.info("No tickets found.")
else:
    # Convert to DataFrame for display
    df = pd.DataFrame(st.session_state.tickets)
    
    # Simple list view for everyone
    for i, ticket in enumerate(st.session_state.tickets):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"**[{ticket['priority']}] {ticket['subject']}**")
            st.caption(f"ID: {ticket['id']} | Status: {ticket['status']} | Filed: {ticket['timestamp']}")
            st.write(ticket['description'])
        
        with col2:
            # EDITING RIGHTS ONLY FOR ADMIN
            if st.session_state.logged_in:
                new_status = st.selectbox(
                    "Update Status", 
                    ["Open", "In Progress", "Resolved", "Closed"], 
                    index=["Open", "In Progress", "Resolved", "Closed"].index(ticket['status']),
                    key=f"status_{ticket['id']}"
                )
                
                if new_status != ticket['status']:
                    st.session_state.tickets[i]['status'] = new_status
                    st.toast(f"Ticket #{ticket['id']} updated!")
                    st.rerun()
                
                if st.button("🗑️ Delete", key=f"del_{ticket['id']}"):
                    st.session_state.tickets.pop(i)
                    st.rerun()
            else:
                # Non-admins see a status badge
                st.info(ticket['status'])
        
        st.divider()
