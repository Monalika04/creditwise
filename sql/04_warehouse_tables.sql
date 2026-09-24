DROP TABLE IF EXISTS warehouse.dim_applicant CASCADE;

CREATE TABLE warehouse.dim_applicant (
    applicant_key BIGSERIAL PRIMARY KEY,
    applicant_id BIGINT UNIQUE NOT NULL,

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
    has_email INT,
    has_work_phone INT
);



INSERT INTO warehouse.dim_applicant (
    applicant_id,
    gender,
    age,
    num_children,
    family_size,
    family_status,
    education_type,
    housing_type,
    own_car,
    own_property,
    income_type,
    occupation_type,
    annual_income,
    years_employed,
    credit_history_months,
    existing_credit_lines,
    has_email,
    has_work_phone
)
SELECT DISTINCT
    applicant_id,
    gender,
    age,
    num_children,
    family_size,
    family_status,
    education_type,
    housing_type,
    own_car,
    own_property,
    income_type,
    occupation_type,
    annual_income,
    years_employed,
    credit_history_months,
    existing_credit_lines,
    has_email,
    has_work_phone
FROM staging.credit_applications;


SELECT COUNT(*)
FROM warehouse.dim_applicant;


-- products
DROP TABLE IF EXISTS warehouse.dim_product CASCADE;

CREATE TABLE warehouse.dim_product (
    product_key BIGSERIAL PRIMARY KEY,
    product_type VARCHAR(50) UNIQUE NOT NULL
);


INSERT INTO warehouse.dim_product (product_type)
SELECT DISTINCT product_type
FROM staging.credit_applications;


SELECT *
FROM warehouse.dim_product
ORDER BY product_key;

-- Create dim_date

DROP TABLE IF EXISTS warehouse.dim_date CASCADE;

CREATE TABLE warehouse.dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INT,
    quarter INT,
    month INT,
    month_name VARCHAR(20),
    day INT,
    day_of_week INT,
    day_name VARCHAR(20)
);


INSERT INTO warehouse.dim_date (
    date_key,
    full_date,
    year,
    quarter,
    month,
    month_name,
    day,
    day_of_week,
    day_name
)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INT AS date_key,
    d::DATE AS full_date,
    EXTRACT(YEAR FROM d)::INT,
    EXTRACT(QUARTER FROM d)::INT,
    EXTRACT(MONTH FROM d)::INT,
    TO_CHAR(d, 'Month'),
    EXTRACT(DAY FROM d)::INT,
    EXTRACT(ISODOW FROM d)::INT,
    TO_CHAR(d, 'Day')
FROM generate_series(
    '2025-01-01'::DATE,
    '2026-12-31'::DATE,
    '1 day'::INTERVAL
) AS d;


SELECT *
FROM warehouse.dim_date
LIMIT 10;

-- Create the FACT table

DROP TABLE IF EXISTS warehouse.fact_application CASCADE;

CREATE TABLE warehouse.fact_application (
    application_key BIGSERIAL PRIMARY KEY,

    applicant_key BIGINT NOT NULL,
    product_key BIGINT NOT NULL,
    application_date_key INT NOT NULL,

    requested_credit_limit NUMERIC(14,2),

    monthly_income NUMERIC(14,2),
    monthly_debt_obligation NUMERIC(14,2),
    monthly_expenses NUMERIC(14,2),
    disposable_income NUMERIC(14,2),

    total_outstanding_debt NUMERIC(14,2),
    current_credit_limit NUMERIC(14,2),
    current_credit_balance NUMERIC(14,2),

    credit_score INT,
    debt_to_income_ratio NUMERIC(8,4),
    credit_utilization_ratio NUMERIC(8,4),
    total_credit_exposure NUMERIC(14,2),

    existing_credit_lines INT,
    late_payments_24m INT,

    application_channel VARCHAR(50),
    application_purpose VARCHAR(100),

    income_band VARCHAR(30),
    dti_band VARCHAR(30),
    credit_history_band VARCHAR(30),
    employment_band VARCHAR(30),
    payment_risk_indicator VARCHAR(30),

    approved INT,

    CONSTRAINT fk_applicant
        FOREIGN KEY (applicant_key)
        REFERENCES warehouse.dim_applicant(applicant_key),

    CONSTRAINT fk_product
        FOREIGN KEY (product_key)
        REFERENCES warehouse.dim_product(product_key),

    CONSTRAINT fk_date
        FOREIGN KEY (application_date_key)
        REFERENCES warehouse.dim_date(date_key)
);

INSERT INTO warehouse.fact_application (
    applicant_key,
    product_key,
    application_date_key,

    requested_credit_limit,

    monthly_income,
    monthly_debt_obligation,
    monthly_expenses,
    disposable_income,

    total_outstanding_debt,
    current_credit_limit,
    current_credit_balance,

    credit_score,
    debt_to_income_ratio,
    credit_utilization_ratio,
    total_credit_exposure,

    existing_credit_lines,
    late_payments_24m,

    application_channel,
    application_purpose,

    income_band,
    dti_band,
    credit_history_band,
    employment_band,
    payment_risk_indicator,

    approved
)
SELECT
    a.applicant_key,
    p.product_key,
    d.date_key,

    s.requested_credit_limit,

    s.monthly_income,
    s.monthly_debt_obligation,
    s.monthly_expenses,
    s.disposable_income,

    s.total_outstanding_debt,
    s.current_credit_limit,
    s.current_credit_balance,

    s.credit_score,
    s.debt_to_income_ratio,
    s.credit_utilization_ratio,
    s.total_credit_exposure,

    s.existing_credit_lines,
    s.late_payments_24m,

    s.application_channel,
    s.application_purpose,

    s.income_band,
    s.dti_band,
    s.credit_history_band,
    s.employment_band,
    s.payment_risk_indicator,

    s.approved

FROM staging.credit_applications s

JOIN warehouse.dim_applicant a
    ON s.applicant_id = a.applicant_id

JOIN warehouse.dim_product p
    ON s.product_type = p.product_type

JOIN warehouse.dim_date d
    ON s.application_date = d.full_date;


SELECT COUNT(*) FROM staging.credit_applications;

SELECT COUNT(*) FROM warehouse.dim_applicant;

SELECT COUNT(*) FROM warehouse.dim_product;

SELECT COUNT(*) FROM warehouse.fact_application;