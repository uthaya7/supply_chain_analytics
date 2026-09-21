-- 1. Data Integrity Validation Row Count Check

SELECT 'dim_customer' AS table_name, COUNT(*) AS row_count
FROM supply_chain.dim_customer

UNION ALL
SELECT 'dim_product', COUNT(*)
FROM supply_chain.dim_product

UNION ALL
SELECT 'dim_date', COUNT(*)
FROM supply_chain.dim_date

UNION ALL
SELECT 'dim_location', COUNT(*)
FROM supply_chain.dim_location

UNION ALL
SELECT 'dim_shipping', COUNT(*)
FROM supply_chain.dim_shipping

UNION ALL
SELECT 'fact_order_items', COUNT(*)
FROM supply_chain.fact_order_items;


-- 2. Fact Primary Key Uniqueness Check
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT order_item_id) AS unique_order_items
FROM supply_chain.fact_order_items;

-- 3. Foreign-key integrity

SELECT COUNT(*) AS orphan_customers
FROM supply_chain.fact_order_items f
LEFT JOIN supply_chain.dim_customer d
    ON f.customer_id = d.customer_id
WHERE d.customer_id IS NULL;

SELECT COUNT(*) AS orphan_products
FROM supply_chain.fact_order_items f
LEFT JOIN supply_chain.dim_product d
    ON f.product_id = d.product_id
WHERE d.product_id IS NULL;

SELECT COUNT(*) AS orphan_dates
FROM supply_chain.fact_order_items f
LEFT JOIN supply_chain.dim_date d
    ON f.date_id = d.date_id
WHERE d.date_id IS NULL;

SELECT COUNT(*) AS orphan_locations
FROM supply_chain.fact_order_items f
LEFT JOIN supply_chain.dim_location d
    ON f.location_id = d.location_id
WHERE d.location_id IS NULL;

SELECT COUNT(*) AS orphan_shipping
FROM supply_chain.fact_order_items f
LEFT JOIN supply_chain.dim_shipping d
    ON f.shipping_id = d.shipping_id
WHERE d.shipping_id IS NULL;


-- 4. Required FK NULL check

SELECT
    COUNT(*) FILTER (WHERE customer_id IS NULL) AS null_customer,
    COUNT(*) FILTER (WHERE product_id IS NULL) AS null_product,
    COUNT(*) FILTER (WHERE date_id IS NULL) AS null_date,
    COUNT(*) FILTER (WHERE location_id IS NULL) AS null_location,
    COUNT(*) FILTER (WHERE shipping_id IS NULL) AS null_shipping
FROM supply_chain.fact_order_items;

-- 5. Location grain validation

SELECT
    COUNT(*) AS total_locations,
    COUNT(
        DISTINCT (
            market,
            order_region,
            order_country,
            order_state,
            order_city
        )
    ) AS unique_geographic_locations
FROM supply_chain.dim_location;