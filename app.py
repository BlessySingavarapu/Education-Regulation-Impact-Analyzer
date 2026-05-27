import streamlit as st
import os
import json
from google.genai import Client
from google.genai import types
from pydantic import BaseModel

# -----------------------------------------------------------------------------
# 1. ROOT INITIALIZATION
# -----------------------------------------------------------------------------
ENV_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCX02Yr2foVix1J4EC62olF8_X_fSFNxmY")

if ENV_KEY.startswith("AIzaSy"):
    client = Client(api_key=ENV_KEY)
else:
    st.sidebar.error("❌ ERIA Engine Error: Valid GEMINI_API_KEY not found in background kernel.")
    st.info("Please make sure you executed the getpass cell inside your notebook before running the server.")
    st.stop()

# -----------------------------------------------------------------------------
# 2. FIXED DATA STRUCTURES (Removing raw Dicts to avoid additionalProperties)
# -----------------------------------------------------------------------------
class StakeholderImpact(BaseModel):
    impact_nature: str  # "Positive", "Negative", or "Neutral"
    summary: str
    action_items: list[str]

class StakeholderMatrix(BaseModel):
    students: StakeholderImpact
    faculty: StakeholderImpact
    administrators: StakeholderImpact
    compliance_teams: StakeholderImpact

class TimeframeAnalysis(BaseModel):
    compliance_demands: str
    risk_level: str     # "Low", "Medium", or "High"

class ImpactForecast(BaseModel):
    short_term: TimeframeAnalysis
    medium_term: TimeframeAnalysis
    long_term: TimeframeAnalysis

class PolicyChronology(BaseModel):
    predecessor_circulars: list[str]
    historical_context: str

class RegulationAnalysisSchema(BaseModel):
    topic_category: str 
    plain_english_summary: str
    positives: list[str]
    negatives: list[str]
    stakeholder_matrix: StakeholderMatrix  # Swapped from dict to explicit sub-model
    impact_forecast: ImpactForecast        # Swapped from dict to explicit sub-model
    chronology: PolicyChronology
    institutional_burden_score: int                 

# -----------------------------------------------------------------------------
# 3. WORKSPACE UI RENDERING
# -----------------------------------------------------------------------------
st.set_page_config(page_title="ERIA Workspace", page_icon="🎓", layout="wide")
st.title("🎓 Education Regulation Impact Analyzer (ERIA)")
st.caption("Simplifying regulatory structures using structured multimodality.")

uploaded_file = st.sidebar.file_uploader("Upload Official Regulation PDF", type=["pdf"])
#llm_model = st.sidebar.selectbox("LLM Processing Engine", ["gemini-2.5-flash", "gemini-2.5-pro"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    with st.spinner("🚀 ERIA Engine compiling extraction targets..."):
        try:
            # We transform the Pydantic class to a raw schema dictionary to prevent additionalProperties conflicts
            raw_json_schema = RegulationAnalysisSchema.model_json_schema()

            response = client.models.generate_content(
                #model=llm_model,
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=file_bytes, mime_type="application/pdf"),
                    "Analyze this education circular. Classify its category, extract historical context, map persona impacts, and grade compliance burden."
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=raw_json_schema,  # Passing the generated structural map directly
                    temperature=0.1
                ),
            )
            analysis_data = json.loads(response.text)
            st.success("Analysis complete!")
            from pdf_generator import generate_policy_pdf
            # DOWNLOAD UTILITY LAYER
            # -------------------------------------------------------------------------
            try:
                # Compile your layout bytes out of the pipeline data map
                pdf_bytes = generate_policy_pdf(analysis_data)

                st.sidebar.markdown("---")
                st.sidebar.markdown("### 📤 Export Artifact Workspace")
                st.sidebar.download_button(
                label="📥 Download Structured PDF Report",
                data=pdf_bytes,
                file_name=f"ERIA_Analysis_{analysis_data.get('topic_category', 'Regulation')}.pdf",
                mime="application/pdf",
                use_container_width=True
                )
                st.sidebar.caption("Generates a print-ready document with custom page counts and compliance headers.")
            except Exception as pdf_error:
                                        st.sidebar.warning(f"Export engine initialization paused: {pdf_error}")

            # Workspace Presentation
            col1, col2 = st.columns([3, 1])
            with col1:
                st.metric("Topic Classification", analysis_data['topic_category'])
                st.markdown("### 📝 Plain-English Summary")
                st.info(analysis_data['plain_english_summary'])
            with col2:
                st.metric("Institutional Burden Score", f"{analysis_data['institutional_burden_score']}/10")

            st.markdown("---")

            # Positives and Negatives Section
            col_pos, col_neg = st.columns(2)
            with col_pos:
                st.markdown("### 👍 Positives & Opportunities")
                for item in analysis_data.get('positives', []):
                    st.markdown(f"- {item}")
            with col_neg:
                st.markdown("### ⚠️ Challenges & Constraints")
                for item in analysis_data.get('negatives', []):
                    st.markdown(f"- {item}")

            st.markdown("---")
            st.markdown("### ⏳ Policy Chronology Background")
            st.write(analysis_data['chronology']['historical_context'])

            # Stakeholder Matrix Visualization Layer
            st.markdown("## 👥 Persona-Based Stakeholder Matrix")
            tabs = st.tabs(["Students", "Faculty Members", "Academic Administrators", "Accreditation Teams"])
            matrix = analysis_data.get('stakeholder_matrix', {})

            stakeholder_mapping = {
                "Students": matrix.get('students'),
                "Faculty Members": matrix.get('faculty'),
                "Academic Administrators": matrix.get('administrators'),
                "Accreditation Teams": matrix.get('compliance_teams')
            }

            for tab_name, tab_view in zip(stakeholder_mapping.keys(), tabs):
                data = stakeholder_mapping[tab_name]
                with tab_view:
                    if data:
                        if data['impact_nature'] == "Positive":
                            st.success("Impact Nature: Positive / Opportunity-Rich")
                        elif data['impact_nature'] == "Negative":
                            st.error("Impact Nature: High Constraints / Action Needed")
                        else:
                            st.warning("Impact Nature: Neutral / General Operational Adjustment")
                        st.markdown(f"**Summary:** {data['summary']}")
                        st.markdown("**Required Action Checklist:**")
                        for action in data.get('action_items', []):
                            st.checkbox(action, key=f"chk_{tab_name[:3]}_{action[:20]}")
                    else:
                        st.caption("No specific modifications extracted for this target workspace profile.")

        except Exception as error:
            st.error(f"Execution Error: {error}")
