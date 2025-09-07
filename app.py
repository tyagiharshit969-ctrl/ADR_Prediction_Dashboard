import streamlit as st
import pandas as pd

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
    index=4  # Default Adult (25–60)
)
gender = st.sidebar.selectbox("Select Gender", ["Male", "Female"])
dark_mode = st.sidebar.checkbox("Dark Mode", value=False)
predict_button = st.sidebar.button("Predict ADR")

# ===== Color Palettes =====
colors_light = {
    "primary_heading": "#1565C0",
    "section_heading": "#1E88E5",
    "common_adr": "#388E3C",
    "serious_adr": "#D32F2F",
    "progress_low": "#4CAF50",
    "progress_mid": "#FFC107",
    "progress_high": "#E53935",
    "card_bg": "#ffffff",
    "text": "#000000"
}

colors_dark = {
    "primary_heading": "#90CAF9",
    "section_heading": "#64B5F6",
    "common_adr": "#81C784",
    "serious_adr": "#EF9A9A",
    "progress_low": "#81C784",
    "progress_mid": "#FFD54F",
    "progress_high": "#EF5350",
    "card_bg": "#2E2E2E",
    "text": "#FFFFFF"
}

colors = colors_dark if dark_mode else colors_light

# ===== Custom CSS =====
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
        background: {"#121212" if dark_mode else "#F5F7FA"};
        color: {colors["text"]};
    }}

    .title {{ font-size:36px; font-weight:700; color:{colors["primary_heading"]}; margin-bottom:0; }}
    .subtitle {{ font-size:16px; color:{colors["text"]}; margin-bottom:20px; }}
    .section {{ font-size:20px; font-weight:600; color:{colors["section_heading"]}; margin-bottom:8px; }}
    .card {{ background:{colors["card_bg"]}; padding:20px; border-radius:12px; box-shadow:0px 3px 10px rgba(0,0,0,0.15); margin-bottom:15px; color:{colors["text"]}; }}
    .footer {{ position: fixed; right: 20px; bottom: 10px; font-size:12px; color: grey; font-style: italic; }}
    .progress-container {{ width:100%; background:#eee; border-radius:12px; height:24px; margin-top:5px; }}
    .progress-bar {{ height:100%; border-radius:12px; text-align:center; color:white; font-weight:bold; line-height:24px; }}
    .kpi {{ background:#F1F8E9; padding:12px 15px; border-radius:10px; margin:5px; display:inline-block; font-weight:600; font-size:14px; text-align:center; min-width:120px; }}
    </style>
""", unsafe_allow_html=True)

# ===== Title =====
st.markdown("<div class='title'>💊 ADR Prediction Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI-powered Adverse Drug Reaction Prediction</div>", unsafe_allow_html=True)
st.markdown("---")

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

            # KPI Panels
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
            common_html = ", ".join([f"<span style='color:{colors['common_adr']}; font-weight:600;'>{adr.strip()}</span>" for adr in common_adrs if adr.strip()!="None"])
            serious_html = ", ".join([f"<span style='color:{colors['serious_adr']}; font-weight:600;'>{adr.strip()}</span>" for adr in serious_adrs if adr.strip()!="None"])

            st.markdown(
                f"<div class='card'>"
                f"<b>Common ADRs:</b> {common_html}<br>"
                f"<b>Serious ADRs:</b> {serious_html}<br>"
                f"<b>ADR Categories:</b> {row.get('ADR Label','N/A')}"
                f"</div>",
                unsafe_allow_html=True
            )

            # Gradient progress bar
            chance_serious = row.get("Chance of Serious ADR (%)", 0)
            if pd.isna(chance_serious): chance_serious = 0

            if chance_serious < 33:
                color = colors["progress_low"]
            elif chance_serious < 66:
                color = colors["progress_mid"]
            else:
                color = colors["progress_high"]

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

            # ---- Download PDF Button ----
            import io
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter

            def generate_pdf():
                buffer = io.BytesIO()
                c = canvas.Canvas(buffer, pagesize=letter)
                textobject = c.beginText(40, 700)
                textobject.setFont("Helvetica-Bold", 14)
                textobject.textLine("ADR Prediction Report")
                textobject.setFont("Helvetica", 12)
                textobject.textLine(f"Patient Age Group: {age_group}")
                textobject.textLine(f"Gender: {gender}")
                textobject.textLine(f"Drug: {row.get('Generic Name','N/A')}")
                textobject.textLine(f"Therapeutic Class: {row.get('Therapeutic Class','N/A')}")
                textobject.textLine(f"Route: {row.get('Route','N/A')}")
                textobject.textLine(f"Usual Dose: {row.get('Usual Adult Dose','N/A')}")
                textobject.textLine("")
                textobject.textLine(f"Common ADRs: {', '.join([adr.strip() for adr in common_adrs if adr.strip()!='None'])}")
                textobject.textLine(f"Serious ADRs: {', '.join([adr.strip() for adr in serious_adrs if adr.strip()!='None'])}")
                textobject.textLine(f"ADR Categories: {row.get('ADR Label','N/A')}")
                textobject.textLine(f"Total ADRs: {total_adrs}")
                textobject.textLine(f"Chance of Serious ADR: {int(chance_serious)}%")
                textobject.textLine(f"ADR Risk Status: {risk_status}")
                c.drawText(textobject)
                c.showPage()
                c.save()
                buffer.seek(0)
                return buffer

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📄 Download ADR Report (PDF)"):
                pdf_buffer = generate_pdf()
                st.download_button("Download PDF", pdf_buffer, file_name="ADR_Report.pdf", mime="application/pdf")

# ===== Footer =====
st.markdown("<div class='footer'>Developed by Harshit Tyagi</div>", unsafe_allow_html=True)
