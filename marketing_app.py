import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Setup
st.set_page_config(page_title="Trimurti Field Marketing", layout="wide")

# 2. Google Sheets Connection
# Tula 'connections.gsheets' secrets madhye asne garjeche ahe
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Connection Error: {e}")
    st.stop()

# 3. Agent Login
AGENTS = {"Dhananjay": "789", "Jitesh": "101"}
AGENT_FULL_NAMES = {"Dhananjay": "Dhananjay Pakhre", "Jitesh": "Jitesh Krishnan"}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Field Agent Login")
    u_id = st.text_input("Agent ID")
    u_pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if u_id in AGENTS and u_pw == AGENTS[u_id]:
            st.session_state.logged_in = True
            st.session_state.agent_name = AGENT_FULL_NAMES[u_id]
            st.rerun()
        else:
            st.error("Invalid Credentials")
else:
    st.sidebar.success(f"Welcome, {st.session_state.agent_name}")
    
    tab1, tab2 = st.tabs(["📝 New Entry", "📂 Upload Executive File"])

    # --- TAB 1: Manual Entry ---
    with tab1:
        with st.form("marketing_form", clear_on_submit=True):
            st.subheader("Add Field Visit Details")
            c_name = st.text_input("Customer Name")
            c_cat = st.selectbox("Category", ["Owner", "Contractor", "Builder", "Architect"])
            c_mob = st.text_input("Mobile Number")
            c_addr = st.text_area("Address")
            b_status = st.text_input("Building Status (e.g. Flooring Start)")
            
            submit = st.form_submit_button("Save to Sheet")
            
            if submit:
                new_data = pd.DataFrame([{
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Agent": st.session_state.agent_name,
                    "Customer Name": c_name,
                    "Category": c_cat,
                    "Mobile Number": f"'{c_mob}",
                    "Address": c_addr,
                    "Building Status": b_status
                }])
                try:
                    existing_df = conn.read(ttl=0)
                    updated_df = pd.concat([existing_df, new_data], ignore_index=True)
                    conn.update(data=updated_df)
                    st.success("✅ Data saved to Google Sheet!")
                except Exception as e:
                    st.error(f"Error saving data: {e}")

    # --- TAB 2: Upload Excel ---
    with tab2:
        st.subheader("Upload Executive's Excel Report")
        uploaded_file = st.file_uploader("Choose Excel File", type=["xlsx", "xls"])
        
        if uploaded_file:
            try:
                # Excel vachnyasathi 'openpyxl' lagel (requirements.txt madhye taka)
                df_raw = pd.read_excel(uploaded_file)
                
                # Column mapping tuzya file pramane
                df_final = pd.DataFrame({
                    "Date": df_raw.get('Date', datetime.now().strftime("%Y-%m-%d")),
                    "Agent": st.session_state.agent_name,
                    "Customer Name": df_raw.get('Contact Person Name', 'N/A'),
                    "Category": df_raw.get('Person Status', 'N/A'),
                    "Mobile Number": df_raw.get('Contact No', 'N/A'),
                    "Address": df_raw.get('Address', 'N/A'),
                    "Building Status": df_raw.get('In Progress', 'N/A')
                })
                
                st.write("Preview of Data:")
                st.dataframe(df_final, use_container_width=True)
                
                if st.button("Confirm & Upload to Sheet"):
                    existing_df = conn.read(ttl=0)
                    updated_df = pd.concat([existing_df, df_final], ignore_index=True)
                    conn.update(data=updated_df)
                    st.success(f"✅ {len(df_final)} entries uploaded successfully!")
            except Exception as e:
                st.error(f"File processing error: {e}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
