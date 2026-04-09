# ==========================================
# PROJECT: TRIMURTI DOORS BILLING SYSTEM
# AUTHOR: DHANANJAY
# VERSION: 2.0 (Google Sheets Integrated)
# ==========================================

import streamlit as st
from fpdf import FPDF
from datetime import date
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
import os

# १. पेज सेटिंग्ज (Page Configurations)
st.set_page_config(
    page_title="Trimurti Doors World",
    page_icon="🚪",
    layout="wide"
)

# २. गुगल शीट कनेक्शन सेट करणे
# (हे तुमच्या Streamlit Secrets मधील लिंकला कनेक्ट होते)
conn = st.connection("gsheets", type=GSheetsConnection)

# ३. दरांचे व्यवस्थापन (Rate Management Logic)
RATES_FILE = "rates_data.json"

def load_rates():
    """फाईल मधून दर लोड करणे"""
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
    """नवीन दर फाईलमध्ये सेव्ह करणे"""
    with open(RATES_FILE, "w") as f:
        json.dump(rates, f)

# ४. युजर लॉगिन सिस्टीम (Security)
USERS = {
    "Dhananjay": "Trimurti@2026",
    "Admin": "Admin@123"
}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'all_entries' not in st.session_state:
    st.session_state.all_entries = []
if 'rates' not in st.session_state:
    st.session_state.rates = load_rates()

# लॉगिन पेज डिझाईन
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #004aad;'>🔐 Trimurti Doors Login</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        
        if st.button("Login to System"):
            if username_input in USERS and password_input == USERS[username_input]:
                st.session_state.logged_in = True
                st.session_state.current_user = username_input
                st.rerun()
            else:
                st.error("Invalid Username or Password!")
