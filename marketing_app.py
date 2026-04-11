import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing Master", layout="wide")

# २. गुगल शीट कनेक्शन (PEM Error टाळण्यासाठी सुधारित पद्धत)
def connect_gsheet():
    try:
        # Secrets वाचणे
        creds = dict(st.secrets["connections"]["gsheets"])
        # की मधील तांत्रिक त्रुटी दुरुस्त करणे
        if "private_key" in creds:
            creds["private_key"] = creds["private_key"].replace("\\n", "\n")
        
        return st.connection("gsheets", type=GSheetsConnection, credentials=creds)
    except Exception as e:
        st.error(f"कन्फिगरेशन एरर: {e}")
        st.stop()

conn = connect_gsheet()

# ३. लॉगिन सिस्टिम
AGENTS = {"Dhananjay": "789", "Jitesh": "101"}
AGENT_FULL_NAMES = {"Dhananjay": "Dhananjay Pakhre", "Jitesh": "Jitesh Krishnan"}

if 'marketing_logged_in' not in st.session_state:
    st.session_state.marketing_logged_in = False

if not st.session_state.marketing_logged_in:
    st.markdown("### 🔐 Agent Login")
    u_id = st.text_input("Agent ID")
    u_pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if u_id in AGENTS and u_pw == AGENTS[u_id]:
            st.session_state.marketing_logged_in = True
            st.session_state.agent_display_name = AGENT_FULL_NAMES[u_id]
            st.rerun()
        else:
            st.error("चुकीचा पासवर्ड!")
else:
    st.sidebar.success(f"एजंट: {st.session_state.agent_display_name}")
    loc = get_geolocation()
    
    tab1, tab2 = st.tabs(["➕ नवीन नोंद (Submit)", "📊 माझा रिपोर्ट (Reports)"])

    # --- TAB 1: ॲपमध्येच डेटा भरणे ---
    with tab1:
        with st.form("visit_form", clear_on_submit=True):
            st.subheader("व्हिजिटची माहिती भरा")
            c_name = st.text_input("Customer Name")
            c_mob = st.text_input("Mobile No.")
            c_addr = st.text_area("Address")
            purpose = st.selectbox("Purpose", ["Inquiry", "Follow-up", "Order"])
            submit = st.form_submit_button("डेटा सेव्ह करा")
            
            if submit:
                # लोकेशन लिंक
                map_link = "-"
                if loc and 'coords' in loc:
                    lat, lon = loc['coords'].get('latitude'), loc['coords'].get('longitude')
                    map_link = f"https://www.google.com/maps?q={lat},{lon}"
                
                new_row = pd.DataFrame([{
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Agent": st.session_state.agent_display_name,
                    "Customer": c_name, "Mobile": f"'{c_mob}", "Address": c_addr,
                    "Purpose": purpose, "Location": map_link
                }])
                
                try:
                    existing_df = conn.read(ttl=0)
                    updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                    conn.update(data=updated_df)
                    st.success("✅ डेटा यशस्वीरित्या मार्केटिंग शीटमध्ये सेव्ह झाला!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- TAB 2: रिपोर्ट पाहणे ---
    with tab2:
        try:
            full_df = conn.read(ttl=0)
            my_data = full_df[full_df['Agent'] == st.session_state.agent_display_name]
            st.dataframe(my_data, use_container_width=True, hide_index=True)
        except:
            st.info("डेटा उपलब्ध नाही.")

    if st.sidebar.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
