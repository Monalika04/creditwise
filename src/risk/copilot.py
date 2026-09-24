import pandas as pd
import numpy as np


def format_currency(value):
    return f"₹{value:,.0f}"


def generate_applicant_context(
    applicant,
    prediction,
    probability,
    risk_record,
    shap_df
):

    outcome = (
        "historical approval"
        if prediction == 1
        else "historical non-approval"
    )

    probability_percent = probability * 100

    # --------------------------------------------------------
    # SHAP
    # --------------------------------------------------------

    positive = (
        shap_df[
            shap_df["shap_value"] > 0.0001
        ]
        .head(5)
    )

    negative = (
        shap_df[
            shap_df["shap_value"] < -0.0001
        ]
        .head(5)
    )

    positive_features = (
        positive["feature"]
        .tolist()
    )

    negative_features = (
        negative["feature"]
        .tolist()
    )

    # --------------------------------------------------------
    # RISK FLAGS
    # --------------------------------------------------------

    risk_flags = []

    if risk_record["dti_flag"] == 1:
        risk_flags.append(
            "High debt-to-income ratio"
        )

    if risk_record["utilization_flag"] == 1:
        risk_flags.append(
            "High credit utilization"
        )

    if risk_record["late_payment_flag"] == 1:
        risk_flags.append(
            "Multiple recent late payments"
        )

    if risk_record["credit_score_flag"] == 1:
        risk_flags.append(
            "Low credit score"
        )

    if not risk_flags:
        risk_flags.append(
            "No major hypothetical risk indicators triggered"
        )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = f"""
CREDITWISE APPLICANT CONTEXT

Applicant ID:
{applicant['applicant_id']}

MODEL RESULT
Predicted historical outcome:
{outcome}

Model probability of historical approval:
{probability_percent:.2f}%

IMPORTANT:
This is a historical approval model.
It is NOT a default prediction.
The probability is a model output and has not been
calibrated as a real-world lending probability.

APPLICANT PROFILE

Annual income:
{format_currency(applicant['annual_income'])}

Credit score:
{applicant['credit_score']:.0f}

Debt-to-income ratio:
{applicant['debt_to_income_ratio'] * 100:.2f}%

Credit utilization:
{applicant['credit_utilization_ratio'] * 100:.2f}%

Years employed:
{applicant['years_employed']:.1f}

Credit history:
{applicant['credit_history_months']} months

Late payments in last 24 months:
{applicant['late_payments_24m']}

Existing credit lines:
{applicant['existing_credit_lines']}

Disposable income:
{format_currency(applicant['disposable_income'])}

Requested credit limit:
{format_currency(applicant['requested_credit_limit'])}

Product:
{applicant['product_type']}

HYPOTHETICAL RISK INDICATORS

Risk segment:
{risk_record['risk_segment']}

Risk indicator count:
{risk_record['risk_indicator_count']}

Risk flags:
{', '.join(risk_flags)}

SHAP MODEL INFLUENCES

Features pushing the model toward historical approval:
{', '.join(positive_features)}

Features pushing the model toward historical non-approval:
{', '.join(negative_features)}
"""

    return context


