from fastapi import FastAPI, HTTPException, Query

from .database import get_cursor
from .schemas import (
    CustomerCreate,
    InventoryAdd,
    InventoryUpdate,
    OrderCreate,
    ProductCreate,
)
from .services import cancel_order, create_order

app = FastAPI(
    title="E-Commerce Inventory & Order Management API",
    version="1.0.0",
    description="Beginner-friendly e-commerce backend using FastAPI and PostgreSQL.",
)


@app.get("/")
def root():
    return {"message": "E-Commerce API is running"}


@app.get("/products")
def list_products(
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
):
    query = """
        SELECT p.product_id, p.name, p.category, p.price,
               i.stock
        FROM products p
        JOIN inventory i ON p.product_id = i.product_id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND p.name ILIKE %s"
        params.append(f"%{search}%")

    if category:
        query += " AND p.category ILIKE %s"
        params.append(category)

    query += " ORDER BY p.product_id"

    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


@app.post("/products", status_code=201)
def add_product(product: ProductCreate):
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO products (name, category, price)
            VALUES (%s, %s, %s)
            RETURNING product_id, name, category, price
            """,
            (product.name, product.category, product.price),
        )
        result = cur.fetchone()

        cur.execute(
            "INSERT INTO inventory (product_id, stock) VALUES (%s, 0)",
            (result["product_id"],),
        )

        return result


@app.post("/products/{product_id}/inventory")
def add_inventory(product_id: int, data: InventoryAdd):
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            UPDATE inventory
            SET stock = stock + %s
            WHERE product_id = %s
            RETURNING product_id, stock
            """,
            (data.quantity, product_id),
        )
        result = cur.fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="Product not found")

        return result


@app.put("/products/{product_id}/inventory")
def set_inventory(product_id: int, data: InventoryUpdate):
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            UPDATE inventory
            SET stock = %s
            WHERE product_id = %s
            RETURNING product_id, stock
            """,
            (data.stock, product_id),
        )
        result = cur.fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="Product not found")

        return result


@app.post("/customers", status_code=201)
def add_customer(customer: CustomerCreate):
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO customers (name, email)
            VALUES (%s, %s)
            RETURNING customer_id, name, email
            """,
            (customer.name, customer.email),
        )
        return cur.fetchone()


@app.post("/orders", status_code=201)
def place_order(order: OrderCreate):
    try:
        order_id, total = create_order(
            order.customer_id,
            [item.model_dump() for item in order.items],
        )
        return {
            "order_id": order_id,
            "customer_id": order.customer_id,
            "total_amount": float(total),
            "status": "PLACED",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT order_id, customer_id, order_date,
                   total_amount, status
            FROM orders
            WHERE order_id = %s
            """,
            (order_id,),
        )
        order = cur.fetchone()

        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")

        cur.execute(
            """
            SELECT oi.product_id, p.name, oi.quantity, oi.price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
            ORDER BY oi.product_id
            """,
            (order_id,),
        )
        items = cur.fetchall()

        return {"order": order, "items": items}


@app.post("/orders/{order_id}/cancel")
def cancel(order_id: int):
    try:
        cancel_order(order_id)
        return {"message": "Order cancelled successfully"}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
