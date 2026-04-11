import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing Master", layout="wide")

# २. गुगल शीट कनेक्शन (Secrets मधील लिंक आणि क्रेडेंशियल्स वापरून)
conn = st.connection(
    "gsheets", 
    type=GSheetsConnection, 
    credentials=st.secrets, 
    spreadsheet=st.secrets["spreadsheet"]
)

# ३. एजंट लिस्ट
AGENTS = {"Dhananjay": "789", "Jitesh": "101"}
AGENT_FULL_NAMES = {"Dhananjay": "Dhananjay Pakhre", "Jitesh": "Jitesh Krishnan"}

if 'marketing_logged_in' not in st.session_state:
    st.session_state.marketing_logged_in = False

if not st.session_state.marketing_logged_in:
    u_input = st.text_input("Agent ID")
    p_input = st.text_input("Password", type="password")
    if st.button("Login"):
        if u_input in AGENTS and p_input == AGENTS[u_input]:
            st.session_state.marketing_logged_in = True
            st.session_state.agent_display_name = AGENT_FULL_NAMES[u_input]
            st.rerun()
        else: st.error("ID किंवा पासवर्ड चुकलाय!")
else:
    st.markdown(f"### नमस्ते, {st.session_state.agent_display_name}! 🙏")
    loc = get_geolocation()
    
    tab1, tab2 = st.tabs(["➕ New Visit", "🛠️ Manage Records"])

    with tab1:
        with st.form("visit_form", clear_on_submit=True):
            c_name = st.text_input("Customer Name")
            c_mob = st.text_input("Mobile No.")
            c_addr = st.text_area("Address")
            purpose = st.selectbox("Purpose", ["New Inquiry", "Follow-up", "Order"])
            submit = st.form_submit_button("SUBMIT DATA")
            
            if submit:
                if loc and 'coords' in loc:
                    lat, lon = loc['coords'].get('latitude'), loc['coords'].get('longitude')
                    map_link = f"https://www.google.com/maps?q={lat},{lon}"
                    
                    visit_data = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Agent": st.session_state.agent_display_name,
                        "Customer": c_name, "Mobile": f"'{c_mob}", "Address": c_addr,
                        "Purpose": purpose, "Quotation_Sent": "No", "Follow_up_Date": "-", 
                        "Location": map_link
                    }])
                    try:
                        df_existing = conn.read(ttl=0)
                        df_updated = pd.concat([df_existing, visit_data], ignore_index=True)
                        conn.update(data=df_updated)
                        st.success("डेटा यशस्वीरित्या सेव्ह झाला!")
                        st.balloons()
                    except Exception as e: st.error(f"Error: {e}")
                else: st.error("लोकेशन सापडले नाही.")

    with tab2:
        try:
            full_df = conn.read(ttl=0)
            my_leads = full_df[full_df['Agent'] == st.session_state.agent_display_name].copy()
            if not my_leads.empty:
                edited_df = st.data_editor(my_leads, use_container_width=True, num_rows="dynamic", hide_index=True)
                if st.button("SAVE CHANGES"):
                    other_df = full_df[full_df['Agent'] != st.session_state.agent_display_name]
                    final_df = pd.concat([other_df, edited_df], ignore_index=True)
                    conn.update(data=final_df)
                    st.success("अपडेट झाले!")
                    st.rerun()
            else: st.info("डेटा नाही.")
        except: st.error("डेटा लोड झाला नाही.")

    if st.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
