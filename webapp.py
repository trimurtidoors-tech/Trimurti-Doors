import streamlit as st
from fpdf import FPDF
from datetime import date
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import os

# १. पेज सेटिंग्ज
st.set_page_config(page_title="Trimurti Doors World", layout="wide")

# २. गुगल शीट कनेक्शन
conn = st.connection("gsheets", type=GSheetsConnection)

# ३. दरांचे व्यवस्थापन
RATES_FILE = "rates_data.json"
def load_rates():
    default_rates = {"FT": 720, "Deco": 685, "PD": 585, "Delux": 385, "Diamond": 315, "Classic": 285, "Silver": 240, "FRP": 185, "Ls": 240, "T": 160, "Eg": 630}
    if os.path.exists(RATES_FILE):
        with open(RATES_FILE, "r") as f: return json.load(f)
    return default_rates

def save_rates(rates):
    with open(RATES_FILE, "w") as f: json.dump(rates, f)

# ४. युजर लॉगिन (Password: Dhananjay-789, Admin-123)
USERS = {"Dhananjay": "789", "Admin": "123"}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'all_entries' not in st.session_state: st.session_state.all_entries = []
if 'rates' not in st.session_state: st.session_state.rates = load_rates()

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #004aad;'>🔐 Trimurti Doors Login</h2>", unsafe_allow_html=True)
    u_input = st.text_input("Username")
    p_input = st.text_input("Password", type="password")
    if st.button("Login"):
        if u_input in USERS and p_input == USERS[u_input]:
            st.session_state.logged_in = True
            st.session_state.current_user = u_input
            st.rerun()
        else: st.error("Invalid Username or Password!")
