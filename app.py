import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from reportlab.pdfgen import canvas

# ===== Page Config =====
st.set_page_config(page_title="ADR Prediction Dashboard", layout="wide")

# ===== Load Data =====
data = pd.read_csv("ADR_multi_label_100.csv")

# ===== Custom CSS =====
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    html, body, [class*="css"] { 
        font-family: 'Poppins', sans-serif; 
    }

    .title { font-size:36px; font-weight:700; color:#1565C0; margin-bottom:0; display:inline-block; vertical-align:middle; }
    .subtitle { font-size:16px; color:#555555; margin-bottom:10px; display:inline-block; margin-left:15px; vertical-align:middle; }
    .section { font-size:20px; font-weight:600; color:#1E88E5; margin-bottom:8px; }
    .card { background:#ffffff; padding:20px; border-radius:12px; box-shadow:0px 3px 10px rgba(0,0,0,0.15); margin-bottom:15px; transition: transform 0.2s; }
    .card:hover { transform: translateY(-5px); }
    .footer { position: fixed; right: 20px; bottom: 10px; font-size:12px; color: grey; font-style: italic; }
    .progress-container { width:100%; background:#eee; border-radius:12px; height:24px; margin-top:5px; }
    .progress-bar { height:100%; border-radius:12px; text-align:center; font-weight:bold; line-height:24px; }
    .kpi { background:#F1F8E9; padding:12px 15px; border-radius:10px; margin:5px; display:inline-block; font-weight:600; font-size:14px; text-align:center; min-width:120px; transition: transform 0.2s; }
    .kpi:hover { transform: translateY(-3px); }
    .howto-card { background:#fefefe; padding:20px; border-radius:12px; box-shadow:0px 3px 10px rgba(0,0,0,0.1); margin-bottom:20px; }
    .dark .card, .dark .howto-card { background:#1e1e1e; color:white; box-shadow:0px 3px 10px rgba(255,255,255,0.05); }
    .dark .kpi { background:#333; color:white; }
    </style>
""", unsafe_allow_html=True)

# ===== Sidebar Inputs =====
st.sidebar.header("Patient Information")
selected_drug = st.sidebar.selectbox("Select Drug", sorted(data["Generic Name"].unique()))
age_group = st.sidebar.selectbox("Select Age Group", ["Baby (0–3)", "Child (4–12)", "Teen (13–19)",
                                                      "Young Adult (18–25)", "Adult (25–60)", "Senior (60+)"], index=4)
gender = st.sidebar.selectbox("Select Gender", ["Male", "Female"])

# Center the Predict ADR button in sidebar
st.sidebar.markdown("<div style='text-align:center; margin-top:20px;'>", unsafe_allow_html=True)
predict_button = st.sidebar.button("Predict ADR")
st.sidebar.markdown("</div>", unsafe_allow_html=True)

# ===== Title =====
st.markdown("<div class='title'>💊 ADR Prediction Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI-powered Adverse Drug Reaction Prediction</div>", unsafe_allow_html=True)
st.markdown("---")

# ===== How-to-use section =====
if not predict_button:
    st.markdown(
        f"<div class='howto-card'>"
        f"<h3>How to Use</h3>"
        f"<ol>"
        f"<li>Select the drug from the dropdown menu.</li>"
        f"<li>Choose the patient's age group.</li>"
        f"<li>Select the patient's gender.</li>"
        f"<li>Click <b>Predict ADR</b> to view predicted adverse drug reactions and statistics.</li>"
        f"</ol>"
        f"</div>", unsafe_allow_html=True
    )

# ===== Main Output =====
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

            # Make statistics text visible in dark mode
            kpi_html = (
                f"<div class='kpi' style='color:inherit;'>Total ADRs<br>{total_adrs}</div>"
                f"<div class='kpi' style='color:inherit;'>Common ADRs<br>{num_common}</div>"
                f"<div class='kpi' style='color:inherit;'>Serious ADRs<br>{num_serious}</div>"
            )
            st.markdown(kpi_html, unsafe_allow_html=True)

        # ---- RIGHT SIDE: ADR Prediction ----
        with col2:
            st.markdown("<div class='section'>ADR Prediction</div>", unsafe_allow_html=True)

            common_adrs = str(row.get('Common ADRs','')).split(",")
            serious_adrs = str(row.get('Serious ADRs','')).split(",")

            # ADR Details Card
            common_html = "".join([f"<span style='color:green; font-weight:600;'>{adr.strip()}</span>, " for adr in common_adrs if adr.strip()!="None"])
            serious_html = "".join([f"<span style='color:red; font-weight:600;'>{adr.strip()}</span>, " for adr in serious_adrs if adr.strip()!="None"])

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

# ===== Footer =====
st.markdown("<div class='footer'>Developed by Harshit Tyagi</div>", unsafe_allow_html=True)
