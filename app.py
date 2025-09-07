import streamlit as st
import pandas as pd
import numpy as np
from reportlab.pdfgen import canvas
import io

# ===== Page Config =====
st.set_page_config(page_title="ADR Prediction Dashboard", layout="wide")

# ===== Load Data =====
data = pd.read_csv("ADR_multi_label_100.csv")

# ===== Sidebar Inputs =====
st.sidebar.header("Patient Information")
selected_drug = st.sidebar.selectbox("Select Drug", sorted(data["Generic Name"].unique()))
age_group = st.sidebar.selectbox(
    "Select Age Group",
    ["Baby (0–3)", "Child (4–12)", "Teen (13–19)",
     "Young Adult (18–25)", "Adult (25–60)", "Senior (60+)"], index=4)
gender = st.sidebar.selectbox("Select Gender", ["Male", "Female"])

# ===== Sidebar: Centered Predict Button =====
st.sidebar.markdown(
    "<div style='display:flex; justify-content:center; margin-top:15px; margin-bottom:10px;'>"
    "<div style='width:80%;'>", unsafe_allow_html=True)
predict_button = st.sidebar.button("Predict ADR", key="predict")
st.sidebar.markdown("</div></div>", unsafe_allow_html=True)

# ===== Sidebar: Dark Mode Toggle Below Button =====
dark_mode = st.sidebar.checkbox("🌙 Dark Mode")

# ===== Custom CSS =====
if dark_mode:
    bg_color = "#111111"
    text_color = "#EEEEEE"
    card_color = "#1E1E1E"
    hover_color = "#2C2C2C"
    kpi_text = "#FFFFFF"
    common_color = "#A5D6A7"
    serious_color = "#EF9A9A"
    heading_color = "#90CAF9"
