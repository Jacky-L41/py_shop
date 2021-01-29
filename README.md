# py_shop
A multithread TCP server API using ThreadedTCPServer, using data by connectting database.db SQLite database

SQLite tables schema
```
CREATE TABLE clients (client_id integer primary key);

CREATE TABLE products (product_id integer primary key, name text NOT NULL, description text, price decimal (10,2) NOT NULL, quantity integer NOT NULL, check (price >= 0 and quantity >= 0));

CREATE TABLE carts (client_id integer not null, product_id integer not null, quantity integer not null, time text, primary key (client_id,product_id), foreign key (client_id) references clients (client_id), foreign key (product_id) references products (product_id), check (quantity >=0));
```
# API
`START <client_id>`\
Check whether user exists in table `clients`\
Return: stringified JSON object
if exist
{"exist": true, "client_id": `<client_id>`}
else
{"exist": false}

`UPDATE <client_id> <product_id> <quantity>`\
Update shopping cart of `client_id` with `product_id` and `quantity`\
Return:
{"msg": "Success", "product_id": `<product_id>`, "cart_owner_id": `<client_id>`, "total_amount": `<quantity>`, "subtotal": , "update_GMT_time": , "available": }

`CART <client_id>`\
Get shopping cart info of client_id\
Return:
{"client_id": "1", "items": \[\], "total": 0.0}

`REPLENISH <product_id> <quantity>`
Add `<quantity>` to `<product_id>`
Return:


## Test client
`
single_client_auto_and_sys_argv_api.py
`
