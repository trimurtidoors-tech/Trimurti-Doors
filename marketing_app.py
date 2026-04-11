import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing Master", layout="wide")

# २. गुगल शीट कॉन्फिगरेशन (Public Link)
# टीप: तुमची शीट 'Anyone with link can edit' असणे आवश्यक आहे.
SHEET_ID = "1F8XY5rjNSA3sY_5aeHAm905KSMwiaoWBqMZsf1NxSjk"
# डेटा वाचण्यासाठी CSV लिंक
READ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
# डेटा सबमिट करण्यासाठी मूळ लिंक
EDIT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"

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
    st.markdown(f"### नमस्ते, {st.session_state.agent_display_name}! 🙏")
    
    # लोकेशन मिळवणे
    loc = get_geolocation()
    
    tab1, tab2 = st.tabs(["➕ नवीन नोंद (Submit)", "📊 माझा डेटा (View Reports)"])

    # --- TAB 1: डेटा सबमिट करण्यासाठी ---
    with tab1:
        st.subheader("नवीन व्हिजिट नोंदवा")
        st.warning("सूचना: क्रेडेंशियल एररमुळे सध्या डेटा थेट शीटमध्ये भरण्यासाठी खालील बटण वापरा.")
        
        # गुगल शीटवर नेणारे बटण
        st.link_button("📝 गुगल शीटमध्ये डेटा भरा", EDIT_URL, use_container_width=True)
        
        st.write("---")
        st.write("तुमचे सध्याचे लोकेशन:")
        if loc and 'coords' in loc:
            lat, lon = loc['coords'].get('latitude'), loc['coords'].get('longitude')
            st.success(f"Location Found: {lat}, {lon}")
            st.write(f"Link: http://maps.google.com/?q={lat},{lon}")
        else:
            st.info("लोकेशन शोधत आहे... कृपया GPS सुरू ठेवा.")

    # --- TAB 2: डेटा पाहण्यासाठी ---
    with tab2:
        try:
            # CSV मधून डेटा वाचणे
            df = pd.read_csv(READ_URL)
            
            # कॉलमची नावे स्वच्छ करणे (Spaces काढणे)
            df.columns = df.columns.str.strip()
            
            # जर 'Agent' कॉलम असेल तरच फिल्टर करणे
            if 'Agent' in df.columns:
                my_leads = df[df['Agent'] == st.session_state.agent_display_name]
                
                if not my_leads.empty:
                    st.success(f"तुमचे एकूण {len(my_leads)} रेकॉर्ड्स सापडले.")
                    st.dataframe(my_leads, use_container_width=True, hide_index=True)
                else:
                    st.info("तुमच्या नावावर अजून कोणताही डेटा नाही.")
            else:
                st.error("शीटमध्ये 'Agent' नावाचा कॉलम सापडला नाही.")
                st.write("उपलब्ध कॉलम्स:", list(df.columns))
                
        except Exception as e:
            st.error(f"डेटा लोड करताना एरर आली: {e}")

    if st.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
