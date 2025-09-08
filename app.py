import streamlit as st
import pandas as pd
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

# ===== Page Config =====
st.set_page_config(page_title="ADR Prediction Dashboard", layout="wide")

# ===== Custom CSS =====
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    html, body, [class*="css"] { 
        font-family: 'Poppins', sans-serif; 
        background: #ffffff;
    }

    .title { font-size:36px; font-weight:700; color:#1565C0; margin-bottom:0; }
    .subtitle { font-size:16px; color:#555555; margin-bottom:10px; }
    .section { font-size:20px; font-weight:600; color:#1E88E5; margin-bottom:8px; }
    .card { background:#ffffff; padding:20px; border-radius:12px; box-shadow:0px 3px 10px rgba(0,0,0,0.15); margin-bottom:15px; transition: transform 0.2s; }
    .card:hover { transform: scale(1.02); }
    .footer { position: fixed; right: 20px; bottom: 10px; font-size:12px; color: grey; font-style: italic; }
    .progress-container { width:100%; background:#eee; border-radius:12px; height:24px; margin-top:5px; }
    .progress-bar { height:100%; border-radius:12px; text-align:center; color:white; font-weight:bold; line-height:24px; }
    .kpi { background:#F1F8E9; padding:12px 15px; border-radius:10px; margin:5px; display:inline-block; font-weight:600; font-size:14px; text-align:center; min-width:120px;}
    .blue-card { background:#E3F2FD; padding:20px; border-radius:12px; box-shadow:0px 3px 10px rgba(0,0,0,0.15); margin-bottom:20px; }
    .dark-mode { background-color:#1E1E1E !important; color:white !important; }
    .dark-card { background:#2C2C2C !important; }
    .dark-kpi { background:#444 !important; color:white !important; }
    </style>
""", unsafe_allow_html=True)

# ===== Load Data =====
data = pd.read_csv("ADR_multi_label_100.csv")

# ===== Sidebar Inputs =====
st.sidebar.header("Patient Information")
selected_drug = st.sidebar.selectbox("Select Drug", sorted(data["Generic Name"].unique()))
age_group = st.sidebar.selectbox("Select Age Group", ["Baby (0–3)", "Child (4–12)", "Teen (13–19)",
                                                      "Young Adult (18–25)", "Adult (25–60)", "Senior (60+)"], index=4)
gender = st.sidebar.selectbox("Select Gender", ["Male", "Female"])

# Centered Predict Button
st.sidebar.markdown("<div style='display:flex; justify-content:center; margin-top:10px;'>", unsafe_allow_html=True)
predict_button = st.sidebar.button("Predict ADR")
st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Dark mode toggle in sidebar
dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=False)

# ===== Title & How to Use =====
st.markdown("<div class='title'>💊 ADR Prediction Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI-powered Adverse Drug Reaction Prediction</div>", unsafe_allow_html=True)
st.markdown("---")

# How to Use box before prediction
if not predict_button:
    how_to_text = """
    <div class='blue-card'>
        <h3>How to Use:</h3>
        <ol>
            <li>Select the drug from the dropdown.</li>
            <li>Choose the patient's age group and gender.</li>
            <li>Click on <b>Predict ADR</b> to view the predicted Adverse Drug Reactions.</li>
            <li>You can download the report as a PDF once the prediction is displayed.</li>
        </ol>
    </div>
    """
    st.markdown(how_to_text, unsafe_allow_html=True)

# ===== Main Output =====
if predict_button:
    filtered_data = data[data["Generic Name"] == selected_drug]

    if filtered_data.empty:
        st.warning("No data found for this drug.")
    else:
        row = filtered_data.iloc[0]

        # Dark mode classes
        dark_class = "dark-mode" if dark_mode else ""
        card_class = "dark-card" if dark_mode else "card"
        kpi_class = "dark-kpi" if dark_mode else "kpi"

        # Columns: Left = Drug Profile + KPI, Right = ADR Prediction
        col1, col2 = st.columns([2,2])

        # ---- LEFT SIDE: Drug Profile + KPI ----
        with col1:
            st.markdown(f"<div class='section {dark_class}'>Drug Profile</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='{card_class}'>"
                f"<b>Generic Name:</b> {row.get('Generic Name','N/A')}<br>"
                f"<b>Therapeutic Class:</b> {row.get('Therapeutic Class','N/A')}<br>"
                f"<b>Route:</b> {row.get('Route','N/A')}<br>"
                f"<b>Usual Dose:</b> {row.get('Usual Adult Dose','N/A')}<br>"
                f"<b>Age Group:</b> {age_group}<br>"
                f"<b>Gender:</b> {gender}"
                f"</div>",
                unsafe_allow_html=True
            )

            # ---- KPI Panels ----
            st.markdown(f"<div class='section {dark_class}'>Drug Statistics</div>", unsafe_allow_html=True)
            total_adrs = row.get('Total ADRs', 0)
            num_common = len(str(row.get('Common ADRs','')).split(",")) if row.get('Common ADRs') else 0
            num_serious = len(str(row.get('Serious ADRs','')).split(",")) if row.get('Serious ADRs') else 0

            kpi_html = (
                f"<div class='{kpi_class}'>{'Total ADRs'}<br>{total_adrs}</div>"
                f"<div class='{kpi_class}' style='color:lightgreen'>{'Common ADRs'}<br>{num_common}</div>"
                f"<div class='{kpi_class}' style='color:#FF8080'>{'Serious ADRs'}<br>{num_serious}</div>"
            )
            st.markdown(kpi_html, unsafe_allow_html=True)

        # ---- RIGHT SIDE: ADR Prediction ----
        with col2:
            st.markdown(f"<div class='section {dark_class}'>ADR Prediction</div>", unsafe_allow_html=True)

            common_adrs = str(row.get('Common ADRs','')).split(",")
            serious_adrs = str(row.get('Serious ADRs','')).split(",")

            # ADR Details Card
            common_html = "".join([f"<span style='color:lightgreen; font-weight:600;'>{adr.strip()}</span>, " 
                                   for adr in common_adrs if adr.strip()!="None"])
            serious_html = "".join([f"<span style='color:#FF8080; font-weight:600;'>{adr.strip()}</span>, " 
                                    for adr in serious_adrs if adr.strip()!="None"])

            st.markdown(
                f"<div class='{card_class}'>"
                f"<b>Common ADRs:</b> {common_html[:-2]}<br>"
                f"<b>Serious ADRs:</b> {serious_html[:-2]}<br>"
                f"<b>ADR Categories:</b> {row.get('ADR Label','N/A')}"
                f"</div>",
                unsafe_allow_html=True
            )

            # Gradient progress bar aligned under ADR details
            chance_serious = row.get("Chance of Serious ADR (%)", 0)
            if pd.isna(chance_serious): chance_serious = 0

            if chance_serious < 33:
                color = "#4CAF50"
            elif chance_serious < 66:
                color = "#FFC107"
            else:
                color = "#FF6B6B"

            st.markdown("*Chance of Serious ADR:*")
            st.markdown(
                f"""
                <div class='progress-container'>
                    <div class='progress-bar' style='width:{chance_serious}%; background:{color};'>
                        {int(chance_serious)}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # ADR Risk Status
            risk_status = row.get("ADR Risk Status", "N/A")
            if str(risk_status).lower()=="high":
                risk_color = "#FF6B6B"
            elif str(risk_status).lower()=="moderate":
                risk_color = "#FFC107"
            else:
                risk_color = "#4CAF50"

            st.markdown(f"*ADR Risk Status:* <span style='color:{risk_color}; font-weight:bold;'>{risk_status}</span>", unsafe_allow_html=True)

            # ---- PDF Download ----
            pdf_button_space = st.empty()  # Add space before button
            st.markdown("<br>", unsafe_allow_html=True)

            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.drawString(50, 750, f"ADR Prediction Report for {selected_drug}")
            c.drawString(50, 730, f"Age Group: {age_group}")
            c.drawString(50, 710, f"Gender: {gender}")
            c.drawString(50, 690, f"Common ADRs: {row.get('Common ADRs','N/A')}")
            c.drawString(50, 670, f"Serious ADRs: {row.get('Serious ADRs','N/A')}")
            c.drawString(50, 650, f"ADR Categories: {row.get('ADR Label','N/A')}")
            c.drawString(50, 630, f"Chance of Serious ADR: {chance_serious}%")
            c.drawString(50, 610, f"ADR Risk Status: {risk_status}")
            c.save()
            buffer.seek(0)

            st.download_button(
                label="📄 Download PDF Report",
                data=buffer,
                file_name=f"{selected_drug}_ADR_Report.pdf",
                mime="application/pdf"
            )

# ===== Footer =====
st.markdown("<div class='footer'>Developed by Harshit Tyagi</div>", unsafe_allow_html=True)
