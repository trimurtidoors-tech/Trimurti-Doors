import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing Master", layout="wide")

# २. गुगल शीट ID
MARKETING_SHEET_ID = "1hMy9ETB_wfGGLEE3F6JF1t1AJLOHtR4Gqs_apiJkFss" 

# ३. गुगल शीट कनेक्शन (पक्की पद्धत)
@st.cache_resource
def get_gspread_client():
    try:
        # Secrets मधून माहिती मिळवणे
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        
        # महत्त्वाची पायरी: की मधील बॅकस्लॅश \\n दुरुस्त करणे
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
        # क्रेडेंशियल्स तयार करणे
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"PEM/Key Error: {e}")
        st.stop()

# ४. डेटा मॅनेजमेंट फंक्शन
def handle_data():
    client = get_gspread_client()
    sh = client.open_by_key(MARKETING_SHEET_ID)
    worksheet = sh.get_worksheet(0)
    data = worksheet.get_all_records()
    return pd.DataFrame(data), worksheet

# ५. लॉगिन माहिती
AGENTS = {"Dhananjay": "789", "Jitesh": "101"}
AGENT_FULL_NAMES = {"Dhananjay": "Dhananjay Pakhre", "Jitesh": "Jitesh Krishnan"}

if 'marketing_logged_in' not in st.session_state:
    st.session_state.marketing_logged_in = False

if not st.session_state.marketing_logged_in:
    st.markdown("### 🔐 Agent Login")
    u_input = st.text_input("Agent ID")
    p_input = st.text_input("Password", type="password")
    if st.button("Login"):
        if u_input in AGENTS and p_input == AGENTS[u_input]:
            st.session_state.marketing_logged_in = True
            st.session_state.agent_display_name = AGENT_FULL_NAMES[u_input]
            st.rerun()
        else:
            st.error("आयडी किंवा पासवर्ड चुकीचा आहे!")
else:
    st.sidebar.success(f"एजंट: {st.session_state.agent_display_name}")
    loc = get_geolocation()
    
    tab1, tab2 = st.tabs(["➕ नवीन व्हिजिट", "📊 रिपोर्ट"])

    with tab1:
        with st.form("marketing_form", clear_on_submit=True):
            c_name = st.text_input("Customer Name")
            c_mob = st.text_input("Mobile No.")
            c_addr = st.text_area("Address")
            purpose = st.selectbox("Purpose", ["Inquiry", "Follow-up", "Order"])
            submit = st.form_submit_button("डेटा सेव्ह करा")
            
            if submit:
                try:
                    df, worksheet = handle_data()
                    
                    # लोकेशन लिंक
                    map_link = "-"
                    if loc and 'coords' in loc:
                        lat, lon = loc['coords'].get('latitude'), loc['coords'].get('longitude')
                        map_link = f"https://www.google.com/maps?q={lat},{lon}"
                    
                    new_row = [
                        datetime.now().strftime("%Y-%m-%d %H:%M"),
                        st.session_state.agent_display_name,
                        c_name, f"'{c_mob}", c_addr, purpose, map_link
                    ]
                    worksheet.append_row(new_row)
                    st.success("✅ डेटा मार्केटिंग शीटमध्ये सेव्ह झाला!")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab2:
        try:
            df, _ = handle_data()
            my_data = df[df['Agent'] == st.session_state.agent_display_name]
            st.dataframe(my_data, use_container_width=True, hide_index=True)
        except:
            st.info("डेटा उपलब्ध नाही.")

    if st.sidebar.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
