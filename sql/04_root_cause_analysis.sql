-- ROOT CAUSE ANALYSIS
-- ============================================================

-- 1. LATE DELIVERY RISK BY SHIPPING MODE
-- ============================================================

SELECT
    s.shipping_mode,

    COUNT(*) AS total_order_items,

    SUM(
        CASE
            WHEN f.late_delivery_risk = 1
            THEN 1
            ELSE 0
        END
    ) AS late_risk_items,

    ROUND(
        AVG(
            CASE
                WHEN f.late_delivery_risk = 1
                THEN 1.0
                ELSE 0.0
            END
        ) * 100,
        2
    ) AS late_risk_percentage,

    ROUND(AVG(f.shipping_delay_days),2) AS avg_shipping_delay_days,

    ROUND(AVG(f.days_for_shipping_real),2) AS avg_actual_shipping_days

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_shipping s
    ON f.shipping_id = s.shipping_id

GROUP BY s.shipping_mode

ORDER BY late_risk_percentage DESC;



-- 2. LATE DELIVERY RISK BY REGION
-- ============================================================

SELECT
    l.order_region,

    COUNT(*) AS total_order_items,

    SUM(
        CASE
            WHEN f.late_delivery_risk = 1
            THEN 1
            ELSE 0
        END
    ) AS late_risk_items,

    ROUND(
        AVG(
            CASE
                WHEN f.late_delivery_risk = 1
                THEN 1.0
                ELSE 0.0
            END
        ) * 100,
        2
    ) AS late_risk_percentage,

    ROUND(AVG(f.shipping_delay_days),2) AS avg_shipping_delay_days,

    ROUND(SUM(f.sales),2) AS total_sales,

    ROUND(SUM(f.order_profit_per_order),2) AS total_profit

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_location l
    ON f.location_id = l.location_id

GROUP BY l.order_region

ORDER BY late_risk_percentage DESC;


-- 3. COUNTRY-LEVEL DELIVERY RISK
-- ============================================================

SELECT
    l.order_country,

    COUNT(*) AS total_order_items,

    SUM(
        CASE
            WHEN f.late_delivery_risk = 1
            THEN 1
            ELSE 0
        END
    ) AS late_risk_items,

    ROUND(
        AVG(
            CASE
                WHEN f.late_delivery_risk = 1
                THEN 1.0
                ELSE 0.0
            END
        ) * 100,
        2
    ) AS late_risk_percentage,

    ROUND(AVG(f.shipping_delay_days),2) AS avg_shipping_delay_days,

    ROUND(SUM(f.sales),2) AS total_sales

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_location l
    ON f.location_id = l.location_id

GROUP BY l.order_country

HAVING COUNT(*) >= 100

ORDER BY late_risk_percentage DESC;


-- 4. SHIPPING MODE × REGION
-- ============================================================

SELECT
    s.shipping_mode,
    l.order_region,

    COUNT(*) AS total_order_items,

    ROUND(
        AVG(
            CASE
                WHEN f.late_delivery_risk = 1
                THEN 1.0
                ELSE 0.0
            END
        ) * 100,
        2
    ) AS late_risk_percentage,

    ROUND(AVG(f.shipping_delay_days),2) AS avg_shipping_delay_days,

    ROUND(AVG(f.days_for_shipping_real),2) AS avg_actual_shipping_days,

    ROUND(SUM(f.sales),2) AS total_sales

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_shipping s
    ON f.shipping_id = s.shipping_id

JOIN supply_chain.dim_location l
    ON f.location_id = l.location_id

GROUP BY
    s.shipping_mode,
    l.order_region

HAVING COUNT(*) >= 100

ORDER BY
    late_risk_percentage DESC;

-- 5. CATEGORY × DELIVERY RISK
-- ============================================================

SELECT
    p.category_id,
    p.category_name,

    COUNT(*) AS total_order_items,

    SUM(
        CASE
            WHEN f.late_delivery_risk = 1
            THEN 1
            ELSE 0
        END
    ) AS late_risk_items,

    ROUND(
        AVG(
            CASE
                WHEN f.late_delivery_risk = 1
                THEN 1.0
                ELSE 0.0
            END
        ) * 100,
        2
    ) AS late_risk_percentage,

    ROUND(AVG(f.shipping_delay_days),2) AS avg_shipping_delay_days,

    ROUND(SUM(f.sales),2) AS total_sales,

    ROUND(SUM(f.order_profit_per_order),2) AS total_profit

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_product p
    ON f.product_id = p.product_id

