import os
import sys

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from src.risk.ai_copilot import ask_creditwise
from src.risk.copilot import build_copilot_context
# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CreditWise AI",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.models.scoring import score_applicant
DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
OUTPUT_DIR = os.path.join(DATA_DIR, "outputs")


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_cleaned_data():

    path = os.path.join(
        PROCESSED_DIR,
        "creditwise_cleaned.csv"
    )

    return pd.read_csv(path)


@st.cache_data
def load_risk_simulation():

    path = os.path.join(
        OUTPUT_DIR,
        "applicant_risk_simulation.csv"
    )

    return pd.read_csv(path)


@st.cache_data
def load_risk_summary():

    path = os.path.join(
        OUTPUT_DIR,
        "risk_segment_simulation.csv"
    )

    return pd.read_csv(path)


@st.cache_data
def load_policy_scenarios():

    path = os.path.join(
        OUTPUT_DIR,
        "risk_policy_scenarios.csv"
    )

    return pd.read_csv(path)


@st.cache_data
def load_model_comparison():

    path = os.path.join(
        OUTPUT_DIR,
        "model_comparison.csv"
    )

    return pd.read_csv(path)


@st.cache_data
def load_monitoring():

    path = os.path.join(
        OUTPUT_DIR,
        "model_monitoring_metrics.csv"
    )

    return pd.read_csv(path)


@st.cache_data
def load_shap_importance():

    path = os.path.join(
        OUTPUT_DIR,
        "shap_feature_importance.csv"
    )

    return pd.read_csv(path)


# ============================================================
# LOAD EVERYTHING
# ============================================================

df = load_cleaned_data()
risk_df = load_risk_simulation()
risk_summary = load_risk_summary()
policy_df = load_policy_scenarios()
model_comparison = load_model_comparison()
monitoring_df = load_monitoring()
shap_importance = load_shap_importance()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("💳 CreditWise AI")

st.sidebar.caption(
    "Credit Risk & Lending Intelligence Platform"
)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Executive Dashboard",
        "📊 Portfolio Analytics",
        "⚠️ Risk & Exposure",
        "🤖 Model Intelligence",
        "👤 Applicant Explorer",
        "💬 AI Risk Copilot"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    """
    **Important**

    Historical `approved` is an approval outcome,
    not a repayment/default target.

    Risk segments and policy scenarios are
    hypothetical simulations.
    """
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_currency(value):

    if pd.isna(value):
        return "₹0"

    value = float(value)

    if abs(value) >= 10_000_000:
        return f"₹{value / 10_000_000:.2f} Cr"

    if abs(value) >= 1_000_000:
        return f"₹{value / 1_000_000:.2f}M"

    return f"₹{value:,.0f}"


def format_percent(value):

    return f"{value:.2f}%"


# ============================================================
# PAGE 1 — EXECUTIVE DASHBOARD
# ============================================================

