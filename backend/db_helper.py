import os
import mysql.connector

def get_connection():
    return mysql.connector.connect(
    host=os.getenv("MYSQLHOST"),
    user=os.getenv("MYSQLUSER"),
    password=os.getenv("MYSQLPASSWORD"),
    database=os.getenv("MYSQLDATABASE"),
    port=int(os.getenv("MYSQLPORT"))
)

def insert_order_tracking(order_id, status):
    cnx=get_connection()
    cursor = cnx.cursor()

    # Inserting the record into the order_tracking table
    insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
    cursor.execute(insert_query, (order_id, status))

    # Committing the changes
    cnx.commit()

    # Closing the cursor
    cursor.close()


def insert_order_item(food_item, quantity, order_id):
    cnx=get_connection()
    try:
        cursor = cnx.cursor()

        # Calling the stored procedure
        cursor.callproc('insert_order_item', ( food_item, quantity, order_id))

        # Committing the changes
        cnx.commit()

        # Closing the cursor
        cursor.close()

        print("Order item inserted successfully!")

        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")

        # Rollback changes if necessary
        cnx.rollback()

        return -1

    except Exception as e:
        print(f"An error occurred: {e}")
        # Rollback changes if necessary
        cnx.rollback()

        return -1

def get_total_order_price(order_id):
    cnx=get_connection()
    cursor = cnx.cursor()

    # Executing the SQL query to get the total order price
    query = f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()

    # Closing the cursor
    cursor.close()

    return result[0] if result else 0

def get_next_order_id():
    cnx=get_connection()
    cursor = cnx.cursor()

    # Executing the SQL query to get the next available order_id
    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()[0]

    # Closing the cursor
    cursor.close()

    # Returning the next available order_id
    if result is None:
        return 1
    else:
        return result+1
def get_order_status(order_id: int):
    cnx=get_connection()
    # Create a cursor object
    cursor = cnx.cursor()

    # Write the SQL query
    query = "SELECT status FROM order_tracking WHERE order_id = %s"

    try:
        # Execute the query with a proper 1-element tuple
        cursor.execute(query, (order_id,))

        # Fetch the result
        result = cursor.fetchone()

        if result is not None:
            return result[0]
        return None

    finally:
        # ALWAYS close the cursor inside a finally block to prevent resource leaks,
        # but leave cnx alone so other calls can use it.
        cursor.close()
