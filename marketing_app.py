import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing Master", layout="wide")

# २. गुगल शीट कॉन्फिगरेशन (Marketing Sheet साठी)
# तुमची मार्केटिंग शीट उघडा आणि ब्राउझरमधील लिंकमधून हा ID बदला
MARKETING_SHEET_ID = "1F8XY5rjNSA3sY_5aeHAm905KSMwiaoWBqMZsf1NxSjk"
# डेटा वाचण्यासाठी CSV लिंक
READ_URL = f"https://docs.google.com/spreadsheets/d/{MARKETING_SHEET_ID}/gviz/tq?tqx=out:csv"

# ३. लॉगिन माहिती
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
    st.sidebar.markdown(f"**Agent:** {st.session_state.agent_display_name}")
    if st.sidebar.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()

    loc = get_geolocation()
    
    tab1, tab2 = st.tabs(["➕ नवीन नोंद (Submit)", "📊 माझा रिपोर्ट (Reports)"])

    # --- TAB 1: डेटा सबमिट करणे ---
    with tab1:
        st.subheader("व्हिजिटची माहिती भरा")
        
        with st.form("marketing_form", clear_on_submit=True):
            c_name = st.text_input("Customer Name")
            c_mob = st.text_input("Mobile No.")
            c_addr = st.text_area("Address")
            purpose = st.selectbox("Purpose", ["New Inquiry", "Follow-up", "Order"])
            
            # लोकेशन लिंक तयार करणे
            map_link = "-"
            if loc and 'coords' in loc:
                lat, lon = loc['coords'].get('latitude'), loc['coords'].get('longitude')
                map_link = f"https://www.google.com/maps?q={lat},{lon}"
                st.success("📍 लोकेशन सापडले आहे!")
            
            submit = st.form_submit_button("डेटा सेव्ह करा")
            
            if submit:
                # आपण क्रेडेंशियल्सऐवजी डेटा सबमिट करण्यासाठी गुगल शीटची 'Edit Link' वापरणार आहोत
                # किंवा सोपा पर्याय म्हणून सध्या येथे एक मेसेज देऊ:
                st.warning("नोंद करण्यासाठी खालील 'Direct Entry' बटण वापरा (PEM एरर टाळण्यासाठी):")
                st.link_button("🚀 शीटमध्ये एंट्री करा", f"https://docs.google.com/spreadsheets/d/{MARKETING_SHEET_ID}/edit", use_container_width=True)

    # --- TAB 2: डेटा पाहणे ---
    with tab2:
        try:
            # थेट CSV लिंकवरून डेटा वाचणे (यात PEM एरर येत नाही)
            df = pd.read_csv(READ_URL)
            df.columns = df.columns.str.strip() # नावे स्वच्छ करणे
            
            if 'Agent' in df.columns:
                my_data = df[df['Agent'] == st.session_state.agent_display_name]
                if not my_data.empty:
                    st.dataframe(my_data, use_container_width=True, hide_index=True)
                else:
                    st.info("तुमच्या नावावर अजून डेटा नाही.")
            else:
                st.error("शीटमध्ये 'Agent' नावाचा कॉलम मिळाला नाही.")
        except Exception as e:
            st.error(f"डेटा लोड एरर: {e}")
