import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज सेटिंग्ज
st.set_page_config(page_title="Trimurti Marketing Tracker", layout="wide")

# २. गुगल शीट कनेक्शन
# टीप: खात्री करा की 'spreadsheet' की मध्ये नवीन शीटची लिंक आहे
conn = st.connection("gsheets", type=GSheetsConnection)

# ३. एजंट्सची माहिती
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
        else: st.error("चुकीचा ID किंवा पासवर्ड!")
else:
    st.markdown(f"### नमस्ते, {st.session_state.agent_display_name}! 🙏")
    
    tab1, tab2 = st.tabs(["➕ New Visit", "📝 Updates"])

    with tab1:
        with st.form("visit_form", clear_on_submit=True):
            c_name = st.text_input("Customer Name")
            c_mob = st.text_input("Mobile No.")
            c_addr = st.text_area("Address")
            purpose = st.selectbox("Purpose", ["New Inquiry", "Follow-up", "Payment"])
            
            # --- लोकेशनसाठी नवीन बटण ---
            st.info("खालील 'Get My Location' वर क्लिक करा आणि वर 'Allow' निवडा.")
            # हे फंक्शन आता फॉर्मच्या आतून लोकेशन खेचून घेईल
            loc = get_geolocation() 
            
            if st.form_submit_button("SUBMIT VISIT"):
                if loc:
                    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
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
                        st.success("डेटा सेव्ह झाला!")
                    except Exception as e: st.error(f"Spreadsheet Error: {e}")
                else:
                    st.warning("कृपया लोकेशन मिळवण्यासाठी परवानगी द्या आणि पुन्हा प्रयत्न करा.")

    with tab2:
        try:
            df_leads = conn.read(ttl=0)
            agent_leads = df_leads[df_leads['Agent'] == st.session_state.agent_display_name]
            st.data_editor(agent_leads, use_container_width=True)
        except: st.error("शीट लोड होऊ शकली नाही. कृपया Secrets तपासा.")

    if st.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
