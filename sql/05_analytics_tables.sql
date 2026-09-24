-- PART 1 — PORTFOLIO OVERVIEW

-- Open your PostgreSQL Query Tool.

-- Query 1 — Basic portfolio KPIs

SELECT
    COUNT(*) AS total_applications,
    COUNT(DISTINCT applicant_key) AS unique_applicants,
    ROUND(AVG(approved) * 100, 2) AS approval_rate,
    ROUND(AVG(credit_score), 2) AS avg_credit_score,
    ROUND(AVG(debt_to_income_ratio) * 100, 2) AS avg_dti_pct,
    ROUND(AVG(credit_utilization_ratio) * 100, 2) AS avg_utilization_pct,
    ROUND(AVG(requested_credit_limit), 2) AS avg_requested_limit,
    ROUND(SUM(requested_credit_limit), 2) AS total_requested_exposure
FROM warehouse.fact_application;

-- ART 2 — APPROVAL ANALYSIS
-- Query 2 — Approved vs rejected 

SELECT
    approved,
    COUNT(*) AS applications,
    ROUND(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM warehouse.fact_application
GROUP BY approved
ORDER BY approved;

-- PART 3 — PRODUCT ANALYSIS
-- Query 3 — Approval by product

SELECT
    p.product_type,
    COUNT(*) AS applications,
    SUM(f.approved) AS approved_applications,
    ROUND(AVG(f.approved) * 100, 2) AS approval_rate,
    ROUND(AVG(f.requested_credit_limit), 2) AS avg_requested_limit
FROM warehouse.fact_application f
JOIN warehouse.dim_product p
    ON f.product_key = p.product_key
GROUP BY p.product_type
ORDER BY approval_rate DESC;


-- PART 4 — CREDIT SCORE ANALYSIS 
-- Query 4 — Approval by credit-score band

SELECT
    CASE
        WHEN credit_score < 580 THEN 'Poor'
        WHEN credit_score < 670 THEN 'Fair'
        WHEN credit_score < 740 THEN 'Good'
        WHEN credit_score < 800 THEN 'Very Good'
        ELSE 'Excellent'
    END AS credit_score_band,

    COUNT(*) AS applications,

    SUM(approved) AS approved_applications,

    ROUND(AVG(approved) * 100, 2) AS approval_rate,

    ROUND(AVG(debt_to_income_ratio) * 100, 2) AS avg_dti_pct

FROM warehouse.fact_application

GROUP BY
    CASE
        WHEN credit_score < 580 THEN 'Poor'
        WHEN credit_score < 670 THEN 'Fair'
        WHEN credit_score < 740 THEN 'Good'
        WHEN credit_score < 800 THEN 'Very Good'
        ELSE 'Excellent'
    END

ORDER BY MIN(credit_score);

-- PART 5 — DTI ANALYSIS
-- Query 5 — Approval by DTI band

SELECT
    dti_band,
    COUNT(*) AS applications,
    SUM(approved) AS approved_applications,
    ROUND(AVG(approved) * 100, 2) AS approval_rate,
    ROUND(AVG(credit_score), 2) AS avg_credit_score,
    ROUND(AVG(requested_credit_limit), 2) AS avg_requested_limit
FROM warehouse.fact_application
GROUP BY dti_band
ORDER BY
    CASE dti_band
        WHEN 'Low' THEN 1
        WHEN 'Moderate' THEN 2
        WHEN 'High' THEN 3
        WHEN 'Very High' THEN 4
    END;



-- PART 6 — LATE PAYMENT ANALYSIS
SELECT
    payment_risk_indicator,
    COUNT(*) AS applications,
    SUM(approved) AS approved_applications,
    ROUND(AVG(approved) * 100, 2) AS approval_rate,
    ROUND(AVG(late_payments_24m), 2) AS avg_late_payments
FROM warehouse.fact_application
GROUP BY payment_risk_indicator
ORDER BY
    CASE payment_risk_indicator
        WHEN 'Low' THEN 1
        WHEN 'Moderate' THEN 2
        WHEN 'High' THEN 3
        WHEN 'Very High' THEN 4
    END;

-- PART 7 — CREDIT UTILIZATION
SELECT
    CASE
        WHEN credit_utilization_ratio < 0.30 THEN 'Low'
        WHEN credit_utilization_ratio < 0.50 THEN 'Moderate'
        WHEN credit_utilization_ratio < 0.75 THEN 'High'
        ELSE 'Very High'
    END AS utilization_band,

    COUNT(*) AS applications,

    ROUND(AVG(approved) * 100, 2) AS approval_rate,

    ROUND(
        AVG(credit_utilization_ratio) * 100,
        2
    ) AS avg_utilization_pct,

    ROUND(
        AVG(total_credit_exposure),
        2
    ) AS avg_credit_exposure

FROM warehouse.fact_application

GROUP BY
    CASE
        WHEN credit_utilization_ratio < 0.30 THEN 'Low'
        WHEN credit_utilization_ratio < 0.50 THEN 'Moderate'
        WHEN credit_utilization_ratio < 0.75 THEN 'High'
        ELSE 'Very High'
    END

ORDER BY MIN(credit_utilization_ratio);

-- PART 8 — INCOME ANALYSIS

SELECT
    income_band,
    COUNT(*) AS applications,
    SUM(approved) AS approved_applications,
    ROUND(AVG(approved) * 100, 2) AS approval_rate,
    ROUND(AVG(annual_income), 2) AS avg_annual_income,
    ROUND(AVG(disposable_income), 2) AS avg_disposable_income
FROM warehouse.fact_application f
JOIN warehouse.dim_applicant a
    ON f.applicant_key = a.applicant_key
GROUP BY income_band
ORDER BY
    CASE income_band
        WHEN 'Low' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'High' THEN 3
        WHEN 'Very High' THEN 4
    END;


-- PART 9 — HIGH-RISK APPLICANTS

SELECT
    f.application_key,
    a.applicant_id,
    a.age,
    a.annual_income,
    f.credit_score,
    f.debt_to_income_ratio,
    f.credit_utilization_ratio,
    f.late_payments_24m,
    f.total_credit_exposure,
    f.approved,

    (
        CASE WHEN f.credit_score < 580 THEN 1 ELSE 0 END +
        CASE WHEN f.debt_to_income_ratio > 0.50 THEN 1 ELSE 0 END +
        CASE WHEN f.credit_utilization_ratio > 0.75 THEN 1 ELSE 0 END +
        CASE WHEN f.late_payments_24m >= 3 THEN 1 ELSE 0 END
    ) AS risk_indicator_count

FROM warehouse.fact_application f

JOIN warehouse.dim_applicant a
    ON f.applicant_key = a.applicant_key

ORDER BY risk_indicator_count DESC;

-- PART 10 — TOP EXPOSURE APPLICATIONS
SELECT
    f.application_key,
    a.applicant_id,
    p.product_type,
    f.requested_credit_limit,
    f.total_credit_exposure,
    f.credit_score,
    f.debt_to_income_ratio,
    f.credit_utilization_ratio,
    f.approved
FROM warehouse.fact_application f

JOIN warehouse.dim_applicant a
    ON f.applicant_key = a.applicant_key

JOIN warehouse.dim_product p
    ON f.product_key = p.product_key

ORDER BY f.requested_credit_limit DESC
LIMIT 20;

-- PART 11 — APPROVAL BY APPLICATION CHANNEL
SELECT
    application_channel,
    COUNT(*) AS applications,
    SUM(approved) AS approved_applications,
    ROUND(AVG(approved) * 100, 2) AS approval_rate,
    ROUND(AVG(requested_credit_limit), 2) AS avg_requested_limit
FROM warehouse.fact_application
GROUP BY application_channel
ORDER BY approval_rate DESC;

-- PART 12 — MONTHLY APPROVAL TREND

SELECT
    d.year,
    d.month,
    d.month_name,

    COUNT(*) AS applications,

    SUM(f.approved) AS approved_applications,

    ROUND(
        AVG(f.approved) * 100,
        2
    ) AS approval_rate

FROM warehouse.fact_application f

JOIN warehouse.dim_date d
    ON f.application_date_key = d.date_key

GROUP BY
    d.year,
    d.month,
    d.month_name

ORDER BY
    d.year,
    d.month;

-- PART 13 — CREATE OUR FIRST ANALYTICS TABLE
DROP TABLE IF EXISTS analytics.approval_summary;

CREATE TABLE analytics.approval_summary AS

SELECT
    approved,
    COUNT(*) AS applications,
    ROUND(
        AVG(credit_score),
        2
    ) AS avg_credit_score,

    ROUND(
        AVG(debt_to_income_ratio) * 100,
        2
    ) AS avg_dti_pct,

    ROUND(
        AVG(credit_utilization_ratio) * 100,
        2
    ) AS avg_utilization_pct,

    ROUND(
        AVG(requested_credit_limit),
        2
    ) AS avg_requested_limit

FROM warehouse.fact_application

GROUP BY approved;


SELECT *
FROM analytics.approval_summary;