if page == "🏠 Executive Dashboard":

    st.title("💳 CreditWise AI")
    st.subheader(
        "Credit Risk & Lending Intelligence Platform"
    )

    st.caption(
        "Historical portfolio analytics, model intelligence, "
        "explainability and hypothetical risk simulation"
    )

    st.markdown("---")

    # -------------------------
    # KPIs
    # -------------------------

    total_applications = len(df)

    approval_rate = (
        df["approved"].mean() * 100
    )

    avg_credit_score = (
        df["credit_score"].mean()
    )

    avg_dti = (
        df["debt_to_income_ratio"].mean() * 100
    )

    total_exposure = (
        df["requested_credit_limit"].sum()
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Applications",
        f"{total_applications:,}"
    )

    col2.metric(
        "Historical Approval Rate",
        f"{approval_rate:.2f}%"
    )

    col3.metric(
        "Average Credit Score",
        f"{avg_credit_score:.1f}"
    )

    col4.metric(
        "Average DTI",
        f"{avg_dti:.2f}%"
    )

    col5.metric(
        "Requested Exposure",
        format_currency(total_exposure)
    )

    st.markdown("---")

    # -------------------------
    # Approval Distribution
    # -------------------------

    col1, col2 = st.columns(2)

    with col1:

        approval_data = pd.DataFrame({
            "Outcome": [
                "Historical Non-Approval",
                "Historical Approval"
            ],
            "Applications": [
                (df["approved"] == 0).sum(),
                (df["approved"] == 1).sum()
            ]
        })

        fig = px.pie(
            approval_data,
            names="Outcome",
            values="Applications",
            title="Historical Application Outcomes",
            hole=0.45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -------------------------
    # Risk Distribution
    # -------------------------

    with col2:

        fig = px.bar(
            risk_summary,
            x="risk_segment",
            y="applications",
            title="Applications by Hypothetical Risk Segment",
            text="applications"
        )

        fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -------------------------
    # Quick Insights
    # -------------------------

    st.markdown("### 🔎 Portfolio Snapshot")

    high_count = int(
        risk_df["risk_segment"]
        .eq("High Indicator")
        .sum()
    )

    st.write(
        f"""
        - The portfolio contains **{total_applications:,} applications**.
        - Historical approval rate is **{approval_rate:.2f}%**.
        - Average credit score is **{avg_credit_score:.1f}**.
        - Average DTI is **{avg_dti:.2f}%**.
        - Total requested credit exposure is **{format_currency(total_exposure)}**.
        - The hypothetical **High Indicator** segment contains **{high_count:,} applications**.
        """
    )


# ============================================================
# PAGE 2 — PORTFOLIO ANALYTICS
# ============================================================

elif page == "📊 Portfolio Analytics":

    st.title("📊 Portfolio Analytics")

    # -------------------------
    # Product Analysis
    # -------------------------

    st.subheader("Product Distribution")

    product_summary = (
        df.groupby("product_type")
        .agg(
            Applications=("applicant_id", "count"),
            Historical_Approval_Rate=("approved", "mean")
        )
        .reset_index()
    )

    product_summary[
        "Historical_Approval_Rate"
    ] *= 100

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            product_summary,
            x="product_type",
            y="Applications",
            title="Applications by Product",
            text="Applications"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        fig = px.bar(
            product_summary,
            x="product_type",
            y="Historical_Approval_Rate",
            title="Historical Approval Rate by Product",
            text="Historical_Approval_Rate"
        )

        fig.update_traces(
            texttemplate="%{text:.2f}%"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -------------------------
    # Income
    # -------------------------

    st.subheader("Income Analysis")

    income_summary = (
        df.groupby("income_band")
        .agg(
            Applications=("applicant_id", "count"),
            Historical_Approval_Rate=("approved", "mean")
        )
        .reset_index()
    )

    income_summary[
        "Historical_Approval_Rate"
    ] *= 100

    fig = px.bar(
        income_summary,
        x="income_band",
        y="Historical_Approval_Rate",
        title="Historical Approval Rate by Income Band",
        text="Historical_Approval_Rate"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -------------------------
    # DTI
    # -------------------------

    st.subheader("Debt-to-Income Analysis")

    dti_summary = (
        df.groupby("dti_band")
        .agg(
            Applications=("applicant_id", "count"),
            Historical_Approval_Rate=("approved", "mean")
        )
        .reset_index()
    )

    dti_summary[
        "Historical_Approval_Rate"
    ] *= 100

    fig = px.bar(
        dti_summary,
        x="dti_band",
        y="Historical_Approval_Rate",
        title="Historical Approval Rate by DTI Band",
        text="Historical_Approval_Rate"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# PAGE 3 — RISK & EXPOSURE
# ============================================================

elif page == "⚠️ Risk & Exposure":

    st.title("⚠️ Risk & Exposure Intelligence")

    st.warning(
        "Risk segments and policy scenarios shown here "
        "are hypothetical simulations, not default predictions "
        "or actual lending policies."
    )

    # -------------------------
    # Risk summary
    # -------------------------

    st.subheader("Hypothetical Risk Segments")

    display_risk = risk_summary.copy()

    display_risk[
        "total_requested_exposure"
    ] = display_risk[
        "total_requested_exposure"
    ].round(2)

    display_risk[
        "exposure_share_percent"
    ] = display_risk[
        "exposure_share_percent"
    ].round(2)

    st.dataframe(
        display_risk,
        use_container_width=True,
        hide_index=True
    )

    # -------------------------
    # Exposure chart
    # -------------------------

    fig = px.bar(
        risk_summary,
        x="risk_segment",
        y="total_requested_exposure",
        title="Requested Exposure by Hypothetical Risk Segment",
        text="exposure_share_percent"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -------------------------
    # Policy scenarios
    # -------------------------

    st.subheader(
        "Hypothetical Screening Scenarios"
    )

    scenario_display = policy_df.copy()

    scenario_display[
        "Requested Exposure"
    ] = scenario_display[
        "Requested Exposure"
    ].map(format_currency)

    st.dataframe(
        scenario_display,
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        policy_df,
        x="Scenario",
        y="Eligible Applications",
        title="Eligible Applications Under Hypothetical Scenarios",
        text="Eligible Applications"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig = px.bar(
        policy_df,
        x="Scenario",
        y="Requested Exposure",
        title="Requested Exposure Under Hypothetical Scenarios",
        text="Requested Exposure"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# PAGE 4 — MODEL INTELLIGENCE
# ============================================================

elif page == "🤖 Model Intelligence":

    st.title("🤖 Model Intelligence")

    st.subheader("Model Comparison")

    comparison_display = model_comparison.copy()

    numeric_cols = [
        "Accuracy",
        "Precision",
        "Recall",
        "F1",
        "ROC_AUC",
        "PR_AUC"
    ]

    for col in numeric_cols:

        if col in comparison_display.columns:

            comparison_display[col] = (
                comparison_display[col].round(4)
            )

    st.dataframe(
        comparison_display,
        use_container_width=True,
        hide_index=True
    )

    # -------------------------
    # ROC-AUC comparison
    # -------------------------

    fig = px.bar(
        model_comparison,
        x="Model",
        y="ROC_AUC",
        title="ROC-AUC Comparison",
        text="ROC_AUC"
    )

    fig.update_traces(
        texttemplate="%{text:.4f}"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -------------------------
    # Monitoring
    # -------------------------

    st.subheader(
        "Current Model Monitoring Snapshot"
    )

    monitoring_display = monitoring_df.copy()

    monitoring_display["Value"] = (
        monitoring_display["Value"].round(4)
    )

    st.dataframe(
        monitoring_display,
        use_container_width=True,
        hide_index=True
    )

    # -------------------------
    # SHAP
    # -------------------------

    st.subheader(
        "Global SHAP Feature Importance"
    )

    top_shap = (
        shap_importance
        .sort_values(
            "Mean_Absolute_SHAP",
            ascending=False
        )
        .head(15)
        .sort_values(
            "Mean_Absolute_SHAP"
        )
    )

    fig = px.bar(
        top_shap,
        x="Mean_Absolute_SHAP",
        y="Feature",
        orientation="h",
        title="Top Model Features by Mean Absolute SHAP"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(
        "SHAP magnitude indicates how strongly a feature "
        "influences model output on average. It does not by "
        "itself indicate the direction of the effect."
    )


# ============================================================
# PAGE 5 — APPLICANT EXPLORER
# ============================================================

elif page == "👤 Applicant Explorer":

    st.title("👤 Applicant Risk Explorer")

    st.caption(
        "Interactive applicant analysis using the trained "
        "CreditWise Logistic Regression model."
    )

    # --------------------------------------------------------
    # SELECT APPLICANT
    # --------------------------------------------------------

    applicant_ids = (
        df["applicant_id"]
        .astype(str)
        .tolist()
    )

    selected_id = st.selectbox(
        "Select Applicant",
        applicant_ids
    )

    applicant = df[
        df["applicant_id"].astype(str)
        == selected_id
    ].iloc[0]

    applicant_df = applicant.to_frame().T

    # --------------------------------------------------------
    # REAL ML PREDICTION
    # --------------------------------------------------------

    prediction, probability, processed_features = (
        score_applicant(applicant_df)
    )

    probability_percent = probability * 100

    # Get risk information
    risk_record = risk_df[
        risk_df["applicant_id"]
        == applicant["applicant_id"]
    ].iloc[0]

    st.markdown("---")

    # --------------------------------------------------------
    # MODEL RESULT
    # --------------------------------------------------------

    st.subheader("🤖 Model Prediction")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Historical Approval Probability",
        f"{probability_percent:.2f}%"
    )

    col2.metric(
        "Predicted Historical Outcome",
        "Approved"
        if prediction == 1
        else "Not Approved"
    )

    col3.metric(
        "Risk Indicators",
        int(risk_record["risk_indicator_count"])
    )

    st.info(
        "This model predicts the historical approval outcome "
        "represented by the dataset. It does not predict "
        "default or repayment failure."
    )

    # --------------------------------------------------------
    # PROBABILITY GAUGE
    # --------------------------------------------------------

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=probability_percent,
            title={
                "text":
                "Probability of Historical Approval"
            },
            gauge={
                "axis": {
                    "range": [0, 100]
                }
            }
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # APPLICANT PROFILE
    # --------------------------------------------------------

    st.subheader("📋 Applicant Profile")

    profile = pd.DataFrame({
        "Metric": [
            "Applicant ID",
            "Annual Income",
            "Credit Score",
            "DTI",
            "Credit Utilization",
            "Years Employed",
            "Late Payments - 24 Months",
            "Monthly Debt Obligation",
            "Disposable Income",
            "Requested Credit Limit",
            "Product Type"
        ],
        "Value": [
            applicant["applicant_id"],
            format_currency(
                applicant["annual_income"]
            ),
            f"{applicant['credit_score']:.0f}",
            f"{applicant['debt_to_income_ratio'] * 100:.2f}%",
            f"{applicant['credit_utilization_ratio'] * 100:.2f}%",
            f"{applicant['years_employed']:.1f}",
            int(applicant["late_payments_24m"]),
            format_currency(
                applicant["monthly_debt_obligation"]
            ),
            format_currency(
                applicant["disposable_income"]
            ),
            format_currency(
                applicant["requested_credit_limit"]
            ),
            applicant["product_type"]
        ]
    })

    st.dataframe(
        profile,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # HYPOTHETICAL RISK INDICATORS
    # --------------------------------------------------------

    st.subheader(
        "⚠️ Hypothetical Risk Indicators"
    )

    flags = {
        "High DTI":
            risk_record["dti_flag"],

        "High Utilization":
            risk_record["utilization_flag"],

        "Multiple Late Payments":
            risk_record["late_payment_flag"],

        "Low Credit Score":
            risk_record["credit_score_flag"]
    }

    for name, value in flags.items():

        if value == 1:

            st.warning(
                f"⚠️ {name}"
            )

        else:

            st.success(
                f"✓ {name}: not triggered"
            )

    # --------------------------------------------------------
    # RISK SEGMENT
    # --------------------------------------------------------

    st.subheader("Risk Indicator Segment")

    segment = risk_record["risk_segment"]

    if segment == "High Indicator":

        st.error(
            f"Hypothetical segment: **{segment}**"
        )

    elif segment == "Moderate Indicator":

        st.warning(
            f"Hypothetical segment: **{segment}**"
        )

    else:

        st.success(
            f"Hypothetical segment: **{segment}**"
        )

    st.caption(
        "Risk segments are hypothetical screening indicators "
        "created for this project. They are not default "
        "predictions or actual lending policies."
    )
    # ========================================================
    # SHAP EXPLAINABILITY
    # ========================================================

    st.markdown("---")

    st.subheader("🧠 Why Did the Model Make This Prediction?")

    st.caption(
        "SHAP shows how each feature influenced the model's "
        "historical approval prediction for this applicant."
    )

    try:

        from src.models.explainability import (
            explain_applicant
        )

        shap_df = explain_applicant(
            applicant_df
        )

        # Top 10 features
        top_shap = shap_df.head(10).copy()

        # Display-friendly names
        top_shap["feature_display"] = (
            top_shap["feature"]
            .str.replace("num_", "", regex=False)
            .str.replace("cat_", "", regex=False)
            .str.replace("_", " ", regex=False)
            .str.title()
        )

        # Positive / negative influence
        top_shap["impact"] = np.select(
        [
            top_shap["shap_value"] > 0.0001,
            top_shap["shap_value"] < -0.0001
        ],
        [
            "Increases historical approval",
            "Decreases historical approval"
        ],
        default="Minimal / neutral influence"
    )

        # ----------------------------------------------------
        # SHAP BAR CHART
        # ----------------------------------------------------
        fig_shap = px.bar(
            top_shap.sort_values("shap_value"),
            x="shap_value",
            y="feature_display",
            orientation="h",
            title="Top Features Influencing This Prediction",
            labels={
                "shap_value": "SHAP Impact",
                "feature_display": "Feature"
            }
        )

        fig_shap.add_vline(
            x=0,
            line_width=1
        )

        fig_shap.update_layout(
            height=500,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )
        )

        st.plotly_chart(
            fig_shap,
            use_container_width=True
        )
        

        # ----------------------------------------------------
        # SHAP TABLE
        # ----------------------------------------------------

        display_shap = top_shap[
            [
                "feature_display",
                "shap_value",
                "impact"
            ]
        ].copy()

        display_shap.columns = [
            "Feature",
            "SHAP Impact",
            "Model Influence"
        ]

        display_shap["SHAP Impact"] = (
            display_shap["SHAP Impact"]
            .round(4)
        )

        st.dataframe(
            display_shap,
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # SIMPLE EXPLANATION
        # ----------------------------------------------------

        positive_features = (
            top_shap[
                top_shap["shap_value"] > 0.0001
            ]
            .head(3)
            ["feature_display"]
            .tolist()
        )

        negative_features = (
            top_shap[
                top_shap["shap_value"] < -0.0001
            ]
            .head(3)
            ["feature_display"]
            .tolist()
        )

        if positive_features:
            st.success(
                "Features pushing the model toward "
                "historical approval: "
                + ", ".join(positive_features)
            )

        if negative_features:
            st.warning(
                "Features pushing the model toward "
                "historical non-approval: "
                + ", ".join(negative_features)
            )

        st.caption(
            "SHAP values describe model influence, not "
            "causation. Because this dataset contains "
            "synthetically enriched variables, these "
            "relationships should not be interpreted as "
            "real-world lending causality."
        )

    except Exception as e:

        st.error(
            f"SHAP explanation could not be generated: {e}"
        )
# ============================================================
# PAGE 6 — AI RISK COPILOT
# ============================================================

elif page == "💬 AI Risk Copilot":

    st.title("💬 CreditWise AI Risk Copilot")

    st.caption(
        "Ask questions about an applicant's model prediction, "
        "risk indicators, and explainability."
    )

    # --------------------------------------------------------
    # SELECT APPLICANT
    # --------------------------------------------------------

    applicant_ids = (
        df["applicant_id"]
        .astype(str)
        .tolist()
    )

    selected_id = st.selectbox(
        "Select Applicant",
        applicant_ids,
        key="copilot_applicant"
    )

    applicant = df[
        df["applicant_id"].astype(str)
        == selected_id
    ].iloc[0]

    applicant_df = applicant.to_frame().T

    # --------------------------------------------------------
    # MODEL SCORE
    # --------------------------------------------------------

    prediction, probability, processed = (
        score_applicant(
            applicant_df
        )
    )

    # --------------------------------------------------------
    # RISK RECORD
    # --------------------------------------------------------

    risk_record = risk_df[
        risk_df["applicant_id"]
        == applicant["applicant_id"]
    ].iloc[0]

    # --------------------------------------------------------
    # SHAP
    # --------------------------------------------------------

    from src.models.explainability import (
        explain_applicant
    )

    shap_df = explain_applicant(
        applicant_df
    )

    # --------------------------------------------------------
    # QUESTION
    # --------------------------------------------------------

    question = st.text_input(
        "Ask CreditWise",
        placeholder=(
            "Example: Why was this applicant "
            "predicted this way?"
        )
    )

    if st.button(
    "🔍 Analyze",
    use_container_width=True
):

     if question.strip():

        # Build verified CreditWise context
        context = build_copilot_context(
            applicant,
            prediction,
            probability,
            risk_record,
            shap_df
        )

        # Ask Gemini
        with st.spinner("🤖 CreditWise AI is analyzing..."):

            try:

                answer = ask_creditwise(
                    question,
                    context
                )

                st.markdown(
                    "### 🤖 CreditWise AI Analysis"
                )

                st.markdown(answer)

            except Exception as e:

                st.error(
                    f"CreditWise AI error: {e}"
                )

    else:

        st.warning(
            "Please enter a question."
        )

else:

            st.warning(
                "Please enter a question."
            )

    # --------------------------------------------------------
    # EXAMPLE QUESTIONS
    # --------------------------------------------------------

st.markdown("---")

st.subheader("💡 Try asking")

st.markdown(
        """
        - **Why was this applicant predicted this way?**
        - **What are the main risk factors?**
        - **Summarize this applicant**
        - **Explain the model prediction**
        """
    )

st.info(
        "CreditWise Copilot uses the project's actual model "
        "outputs and SHAP explanations. It does not make "
        "real lending decisions."
    )