def answer_question(
    question,
    applicant,
    prediction,
    probability,
    risk_record,
    shap_df
):

    question = question.lower().strip()

    outcome = (
        "historical approval"
        if prediction == 1
        else "historical non-approval"
    )

    probability_percent = probability * 100

    # --------------------------------------------------------
    # WHY
    # --------------------------------------------------------

    if (
        "why" in question
        or "reason" in question
        or "explain" in question
    ):

        positive = (
            shap_df[
                shap_df["shap_value"] > 0.0001
            ]
            .head(3)
        )

        negative = (
            shap_df[
                shap_df["shap_value"] < -0.0001
            ]
            .head(3)
        )

        answer = (
            f"The model predicts {outcome} "
            f"with a historical approval probability "
            f"of {probability_percent:.2f}%.\n\n"
        )

        if len(positive) > 0:

            answer += (
                "**Factors pushing toward historical approval:**\n"
            )

            for _, row in positive.iterrows():

                answer += (
                    f"- {row['feature']}: "
                    f"SHAP {row['shap_value']:.3f}\n"
                )

        if len(negative) > 0:

            answer += (
                "\n**Factors pushing toward historical "
                "non-approval:**\n"
            )

            for _, row in negative.iterrows():

                answer += (
                    f"- {row['feature']}: "
                    f"SHAP {row['shap_value']:.3f}\n"
                )

        return answer

    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    if "risk" in question:

        flags = []

        if risk_record["dti_flag"] == 1:
            flags.append(
                "High debt-to-income ratio"
            )

        if risk_record["utilization_flag"] == 1:
            flags.append(
                "High credit utilization"
            )

        if risk_record["late_payment_flag"] == 1:
            flags.append(
                "Multiple late payments"
            )

        if risk_record["credit_score_flag"] == 1:
            flags.append(
                "Low credit score"
            )

        if not flags:

            return (
                "No major hypothetical risk indicators "
                "were triggered for this applicant."
            )

        return (
            "**Hypothetical risk indicators:**\n\n"
            + "\n".join(
                f"- {flag}"
                for flag in flags
            )
        )

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    if (
        "profile" in question
        or "summary" in question
        or "summarize" in question
    ):

        return f"""
### Applicant Summary

**Applicant:** {applicant['applicant_id']}

**Model outcome:** {outcome}

**Historical approval probability:** {probability_percent:.2f}%

**Credit score:** {applicant['credit_score']:.0f}

**DTI:** {applicant['debt_to_income_ratio'] * 100:.2f}%

**Credit utilization:** {applicant['credit_utilization_ratio'] * 100:.2f}%

**Annual income:** {format_currency(applicant['annual_income'])}

**Requested credit limit:** {format_currency(applicant['requested_credit_limit'])}

**Risk segment:** {risk_record['risk_segment']}

This summary describes the dataset, model output,
and hypothetical risk indicators. It does not represent
a real lending decision.
"""

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    return f"""
I can analyze this applicant using:

• Model prediction
• Historical approval probability
• SHAP explanations
• Hypothetical risk indicators
• Applicant financial profile

Try asking:

**"Why was this applicant predicted this way?"**

or

**"What are the main risk factors?"**

or

**"Summarize this applicant."**
"""


def build_copilot_context(
    applicant,
    prediction,
    probability,
    risk_record,
    shap_df
):

    outcome = (
        "historical approval"
        if prediction == 1
        else "historical non-approval"
    )

    positive = (
        shap_df[
            shap_df["shap_value"] > 0.0001
        ]
        .head(5)
    )

    negative = (
        shap_df[
            shap_df["shap_value"] < -0.0001
        ]
        .head(5)
    )

    positive_text = "\n".join(
        [
            f"- {row['feature']}: "
            f"{row['shap_value']:.4f}"
            for _, row in positive.iterrows()
        ]
    )

    negative_text = "\n".join(
        [
            f"- {row['feature']}: "
            f"{row['shap_value']:.4f}"
            for _, row in negative.iterrows()
        ]
    )

    context = f"""
Applicant ID:
{applicant['applicant_id']}

MODEL OUTPUT

Historical outcome prediction:
{outcome}

Historical approval probability:
{probability * 100:.2f}%

APPLICANT FACTS

Annual income:
₹{applicant['annual_income']:,.0f}

Credit score:
{applicant['credit_score']:.0f}

Debt-to-income ratio:
{applicant['debt_to_income_ratio'] * 100:.2f}%

Credit utilization:
{applicant['credit_utilization_ratio'] * 100:.2f}%

Years employed:
{applicant['years_employed']:.1f}

Credit history:
{applicant['credit_history_months']} months

Late payments in previous 24 months:
{applicant['late_payments_24m']}

Existing credit lines:
{applicant['existing_credit_lines']}

Disposable income:
₹{applicant['disposable_income']:,.0f}

Requested credit limit:
₹{applicant['requested_credit_limit']:,.0f}

Product:
{applicant['product_type']}

HYPOTHETICAL RISK INDICATORS

Risk segment:
{risk_record['risk_segment']}

Risk indicator count:
{risk_record['risk_indicator_count']}

DTI flag:
{risk_record['dti_flag']}

Utilization flag:
{risk_record['utilization_flag']}

Late payment flag:
{risk_record['late_payment_flag']}

Credit score flag:
{risk_record['credit_score_flag']}

SHAP INFLUENCES

Positive model influences:
{positive_text}

Negative model influences:
{negative_text}
"""

    return context