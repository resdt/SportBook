-- Drop tables
DROP TABLE IF EXISTS requests CASCADE;
DROP TABLE IF EXISTS provider_items CASCADE;
DROP TABLE IF EXISTS user_inventory CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS items CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop ENUM types
DROP TYPE IF EXISTS user_type_enum;
DROP TYPE IF EXISTS inventory_status_enum;
DROP TYPE IF EXISTS request_type_enum;
DROP TYPE IF EXISTS request_status_enum;

-- Create ENUM types
CREATE TYPE user_type_enum AS ENUM ('admin', 'user');
CREATE TYPE inventory_status_enum AS ENUM ('новый', 'используемый', 'сломанный');
CREATE TYPE request_type_enum AS ENUM ('получить', 'отремонтировать', 'заменить');
CREATE TYPE request_status_enum AS ENUM ('на рассмотрении', 'одобрено', 'отклонено');

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(255) NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    user_type user_type_enum NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create items table
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- Create inventory table (unallocated)
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    item_id INT NOT NULL REFERENCES items(id),
    quantity INT NOT NULL CHECK (quantity >= 0),
    status inventory_status_enum NOT NULL,
    UNIQUE (item_id, status)
);

-- Create user_inventory table (allocated to users)
CREATE TABLE user_inventory (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    item_id INT NOT NULL REFERENCES items(id),
    quantity INT NOT NULL CHECK (quantity >= 0),
    status inventory_status_enum NOT NULL,
    UNIQUE (user_id, item_id, status)
);

-- Create provider_items table
CREATE TABLE provider_items (
    id SERIAL PRIMARY KEY,
    provider_name VARCHAR(255) NOT NULL,
    item_id INT NOT NULL REFERENCES items(id),
    price DECIMAL(10, 2) NOT NULL,
    UNIQUE (provider_name, item_id)
);

-- Create requests table
CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    item_id INT NOT NULL REFERENCES items(id),
    request_type request_type_enum NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    status request_status_enum DEFAULT 'на рассмотрении',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
