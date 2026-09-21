-- Create the supply_chain schema

CREATE SCHEMA supply_chain;


-- Create the dim_customer table

CREATE TABLE supply_chain.dim_customer (
    customer_id INTEGER PRIMARY KEY,
    customer_segment VARCHAR(50),
    customer_city VARCHAR(100),
    customer_state VARCHAR(100),
    customer_country VARCHAR(100)
);

-- Create the dim_product table

CREATE TABLE supply_chain.dim_product (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(255),
    product_price NUMERIC(12,2),
    product_status INTEGER,
    category_id INTEGER,
    category_name VARCHAR(150),
    department_id INTEGER,
    department_name VARCHAR(150)
);

-- Create the dim_date table

CREATE TABLE supply_chain.dim_date (
    date_id INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    week INTEGER,
    day INTEGER,
    day_name VARCHAR(20)
);

-- Create the dim_location table

CREATE TABLE supply_chain.dim_location (
    location_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    market VARCHAR(100),
    order_region VARCHAR(100),
    order_country VARCHAR(100),
    order_state VARCHAR(100),
    order_city VARCHAR(100),
    latitude NUMERIC(10,6),
    longitude NUMERIC(10,6)
);

-- Create the dim_shipping table
CREATE TABLE supply_chain.dim_shipping (
    shipping_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    shipping_mode VARCHAR(50) UNIQUE NOT NULL
);

-- Create the fact_order_items table

CREATE TABLE supply_chain.fact_order_items (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,

    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    shipping_id INTEGER NOT NULL,

    days_for_shipping_real INTEGER,
    days_for_shipment_scheduled INTEGER,
    shipping_delay_days INTEGER,

    order_item_quantity INTEGER,

    benefit_per_order NUMERIC(12,2),
    sales_per_customer NUMERIC(12,2),
    order_item_discount NUMERIC(12,2),
    order_item_discount_rate NUMERIC(8,4),
    order_item_product_price NUMERIC(12,2),
    order_item_profit_ratio NUMERIC(12,4),

    sales NUMERIC(14,2),
    order_item_total NUMERIC(14,2),
    order_profit_per_order NUMERIC(14,2),
    profit_margin NUMERIC(12,4),
    discount_percentage NUMERIC(8,4),

    delivery_status VARCHAR(50),
    late_delivery_risk INTEGER,
    order_status VARCHAR(50),
    shipping_performance VARCHAR(50),
    type VARCHAR(50),

    CONSTRAINT fk_fact_customer
        FOREIGN KEY (customer_id)
        REFERENCES supply_chain.dim_customer(customer_id),

    CONSTRAINT fk_fact_product
        FOREIGN KEY (product_id)
        REFERENCES supply_chain.dim_product(product_id),

    CONSTRAINT fk_fact_date
        FOREIGN KEY (date_id)
        REFERENCES supply_chain.dim_date(date_id),

    CONSTRAINT fk_fact_location
        FOREIGN KEY (location_id)
        REFERENCES supply_chain.dim_location(location_id),

    CONSTRAINT fk_fact_shipping
        FOREIGN KEY (shipping_id)
        REFERENCES supply_chain.dim_shipping(shipping_id)
);


-- Query to list all tables in the supply_chain schema
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'supply_chain'
ORDER BY table_name;

-- Query to list all columns in the supply_chain schema

SELECT * FROM supply_chain.dim_customer;
SELECT * FROM supply_chain.dim_product;
SELECT * FROM supply_chain.dim_date;
SELECT * FROM supply_chain.dim_location;
SELECT * FROM supply_chain.dim_shipping;

-- Query to truncate all tables in the supply_chain schema
BEGIN;

TRUNCATE TABLE
    supply_chain.fact_order_items,
    supply_chain.dim_customer,
    supply_chain.dim_product,
    supply_chain.dim_date,
    supply_chain.dim_location,
    supply_chain.dim_shipping
RESTART IDENTITY;

COMMIT;

-- Add a unique constraint to the dim_location table to ensure that the combination of market, 
-- order_region, order_country, order_state, and order_city is unique.

ALTER TABLE supply_chain.dim_location
ADD CONSTRAINT uq_dim_location_geography
UNIQUE (
    market,
    order_region,
    order_country,
    order_state,
    order_city
);


-- Query to count the total number of locations and 
-- the number of unique geographic locations in the dim_location table
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