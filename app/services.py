from decimal import Decimal

from .database import get_connection


def create_order(customer_id, items):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT customer_id FROM customers WHERE customer_id = %s",
                (customer_id,),
            )
            if cur.fetchone() is None:
                raise ValueError("Customer not found")

            total_amount = Decimal("0.00")

            cur.execute(
                """
                INSERT INTO orders (customer_id, total_amount)
                VALUES (%s, 0)
                RETURNING order_id
                """,
                (customer_id,),
            )
            order_id = cur.fetchone()[0]

            for item in items:
                product_id = item["product_id"]
                quantity = item["quantity"]

                cur.execute(
                    """
                    SELECT price
                    FROM products
                    WHERE product_id = %s
                    """,
                    (product_id,),
                )
                product = cur.fetchone()

                if product is None:
                    raise ValueError(f"Product {product_id} not found")

                price = product[0]

                # Atomic stock check + decrement.
                cur.execute(
                    """
                    UPDATE inventory
                    SET stock = stock - %s
                    WHERE product_id = %s AND stock >= %s
                    """,
                    (quantity, product_id, quantity),
                )

                if cur.rowcount == 0:
                    raise ValueError(
                        f"Insufficient stock for product {product_id}"
                    )

                cur.execute(
                    """
                    INSERT INTO order_items
                    (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (order_id, product_id, quantity, price),
                )

                total_amount += price * quantity

            cur.execute(
                """
                UPDATE orders
                SET total_amount = %s
                WHERE order_id = %s
                """,
                (total_amount, order_id),
            )

        conn.commit()
        return order_id, total_amount

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def cancel_order(order_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT status FROM orders WHERE order_id = %s",
                (order_id,),
            )
            order = cur.fetchone()

            if order is None:
                raise ValueError("Order not found")

            if order[0] == "CANCELLED":
                raise ValueError("Order is already cancelled")

            if order[0] == "COMPLETED":
                raise ValueError("Completed order cannot be cancelled")

            cur.execute(
                """
                SELECT product_id, quantity
                FROM order_items
                WHERE order_id = %s
                """,
                (order_id,),
            )
            items = cur.fetchall()

            for product_id, quantity in items:
                cur.execute(
                    """
                    UPDATE inventory
                    SET stock = stock + %s
                    WHERE product_id = %s
                    """,
                    (quantity, product_id),
                )

            cur.execute(
                """
                UPDATE orders
                SET status = 'CANCELLED'
                WHERE order_id = %s
                """,
                (order_id,),
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
