import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Smart Follow-up", layout="wide")

# २. गुगल शीट माहिती
SHEET_ID = "1hMy9ETB_wfGGLEE3F6JF1t1AJLOHtR4Gqs_apiJkFss"

# ३. लॉगिन सिस्टिम
AGENTS = {"Dhananjay": "789", "Jitesh": "101"}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Agent Login")
    u_id = st.text_input("ID")
    u_pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if u_id in AGENTS and u_pw == AGENTS[u_id]:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("चुकीचा पासवर्ड!")
else:
    st.title("📞 Trimurti Smart Follow-up")
    
    # ४. डेटा वाचणे (Public Link द्वारे - No PEM Error)
    DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
    
    try:
        df = pd.read_csv(DATA_URL)
        
        # आजचे रिमाइंडर्स
        today = date.today()
        if 'Next Date' in df.columns:
            df['Next Date'] = pd.to_datetime(df['Next Date']).dt.date
            overdue = df[df['Next Date'] <= today]
            
            if not overdue.empty:
                st.error(f"🚨 **आजचे फॉलो-अप्स ({len(overdue)}):**")
                st.dataframe(overdue[["Contact Person Name", "Contact No", "Next Date"]], use_container_width=True, hide_index=True)
            else:
                st.success("✅ आज कोणतेही प्रलंबित कॉल्स नाहीत.")

        st.divider()

        # ५. मुख्य विभाग
        tab1, tab2 = st.tabs(["📋 फॉलो-अप लिस्ट", "📂 नवीन डेटा जोडा"])

        with tab1:
            st.subheader("मार्केटिंग डेटा")
            st.dataframe(df, use_container_width=True)
            st.info("💡 टीप: डेटा अपडेट करण्यासाठी खालील बटण दाबून थेट शीटमध्ये बदल करा.")
            st.link_button("🚀 गुगल शीटमध्ये तारीख अपडेट करा", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")

        with tab2:
            st.subheader("एक्झिक्युटिव्हची फाईल अपलोड करा")
            uploaded_file = st.file_uploader("Excel फाईल निवडा", type=["xlsx"])
            if uploaded_file:
                df_new = pd.read_excel(uploaded_file)
                st.write("डेटा प्रीव्ह्यू:")
                st.dataframe(df_new.head())
                st.warning("हा डेटा शीटमध्ये टाकण्यासाठी 'Copy' करून थेट गुगल शीटमध्ये पेस्ट करा.")
                st.link_button("🚀 गुगल शीट उघडा", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")

    except Exception as e:
        st.error(f"डेटा लोड करताना अडचण: {e}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
