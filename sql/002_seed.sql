BEGIN;

INSERT INTO customers (email, region) VALUES
    ('ana@example.test', 'EU'),
    ('ben@example.test', 'UK'),
    ('chen@example.test', 'APAC')
ON CONFLICT (email) DO NOTHING;

INSERT INTO products (category, name, unit_price)
SELECT * FROM (VALUES
    ('hardware', 'Mechanical Keyboard', 120.00::numeric),
    ('hardware', 'Wireless Mouse', 60.00::numeric),
    ('software', 'Analytics License', 300.00::numeric)
) AS incoming(category, name, unit_price)
WHERE NOT EXISTS (SELECT 1 FROM products);

INSERT INTO orders (customer_id, status, ordered_at, region)
SELECT customer_id, 'completed', now() - interval '10 days', region FROM customers
WHERE NOT EXISTS (SELECT 1 FROM orders);

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT o.order_id, p.product_id, 1, p.unit_price
FROM orders o
JOIN LATERAL (SELECT * FROM products ORDER BY product_id LIMIT 1) p ON true
ON CONFLICT DO NOTHING;

INSERT INTO payments (order_id, status, method, amount, paid_at)
SELECT o.order_id, 'captured', 'card', oi.quantity * oi.unit_price, o.ordered_at
FROM orders o JOIN order_items oi USING (order_id)
WHERE NOT EXISTS (SELECT 1 FROM payments);

COMMIT;

