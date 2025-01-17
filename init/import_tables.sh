#!/bin/bash
set -e  # Exit on error

echo "Starting data import..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
\copy users(login, hashed_password, user_type, created_at) FROM '/data/tables/users.csv' DELIMITER ',' CSV HEADER;
\copy items(name) FROM '/data/tables/items.csv' DELIMITER ',' CSV HEADER;
\copy inventory(item_id, quantity, status) FROM '/data/tables/inventory.csv' DELIMITER ',' CSV HEADER;
\copy user_inventory(user_id, item_id, quantity, status) FROM '/data/tables/user_inventory.csv' DELIMITER ',' CSV HEADER;
\copy provider_items(provider_name, item_id, price) FROM '/data/tables/provider_items.csv' DELIMITER ',' CSV HEADER;
EOSQL

echo "Data import completed successfully."
