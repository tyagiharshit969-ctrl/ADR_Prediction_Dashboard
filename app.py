import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from reportlab.pdfgen import canvas

# ===== Page Config =====
st.set_page_config(page_title="ADR Prediction Dashboard", layout="wide")

# ===== Load Data =====
data = pd.read_csv("ADR_multi_label_100.csv")

# ===== Sidebar Inputs =====
st.sidebar.header("Patient Information")
selected_drug = st.sidebar.selectbox("Select Drug", sorted(data["Generic Name"].unique()))
age_group = st.sidebar.selectbox(
    "Select Age Group", 
    ["Baby (0–3)", "Child (4–12)", "Teen (13–19)", "Young Adult (18–25)", "Adult (25–60)", "Senior (60+)"], 
    index=4  # Default Adult
)
gender = st.sidebar.selectbox("Select Gender", ["Male", "Female"])
predict_button = st.sidebar.button("Predict ADR")

# Dark Mode toggle a little below the predict button
st.sidebar.markdown("<br>", unsafe_allow_html=True)  # Add spacing
dark_mode = st.sidebar.checkbox("🌙 Dark Mode")

# ===== Custom CSS =====
if dark_mode:
    bg_color = "#1e1e1e"
    text_color = "#f5f5f5"
    card_hover = "rgba(255,255,255,0.05)"
    common_color = "#8ef58e"
    serious_color = "#ff7f7f"
    heading_color = "#8ec6ff"
else:
    bg_color = "#f5f7fa"
    text_color = "#333333"
    card_hover = "rgba(0,0,0,0.05)"
    common_color = "green"
    serious_color = "red"
    heading_color = "#1565C0"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    html, body, [class*="css"] {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Poppins', sans-serif;
    }}
    .title {{ font-size:36px; font-weight:700; color:{heading_color}; margin-bottom:0; }}
    .subtitle {{ font-size:16px; color:{text_color}; margin-bottom:20px; }}
    .section {{ font-size:20px; font-weight:600; color:{heading_color}; margin-bottom:8px; }}
    .card {{ background:#ffffff; padding:20px; border-radius:12px; box-shadow:0px 3px 10px rgba(0,0,0,0.15); margin-bottom:15px; transition: all 0.2s ease-in-out; }}
    .card:hover {{ background:{card_hover}; transform: scale(1.01); }}
    .footer {{ text-align:right; font-size:12px; color: grey; font-style: italic; }}
    .progress-container {{ width:100%; background:#eee; border-radius:12px; height:24px; margin-top:5px; }}
    .progress-bar {{ height:100%; border-radius:12px; text-align:center; color:white; font-weight:bold; line-height:24px; }}
    .kpi {{ background:#F1F8E9; padding:12px 15px; border-radius:10px; margin:5px; display:inline-block; font-weight:600; font-size:14px; text-align:center; min-width:120px;}}
    </style>
""", unsafe_allow_html=True)

# ===== Title =====
st.markdown(f"<div class='title'>💊 ADR Prediction Dashboard</div>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>AI-powered Adverse Drug Reaction Prediction</div>", unsafe_allow_html=True)
st.markdown("---")

# ===== How to Use =====
if not predict_button:
    st.markdown(f"""
    <div class='card'>
    <b style='font-size:18px;'>📖 How to Use:</b>
    <ul>
        <li>Select the drug from the sidebar dropdown.</li>
        <li>Select the patient's age group and gender.</li>
        <li>Click the <b>Predict ADR</b> button to view drug profile and predicted adverse reactions.</li>
        <li>You can download the prediction report in PDF format.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ===== ADR Prediction =====
if predict_button:
    filtered_data = data[data["Generic Name"] == selected_drug]
    if filtered_data.empty:
        st.warning("No data found for this drug.")
    else:
        row = filtered_data.iloc[0]

        # Columns: Left = Drug Profile + KPI, Right = ADR Prediction
        col1, col2 = st.columns([2,2])

        # ---- LEFT SIDE: Drug Profile + KPI ----
        with col1:
            st.markdown("<div class='section'>Drug Profile</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='card'>"
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
            st.markdown("<div class='section'>Drug Statistics</div>", unsafe_allow_html=True)
            total_adrs = row.get('Total ADRs', 0)
            num_common = len(str(row.get('Common ADRs','')).split(",")) if row.get('Common ADRs') else 0
            num_serious = len(str(row.get('Serious ADRs','')).split(",")) if row.get('Serious ADRs') else 0

            kpi_html = (
                f"<div class='kpi'>Total ADRs<br>{total_adrs}</div>"
                f"<div class='kpi'>Common ADRs<br>{num_common}</div>"
                f"<div class='kpi'>Serious ADRs<br>{num_serious}</div>"
            )
            st.markdown(kpi_html, unsafe_allow_html=True)

        # ---- RIGHT SIDE: ADR Prediction ----
        with col2:
            st.markdown("<div class='section'>ADR Prediction</div>", unsafe_allow_html=True)

            common_adrs = str(row.get('Common ADRs','')).split(",")
            serious_adrs = str(row.get('Serious ADRs','')).split(",")

            # ADR Details Card
            common_html = "".join([f"<span style='color:{common_color}; font-weight:600;'>{adr.strip()}</span>, " for adr in common_adrs if adr.strip()!="None"])
            serious_html = "".join([f"<span style='color:{serious_color}; font-weight:600;'>{adr.strip()}</span>, " for adr in serious_adrs if adr.strip()!="None"])

            st.markdown(
                f"<div class='card'>"
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
                color = "#E53935"

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
                risk_color = "#E53935"
            elif str(risk_status).lower()=="moderate":
                risk_color = "#FFC107"
            else:
                risk_color = "#4CAF50"

            st.markdown(f"*ADR Risk Status:* <span style='color:{risk_color}; font-weight:bold;'>{risk_status}</span>", unsafe_allow_html=True)

            # ---- PDF Download Button ----
            st.markdown("<br>", unsafe_allow_html=True)
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer)
            c.drawString(50, 800, "ADR Prediction Report")
            c.drawString(50, 780, f"Drug: {selected_drug}")
            c.drawString(50, 760, f"Age Group: {age_group}")
            c.drawString(50, 740, f"Gender: {gender}")
            c.drawString(50, 720, f"Common ADRs: {row.get('Common ADRs','N/A')}")
            c.drawString(50, 700, f"Serious ADRs: {row.get('Serious ADRs','N/A')}")
            c.drawString(50, 680, f"ADR Categories: {row.get('ADR Label','N/A')}")
            c.drawString(50, 660, f"Total ADRs: {total_adrs}")
            c.drawString(50, 640, f"Chance of Serious ADR: {chance_serious}%")
            c.drawString(50, 620, f"ADR Risk Status: {risk_status}")
            c.save()
            pdf_buffer.seek(0)
            st.download_button("📄 Download PDF Report", data=pdf_buffer, file_name=f"{selected_drug}_ADR_Report.pdf", mime="application/pdf")

# ===== Footer =====
st.markdown("<div class='footer'>Developed by Harshit Tyagi</div>", unsafe_allow_html=True)
