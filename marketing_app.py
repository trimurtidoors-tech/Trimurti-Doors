import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing Master", layout="wide")

# २. गुगल शीट कनेक्शन (Gspread पद्धत - १००% सुरक्षित)
@st.cache_resource
def get_gspread_client():
    # Secrets मधील माहिती डिक्शनरी स्वरूपात घेणे
    creds_info = dict(st.secrets["connections"]["gsheets"])
    # की (Key) नीट करणे
    if "private_key" in creds_info:
        creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
    
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    return gspread.authorize(creds)

# शीटमधील डेटा वाचण्यासाठी फंक्शन
def read_data():
    client = get_gspread_client()
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sh = client.open_by_url(sheet_url)
    worksheet = sh.get_worksheet(0)
    data = worksheet.get_all_records()
    return pd.DataFrame(data), worksheet

# लॉगिन माहिती
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
            st.error("चुकीचा आयडी किंवा पासवर्ड!")
else:
    st.markdown(f"### नमस्ते, {st.session_state.agent_display_name}! 🙏")
    loc = get_geolocation()
    
    tab1, tab2 = st.tabs(["➕ नवीन नोंद", "🛠️ रेकॉर्ड्स मॅनेज करा"])

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
                    map_link = f"http://maps.google.com/?q={lat},{lon}"
                    
                    new_row = [
                        datetime.now().strftime("%Y-%m-%d"),
                        st.session_state.agent_display_name,
                        c_name, f"'{c_mob}", c_addr, purpose, "No", "-", map_link
                    ]
                    try:
                        _, worksheet = read_data()
                        worksheet.append_row(new_row)
                        st.success("✅ डेटा सेव्ह झाला!")
                    except Exception as e: st.error(f"Error: {e}")
                else: st.error("लोकेशन सापडले नाही.")

    with tab2:
        try:
            df, worksheet = read_data()
            my_leads = df[df['Agent'] == st.session_state.agent_display_name].copy()
            if not my_leads.empty:
                edited_df = st.data_editor(my_leads, use_container_width=True, num_rows="dynamic", hide_index=True)
                if st.button("💾 SAVE CHANGES"):
                    # पूर्ण शीट अपडेट करणे
                    other_df = df[df['Agent'] != st.session_state.agent_display_name]
                    final_df = pd.concat([other_df, edited_df], ignore_index=True)
                    worksheet.clear()
                    worksheet.update([final_df.columns.values.tolist()] + final_df.values.tolist())
                    st.success("✅ अपडेट यशस्वी!")
                    st.rerun()
            else: st.info("डेटा नाही.")
        except Exception as e: st.error(f"डेटा लोड एरर: {e}")

    if st.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
