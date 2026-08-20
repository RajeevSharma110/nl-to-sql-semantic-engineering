BEGIN;

CREATE TABLE IF NOT EXISTS customers (
    customer_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email text NOT NULL UNIQUE,
    region text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS products (
    product_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category text NOT NULL,
    name text NOT NULL,
    unit_price numeric(12,2) NOT NULL CHECK (unit_price >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id bigint NOT NULL REFERENCES customers(customer_id),
    status text NOT NULL CHECK (status IN ('pending', 'completed', 'cancelled')),
    ordered_at timestamptz NOT NULL DEFAULT now(),
    region text NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id bigint NOT NULL REFERENCES orders(order_id),
    product_id bigint NOT NULL REFERENCES products(product_id),
    quantity integer NOT NULL CHECK (quantity > 0),
    unit_price numeric(12,2) NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, product_id)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id bigint NOT NULL REFERENCES orders(order_id),
    status text NOT NULL CHECK (status IN ('captured', 'failed', 'refunded')),
    method text NOT NULL,
    amount numeric(12,2) NOT NULL CHECK (amount >= 0),
    paid_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS returns (
    return_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id bigint NOT NULL REFERENCES orders(order_id),
    product_id bigint NOT NULL REFERENCES products(product_id),
    quantity integer NOT NULL CHECK (quantity > 0),
    refunded_amount numeric(12,2) NOT NULL CHECK (refunded_amount >= 0),
    returned_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_time ON orders(customer_id, ordered_at DESC);
CREATE INDEX IF NOT EXISTS idx_orders_status_time ON orders(status, ordered_at DESC);
CREATE INDEX IF NOT EXISTS idx_payments_order_status ON payments(order_id, status);
CREATE INDEX IF NOT EXISTS idx_returns_order ON returns(order_id);

COMMIT;

