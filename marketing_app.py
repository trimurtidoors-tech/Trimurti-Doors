import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation # लोकेशनसाठी लायब्ररी

# १. पेज सेटिंग्ज
st.set_page_config(page_title="Trimurti Marketing Tracker", layout="wide")

# २. गुगल शीट कनेक्शन
conn = st.connection("gsheets", type=GSheetsConnection)

# ३. एजंट्सची माहिती
AGENTS = {"Dhananjay": "789", "Sales1": "101", "Sales2": "102"}

if 'marketing_logged_in' not in st.session_state:
    st.session_state.marketing_logged_in = False

if not st.session_state.marketing_logged_in:
    st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>🚀 Marketing Team Login</h2>", unsafe_allow_html=True)
    u = st.text_input("Agent Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u in USENTS and p == AGENTS[u]:
            st.session_state.marketing_logged_in = True
            st.session_state.agent_name = u
            st.rerun()
        else:
            st.error("Invalid Username or Password!")
else:
    st.markdown(f"<h3 style='text-align: center;'>नमस्ते, {st.session_state.agent_name}! 🙏</h3>", unsafe_allow_html=True)
    
    # टॅब सिस्टिम: नवीन एन्ट्री आणि जुन्या लीड्स अपडेट करण्यासाठी
    tab1, tab2 = st.tabs(["➕ New Visit", "📝 Follow-ups & Updates"])

    with tab1:
        with st.form("visit_form", clear_on_submit=True):
            st.markdown("#### 📍 Add New Lead/Visit")
            c_name = st.text_input("Customer/Shop Name")
            c_mob = st.text_input("Customer Mobile No.")
            c_addr = st.text_area("Customer Address")
            purpose = st.selectbox("Purpose", ["New Inquiry", "Follow-up", "Payment", "Order"])
            
            st.markdown("---")
            st.info("लोकेशन मिळवण्यासाठी 'Get Location' बटण दाबा.")
            
            # लोकेशन मिळवण्यासाठी
            loc = get_geolocation()
            
            if st.form_submit_button("SUBMIT VISIT"):
                if loc:
                    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
                    map_link = f"https://www.google.com/maps?q={lat},{lon}"
                    
                    visit_data = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Time": datetime.now().strftime("%H:%M:%S"),
                        "Agent": st.session_state.agent_name,
                        "Customer": c_name, "Mobile": f"'{c_mob}", "Address": c_addr,
                        "Purpose": purpose, "Quotation_Sent": "No", "Follow_up_Date": "-", 
                        "Location": map_link, "Latitude": lat, "Longitude": lon
                    }])
                    
                    try:
                        # जुना डेटा वाचून नवीन जोडणे
                        existing_df = conn.read(ttl=0)
                        updated_df = pd.concat([existing_df, visit_data], ignore_index=True)
                        conn.update(data=updated_df)
                        st.success("Visit Saved Successfully!")
                    except Exception as e: st.error(f"Error: {e}")
                else: st.warning("GPS चालू करा आणि परवानगी द्या!")

    with tab2:
        st.markdown("#### 📋 Update Follow-ups & Quotation Status")
        try:
            df_leads = conn.read(ttl=0)
            # फक्त लॉगिन केलेल्या एजंटचा डेटा दाखवणे
            agent_leads = df_leads[df_leads['Agent'] == st.session_state.agent_name]
            
            if not agent_leads.empty:
                # 'data_editor' मुळे एजंट थेट तारीख आणि स्टेटस बदलू शकेल
                updated_leads = st.data_editor(
                    agent_leads,
                    column_config={
                        "Quotation_Sent": st.column_config.SelectboxColumn("Quotation Sent?", options=["Yes", "No"]),
                        "Follow_up_Date": st.column_config.DateColumn("Next Call Date"),
                        "Location": st.column_config.LinkColumn("Map View")
                    },
                    disabled=["Date", "Time", "Agent", "Customer", "Mobile"], # हे कॉलम्स बदलता येणार नाहीत
                    hide_index=True,
                    use_container_width=True
                )
                
                if st.button("UPDATE CHANGES"):
                    # पूर्ण शीट अपडेट करणे
                    df_leads.update(updated_leads)
                    conn.update(data=df_leads)
                    st.success("Leads Updated Successfully!")
            else:
                st.info("कोणतीही लीड उपलब्ध नाही.")
        except Exception as e: st.error(f"Error loading data: {e}")

    if st.button("🚪 Logout"):
        st.session_state.marketing_logged_in = False
        st.rerun()
