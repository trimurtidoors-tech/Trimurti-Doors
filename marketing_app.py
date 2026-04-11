import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing Tracker", layout="wide")

# २. लॉगिन सिस्टिम (तुझ्या गरजेनुसार)
AGENTS = {"Dhananjay": "789", "Jitesh": "101"}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Agent Login")
    user = st.text_input("ID")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user in AGENTS and pw == AGENTS[user]:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("चुकीचा पासवर्ड!")
else:
    # ३. मुख्य ॲप
    st.title("📞 Trimurti Follow-up Manager")
    
    # फाईल अपलोडर - आता Excel (.xlsx) सपोर्ट करेल
    uploaded_file = st.sidebar.file_uploader("Executive ची Excel फाईल निवडा", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            # Excel फाईल वाचणे
            df_raw = pd.read_excel(uploaded_file)
            
            # तुझ्या म्हणण्यानुसार कॉलम्स निवडणे आणि क्रमाने लावणे
            # Date, Name, Category, Mobile, Building Status, Address, Follow-up
            df_clean = pd.DataFrame({
                "Date": df_raw.get('Date', datetime.now().strftime("%Y-%m-%d")),
                "Customer Name": df_raw.get('Contact Person Name', 'N/A'),
                "Category": df_raw.get('Person Status', 'N/A'),
                "Mobile Number": df_raw.get('Contact No', 'N/A'),
                "Building Status": df_raw.get('In Progress', 'N/A'),
                "Address": df_raw.get('Address', 'N/A'),
                "Executive Remark": df_raw.get('Remark', 'N/A'),
                "My Follow-up Status": "Pending", # हा तू अपडेट करशील
                "Next Call Date": (datetime.now() + timedelta(days=7)).date() # डिफॉल्ट ७ दिवस
            })

            # ४. डिस्प्ले आणि अपडेट विभाग
            st.subheader("📋 फिल्ड व्हिजिट डेटा (Clean View)")
            
            # डेटा एडिटर - जिथे तू स्वतः स्टेटस बदलू शकतोस
            updated_df = st.data_editor(
                df_clean,
                column_config={
                    "My Follow-up Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Pending", "Called", "Interested", "Not Answering", "Visit Scheduled"],
                        required=True
                    ),
                    "Next Call Date": st.column_config.DateColumn("पुढचा कॉल कधी?")
                },
                hide_index=True,
                use_container_width=True
            )

            # ५. नोटिफिकेशन लॉजिक (आजचे कॉल्स)
            today = datetime.now().date()
            calls_today = updated_df[updated_df['Next Call Date'] <= today]
            
            if not calls_today.empty:
                st.sidebar.warning(f"🔔 आज तुला {len(calls_today)} लोकांना कॉल करायचे आहेत!")
                if st.sidebar.button("आजचे कॉल्स दाखवा"):
                    st.write("### 🚨 आजचे फॉलो-अप्स")
                    st.table(calls_today[["Customer Name", "Mobile Number", "Next Call Date"]])

            if st.button("💾 बदल सेव्ह करा"):
                # इथे आपण हा डेटा तुझ्या गुगल शीटमध्ये सुद्धा पाठवू शकतो
                st.success("बदल तात्पुरते सेव्ह झाले आहेत!")

        except Exception as e:
            st.error(f"फाईल वाचताना एरर आली: {e}")
    else:
        st.info("कृपया बाजूच्या मेनूमधून Excel फाईल अपलोड करा.")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
