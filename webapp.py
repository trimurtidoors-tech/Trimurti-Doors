import streamlit as st
from fpdf import FPDF
from datetime import date
import json
import os

# १. पेज सेटिंग्ज आणि कॉन्फिगरेशन
st.set_page_config(page_title="Trimurti Doors World", layout="wide")

# २. ऑफलाइन रेट्स लोड/सेव्ह करण्यासाठी फंक्शन
RATES_FILE = "rates_data.json"


def load_rates():
    default_rates = {
        "FT": 720, "Deco": 685, "PD": 585, "Delux": 385,
        "Diamond": 315, "Classic": 285, "Silver": 240,
        "FRP": 185, "Ls": 240, "T": 160, "Eg": 630
    }
    if os.path.exists(RATES_FILE):
        with open(RATES_FILE, "r") as f:
            return json.load(f)
    return default_rates


def save_rates(rates):
    with open(RATES_FILE, "w") as f:
        json.dump(rates, f)


# ३. युजर मॅनेजमेंट
USERS = {"Dhananjay": "Trimurti@2026", "Admin": "Admin@123", "Abhijeet": "123", "Yash": "123"}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'all_entries' not in st.session_state:
    st.session_state.all_entries = []
if 'rates' not in st.session_state:
    st.session_state.rates = load_rates()

# --- लॉगिन सेक्शन ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #004aad;'>🔑 Admin Login</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in USERS and p == USERS[u]:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else:
                st.error("Invalid Login")