else:
    st.markdown(f"<div style='background-color:#004aad;padding:10px;color:white;text-align:center;border-radius:10px;'><h1>TRIMURTI DOORS WORLD</h1></div>", unsafe_allow_html=True)

    # ६. इंच कन्वर्शन (0.1 = 0.125 Inch)
    INCH_CONV = {0.1: 0.125, 0.2: 0.250, 0.3: 0.375, 0.4: 0.500, 0.5: 0.625, 0.6: 0.750, 0.7: 0.875, 0.8: 1.0, 0.9: 1.125}
    def get_val(v):
        m = int(v); f = round(v - m, 1)
        return m + INCH_CONV.get(f, f)

    # ७. कस्टमर माहिती
    st.markdown("### 👤 Customer Details")
    c1, c2, c3 = st.columns([1, 1, 2])
    cust_name = c1.text_input("Customer Name")
    mobile = c2.text_input("Mobile No.")
    address = c3.text_input("Address")

    # ८. डोअर एन्ट्री फॉर्म
    with st.form("door_form", clear_on_submit=True):
        st.markdown("##### ➕ Add Door Item")
        r_cols = st.columns(7)
        ser = r_cols[0].selectbox("Series", list(st.session_state.rates.keys()))
        qty = r_cols[1].number_input("Qty", min_value=1, step=1)
        des = r_cols[2].text_input("Design")
        col = r_cols[3].text_input("Color")
        h_in = r_cols[4].number_input("Height", format="%.1f")
        w1_in = r_cols[5].number_input("W-Top", format="%.1f")
        w2_in = r_cols[6].number_input("W-Bottom", format="%.1f")
        if st.form_submit_button("ADD TO LIST"):
            fh, fw1, fw2 = get_val(h_in), get_val(w1_in), get_val(w2_in)
            sqft = round(max(14.0, (fh * max(fw1, fw2)) / 144), 2)
            st.session_state.all_entries.append({
                "Series": ser, "Design": des, "Color": col, "H": fh, "W1": fw1, "W2": fw2,
                "Qty": qty, "SqFt": sqft, "Rate": st.session_state.rates[ser], "Total": round(sqft * qty * st.session_state.rates[ser], 2)
            })
            st.rerun()

    # ९. एडिटेबल बिलिंग टेबल (EDIT & DELETE Feature)
    if st.session_state.all_entries:
        st.markdown("### 📋 Edit or Delete Items")
        df_entries = pd.DataFrame(st.session_state.all_entries)
        
        # data_editor मुळे युजर थेट बदल करू शकतो किंवा ओळ उडवू शकतो
        edited_df = st.data_editor(df_entries, num_rows="dynamic", use_container_width=True)
        
        # बदललेले आकडे पुन्हा कॅल्क्युलेट करणे
        edited_df['Total'] = edited_df['SqFt'] * edited_df['Qty'] * edited_df['Rate']
        st.session_state.all_entries = edited_df.to_dict('records')
        
        sub_total = sum(i['Total'] for i in st.session_state.all_entries)
        gst_amt = round((sub_total * 18) / 100, 2)
        
        f_cols = st.columns(3)
        trans = f_cols[0].number_input("Transport", 0)
        adv = f_cols[1].number_input("Advance", 0)
        disc = f_cols[2].number_input("Discount", 0)
        
        grand_total = sub_total + gst_amt + trans - disc - adv
        st.subheader(f"💰 Grand Total: ₹ {grand_total:,.2f} (Incl. 18% GST)")

        if st.button("🚀 SAVE & GENERATE PDF"):
            # १०-अ: गुगल शीट सिंक
            try:
                try: df_existing = conn.read(ttl=0)
                except: df_existing = pd.DataFrame()

                new_rows = []
                for entry in st.session_state.all_entries:
                    new_rows.append({
                        "Date": str(date.today()), "User": st.session_state.current_user,
                        "Customer": cust_name, "Mobile": f"'{mobile}", "Address": address,
                        "Qty": entry['Qty'], "Series": entry['Series'], "Design": entry['Design'], "Color": entry['Color'],
                        "H": entry['H'], "W1": entry['W1'], "W2": entry['W2'], "SqFt": entry['SqFt'], "Rate": entry['Rate'], 
                        "Transport": trans, "Advance": adv, "Discount": disc, "Final_Bill": grand_total
                    })
                
                df_updated = pd.concat([df_existing, pd.DataFrame(new_rows)], ignore_index=True)
                conn.update(data=df_updated)
                st.success("Data successfully saved!")
            except Exception as e: st.error(f"Sync Error: {e}")

            # १०-ब: पीडीएफ जनरेशन
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 10, "TRIMURTI DOORS WORLD", 0, 1, 'C')
            pdf.set_font("Arial", '', 9)
            pdf.cell(190, 5, "Plot no. C-4/5, shendra MIDC, Chhatrapati Sambhaji Nagar, Maharashtra-431154", 0, 1, 'C')
            pdf.ln(2); pdf.set_font("Arial", 'B', 14); pdf.cell(190, 10, "QUOTATION", 1, 1, 'C')
            
            pdf.ln(5); pdf.set_font("Arial", '', 10)
            pdf.cell(95, 7, f"Customer: {cust_name}"); pdf.cell(95, 7, f"Date: {date.today()}", 0, 1, 'R')
            pdf.cell(95, 7, f"Mobile: {mobile}"); pdf.cell(95, 7, f"Prepared By: {st.session_state.current_user}", 0, 1, 'R')
            pdf.cell(190, 7, f"Address: {address}", 0, 1); pdf.ln(5)
            
            pdf.set_font("Arial", 'B', 8); pdf.set_fill_color(230, 230, 230)
            h_list = ["Sr", "Series", "Design", "Color", "Qty", "H", "W1", "W2", "SqFt", "Rate", "Total"]
            w_list = [8, 15, 25, 20, 10, 12, 12, 12, 15, 15, 46]
            for idx, h in enumerate(h_list): pdf.cell(w_list[idx], 10, h, 1, 0, 'C', True)
            pdf.ln(); pdf.set_font("Arial", '', 8)
            
            for idx, i in enumerate(st.session_state.all_entries):
                pdf.cell(w_list[0], 8, str(idx+1), 1)
                pdf.cell(w_list[1], 8, i['Series'], 1); pdf.cell(w_list[2], 8, i['Design'], 1)
                pdf.cell(w_list[3], 8, i['Color'], 1); pdf.cell(w_list[4], 8, str(i['Qty']), 1)
                pdf.cell(w_list[5], 8, str(i['H']), 1); pdf.cell(w_list[6], 8, str(i['W1']), 1)
                pdf.cell(w_list[7], 8, str(i['W2']), 1); pdf.cell(w_list[8], 8, str(i['SqFt']), 1)
                pdf.cell(w_list[9], 8, str(i['Rate']), 1); pdf.cell(w_list[10], 8, f"{i['Total']:,.2f}", 1, 1, 'R')
            
            pdf.ln(5); pdf.set_font("Arial", 'B', 10)
            pdf.cell(150, 7, "Subtotal Amount:", 0, 0, 'R'); pdf.cell(40, 7, f"{sub_total:,.2f}", 0, 1, 'R')
            pdf.cell(150, 7, "GST (18%):", 0, 0, 'R'); pdf.cell(40, 7, f"{gst_amt:,.2f}", 0, 1, 'R')
            pdf.cell(150, 7, "Transport Charges:", 0, 0, 'R'); pdf.cell(40, 7, f"{trans:,.2f}", 0, 1, 'R')
            pdf.cell(150, 7, "Discount Amount:", 0, 0, 'R'); pdf.cell(40, 7, f"-{disc:,.2f}", 0, 1, 'R')
            pdf.cell(150, 7, "Advance Paid:", 0, 0, 'R'); pdf.cell(40, 7, f"-{adv:,.2f}", 0, 1, 'R')
            pdf.set_font("Arial", 'B', 12); pdf.set_text_color(200, 0, 0)
            pdf.cell(150, 10, "GRAND TOTAL BALANCE:", 0, 0, 'R'); pdf.cell(40, 10, f"Rs. {grand_total:,.2f}", 0, 1, 'R')
            
            pdf.ln(5); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'BU', 9)
            pdf.cell(190, 7, "Terms & Conditions:", 0, 1, 'L')
            pdf.set_font("Arial", '', 8)
            pdf.cell(190, 5, "* This quotation is valid for 7 days only.", 0, 1, 'L')
            pdf.cell(190, 5, "* 18% GST is applicable on the total amount.", 0, 1, 'L')
            pdf.cell(190, 5, "* Transportation charges are extra as per actuals.", 0, 1, 'L')
            pdf.cell(190, 5, "* Additional charges apply for customized designs and colors.", 0, 1, 'L')
            
            pdf.ln(5); pdf.set_font("Arial", 'B', 9)
            pdf.cell(190, 5, "Contact Us: 8888467733 | 9921587713 | 8669194545", 0, 1, 'C')
            
            st.download_button("📥 DOWNLOAD PDF", data=pdf.output(dest='S').encode('latin-1'), file_name=f"Trimurti_{cust_name}.pdf")

    if st.button("🚪 Logout"):
        st.session_state.all_entries = []; st.session_state.logged_in = False; st.rerun()