GROUP BY
    p.category_id,
    p.category_name

HAVING COUNT(*) >= 100

ORDER BY late_risk_percentage DESC;


-- 6. DELIVERY RISK × PROFITABILITY
-- ============================================================

SELECT
    CASE
        WHEN f.late_delivery_risk = 1
        THEN 'At Risk'
        ELSE 'Not At Risk'
    END AS delivery_risk_group,

    COUNT(*) AS total_order_items,

    COUNT(DISTINCT f.order_id) AS total_orders,

    ROUND(SUM(f.sales),2) AS total_sales,

    ROUND(SUM(f.order_profit_per_order),2) AS total_profit,

    ROUND(
        SUM(f.order_profit_per_order)
        / NULLIF(SUM(f.sales), 0) * 100,
        2
    ) AS profit_margin_percentage,

    ROUND(AVG(f.shipping_delay_days),2) AS avg_shipping_delay_days

FROM supply_chain.fact_order_items f

GROUP BY f.late_delivery_risk

ORDER BY f.late_delivery_risk DESC;



-- 7. DELIVERY STATUS × PROFITABILITY
-- ============================================================

SELECT
    f.delivery_status,

    COUNT(*) AS total_order_items,

    COUNT(DISTINCT f.order_id) AS total_orders,

    ROUND(SUM(f.sales),2) AS total_sales,

    ROUND(
        SUM(f.order_profit_per_order),
        2
    ) AS total_profit,

    ROUND(
        SUM(f.order_profit_per_order)
        / NULLIF(SUM(f.sales), 0) * 100,
        2
    ) AS profit_margin_percentage,

    ROUND(AVG(f.shipping_delay_days),2) AS avg_shipping_delay_days

FROM supply_chain.fact_order_items f

GROUP BY f.delivery_status

ORDER BY total_sales DESC;


-- 8. STATE-LEVEL DELIVERY RISK
-- ============================================================

SELECT
    l.order_country,
    l.order_state,

    COUNT(*) AS total_order_items,

    SUM(
        CASE
            WHEN f.late_delivery_risk = 1
            THEN 1
            ELSE 0
        END
    ) AS late_risk_items,

    ROUND(
        AVG(
            CASE
                WHEN f.late_delivery_risk = 1
                THEN 1.0
                ELSE 0.0
            END
        ) * 100,
        2
    ) AS late_risk_percentage,

    ROUND(AVG(f.shipping_delay_days), 2) AS avg_shipping_delay_days,

    ROUND(SUM(f.sales), 2) AS total_sales

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_location l
    ON f.location_id = l.location_id

GROUP BY
    l.order_country,
    l.order_state

HAVING COUNT(*) >= 100

ORDER BY late_risk_percentage DESC;


-- 9. COUNTRY × SHIPPING MODE RISK
-- ============================================================

SELECT
    l.order_country,
    s.shipping_mode,

    COUNT(*) AS total_order_items,

    ROUND(
        AVG(
            CASE
                WHEN f.late_delivery_risk = 1
                THEN 1.0
                ELSE 0.0
            END
        ) * 100,
        2
    ) AS late_risk_percentage,

    ROUND(AVG(f.shipping_delay_days), 2) AS avg_shipping_delay_days,

    ROUND(SUM(f.sales), 2) AS total_sales

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_location l
    ON f.location_id = l.location_id

JOIN supply_chain.dim_shipping s
    ON f.shipping_id = s.shipping_id

GROUP BY
    l.order_country,
    s.shipping_mode

HAVING COUNT(*) >= 100

ORDER BY late_risk_percentage DESC;



-- 10. HIGH-PRIORITY DELIVERY PROBLEM AREAS
-- ============================================================

SELECT
    l.order_country,

    COUNT(*) AS total_order_items,

    SUM(
        CASE
            WHEN f.late_delivery_risk = 1
            THEN 1
            ELSE 0
        END
    ) AS late_risk_items,

    ROUND(
        AVG(
            CASE
                WHEN f.late_delivery_risk = 1
                THEN 1.0
                ELSE 0.0
            END
        ) * 100,
        2
    ) AS late_risk_percentage,

    ROUND(
        SUM(f.sales),
        2
    ) AS total_sales

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_location l
    ON f.location_id = l.location_id

GROUP BY l.order_country

HAVING COUNT(*) >= 500

ORDER BY
    late_risk_items DESC;