else:
    # --- मुख्य डॅशबोर्ड ---
    st.markdown(f"""
        <div style='background-color:#004aad; padding:15px; border-radius:10px; text-align:center; color:white;'>
            <h1>TRIMURTI DOORS WORLD</h1>
            <p style='margin-bottom:0;'>Logged in as: <b>{st.session_state.current_user}</b></p>
        </div>
    """, unsafe_allow_html=True)

    st.write("") # रिकामी ओळ

    # ५. एडमिन सेटिंग्स (फक्त धनंजय रेट बदलू शकतो)
    if st.session_state.current_user == "Dhananjay":
        with st.expander("⚙️ Admin Settings - Update Item Rates"):
            st.info("येथे बदललेले दर सर्व युजर्ससाठी लागू होतील.")
            updated_rates_dict = {}
            admin_cols = st.columns(4)
            
            for index, (series_name, current_price) in enumerate(st.session_state.rates.items()):
                updated_rates_dict[series_name] = admin_cols[index % 4].number_input(
                    f"{series_name} Rate", 
                    value=float(current_price),
                    key=f"rate_{series_name}"
                )
            
            if st.button("💾 Save All Rates Now"):
                st.session_state.rates = updated_rates_dict
                save_rates(updated_rates_dict)
                st.success("Rates updated in the database!")

    # ६. इंच कन्वर्शन लॉजिक (0.1 = 0.125 Inch)
    INCH_VALS = {0.1: 0.125, 0.2: 0.250, 0.3: 0.375, 0.4: 0.500, 0.5: 0.625, 0.6: 0.750, 0.7: 0.875, 0.8: 1.0, 0.9: 1.125}
    
    def convert_to_actual_inches(input_val):
        main_part = int(input_val)
        fractional_part = round(input_val - main_part, 1)
        return main_part + INCH_VALS.get(fractional_part, fractional_part)

    # ७. कस्टमर माहिती
    st.markdown("### 👤 Customer Details")
    inf_c1, inf_c2, inf_c3 = st.columns([1, 1, 2])
    customer_name = inf_c1.text_input("Full Name")
    customer_mobile = inf_c2.text_input("Mobile No.")
    customer_address = inf_c3.text_input("Delivery Address")

    # ८. डोअर एन्ट्री फॉर्म (जलद एन्ट्रीसाठी फॉर्म वापरला आहे)
    st.markdown("---")
    with st.form("entry_form_fast", clear_on_submit=True):
        st.markdown("##### ➕ Add Door Item")
        input_cols = st.columns(7)
        
        entry_ser = input_cols[0].selectbox("Series", list(st.session_state.rates.keys()))
        entry_qty = input_cols[1].number_input("Qty", min_value=1, step=1)
        entry_des = input_cols[2].text_input("Design Name")
        entry_col = input_cols[3].text_input("Color/Finish")
        entry_h = input_cols[4].number_input("Height", format="%.1f")
        entry_wt = input_cols[5].number_input("W-Top", format="%.1f")
        entry_wb = input_cols[6].number_input("W-Bottom", format="%.1f")
        
        if st.form_submit_button("ADD TO BILL"):
            # कन्वर्शन करणे
            final_h = convert_to_actual_inches(entry_h)
            final_w1 = convert_to_actual_inches(entry_wt)
            final_w2 = convert_to_actual_inches(entry_wb)
            
            # स्क्वेअर फूट हिशोब (किमान १४.०)
            max_width = max(final_w1, final_w2)
            calculated_sqft = round(max(14.0, (final_h * max_width) / 144), 2)
            
            # लिस्ट मध्ये सेव्ह करणे
            item_rate = st.session_state.rates[entry_ser]
            item_total = round(calculated_sqft * entry_qty * item_rate, 2)
            
            st.session_state.all_entries.append({
                "Series": entry_ser, "Design": entry_des, "Color": entry_col,
                "H": final_h, "W1": final_w1, "W2": final_w2,
                "Qty": entry_qty, "SqFt": calculated_sqft, "Rate": item_rate, "Total": item_total
            })
            st.rerun()

    # ९. बिलिंग आणि पीडीएफ जनरेशन
    if st.session_state.all_entries:
        st.markdown("### 📋 Current Quotation List")
        st.table(st.session_state.all_entries)
        
        # फायनल हिशोब रकाने
        subtotal_amt = sum(row['Total'] for row in st.session_state.all_entries)
        
        calc_c1, calc_c2, calc_c3, calc_c4 = st.columns(4)
        gst_percent = calc_c1.number_input("GST (%)", value=18)
        transport_amt = calc_c2.number_input("Transport Charges", value=0)
        discount_amt = calc_c3.number_input("Cash Discount", value=0)
        advance_amt = calc_c4.number_input("Advance Amount Paid", value=0)
        
        gst_val = round((subtotal_amt * gst_percent) / 100, 2)
        grand_total = subtotal_amt + gst_val + transport_amt - discount_amt - advance_amt
        
        st.subheader(f"💰 Final Payable Amount: ₹ {grand_total:,.2f}")

        # १०. सेव्ह आणि पीडीएफ बटण
        if st.button("🚀 FINALIZE, SAVE & DOWNLOAD"):
            # अ. गुगल शीट मध्ये डेटा सेव्ह करणे
            try:
                sheet_data = []
                for e in st.session_state.all_entries:
                    sheet_data.append({
                        "Date": str(date.today()), "User": st.session_state.current_user,
                        "Customer": customer_name, "Mobile": customer_mobile, "Address": customer_address,
                        "Series": e['Series'], "Design": e['Design'], "Color": e['Color'],
                        "H": e['H'], "W1": e['W1'], "W2": e['W2'], "SqFt": e['SqFt'],
                        "Rate": e['Rate'], "Total_Item_Value": e['Total'], "Final_Bill_Amount": grand_total
                    })
                
                existing_df = conn.read()
                new_df = pd.concat([existing_df, pd.DataFrame(sheet_data)], ignore_index=True)
                conn.update(data=new_df)
                st.success("Data successfully synced with Google Sheets!")
            except Exception as error:
                st.error(f"Sync Failed: {error}")

            # ब. पीडीएफ तयार करणे (Detailed Layout)
            pdf = FPDF()
            pdf.add_page()
            
            # Header Section
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 10, "TRIMURTI DOORS WORLD", 0, 1, 'C')
            pdf.set_font("Arial", '', 9)
            pdf.cell(190, 5, "Plot no. C-4/5, shendra MIDC, Chhatrapati Sambhaji Nagar, MS - 431154", 0, 1, 'C')
            pdf.ln(2)
            
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(190, 10, "QUOTATION", 1, 1, 'C')
            
            # Info Section
            pdf.ln(2)
            pdf.set_font("Arial", '', 10)
            pdf.cell(95, 7, f"Customer: {customer_name}", 0, 0)
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(95, 7, f"Prepared By: {st.session_state.current_user}", 0, 1, 'R')
            
            pdf.set_font("Arial", '', 10)
            pdf.cell(95, 7, f"Mobile: {customer_mobile}", 0, 0)
            pdf.cell(95, 7, f"Date: {date.today()}", 0, 1, 'R')
            pdf.cell(190, 7, f"Address: {customer_address}", 0, 1, 'L')
            
            # Table Header
            pdf.ln(5)
            pdf.set_fill_color(230, 230, 230)
            pdf.set_font("Arial", 'B', 8)
            
            cols = ["Sr", "Series", "Design", "Color", "Height", "W1", "W2", "Qty", "SqFt", "Rate", "Total"]
            widths = [8, 15, 25, 20, 15, 12, 12, 10, 15, 15, 43]
            
            for i in range(len(cols)):
                pdf.cell(widths[i], 10, cols[i], 1, 0, 'C', True)
            pdf.ln()
            
            # Table Rows
            pdf.set_font("Arial", '', 8)
            for idx, item in enumerate(st.session_state.all_entries):
                pdf.cell(widths[0], 8, str(idx+1), 1, 0, 'C')
                pdf.cell(widths[1], 8, str(item['Series']), 1)
                pdf.cell(widths[2], 8, str(item['Design']), 1)
                pdf.cell(widths[3], 8, str(item['Color']), 1)
                pdf.cell(widths[4], 8, f"{item['H']:.3f}", 1, 0, 'C')
                pdf.cell(widths[5], 8, f"{item['W1']:.3f}", 1, 0, 'C')
                pdf.cell(widths[6], 8, f"{item['W2']:.3f}", 1, 0, 'C')
                pdf.cell(widths[7], 8, str(item['Qty']), 1, 0, 'C')
                pdf.cell(widths[8], 8, f"{item['SqFt']:.2f}", 1, 0, 'C')
                pdf.cell(widths[9], 8, str(item['Rate']), 1, 0, 'C')
                pdf.cell(widths[10], 8, f"{item['Total']:.2f}", 1, 1, 'R')
            
            # Summary Section (Detailed)
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(150, 7, "Subtotal Amount:", 0, 0, 'R')
            pdf.cell(40, 7, f"{subtotal_amt:,.2f}", 0, 1, 'R')
            
            pdf.cell(150, 7, f"GST ({gst_percent}%):", 0, 0, 'R')
            pdf.cell(40, 7, f"{gst_val:,.2f}", 0, 1, 'R')
            
            pdf.cell(150, 7, "Transport Charges:", 0, 0, 'R')
            pdf.cell(40, 7, f"{transport_amt:,.2f}", 0, 1, 'R')
            
            pdf.cell(150, 7, "Discount & Advance:", 0, 0, 'R')
            pdf.cell(40, 7, f"-{(discount_amt + advance_amt):,.2f}", 0, 1, 'R')
            
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(200, 0, 0)
            pdf.cell(150, 12, "FINAL PAYABLE BALANCE:", 0, 0, 'R')
            pdf.cell(40, 12, f"Rs. {grand_total:,.2f}", 0, 1, 'R')
            
            # Download PDF
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 DOWNLOAD QUOTATION PDF", data=pdf_bytes, file_name=f"Trimurti_Quo_{customer_name}.pdf")

    # ११. लॉगआउट बटण
    st.markdown("---")
    if st.button("🚪 Logout from System"):
        st.session_state.all_entries = []
        st.session_state.logged_in = False
        st.rerun()

# ==========================================
# END OF CODE
# ==========================================