else:
    # --- मुख्य हेडर ---
    st.markdown(f"""<div style='background-color:#004aad;padding:10px;border-radius:5px;text-align:center;color:white;'>
        <h1>TRIMURTI DOORS WORLD</h1><p>Logged in as: {st.session_state.current_user}</p></div>""",
                unsafe_allow_html=True)

    # ४. एडमिन विंडो (Rate Update) - एक्सपँडरमध्ये लपवलेली
    if st.session_state.current_user == "Dhananjay":
        with st.expander("⚙️ Admin Settings (Update Rates)"):
            st.write("येथे तुम्ही डोअर सिरीजचे दर बदलू शकता:")
            new_rates = {}
            cols = st.columns(4)
            for idx, (key, val) in enumerate(st.session_state.rates.items()):
                new_rates[key] = cols[idx % 4].number_input(f"{key} Rate", value=float(val), step=1.0)

            if st.button("💾 Save New Rates"):
                st.session_state.rates = new_rates
                save_rates(new_rates)
                st.success("दर यशस्वीरीत्या अपडेट झाले आहेत!")

    # ५. इंच कन्वर्शन लॉजिक (0.1 = 0.125)
    INCH_CONVERSION = {0.1: 0.125, 0.2: 0.250, 0.3: 0.375, 0.4: 0.500, 0.5: 0.625, 0.6: 0.750, 0.7: 0.875, 0.8: 1.0,
                       0.9: 1.125}


    def get_conv(val):
        m = int(val);
        f = round(val - m, 1)
        return m + INCH_CONVERSION.get(f, f)


    # ६. कस्टमर डिटेल्स
    st.markdown("#### Customer Details")
    c1, c2, c3 = st.columns([1, 1, 2])
    cust_name = c1.text_input("Customer Name")
    mobile = c2.text_input("Mobile Number")
    address = c3.text_input("Address")

    # ७. फास्ट एंट्री फॉर्म
    st.markdown("---")
    with st.form("door_entry", clear_on_submit=True):
        st.markdown("##### Add New Door")
        r1 = st.columns([1, 1, 1, 1, 1, 1, 1])
        ser = r1[0].selectbox("Series", list(st.session_state.rates.keys()))
        qt = r1[1].number_input("Qty", min_value=1)
        des = r1[2].text_input("Design")
        col = r1[3].text_input("Color")
        h_in = r1[4].number_input("Height", format="%.1f")
        wt_in = r1[5].number_input("W-Top", format="%.1f")
        wb_in = r1[6].number_input("W-Bottom", format="%.1f")

        if st.form_submit_button("➕ ADD ITEM"):
            ch, cw1, cw2 = get_conv(h_in), get_conv(wt_in), get_conv(wb_in)
            max_cw = max(cw1, cw2)
            bsqft = round(max(14.0, (ch * max_cw) / 144), 2)
            cur_rate = st.session_state.rates[ser]
            st.session_state.all_entries.append({
                "Series": ser, "Design": des, "Color": col, "H": ch, "W1": cw1, "W2": cw2,
                "Qty": qt, "SqFt": bsqft, "Rate": cur_rate, "Total": round(bsqft * qt * cur_rate, 2)
            })
            st.rerun()

    # ८. टेबल आणि बिलिंग
    if st.session_state.all_entries:
        st.table(st.session_state.all_entries)
        sub = sum(i['Total'] for i in st.session_state.all_entries)

        f1, f2, f3, f4 = st.columns(4)
        gst_p = f1.number_input("GST %", 18)
        trans = f2.number_input("Transport", 0)
        disc = f3.number_input("Discount", 0)
        adv = f4.number_input("Advance Amount", 0)

        gst_a = round((sub * gst_p) / 100, 2)
        final = sub + gst_a + trans - disc - adv
        st.subheader(f"Total Balance: ₹ {final:.2f}")

        if st.button("📄 GENERATE PDF"):
            pdf = FPDF()
            pdf.add_page()
            # Header
            pdf.set_font("Arial", 'B', 16);
            pdf.cell(190, 10, "TRIMURTI DOORS WORLD", 0, 1, 'C')
            pdf.set_font("Arial", '', 9);
            pdf.cell(190, 5, "Plot no. C-4/5, shendra MIDC, Chhatrapati Sambhaji Nagar., Maharashtra. - 431154", 0, 1,
                     'C')
            pdf.ln(2);
            pdf.set_font("Arial", 'B', 14);
            pdf.cell(190, 10, "QUOTATION", 1, 1, 'C')
            # Details
            pdf.ln(2);
            pdf.set_font("Arial", '', 9)
            pdf.cell(95, 7, f"Customer: {cust_name} | Mob: {mobile}", 0, 0)
            pdf.set_font("Arial", 'I', 9);
            pdf.cell(95, 7, f"Prepared By: {st.session_state.current_user}", 0, 1, 'R')
            pdf.set_font("Arial", '', 9);
            pdf.cell(95, 7, f"Address: {address}", 0, 0);
            pdf.cell(95, 7, f"Date: {date.today()}", 0, 1, 'R')
            # Table
            pdf.ln(5);
            pdf.set_fill_color(230, 230, 230);
            pdf.set_font("Arial", 'B', 7)
            h_list = ["Sr", "Series", "Design", "Color", "Height", "W1(Top)", "W2(Bot)", "Qty", "SqFt", "Rate", "Total"]
            w_list = [8, 15, 25, 20, 20, 18, 18, 10, 15, 15, 26]
            for i in range(len(h_list)): pdf.cell(w_list[i], 10, h_list[i], 1, 0, 'C', True)
            pdf.ln();
            pdf.set_font("Arial", '', 7)
            for idx, i in enumerate(st.session_state.all_entries):
                pdf.cell(w_list[0], 8, str(idx + 1), 1, 0, 'C')
                pdf.cell(w_list[1], 8, i['Series'], 1);
                pdf.cell(w_list[2], 8, i['Design'], 1)
                pdf.cell(w_list[3], 8, i['Color'], 1);
                pdf.cell(w_list[4], 8, f"{i['H']:.3f}", 1, 0, 'C')
                pdf.cell(w_list[5], 8, f"{i['W1']:.3f}", 1, 0, 'C');
                pdf.cell(w_list[6], 8, f"{i['W2']:.3f}", 1, 0, 'C')
                pdf.cell(w_list[7], 8, str(i['Qty']), 1, 0, 'C');
                pdf.cell(w_list[8], 8, f"{i['SqFt']:.2f}", 1, 0, 'C')
                pdf.cell(w_list[9], 8, str(i['Rate']), 1, 0, 'C');
                pdf.cell(w_list[10], 8, f"{i['Total']:.2f}", 1, 1, 'R')
            # Summary
            pdf.ln(5);
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(150, 6, "Subtotal:", 0, 0, 'R');
            pdf.cell(40, 6, f"{sub:.2f}", 0, 1, 'R')
            pdf.cell(150, 6, "GST:", 0, 0, 'R');
            pdf.cell(40, 6, f"{gst_a:.2f}", 0, 1, 'R')
            pdf.cell(150, 6, "Transport:", 0, 0, 'R');
            pdf.cell(40, 6, f"{trans:.2f}", 0, 1, 'R')
            pdf.cell(150, 6, "Discount/Advance:", 0, 0, 'R');
            pdf.cell(40, 6, f"-{(disc + adv):.2f}", 0, 1, 'R')
            pdf.ln(2);
            pdf.set_font("Arial", 'B', 12);
            pdf.cell(150, 10, "FINAL BALANCE:", 0, 0, 'R');
            pdf.cell(40, 10, f"Rs. {final:.2f}", 0, 1, 'R')

            st.download_button("📥 DOWNLOAD PDF", data=pdf.output(dest='S').encode('latin-1'),
                               file_name=f"Trimurti_{cust_name}.pdf")

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.all_entries = []
        st.rerun()
