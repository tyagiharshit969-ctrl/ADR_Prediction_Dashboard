import streamlit as st
import pandas as pd
import numpy as np
from reportlab.pdfgen import canvas
from io import BytesIO

# ===== Page Config =====
st.set_page_config(page_title="ADR Prediction Dashboard", layout="wide")

# ===== Load Data =====
data = pd.read_csv("ADR_multi_label_100.csv")

# ===== Dark Mode State =====
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ===== Custom CSS =====
def get_css(dark_mode=False):
    if dark_mode:
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Poppins', sans-serif; background:#121212; color:#FFFFFF; }
        .title { font-size:36px; font-weight:700; color:#BB86FC; }
        .subtitle { font-size:16px; color:#CCCCCC; margin-bottom:20px; }
        .section { font-size:20px; font-weight:600; color:#03DAC6; margin-bottom:8px; }
        .card { background:#1E1E1E; padding:20px; border-radius:12px; box-shadow:0px 3px 10px rgba(0,0,0,0.3); margin-bottom:15px;
                transition: all 0.2s ease-in-out; }
        .card:hover { transform:scale(1.02); box-shadow:0px 5px 15px rgba(0,0,0,0.5); }
        .footer { position: fixed; right: 20px; bottom: 10px; font-size:12px; color: grey; font-style: italic; }
        .progress-container { width:100%; background:#333; border-radius:12px; height:24px; margin-top:5px; }
        .progress-bar { height:100%; border-radius:12px; text-align:center; color:white; font-weight:bold; line-height:24px; }
        .kpi { background:#2C2C2C; padding:12px 15px; border-radius:10px; margin:5px; display:inline-block; font-weight:600; font-size:14px; text-align:center; min-width:120px;}
        .sidebar-button { display:flex; justify-content:center; }
        </style>
        """
    else:
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Poppins', sans-serif; background:#FFFFFF; color:#000000; }
        .title { font-size:36px; font-weight:700; color:#1565C0; }
        .subtitle { font-size:16px; color:#555555; margin-bottom:20px; }
        .section { font-size:20px; font-weight:600; color:#1E88E5; margin-bottom:8px; }
        .card { background:#ffffff; padding:20px; border-radius:12px; box-shadow:0px 3px 10px rgba(0,0,0,0.15); margin-bottom:15px;
                transition: all 0.2s ease-in-out; }
        .card:hover { transform:scale(1.02); box-shadow:0px 5px 15px rgba(0,0,0,0.3); }
        .footer { position: fixed; right: 20px; bottom: 10px; font-size:12px; color: grey; font-style: italic; }
        .progress-container { width:100%; background:#eee; border-radius:12px; height:24px; margin-top:5px; }
        .progress-bar { height:100%; border-radius:12px; text-align:center; color:white; font-weight:bold; line-height:24px; }
        .kpi { background:#F1F8E9; padding:12px 15px; border-radius:10px; margin:5px; display:inline-block; font-weight:600; font-size:14px; text-align:center; min-width:120px;}
        .sidebar-button { display:flex; justify-content:center; }
        </style>
        """

st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)

# ===== Header =====
st.markdown("<div class='title'>💊 ADR Prediction Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI-powered Adverse Drug Reaction Prediction</div>", unsafe_allow_html=True)
st.markdown("---")

# ===== Sidebar Inputs =====
st.sidebar.header("Patient Information")
selected_drug = st.sidebar.selectbox("Select Drug", sorted(data["Generic Name"].unique()))
age_group = st.sidebar.selectbox("Select Age Group", ["Baby (0–3)", "Child (4–12)", "Teen (13–19)",
                                                      "Young Adult (18–25)", "Adult (25–60)", "Senior (60+)"], index=4)
gender = st.sidebar.selectbox("Select Gender", ["Male", "Female"])

# ===== Predict ADR Button (Centered & Slightly Up) =====
st.markdown("""
    <style>
    div[data-testid="stSidebar"] div.stButton > button:first-child {
        width: 100%;
        margin-top: -10px;   /* Move button slightly up, closer to Gender */
    }
    </style>
""", unsafe_allow_html=True)

predict_button = st.sidebar.button("Predict ADR", key="predict", help="Click to predict ADR")

# Small space before Dark Mode toggle
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Dark Mode Toggle Below Button
toggle = st.sidebar.checkbox("🌙 Dark Mode", value=st.session_state.dark_mode, key="sidebar_dark")
st.session_state.dark_mode = toggle
st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)
st.markdown("""
    <style>
    .stButton > button {
        margin-top: -10px;  /* adjust value for vertical position */
    }
    </style>
""", unsafe_allow_html=True)

# ===== How to Use Before Prediction =====
if not predict_button:
    st.info(
        """
        *How to Use:*
        1. Select a drug from the sidebar.
        2. Choose the patient's age group.
        3. Select the patient's gender.
        4. Click *Predict ADR* to see the predicted Adverse Drug Reactions.
        5. Download the reports in PDF format.
        """
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
                f"</div>",
                unsafe_allow_html=True
            )

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

        # RIGHT: ADR Prediction + PDF
        with col2:
            st.markdown("<div class='section'>ADR Prediction</div>", unsafe_allow_html=True)
            common_adrs = str(row.get('Common ADRs','')).split(",")
            serious_adrs = str(row.get('Serious ADRs','')).split(",")

            common_html = "".join([f"<span style='color:#00FF00; font-weight:600;'>{adr.strip()}</span>, " for adr in common_adrs if adr.strip()!="None"])
            serious_html = "".join([f"<span style='color:#FF6961; font-weight:600;'>{adr.strip()}</span>, " for adr in serious_adrs if adr.strip()!="None"])

            st.markdown(
                f"<div class='card'>"
                f"<b>Common ADRs:</b> {common_html[:-2]}<br>"
                f"<b>Serious ADRs:</b> {serious_html[:-2]}<br>"
                f"<b>ADR Categories:</b> {row.get('ADR Label','N/A')}"
                f"</div>",
                unsafe_allow_html=True
            )

            # Progress bar
            chance_serious = row.get("Chance of Serious ADR (%)", 0)
            if pd.isna(chance_serious): chance_serious = 0
            if chance_serious < 33:
                color = "#4CAF50"
            elif chance_serious < 66:
                color = "#FFC107"
            else:
                color = "#FF5555"
            st.markdown("*Chance of Serious ADR:*")
            st.markdown(
                f"""
                <div class='progress-container'>
                    <div class='progress-bar' style='width:{chance_serious}%; background:{color};'>
                        {int(chance_serious)}%
                    </div>
                </div>
                """, unsafe_allow_html=True
            )

            risk_status = row.get("ADR Risk Status", "N/A")
            if str(risk_status).lower()=="high":
                risk_color = "#FF5555"
            elif str(risk_status).lower()=="moderate":
                risk_color = "#FFC107"
            else:
                risk_color = "#4CAF50"
            st.markdown(f"*ADR Risk Status:* <span style='color:{risk_color}; font-weight:bold;'>{risk_status}</span>", unsafe_allow_html=True)

            # PDF Button
            st.markdown("<br>", unsafe_allow_html=True)
            buffer = BytesIO()
            c = canvas.Canvas(buffer)
            c.drawString(100, 800, f"ADR Prediction Report - {selected_drug}")
            c.drawString(100, 780, f"Patient Age Group: {age_group}")
            c.drawString(100, 760, f"Gender: {gender}")
            c.drawString(100, 740, f"Common ADRs: {', '.join(common_adrs)}")
            c.drawString(100, 720, f"Serious ADRs: {', '.join(serious_adrs)}")
            c.drawString(100, 700, f"ADR Categories: {row.get('ADR Label','N/A')}")
            c.drawString(100, 680, f"Chance of Serious ADR: {chance_serious}%")
            c.drawString(100, 660, f"ADR Risk Status: {risk_status}")
            c.showPage()
            c.save()
            buffer.seek(0)
            st.download_button("📄 Download PDF Report", buffer, file_name=f"{selected_drug}_ADR_Report.pdf", mime="application/pdf")

# ===== Footer =====
st.markdown("<div class='footer'>Developed by Harshit Tyagi</div>", unsafe_allow_html=True)
