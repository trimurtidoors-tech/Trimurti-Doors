import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing Master", layout="wide")

# २. गुगल शीट लिंक (तुमच्या शीटची लिंक इथे टाका)
# टीप: आपण /edit ऐवजी /export?format=csv वापरून थेट डेटा वाचणार आहोत
SHEET_ID = "1F8XY5rjNSA3sY_5aeHAm905KSMwiaoWBqMZsf1NxSjk"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# ३. लॉगिन सिस्टिम
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
    
    tab1, tab2 = st.tabs(["➕ नवीन नोंद", "🛠️ रेकॉर्ड्स पाहणे"])

    with tab1:
        st.info("डेटा सबमिट करण्यासाठी सध्या ही सिस्टिम 'Public Mode' मध्ये आहे.")
        # इथे तुम्ही तुमची Google Form लिंक सुद्धा देऊ शकता जर हे काम करत नसेल तर
        st.markdown(f"[येथे क्लिक करून डेटा भरा](https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit)")

    with tab2:
        try:
            # थेट CSV लिंकवरून डेटा वाचणे (क्रेडेंशियल्सची गरज नाही)
            df = pd.read_csv(SHEET_URL)
            my_leads = df[df['Agent'] == st.session_state.agent_display_name]
            st.write(my_leads)
        except Exception as e:
            st.error(f"डेटा लोड एरर: {e}")

    if st.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
