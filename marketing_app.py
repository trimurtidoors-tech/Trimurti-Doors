import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing Master", layout="wide")

# २. क्रेडेंशियल्स डिक्शनरी तयार करणे
# TypeError टाळण्यासाठी आपण प्रत्येक व्हॅल्यू स्वतंत्रपणे देत आहोत
creds_dict = {
    "type": st.secrets["type"],
    "project_id": st.secrets["project_id"],
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"],
    "client_email": st.secrets["client_email"],
    "client_id": st.secrets["client_id"],
    "auth_uri": st.secrets["auth_uri"],
    "token_uri": st.secrets["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["client_x509_cert_url"],
}

# ३. गुगल शीट कनेक्शन
# टीप: आपण 'credentials' आणि 'spreadsheet' स्पष्टपणे वेगळे केले आहेत
try:
    conn = st.connection(
        "gsheets", 
        type=GSheetsConnection, 
        credentials=creds_dict, 
        spreadsheet=st.secrets["spreadsheet"]
    )
except Exception as e:
    st.error(f"Connection Error: {e}")
    st.stop()

# ४. युजर लॉगिन मॅपिंग
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
                    map_link = f"https://www.google.com/maps?q={lat},{lon}"
                    
                    new_entry = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Agent": st.session_state.agent_display_name,
                        "Customer": c_name, "Mobile": f"'{c_mob}", "Address": c_addr,
                        "Purpose": purpose, "Quotation_Sent": "No", "Follow_up_Date": "-", 
                        "Location": map_link
                    }])
                    try:
                        existing_df = conn.read(ttl=0)
                        updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
                        conn.update(data=updated_df)
                        st.success("✅ डेटा यशस्वीरित्या सेव्ह झाला!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("कृपया लोकेशन 'Allow' करा.")

    with tab2:
        try:
            full_df = conn.read(ttl=0)
            my_leads = full_df[full_df['Agent'] == st.session_state.agent_display_name].copy()
            if not my_leads.empty:
                edited_df = st.data_editor(my_leads, use_container_width=True, num_rows="dynamic", hide_index=True)
                if st.button("💾 SAVE CHANGES"):
                    try:
                        other_df = full_df[full_df['Agent'] != st.session_state.agent_display_name]
                        final_df = pd.concat([other_df, edited_df], ignore_index=True)
                        conn.update(data=final_df)
                        st.success("✅ रेकॉर्ड्स अपडेट झाले!")
                        st.rerun()
                    except Exception as e: st.error(f"Update Error: {e}")
            else: st.info("डेटा उपलब्ध नाही.")
        except: st.error("डेटा लोड झाला नाही.")

    if st.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
