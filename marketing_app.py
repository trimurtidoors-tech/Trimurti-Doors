import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing Master", layout="wide")

# २. गुगल शीट कॉन्फिगरेशन
# तुझ्या मार्केटिंग शीटचा ID: 1hMy9ETB_wfGGLEE3F6JF1t1AJLOHtR4Gqs_apiJkFss
SHEET_ID = "1hMy9ETB_wfGGLEE3F6JF1t1AJLOHtR4Gqs_apiJkFss"
# डेटा वाचण्यासाठी पब्लिक CSV लिंक
READ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

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
            st.error("आयडी किंवा पासवर्ड चुकीचा आहे!")
else:
    st.sidebar.success(f"एजंट: {st.session_state.agent_display_name}")
    
    # लोकेशन मिळवणे
    loc = get_geolocation()
    
    tab1, tab2 = st.tabs(["➕ नवीन नोंद (Submit)", "📊 माझा रिपोर्ट (View)"])

    # --- TAB 1: डेटा सबमिट करणे ---
    with tab1:
        st.subheader("व्हिजिटची नोंद करा")
        st.info("क्रेडेंशियल एररमुळे आपण सध्या डेटा भरण्यासाठी 'Direct Entry' वापरत आहोत.")
        
        # गुगल शीटची डायरेक्ट लिंक उघडणारे बटण
        st.link_button("🚀 गुगल शीटमध्ये माहिती भरा", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit", use_container_width=True)
        
        st.write("---")
        if loc and 'coords' in loc:
            lat, lon = loc['coords'].get('latitude'), loc['coords'].get('longitude')
            st.success("📍 तुमचे लोकेशन मिळाले आहे!")
            st.code(f"Link: https://www.google.com/maps?q={lat},{lon}")
            st.caption("ही लिंक कॉपी करून शीटमधील Location कॉलममध्ये पेस्ट करा.")
        else:
            st.warning("लोकेशन शोधत आहे... कृपया फोनचे GPS सुरू ठेवा.")

    # --- TAB 2: डेटा पाहणे ---
    with tab2:
        try:
            # पब्लिक लिंकवरून डेटा वाचणे (यात कोणतीही PEM एरर येत नाही)
            df = pd.read_csv(READ_URL)
            df.columns = df.columns.str.strip() # कॉलमची नावे साफ करणे
            
            if 'Agent' in df.columns:
                my_data = df[df['Agent'] == st.session_state.agent_display_name]
                if not my_data.empty:
                    st.dataframe(my_data, use_container_width=True, hide_index=True)
                else:
                    st.info("तुमच्या नावावर अजून कोणताही डेटा नाही.")
            else:
                st.error("शीटमध्ये 'Agent' नावाचा कॉलम मिळाला नाही.")
                st.write("उपलब्ध कॉलम्स:", list(df.columns))
        except Exception as e:
            st.error(f"डेटा लोड करताना अडचण आली: {e}")

    if st.sidebar.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
