import streamlit as st
import pandas as pd
from datetime import datetime, date

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Smart Follow-up", layout="wide")

# २. तुमची शीट माहिती
SHEET_ID = "1hMy9ETB_wfGGLEE3F6JF1t1AJLOHtR4Gqs_apiJkFss"
# डेटा वाचण्यासाठी पब्लिक लिंक (यात PEM एरर येत नाही)
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

st.title("📞 Trimurti Marketing Assistant")

try:
    # ३. डेटा वाचणे (कोणत्याही क्रेडेंशियल्सशिवाय)
    df = pd.read_csv(DATA_URL)
    
    # ४. आजचे फॉलो-अप रिमांडर्स (स्मार्ट रिमाइयंडर)
    today = date.today()
    
    # तारखेचा कॉलम नीट करणे (तुमच्या शीटमध्ये 'Next Date' हा कॉलम असणे आवश्यक आहे)
    if 'Next Date' in df.columns:
        df['Next Date'] = pd.to_datetime(df['Next Date'], errors='coerce').dt.date
        overdue = df[df['Next Date'] <= today].dropna(subset=['Next Date'])
        
        if not overdue.empty:
            st.error(f"🚨 **आजचे फॉलो-अप्स ({len(overdue)}):**")
            # महत्त्वाचे कॉलम्स दाखवणे (नाव आणि मोबाईल)
            st.dataframe(overdue[["Customer Name", "Mobile Number", "Next Date"]], use_container_width=True, hide_index=True)
        else:
            st.success("✅ आज कोणतेही प्रलंबित कॉल्स नाहीत.")

    st.divider()

    # ५. व्ह्यू आणि अपडेट टॅब्स
    tab1, tab2 = st.tabs(["📊 सर्व डेटा पहा", "📝 स्टेटस/तारीख अपडेट करा"])

    with tab1:
        st.subheader("मार्केटिंग रिपोर्ट")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.info("💡 **अपडेट करण्याची सर्वात सोपी पद्धत:**")
        st.write("सध्या गुगलच्या सिक्युरिटी एररमुळे आपण थेट ॲपमधून सेव्ह करू शकत नाही आहोत. पण खालील बटण दाबून तुम्ही थेट तुमच्या मोबाईलवर शीट उघडून बदल करू शकता.")
        
        # ही लिंक तुम्हाला थेट शीटवर नेईल
        st.link_button("🚀 थेट गुगल शीट उघडा आणि बदल करा", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
        
        st.markdown("""
        ---
        **कसे करावे?**
        1. वरील बटण दाबा.
        2. समोर शीट उघडेल, तिथे त्या क्लायंटची **Next Date** किंवा **Status** बदला.
        3. बदल आपोआप सेव्ह होतील. 
        4. पुन्हा या ॲपवर येऊन पेज रिफ्रेश करा, तुम्हाला नवीन तारखांचे रिमांडर्स दिसतील.
        """)

except Exception as e:
    st.error(f"डेटा लोड करताना अडचण आली: {e}")
    st.info("कृपया तुमची गुगल शीट 'Anyone with the link' (Editor) अशी शेअर केली आहे का ते तपासा.")

# ६. लॉगआउट (पर्यायी)
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
