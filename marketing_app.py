import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# १. पेज सेटिंग्ज
st.set_page_config(page_title="Trimurti Marketing Tracker", layout="wide")

# २. गुगल शीट कनेक्शन
conn = st.connection("gsheets", type=GSheetsConnection)

# ३. एजंट्सची माहिती (जितेशचे नाव आणि लॉगिन आयडी जोडले आहे)
AGENTS = {
    "Dhananjay": "789", 
    "Jitesh": "101", 
    "Admin": "Admin@123"
}

# पूर्ण नावाचा मॅपिंग (शीटमध्ये जाण्यासाठी)
AGENT_FULL_NAMES = {
    "Dhananjay": "Dhananjay Pakhre",
    "Jitesh": "Jitesh Krishnan",
    "Admin": "Administrator"
}

if 'marketing_logged_in' not in st.session_state:
    st.session_state.marketing_logged_in = False

if not st.session_state.marketing_logged_in:
    st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>🚀 Marketing Team Login</h2>", unsafe_allow_html=True)
    u_input = st.text_input("Agent Username (ID)")
    p_input = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # येथे आपण 'USENTS' ऐवजी बरोबर 'AGENTS' वापरले आहे
        if u_input in AGENTS and p_input == AGENTS[u_input]:
            st.session_state.marketing_logged_in = True
            st.session_state.agent_id = u_input
            st.session_state.agent_display_name = AGENT_FULL_NAMES[u_input]
            st.rerun()
        else:
            st.error("Invalid Username or Password!")
else:
    st.markdown(f"<div style='background-color:#ff4b4b;padding:10px;color:white;text-align:center;border-radius:10px;'><h3>नमस्ते, {st.session_state.agent_display_name}! 🙏</h3></div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ New Visit (नवीन भेट)", "📝 Follow-ups & Updates (अपडेट्स)"])

    with tab1:
        with st.form("visit_form", clear_on_submit=True):
            st.markdown("#### 📍 Add New Lead/Visit")
            c_name = st.text_input("Customer/Shop Name")
            c_mob = st.text_input("Customer Mobile No.")
            c_addr = st.text_area("Customer Address")
            purpose = st.selectbox("Purpose", ["New Inquiry", "Follow-up", "Payment Collection", "Order Booking"])
            
            st.markdown("---")
            st.info("लोकेशन मिळवण्यासाठी 'Get Location' बटण दाबा.")
            loc = get_geolocation()
            
            if st.form_submit_button("SUBMIT VISIT"):
                if loc:
                    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
                    map_link = f"https://www.google.com/maps?q={lat},{lon}"
                    
                    visit_data = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Time": datetime.now().strftime("%H:%M:%S"),
                        "Agent": st.session_state.agent_display_name,
                        "Customer": c_name, "Mobile": f"'{c_mob}", "Address": c_addr,
                        "Purpose": purpose, "Quotation_Sent": "No", "Follow_up_Date": "-", 
                        "Location": map_link
                    }])
                    
                    try:
                        df_existing = conn.read(ttl=0)
                        df_updated = pd.concat([df_existing, visit_data], ignore_index=True)
                        conn.update(data=df_updated)
                        st.success(f"Visit saved for {c_name}!")
                        st.balloons()
                    except Exception as e: st.error(f"Sync Error: {e}")
                else:
                    st.warning("GPS चालू करा आणि ब्राउझरमध्ये लोकेशनला 'Allow' करा!")

    with tab2:
        st.markdown("#### 📋 Update Follow-ups & Quotation Status")
        try:
            df_leads = conn.read(ttl=0)
            # फक्त सध्याच्या एजंटचा डेटा दाखवणे
            agent_leads = df_leads[df_leads['Agent'] == st.session_state.agent_display_name]
            
            if not agent_leads.empty:
                updated_leads = st.data_editor(
                    agent_leads,
                    column_config={
                        "Quotation_Sent": st.column_config.SelectboxColumn("Quotation Sent?", options=["Yes", "No"]),
                        "Follow_up_Date": st.column_config.DateColumn("Next Action Date"),
                        "Location": st.column_config.LinkColumn("View Map")
                    },
                    disabled=["Date", "Time", "Agent", "Customer", "Mobile"],
                    hide_index=True,
                    use_container_width=True
                )
                
                if st.button("SAVE UPDATES"):
                    df_leads.update(updated_leads)
                    conn.update(data=df_leads)
                    st.success("Lead updates saved successfully!")
            else:
                st.info("तुमच्या खात्यावर कोणतीही लीड सापडली नाही.")
        except Exception as e: st.error(f"Error: {e}")

    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
