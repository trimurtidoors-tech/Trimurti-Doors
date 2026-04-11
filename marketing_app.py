import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing Master", layout="wide")

# २. गुगल शीट कॉन्फिगरेशन (तुझ्या नवीन मार्केटिंग शीटचा ID)
MARKETING_SHEET_ID = "1hMy9ETB_wfGGLEE3F6JF1t1AJLOHtR4Gqs_apiJkFss" 

# ३. गुगल शीट कनेक्शन (PEM Error टाळण्यासाठी सुधारित पद्धत)
@st.cache_resource
def get_gspread_client():
    # Secrets मधून क्रेडेंशियल्स मिळवणे
    creds_info = dict(st.secrets["connections"]["gsheets"])
    # की (Key) मधील तांत्रिक त्रुटी (\n) नीट करणे
    if "private_key" in creds_info:
        creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
    
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    return gspread.authorize(creds)

# ४. लॉगिन सिस्टम
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
    st.sidebar.info(f"लॉगिन: {st.session_state.agent_display_name}")
    
    # लोकेशन मिळवणे
    loc = get_geolocation()
    
    tab1, tab2 = st.tabs(["➕ नवीन नोंद (Submit)", "📊 माझा डेटा (Reports)"])

    # --- TAB 1: डेटा सबमिट करणे ---
    with tab1:
        with st.form("marketing_form", clear_on_submit=True):
            st.subheader("व्हिजिट डिटेल्स भरा")
            c_name = st.text_input("Customer Name")
            c_mob = st.text_input("Mobile No.")
            c_addr = st.text_area("Address")
            purpose = st.selectbox("Purpose", ["New Inquiry", "Follow-up", "Order"])
            submit = st.form_submit_button("डेटा सेव्ह करा")
            
            if submit:
                try:
                    client = get_gspread_client()
                    sh = client.open_by_key(MARKETING_SHEET_ID)
                    worksheet = sh.get_worksheet(0)
                    
                    # लोकेशन लिंक तयार करणे
                    map_link = "-"
                    if loc and 'coords' in loc:
                        lat, lon = loc['coords'].get('latitude'), loc['coords'].get('longitude')
                        map_link = f"http://www.google.com/maps/place/{lat},{lon}"
                    
                    # नवीन ओळ तयार करणे (तुमच्या शीटमधील कॉलमप्रमाणे)
                    new_row = [
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        st.session_state.agent_display_name,
                        c_name, f"'{c_mob}", c_addr, purpose, map_link
                    ]
                    
                    worksheet.append_row(new_row)
                    st.success("✅ मार्केटिंग डेटा यशस्वीरित्या सेव्ह झाला!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- TAB 2: डेटा पाहणे ---
    with tab2:
        try:
            client = get_gspread_client()
            sh = client.open_by_key(MARKETING_SHEET_ID)
            # पूर्ण डेटा वाचणे
            all_data = sh.get_worksheet(0).get_all_records()
            if all_data:
                df = pd.DataFrame(all_data)
                # फक्त स्वतःचा डेटा फिल्टर करणे
                my_data = df[df['Agent'] == st.session_state.agent_display_name]
                st.dataframe(my_data, use_container_width=True, hide_index=True)
            else:
                st.info("शीटमध्ये अजून कोणताही डेटा नाही.")
        except Exception as e:
            st.error(f"डेटा लोड करताना अडचण आली: {e}")

    if st.sidebar.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
