import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing Master", layout="wide")

# २. गुगल शीट कनेक्शन (PEM Error घालवण्यासाठी सुधारित पद्धत)
def connect_to_gsheets():
    try:
        # Secrets मधील [connections.gsheets] मधून क्रेडेंशियल्स मिळवणे
        creds = dict(st.secrets["connections"]["gsheets"])
        
        # मुख्य उपाय: की मधील बॅकस्लॅश (\n) तांत्रिकदृष्ट्या नीट करणे
        # यामुळे 'InvalidByte(1625, 61)' ही एरर येणार नाही
        if "private_key" in creds:
            creds["private_key"] = creds["private_key"].replace("\\n", "\n")
        
        # क्रेडेंशियल्स वापरून कनेक्शन तयार करणे
        return st.connection(
            "gsheets", 
            type=GSheetsConnection, 
            credentials=creds
        )
    except Exception as e:
        st.error(f"कन्फिगरेशन एरर (Connection): {e}")
        st.stop()

# कनेक्शन मिळवणे
conn = connect_to_gsheets()

# ३. एजंट लॉगिन सिस्टम
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
    
    tab1, tab2 = st.tabs(["➕ नवीन नोंद (Create)", "🛠️ रेकॉर्ड्स मॅनेज करा (Update/Delete)"])

    # --- CREATE SECTION ---
    with tab1:
        with st.form("visit_form", clear_on_submit=True):
            st.subheader("व्हिजिट डिटेल्स भरा")
            c_name = st.text_input("Customer Name")
            c_mob = st.text_input("Mobile No.")
            c_addr = st.text_area("Address")
            purpose = st.selectbox("Purpose", ["New Inquiry", "Follow-up", "Order"])
            submit = st.form_submit_button("SUBMIT DATA")
            
            if submit:
                if loc and 'coords' in loc:
                    lat, lon = loc['coords'].get('latitude'), loc['coords'].get('longitude')
                    map_link = f"http://maps.google.com/?q={lat},{lon}"
                    
                    new_entry = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Agent": st.session_state.agent_display_name,
                        "Customer": c_name, 
                        "Mobile": f"'{c_mob}", 
                        "Address": c_addr,
                        "Purpose": purpose, 
                        "Quotation_Sent": "No", 
                        "Follow_up_Date": "-", 
                        "Location": map_link
                    }])
                    try:
                        # डेटा वाचणे आणि अपडेट करणे
                        existing_df = conn.read(ttl=0)
                        updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
                        conn.update(data=updated_df)
                        st.success("✅ डेटा यशस्वीरित्या सेव्ह झाला!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"डेटा सेव्ह करताना एरर: {e}")
                else:
                    st.error("लोकेशन सापडले नाही. कृपया फोनचे GPS सुरू करा आणि लोकेशनला परवानगी द्या.")

    # --- UPDATE SECTION ---
    with tab2:
        try:
            full_df = conn.read(ttl=0)
            my_leads = full_df[full_df['Agent'] == st.session_state.agent_display_name].copy()
            
            if not my_leads.empty:
                st.info("बदल करण्यासाठी खालील टेबल वापरा आणि 'SAVE' दाबा:")
                edited_df = st.data_editor(
                    my_leads, 
                    use_container_width=True, 
                    num_rows="dynamic", 
                    hide_index=True
                )
                
                if st.button("💾 SAVE CHANGES"):
                    try:
                        other_agents_df = full_df[full_df['Agent'] != st.session_state.agent_display_name]
                        final_df = pd.concat([other_agents_df, edited_df], ignore_index=True)
                        conn.update(data=final_df)
                        st.success("✅ तुमचे रेकॉर्ड्स अपडेट झाले आहेत!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update Error: {e}")
            else:
                st.info("तुमच्या नावावर कोणताही डेटा सापडला नाही.")
        except Exception as e:
            st.error(f"डेटा लोड करताना अडचण आली: {e}")

    if st.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
