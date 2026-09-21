-- ============================================================
-- SPRINT 4.1
-- SUPPLY CHAIN EXECUTIVE KPIs
-- ============================================================

-- 1. OVERALL BUSINESS KPIs
-- ============================================================

SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT order_item_id) AS total_order_items,
    SUM(order_item_quantity) AS total_quantity_sold,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(order_profit_per_order), 2) AS total_profit,
    ROUND(
        SUM(order_profit_per_order)
        / NULLIF(SUM(sales), 0) * 100,
        2
    ) AS profit_margin_percentage,
    ROUND(
        SUM(sales)
        / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS average_order_value
FROM supply_chain.fact_order_items;


-- 2. DELIVERY & SHIPPING KPIs
-- ============================================================

SELECT
    COUNT(*) AS total_order_items,

    ROUND(
        AVG(days_for_shipping_real),
        2
    ) AS avg_actual_shipping_days,

    ROUND(
        AVG(days_for_shipment_scheduled),
        2
    ) AS avg_scheduled_shipping_days,

    ROUND(
        AVG(shipping_delay_days),
        2
    ) AS avg_shipping_delay_days,

    ROUND(
        AVG(
            CASE
                WHEN late_delivery_risk = 1
                THEN 1.0
                ELSE 0.0
            END
        ) * 100,
        2
    ) AS late_delivery_risk_rate_percentage

FROM supply_chain.fact_order_items;


-- 4. DELIVERY STATUS
-- ============================================================

SELECT
    delivery_status,
    COUNT(*) AS order_items,
    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage_of_order_items
FROM supply_chain.fact_order_items
GROUP BY delivery_status
ORDER BY order_items DESC;


-- 5. SHIPPING MODE PERFORMANCE
-- ============================================================

SELECT
    s.shipping_mode,

    COUNT(*) AS order_items,

    SUM(f.order_item_quantity) AS quantity_sold,

    ROUND(
        SUM(f.sales),2) AS total_sales,

    ROUND(
        SUM(f.order_profit_per_order),2) AS total_profit,

    ROUND(
        AVG(f.days_for_shipping_real),2 ) AS avg_shipping_days,

    ROUND(
        AVG(f.shipping_delay_days),2) AS avg_shipping_delay_days,

    ROUND(
        AVG(
            CASE
                WHEN f.late_delivery_risk = 1
                THEN 1.0
                ELSE 0.0
            END
        ) * 100,
        2
    ) AS late_delivery_risk_percentage

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_shipping s
    ON f.shipping_id = s.shipping_id

GROUP BY s.shipping_mode

ORDER BY total_sales DESC;


-- 6. MONTHLY BUSINESS TREND
-- ============================================================

SELECT
    d.year,
    d.month,
    d.month_name,

    ROUND(
        SUM(f.sales),
        2
    ) AS total_sales,

    ROUND(
        SUM(f.order_profit_per_order),
        2
    ) AS total_profit,

    COUNT(DISTINCT f.order_id)
        AS total_orders,

    SUM(f.order_item_quantity)
        AS quantity_sold

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_date d
    ON f.date_id = d.date_id

GROUP BY
    d.year,
    d.month,
    d.month_name

ORDER BY
    d.year,
    d.month;


-- 7. YEARLY BUSINESS PERFORMANCE
-- ============================================================

SELECT
    d.year,

    COUNT(DISTINCT f.order_id)
        AS total_orders,

    SUM(f.order_item_quantity)
        AS quantity_sold,

    ROUND(
        SUM(f.sales),
        2
    ) AS total_sales,

    ROUND(
        SUM(f.order_profit_per_order),
        2
    ) AS total_profit,

    ROUND(
        SUM(f.order_profit_per_order)
        / NULLIF(SUM(f.sales), 0) * 100,
        2
    ) AS profit_margin_percentage

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_date d
    ON f.date_id = d.date_id

GROUP BY d.year

ORDER BY d.year;


-- 8. CUSTOMER SEGMENT PERFORMANCE
-- ============================================================

SELECT
    c.customer_segment,

    COUNT(DISTINCT f.customer_id)
        AS unique_customers,

    COUNT(DISTINCT f.order_id)
        AS total_orders,

    SUM(f.order_item_quantity)
        AS quantity_sold,

    ROUND(
        SUM(f.sales),
        2
    ) AS total_sales,

    ROUND(
        SUM(f.order_profit_per_order),
        2
    ) AS total_profit,

    ROUND(
        SUM(f.sales)
        / NULLIF(
            COUNT(DISTINCT f.order_id),
            0
        ),
        2
    ) AS average_order_value

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_customer c
    ON f.customer_id = c.customer_id

GROUP BY c.customer_segment

ORDER BY total_sales DESC;


-- 9. PRODUCT CATEGORY PERFORMANCE
-- ============================================================

SELECT
    p.category_id,
    p.category_name,

    COUNT(DISTINCT p.product_id)
        AS unique_products,

    SUM(f.order_item_quantity)
        AS quantity_sold,

    ROUND(
        SUM(f.sales),
        2
    ) AS total_sales,

    ROUND(
        SUM(f.order_profit_per_order),
        2
    ) AS total_profit,

    ROUND(
        SUM(f.order_profit_per_order)
        / NULLIF(SUM(f.sales), 0) * 100,
        2
    ) AS profit_margin_percentage

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_product p
    ON f.product_id = p.product_id

GROUP BY
    p.category_id,
    p.category_name

ORDER BY total_sales DESC;


-- 10. DEPARTMENT PERFORMANCE
-- ============================================================

SELECT
    p.department_id,
    p.department_name,

    COUNT(DISTINCT f.product_id)
        AS unique_products,

    SUM(f.order_item_quantity)
        AS quantity_sold,

    ROUND(
        SUM(f.sales),
        2
    ) AS total_sales,

    ROUND(
        SUM(f.order_profit_per_order),
        2
    ) AS total_profit,

    ROUND(
        SUM(f.order_profit_per_order)
        / NULLIF(SUM(f.sales), 0) * 100,
        2
    ) AS profit_margin_percentage

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_product p
    ON f.product_id = p.product_id

GROUP BY
    p.department_id,
    p.department_name

ORDER BY total_sales DESC;


-- 11. GEOGRAPHIC PERFORMANCE
-- ============================================================

SELECT
    l.market,
    l.order_region,
    l.order_country,

    COUNT(DISTINCT f.order_id)
        AS total_orders,

    SUM(f.order_item_quantity)
        AS quantity_sold,

    ROUND(
        SUM(f.sales),
        2
    ) AS total_sales,

    ROUND(
        SUM(f.order_profit_per_order),
        2
    ) AS total_profit,

    ROUND(
        AVG(f.shipping_delay_days),
        2
    ) AS avg_shipping_delay_days,

    ROUND(
        AVG(
            CASE
                WHEN f.late_delivery_risk = 1
                THEN 1.0
                ELSE 0.0
            END
        ) * 100,
        2
    ) AS late_delivery_risk_percentage

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_location l
    ON f.location_id = l.location_id

GROUP BY
    l.market,
    l.order_region,
    l.order_country

ORDER BY total_sales DESC;


-- 12. TOP 10 PRODUCTS BY SALES
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.category_name,

    SUM(f.order_item_quantity)
        AS quantity_sold,

    ROUND(
        SUM(f.sales),
        2
    ) AS total_sales,

    ROUND(
        SUM(f.order_profit_per_order),
        2
    ) AS total_profit

FROM supply_chain.fact_order_items f

JOIN supply_chain.dim_product p
    ON f.product_id = p.product_id

GROUP BY
    p.product_id,
    p.product_name,
    p.category_name

ORDER BY total_sales DESC

LIMIT 10;