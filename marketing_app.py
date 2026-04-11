import streamlit as st
import pandas as pd
from datetime import datetime, date

# १. पेज सेटअप
st.set_page_config(page_title="Trimurti Marketing Assistant", layout="wide")

# २. तुमची शीट आयडी आणि पब्लिक लिंक
SHEET_ID = "1hMy9ETB_wfGGLEE3F6JF1t1AJLOHtR4Gqs_apiJkFss"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

st.title("📞 Trimurti Marketing & Follow-up")

try:
    # ३. डेटा वाचणे (क्रेडेंशियल्सशिवाय)
    df = pd.read_csv(DATA_URL)
    
    # ४. आजचे फॉलो-अप रिमांडर्स
    today = date.today()
    if 'Next Date' in df.columns:
        # तारखेचे फॉरमॅट नीट करणे
        df['Next Date'] = pd.to_datetime(df['Next Date']).dt.date
        overdue = df[df['Next Date'] <= today]
        
        if not overdue.empty:
            st.error(f"🚨 **आजचे फॉलो-अप्स ({len(overdue)}):**")
            st.dataframe(overdue[["Customer Name", "Mobile Number", "Next Date"]], use_container_width=True, hide_index=True)
        else:
            st.success("✅ आज कोणतेही प्रलंबित कॉल्स नाहीत.")

    st.divider()

    # ५. व्ह्यू आणि अपडेट पर्याय
    tab1, tab2 = st.tabs(["📊 रिपोर्ट पहा", "📝 डेटा अपडेट करा"])

    with tab1:
        st.subheader("मार्केटिंग डेटा लिस्ट")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.info("डेटा अपडेट करण्यासाठी किंवा पुढची तारीख सेट करण्यासाठी खालील बटण दाबा:")
        # ही लिंक तुला थेट तुझ्या गुगल शीटवर नेईल जिथे तू मोबाईलवरूनही बदल करू शकतोस
        st.link_button("🚀 थेट गुगल शीटमध्ये बदल करा", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
        st.write("---")
        st.markdown("""
        **कसे करावे?**
        1. वरील बटण दाबून गुगल शीट उघडा.
        2. तुम्हाला हव्या त्या क्लायंटचा 'Status' किंवा 'Next Date' तिथे बदला.
        3. बदल आपोआप सेव्ह होतील. 
        4. पुन्हा ॲपवर येऊन पेज रिफ्रेश करा, तुम्हाला नवीन माहिती दिसेल.
        """)

except Exception as e:
    st.error(f"डेटा लोड करताना अडचण आली: {e}")
    st.info("कृपया तुमची गुगल शीट 'Anyone with the link' (Editor) अशी शेअर केली आहे का ते तपासा.")
