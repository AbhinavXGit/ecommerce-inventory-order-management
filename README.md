# E-Commerce Inventory & Order Management System

A beginner-friendly REST API project built with **Python, FastAPI, PostgreSQL and Git**.

## What it does

- Add and list products
- Search products by name/category
- Add inventory
- Update inventory
- Create customers
- Place orders
- Automatically reduce stock after an order
- Prevent orders when stock is insufficient
- Cancel orders and restore stock
- View order details
- Uses SQL transactions for order processing
- Includes validation and error handling

## Architecture

```text
Client → FastAPI REST API → PostgreSQL
```

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- PostgreSQL
- psycopg2-binary
- Pydantic
- pytest

## Setup

### 1. Create the database

```sql
CREATE DATABASE ecommerce_db;
```

Then run:

```bash
psql -U postgres -d ecommerce_db -f sql/schema.sql
psql -U postgres -d ecommerce_db -f sql/seed.sql
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and enter your PostgreSQL password.

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

FastAPI provides interactive Swagger documentation automatically.

## Main API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/products` | List/search products |
| POST | `/products` | Add product |
| POST | `/products/{id}/inventory` | Add stock |
| PUT | `/products/{id}/inventory` | Set stock |
| POST | `/customers` | Create customer |
| POST | `/orders` | Place order |
| GET | `/orders/{id}` | View order |
| POST | `/orders/{id}/cancel` | Cancel order |

## How overselling is prevented

The order service performs the stock check and reduction together:

```sql
UPDATE inventory
SET stock = stock - %s
WHERE product_id = %s AND stock >= %s;
```

If no row is updated, sufficient stock was not available and the order is rejected.

## Example order request

```json
{
  "customer_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

## Interview explanation

> I built a small e-commerce backend using FastAPI and PostgreSQL. The system manages products, customers, inventory and orders. When an order is placed, the API checks and decreases inventory inside a database transaction. If enough stock is not available, the order is rejected. I used REST APIs, SQL queries, foreign keys, validation and exception handling.

## Future improvements

- JWT authentication
- Pagination
- Docker
- CI/CD
- Admin dashboard
- Redis caching
