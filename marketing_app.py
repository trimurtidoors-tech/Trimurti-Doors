import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज कॉन्फिगरेशन
st.set_page_config(page_title="Trimurti Marketing Master", layout="wide")

# २. क्रेडेंशियल्स डिक्शनरी तयार करणे (UnhashableParamError टाळण्यासाठी)
# st.secrets मधील डेटा आपण डिक्शनरी फॉरमॅटमध्ये घेत आहोत
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
# येथे आपण 'credentials' आणि 'spreadsheet' दोन्ही स्पष्टपणे नमूद केले आहेत
conn = st.connection(
    "gsheets", 
    type=GSheetsConnection, 
    credentials=creds_dict, 
    spreadsheet=st.secrets["spreadsheet"]
)

# ४. एजंट डेटा आणि लॉगिन सेटिंग्ज
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
    
    tab1, tab2 = st.tabs(["➕ नवीन भेट (Create)", "🛠️ रेकॉर्ड्स मॅनेज करा (Update/Delete)"])

    # --- CREATE (नवीन नोंद करणे) ---
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
                    map_link = f"https://www.google.com/maps?q={lat},{lon}"
                    
                    new_data = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Agent": st.session_state.agent_display_name,
                        "Customer": c_name, "Mobile": f"'{c_mob}", "Address": c_addr,
                        "Purpose": purpose, "Quotation_Sent": "No", "Follow_up_Date": "-", 
                        "Location": map_link
                    }])
                    try:
                        # सध्याचा डेटा वाचणे
                        existing_df = conn.read(ttl=0)
                        # नवीन ओळ जोडणे
                        updated_df = pd.concat([existing_df, new_data], ignore_index=True)
                        # शीटवर अपडेट करणे
                        conn.update(data=updated_df)
                        st.success("✅ डेटा यशस्वीरित्या सेव्ह झाला!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("लोकेशन सापडले नाही. कृपया ब्राऊझरमध्ये लोकेशन 'Allow' करा.")

    # --- READ / UPDATE / DELETE (डेटा व्यवस्थापन) ---
    with tab2:
        try:
            full_df = conn.read(ttl=0)
            my_leads = full_df[full_df['Agent'] == st.session_state.agent_display_name].copy()
            
            if not my_leads.empty:
                st.info("बदल करण्यासाठी खालील टेबल वापरा आणि 'SAVE' दाबा:")
                # 'dynamic' मुळे ओळी डिलीट करण्याची सोय मिळते
                edited_df = st.data_editor(
                    my_leads, 
                    use_container_width=True, 
                    num_rows="dynamic", 
                    hide_index=True
                )
                
                if st.button("💾 SAVE UPDATES"):
                    try:
                        # इतर एजंटचा डेटा सुरक्षित ठेवणे
                        other_agents_df = full_df[full_df['Agent'] != st.session_state.agent_display_name]
                        # आपला अपडेटेड डेटा एकत्र करणे
                        final_df = pd.concat([other_agents_df, edited_df], ignore_index=True)
                        # गुगल शीटवर अपडेट पाठवणे
                        conn.update(data=final_df)
                        st.success("✅ रेकॉर्ड्स अपडेट झाले!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update Error: {e}")
            else:
                st.info("तुमचा कोणताही डेटा उपलब्ध नाही.")
        except:
            st.error("डेटा लोड करताना तांत्रिक अडचण आली.")

    if st.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
