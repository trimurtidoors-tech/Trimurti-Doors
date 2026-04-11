import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज सेटिंग आणि टायटल
st.set_page_config(page_title="Trimurti Marketing Master", layout="wide")

# २. गुगल शीट कनेक्शन (Secrets मधून 'gsheets' कनेक्शन वापरले आहे)
conn = st.connection("gsheets", type=GSheetsConnection)

# ३. लॉगिन सिस्टिम
AGENTS = {"Dhananjay": "789", "Jitesh": "101"}
AGENT_FULL_NAMES = {"Dhananjay": "Dhananjay Pakhre", "Jitesh": "Jitesh Krishnan"}

if 'marketing_logged_in' not in st.session_state:
    st.session_state.marketing_logged_in = False

if not st.session_state.marketing_logged_in:
    st.markdown("## 🔐 Agent Login")
    u_input = st.text_input("Agent ID")
    p_input = st.text_input("Password", type="password")
    if st.button("Login"):
        if u_input in AGENTS and p_input == AGENTS[u_input]:
            st.session_state.marketing_logged_in = True
            st.session_state.agent_display_name = AGENT_FULL_NAMES[u_input]
            st.rerun()
        else:
            st.error("❌ चुकीचा ID किंवा पासवर्ड!")
else:
    # लॉगिन झाल्यानंतरचा भाग
    st.markdown(f"### नमस्ते, {st.session_state.agent_display_name}! 🙏")
    
    # लोकेशन मिळवणे (KeyError टाळण्यासाठी सुरक्षित पद्धत)
    loc = get_geolocation()
    
    tab1, tab2 = st.tabs(["➕ Add New Visit", "🛠️ Manage Records (Edit/Delete)"])

    # --- CREATE: नवीन व्हिजिट नोंदवणे ---
    with tab1:
        with st.form("visit_form", clear_on_submit=True):
            st.subheader("नवीन ग्राहक भेट नोंदवा")
            c_name = st.text_input("Customer Name (ग्राहकाचे नाव)")
            c_mob = st.text_input("Mobile No. (मोबाईल)")
            c_addr = st.text_area("Address (पत्ता)")
            purpose = st.selectbox("Purpose (हेतू)", ["New Inquiry", "Follow-up", "Order"])
            
            st.info("💡 टीप: सबमिट करण्यापूर्वी मोबाईलचे GPS चालू ठेवा.")
            submit = st.form_submit_button("SUBMIT DATA")
            
            if submit:
                if loc and 'coords' in loc:
                    lat = loc['coords'].get('latitude')
                    lon = loc['coords'].get('longitude')
                    map_link = f"https://www.google.com/maps?q={lat},{lon}"
                    
                    new_row = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Agent": st.session_state.agent_display_name,
                        "Customer": c_name,
                        "Mobile": f"'{c_mob}", # मोबाईल नंबर जसाच्या तसा राहण्यासाठी
                        "Address": c_addr,
                        "Purpose": purpose,
                        "Quotation_Sent": "No",
                        "Follow_up_Date": "-", 
                        "Location": map_link
                    }])
                    
                    try:
                        # सध्याचा डेटा वाचणे
                        df_existing = conn.read(ttl=0)
                        # नवीन डेटा जोडणे
                        df_updated = pd.concat([df_existing, new_row], ignore_index=True)
                        # शीटवर अपडेट करणे (CRUD: Update/Create)
                        conn.update(data=df_updated)
                        st.success("✅ डेटा यशस्वीरित्या सेव्ह झाला!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ एरर: {e}")
                else:
                    st.error("❌ लोकेशन सापडले नाही! कृपया ब्राउझरला लोकेशनची परवानगी द्या.")

    # --- READ/UPDATE/DELETE: डेटा मॅनेजमेंट ---
    with tab2:
        try:
            st.subheader("तुमचे रेकॉर्ड्स मॅनेज करा")
            full_df = conn.read(ttl=0)
            # फक्त स्वतःचा डेटा बघणे
            my_leads = full_df[full_df['Agent'] == st.session_state.agent_display_name].copy()
            
            if not my_leads.empty:
                st.write("टेबलमध्ये थेट बदल करा आणि खालील 'Update Sheet' बटण दाबा.")
                
                # CRUD - Update/Delete साठी Editor
                edited_df = st.data_editor(
                    my_leads, 
                    use_container_width=True, 
                    num_rows="dynamic", # ओळी डिलीट करण्याची सोय
                    hide_index=True
                )
                
                if st.button("💾 UPDATE SHEET"):
                    try:
                        # इतर एजंटचा डेटा सुरक्षित ठेवून आपला अपडेटेड डेटा एकत्र करणे
                        other_agents_df = full_df[full_df['Agent'] != st.session_state.agent_display_name]
                        final_df = pd.concat([other_agents_df, edited_df], ignore_index=True)
                        
                        conn.update(data=final_df)
                        st.success("✅ शीट अपडेट झाली!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"अपडेट करताना एरर आली: {e}")
            else:
                st.info("अजून कोणतीही नोंद केलेली नाही.")
        except:
            st.warning("डेटा लोड होऊ शकला नाही. कृपया गुगल शीटवर 'Editor' परमिशन तपासा.")

    if st.button("Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