else:
    bg_color = "#f5f7fa"
    text_color = "#111111"
    card_color = "#FFFFFF"
    hover_color = "#f0f0f0"
    kpi_text = "#000000"
    common_color = "#4CAF50"
    serious_color = "#E53935"
    heading_color = "#1565C0"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Poppins', sans-serif; background-color:{bg_color}; color:{text_color}; }}
    .title {{ font-size:36px; font-weight:700; color:{heading_color}; margin-bottom:0; }}
    .subtitle {{ font-size:16px; color:{text_color}; margin-bottom:0; }}
    hr {{ border:0; border-top:2px solid {heading_color}; margin-bottom:20px; }}
    .section {{ font-size:20px; font-weight:600; color:{heading_color}; margin-bottom:8px; }}
    .card {{ background:{card_color}; padding:20px; border-radius:12px; box-shadow:0px 3px 10px rgba(0,0,0,0.15); margin-bottom:15px; transition: transform 0.2s; }}
    .card:hover {{ transform: translateY(-5px); background:{hover_color}; }}
    .footer {{ position: fixed; right: 20px; bottom: 10px; font-size:12px; color: grey; font-style: italic; }}
    .progress-container {{ width:100%; background:#eee; border-radius:12px; height:24px; margin-top:5px; }}
    .progress-bar {{ height:100%; border-radius:12px; text-align:center; color:white; font-weight:bold; line-height:24px; }}
    .kpi {{ background:#F1F8E9; padding:12px 15px; border-radius:10px; margin:5px; display:inline-block; font-weight:600; font-size:14px; text-align:center; min-width:120px; color:{kpi_text};}}
    .howto {{ background:{card_color}; padding:15px; border-radius:12px; box-shadow:0px 3px 10px rgba(0,0,0,0.1); margin-bottom:20px; }}
    </style>
""", unsafe_allow_html=True)

# ===== Title & Separator =====
st.markdown("<div class='title'>💊 ADR Prediction Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI-powered Adverse Drug Reaction Prediction</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ===== How-to-Use Section =====
if not predict_button:
    st.markdown(
        f"<div class='howto'>"
        "<h3>How to Use:</h3>"
        "<ol>"
        "<li>Select a drug from the dropdown.</li>"
        "<li>Choose the patient's age group and gender.</li>"
        "<li>Click the <b>Predict ADR</b> button in the sidebar.</li>"
        "<li>View the predicted ADRs, drug statistics, and risk assessment.</li>"
        "<li>Download the report if needed.</li>"
        "</ol>"
        "</div>",
        unsafe_allow_html=True
    )

# ===== Main Output =====
if predict_button:
    filtered_data = data[data["Generic Name"] == selected_drug]

    if filtered_data.empty:
        st.warning("No data found for this drug.")
    else:
        row = filtered_data.iloc[0]

        col1, col2 = st.columns([2,2])

        # LEFT: Drug Profile + KPI
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
                f"</div>", unsafe_allow_html=True
            )

            st.markdown("<div class='section'>Drug Statistics</div>", unsafe_allow_html=True)
            total_adrs = row.get('Total ADRs',0)
            num_common = len(str(row.get('Common ADRs','')).split(",")) if row.get('Common ADRs') else 0
            num_serious = len(str(row.get('Serious ADRs','')).split(",")) if row.get('Serious ADRs') else 0
            kpi_html = (
                f"<div class='kpi'>Total ADRs<br>{total_adrs}</div>"
                f"<div class='kpi'>Common ADRs<br>{num_common}</div>"
                f"<div class='kpi'>Serious ADRs<br>{num_serious}</div>"
            )
            st.markdown(kpi_html, unsafe_allow_html=True)

        # RIGHT: ADR Prediction + PDF
        with col2:
            st.markdown("<div class='section'>ADR Prediction</div>", unsafe_allow_html=True)
            common_adrs = str(row.get('Common ADRs','')).split(",")
            serious_adrs = str(row.get('Serious ADRs','')).split(",")
            common_html = "".join([f"<span style='color:{common_color}; font-weight:600;'>{adr.strip()}</span>, " for adr in common_adrs if adr.strip()!="None"])
            serious_html = "".join([f"<span style='color:{serious_color}; font-weight:600;'>{adr.strip()}</span>, " for adr in serious_adrs if adr.strip()!="None"])
            st.markdown(
                f"<div class='card'>"
                f"<b>Common ADRs:</b> {common_html[:-2]}<br>"
                f"<b>Serious ADRs:</b> {serious_html[:-2]}<br>"
                f"<b>ADR Categories:</b> {row.get('ADR Label','N/A')}"
                f"</div>", unsafe_allow_html=True
            )

            # Progress Bar
            chance_serious = row.get("Chance of Serious ADR (%)",0)
            if pd.isna(chance_serious): chance_serious=0
            if chance_serious<33: color = "#4CAF50" if not dark_mode else "#A5D6A7"
            elif chance_serious<66: color = "#FFC107" if not dark_mode else "#FFEE58"
            else: color = "#E53935" if not dark_mode else "#EF9A9A"
            st.markdown("*Chance of Serious ADR:*")
            st.markdown(
                f"<div class='progress-container'>"
                f"<div class='progress-bar' style='width:{chance_serious}%; background:{color};'>{int(chance_serious)}%</div>"
                f"</div>", unsafe_allow_html=True
            )

            # ADR Risk Status
            risk_status = row.get("ADR Risk Status","N/A")
            if str(risk_status).lower()=="high": risk_color = "#E53935" if not dark_mode else "#EF9A9A"
            elif str(risk_status).lower()=="moderate": risk_color = "#FFC107" if not dark_mode else "#FFEE58"
            else: risk_color = "#4CAF50" if not dark_mode else "#A5D6A7"
            st.markdown(f"*ADR Risk Status:* <span style='color:{risk_color}; font-weight:bold;'>{risk_status}</span>", unsafe_allow_html=True)

            # PDF Download
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer)
            c.setFont("Helvetica", 12)
            c.drawString(50, 800, f"ADR Prediction Report - {row.get('Generic Name')}")
            c.drawString(50, 780, f"Patient Age Group: {age_group}")
            c.drawString(50, 760, f"Patient Gender: {gender}")
            c.drawString(50, 740, f"Common ADRs: {row.get('Common ADRs')}")
            c.drawString(50, 720, f"Serious ADRs: {row.get('Serious ADRs')}")
            c.drawString(50, 700, f"ADR Categories: {row.get('ADR Label')}")
            c.drawString(50, 680, f"Chance of Serious ADR: {chance_serious}%")
            c.drawString(50, 660, f"ADR Risk Status: {risk_status}")
            c.showPage()
            c.save()
            buffer.seek(0)

            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="📄 Download PDF Report",
                data=buffer,
                file_name=f"{selected_drug}_ADR_Report.pdf",
                mime="application/pdf"
            )

# ===== Footer =====
st.markdown("<div class='footer'>Developed by Harshit Tyagi</div>", unsafe_allow_html=True)
