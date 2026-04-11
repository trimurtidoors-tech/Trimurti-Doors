import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing Tracker", layout="wide")

# २. लॉगिन सिस्टिम
AGENTS = {"Dhananjay": "789", "Jitesh": "101"}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Agent Login")
    user = st.text_input("Agent ID")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user in AGENTS and pw == AGENTS[user]:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("चुकीचा पासवर्ड!")
else:
    st.sidebar.success(f"एजंट: {st.session_state.get('user', 'Dhananjay')}")
    
    st.title("📞 Trimurti Marketing Follow-up Manager")
    
    # ३. फाईल अपलोड विभाग (Excel/xlsx सपोर्ट)
    uploaded_file = st.sidebar.file_uploader("एक्झिक्युटिव्हची Excel फाईल निवडा", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            # Excel फाईल वाचणे (openpyxl आता इन्स्टॉल असल्याने ही ओळ चालेल)
            df_raw = pd.read_excel(uploaded_file)
            
            # कॉलमची नावे तुझ्या गरजेनुसार सेट करणे
            # Date, Name, Category, Mobile, Building Status, Address, Follow-up
            df_clean = pd.DataFrame({
                "Date": df_raw.get('Date', datetime.now().strftime("%Y-%m-%d")),
                "Customer Name": df_raw.get('Contact Person Name', 'N/A'),
                "Category": df_raw.get('Person Status', 'N/A'),
                "Mobile Number": df_raw.get('Contact No', 'N/A'),
                "Building Status": df_raw.get('In Progress', 'N/A'),
                "Address": df_raw.get('Address', 'N/A'),
                "Executive Remark": df_raw.get('Remark', 'N/A'),
                "My Follow-up Status": "Pending", 
                "Next Call Date": (datetime.now() + timedelta(days=7)).date() 
            })

            # ४. फॉलो-अप नोटिफिकेशन (आजचे कॉल्स)
            today = datetime.now().date()
            
            # ५. डेटा एडिटर - जिथे तू स्टेटस आणि डेट बदलू शकतोस
            st.subheader("📋 फिल्ड व्हिजिट डेटा (Clean View)")
            st.info("टीप: तुम्ही 'Status' आणि 'Next Call Date' येथेच बदलू शकता.")
            
            updated_df = st.data_editor(
                df_clean,
                column_config={
                    "My Follow-up Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Pending", "Called - Interested", "Called - Busy", "Not Answering", "Meeting Scheduled"],
                        required=True
                    ),
                    "Next Call Date": st.column_config.DateColumn("पुढचा कॉल तारीख")
                },
                hide_index=True,
                use_container_width=True
            )

            # ६. आजचे फॉलो-अप्स दाखवणे
            calls_today = updated_df[updated_df['Next Call Date'] <= today]
            if not calls_today.empty:
                st.sidebar.warning(f"🔔 आज तुला {len(calls_today)} लोकांना कॉल करायचे आहेत!")
                if st.sidebar.button("आजची यादी पहा"):
                    st.write("### 🚨 आजचे फॉलो-अप्स")
                    st.dataframe(calls_today[["Customer Name", "Mobile Number", "Next Call Date"]], use_container_width=True)

            if st.button("💾 बदल सेव्ह करा"):
                st.success("बदल तात्पुरते सेव्ह झाले आहेत! (कायमस्वरूपी सेव्हसाठी गुगल शीट जोडणे आवश्यक आहे)")

        except Exception as e:
            st.error(f"फाईल वाचताना एरर आली: {e}")
            st.info("कृपया खात्री करा की requirements.txt मध्ये openpyxl टाकून Reboot केले आहे.")
    else:
        st.info("बाजूच्या मेनूमधून Excel फाईल अपलोड करा.")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
