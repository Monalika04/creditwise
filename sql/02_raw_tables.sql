CREATE SCHEMA raw;

CREATE SCHEMA staging;

CREATE SCHEMA warehouse;

CREATE SCHEMA analytics;



SELECT schema_name
FROM information_schema.schemata
WHERE schema_name IN (
    'raw',
    'staging',
    'warehouse',
    'analytics'
)
ORDER BY schema_name;

DROP TABLE IF EXISTS raw.credit_applications;

CREATE TABLE raw.credit_applications (
    applicant_id BIGINT,
    gender VARCHAR(20),
    age INT,
    num_children INT,
    family_size INT,
    family_status VARCHAR(50),
    education_type VARCHAR(100),
    housing_type VARCHAR(50),
    own_car VARCHAR(20),
    own_property VARCHAR(20),
    income_type VARCHAR(50),
    occupation_type VARCHAR(100),
    annual_income NUMERIC(14,2),
    years_employed NUMERIC(6,2),
    credit_history_months INT,
    existing_credit_lines INT,
    debt_to_income_ratio NUMERIC(8,4),
    late_payments_24m INT,
    has_email INT,
    has_work_phone INT,
    approved INT,
    application_date DATE,
    product_type VARCHAR(50),
    requested_credit_limit NUMERIC(14,2),
    application_channel VARCHAR(50),
    application_purpose VARCHAR(100),
    monthly_debt_obligation NUMERIC(14,2),
    monthly_expenses NUMERIC(14,2),
    total_outstanding_debt NUMERIC(14,2),
    current_credit_limit NUMERIC(14,2),
    current_credit_balance NUMERIC(14,2),
    credit_score INT,
    synthetic_enrichment INT,
    synthetic_version VARCHAR(20),
    monthly_income NUMERIC(14,2),
    disposable_income NUMERIC(14,2),
    credit_utilization_ratio NUMERIC(8,4),
    total_credit_exposure NUMERIC(14,2),
    income_band VARCHAR(30),
    dti_band VARCHAR(30),
    credit_history_band VARCHAR(30),
    employment_band VARCHAR(30),
    payment_risk_indicator VARCHAR(30),
    model_target_approval INT
);


SELECT COUNT(*)
FROM raw.credit_applications;


SELECT *
FROM raw.credit_applications
LIMIT 10;