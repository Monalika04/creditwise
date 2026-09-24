DROP TABLE IF EXISTS staging.credit_applications;

CREATE TABLE staging.credit_applications AS
SELECT
    applicant_id,
    TRIM(gender) AS gender,
    age,
    num_children,
    family_size,
    TRIM(family_status) AS family_status,
    TRIM(education_type) AS education_type,
    TRIM(housing_type) AS housing_type,
    TRIM(own_car) AS own_car,
    TRIM(own_property) AS own_property,
    TRIM(income_type) AS income_type,
    TRIM(occupation_type) AS occupation_type,

    annual_income,
    years_employed,
    credit_history_months,
    existing_credit_lines,
    debt_to_income_ratio,
    late_payments_24m,

    has_email,
    has_work_phone,

    approved,

    application_date,
    TRIM(product_type) AS product_type,
    requested_credit_limit,
    TRIM(application_channel) AS application_channel,
    TRIM(application_purpose) AS application_purpose,

    monthly_debt_obligation,
    monthly_expenses,
    total_outstanding_debt,
    current_credit_limit,
    current_credit_balance,

    credit_score,

    monthly_income,
    disposable_income,
    credit_utilization_ratio,
    total_credit_exposure,

    TRIM(income_band) AS income_band,
    TRIM(dti_band) AS dti_band,
    TRIM(credit_history_band) AS credit_history_band,
    TRIM(employment_band) AS employment_band,
    TRIM(payment_risk_indicator) AS payment_risk_indicator,

    synthetic_enrichment,
    synthetic_version

FROM raw.credit_applications;


SELECT COUNT(*) AS staging_rows
FROM staging.credit_applications;


-- PART B — STAGING DATA QUALITY

SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT applicant_id) AS unique_applicants
FROM staging.credit_applications;


-- 4. Check missing values

SELECT
    COUNT(*) FILTER (WHERE occupation_type IS NULL) AS missing_occupation,
    COUNT(*) FILTER (WHERE years_employed IS NULL) AS missing_employment,
    COUNT(*) FILTER (WHERE own_car IS NULL) AS missing_car
FROM staging.credit_applications;


-- 5. Validate credit score

SELECT COUNT(*) AS invalid_credit_scores
FROM staging.credit_applications
WHERE credit_score < 300
   OR credit_score > 850;


-- 6. Validate DTI


SELECT COUNT(*) AS invalid_dti
FROM staging.credit_applications
WHERE debt_to_income_ratio < 0
   OR debt_to_income_ratio > 1;