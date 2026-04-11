import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="Trimurti Marketing Master", layout="wide")

# १. कनेक्शन सेटिंग्ज
conn = st.connection("gsheets", type=GSheetsConnection)

# २. लॉगिन आणि एजंट मॅपिंग
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
        else: st.error("ID किंवा पासवर्ड चुकलाय!")
else:
    st.markdown(f"### नमस्ते, {st.session_state.agent_display_name}! 🙏")
    loc = get_geolocation()
    
    tab1, tab2 = st.tabs(["➕ Add New (Create)", "🛠️ Manage Records (Read/Update/Delete)"])

    # --- CREATE (नवीन एन्ट्री करणे) ---
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
                    
                    new_data = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Agent": st.session_state.agent_display_name,
                        "Customer": c_name, "Mobile": f"'{c_mob}", "Address": c_addr,
                        "Purpose": purpose, "Quotation_Sent": "No", "Follow_up_Date": "-", 
                        "Location": map_link
                    }])
                    try:
                        existing_df = conn.read(ttl=0)
                        updated_df = pd.concat([existing_df, new_data], ignore_index=True)
                        conn.update(data=updated_df)
                        st.success("Create: नवीन एन्ट्री यशस्वी!")
                        st.balloons()
                    except Exception as e: st.error(f"Error: {e}")
                else: st.error("कृपया लोकेशन 'Allow' करा.")

    # --- READ, UPDATE, DELETE (डेटा मॅनेजमेंट) ---
    with tab2:
        try:
            # १. READ (डेटा वाचणे)
            df = conn.read(ttl=0)
            # सध्याच्या एजंटचा डेटा फिल्टर करणे
            agent_df = df[df['Agent'] == st.session_state.agent_display_name].copy()
            
            if not agent_df.empty:
                st.info("खालील टेबलमध्ये बदल करून 'Save' करा (Update/Delete).")
                
                # २. UPDATE (डेटा सुधारणे)
                # data_editor वापरून युजर टेबलमध्येच बदल करू शकतो
                edited_df = st.data_editor(
                    agent_df, 
                    use_container_width=True, 
                    num_rows="dynamic", # "dynamic" मुळे 'Delete' पर्याय सुरू होतो
                    hide_index=True
                )
                
                if st.button("SAVE CHANGES"):
                    try:
                        # जुन्या डेटा फ्रेममध्ये या एजंटचा डेटा नवीन (Edited) डेटाने बदलणे
                        df = df[df['Agent'] != st.session_state.agent_display_name]
                        final_df = pd.concat([df, edited_df], ignore_index=True)
                        
                        # ३. SYNC (शीटवर अपडेट करणे)
                        conn.update(data=final_df)
                        st.success("Update/Delete: डेटा यशस्वीरित्या अपडेट झाला!")
                        st.rerun()
                    except Exception as e: st.error(f"Update Error: {e}")
            else:
                st.info("डेटा उपलब्ध नाही.")
        except: st.error("शीट लोड करताना अडचण आली.")

    if st.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
