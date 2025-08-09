import sqlite3
from datetime import datetime
import cv2
from pyzbar.pyzbar import decode

# Archive current day's transactions
def archive_and_reset_transactions():
    today = datetime.now().strftime('%Y_%m_%d')
    conn = sqlite3.connect('transaction_log.db')
    cursor = conn.cursor()

    # Archive today's table in a separate database
    try:
        # Check if today's transactions exist
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='transactions_{today}'")
        if cursor.fetchone():
            # Connect to the archive database
            archive_conn = sqlite3.connect('daily_archives.db')
            archive_cursor = archive_conn.cursor()

            # Create a table for today in the archive database if not exists
            archive_cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS transactions_{today} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    barcode TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    mrp REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    transaction_date TEXT NOT NULL
                )
            ''')

            # Copy data from today's table in transaction_log.db to daily_archives.db
            cursor.execute(f"SELECT * FROM transactions_{today}")
            rows = cursor.fetchall()
            if rows:
                archive_cursor.executemany(f'''
                    INSERT INTO transactions_{today} (id, barcode, product_name, mrp, quantity, transaction_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', rows)
                archive_conn.commit()

            # Drop today's table in transaction_log.db
            cursor.execute(f"DROP TABLE IF EXISTS transactions_{today}")
            conn.commit()

            print(f"Data for {today} archived successfully and reset.")
            archive_conn.close()
        else:
            print(f"No data to reset for {today}.")
    except Exception as e:
        print(f"Error during archiving/reset: {e}")
    finally:
        conn.close()

# Retrieve data for a specific date
def retrieve_data_for_date(date):
    try:
        archive_conn = sqlite3.connect('daily_archives.db')
        archive_cursor = archive_conn.cursor()

        # Fetch all data for the specified date
        archive_cursor.execute(f"SELECT * FROM transactions_{date}")
        data = archive_cursor.fetchall()
        archive_conn.close()

        if data:
            print(f"Data for {date}:")
            for row in data:
                print(row)
        else:
            print(f"No data found for {date}.")
    except Exception as e:
        print(f"Error retrieving data: {e}")

# Log a transaction
def log_transaction(barcode, product_name, mrp, quantity):
    today = datetime.now().strftime('%Y_%m_%d')
    conn = sqlite3.connect('transaction_log.db')
    cursor = conn.cursor()

    # Create today's transaction table if not exists
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS transactions_{today} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT NOT NULL,
            product_name TEXT NOT NULL,
            mrp REAL NOT NULL,
            quantity INTEGER NOT NULL,
            transaction_date TEXT NOT NULL
        )
    ''')
    transaction_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute(f'''
        INSERT INTO transactions_{today} (barcode, product_name, mrp, quantity, transaction_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (barcode, product_name, mrp, quantity, transaction_date))
    conn.commit()
    conn.close()
    print(f"Transaction logged: {product_name}, Quantity: {quantity}")

# Fetch product details from main database
def fetch_product_from_main_db(barcode):
    conn = sqlite3.connect('product_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE barcode = ?', (barcode,))
    product = cursor.fetchone()
    conn.close()
    return product

# Process scanned barcode
def process_product(barcode):
    product = fetch_product_from_main_db(barcode)
    if product:
        _, barcode, product_name, mrp, packed_date, expiry_date, fssai_no, quantity = product
        print(f"Product Found: {product_name}, MRP: {mrp}, Quantity: {quantity}")
        log_transaction(barcode, product_name, mrp, 1)  # Log with quantity = 1 for each scan
    else:
        print("Product not found in the main database.")

# Barcode detection
def detect_and_decode_barcode():
    cap = cv2.VideoCapture(0)
    print("Press 's' to scan a product or 'q' to quit scanning.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        cv2.imshow("Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):  # Detect barcode when 's' is pressed
            barcodes = decode(frame)
            if barcodes:
                for barcode in barcodes:
                    barcode_data = barcode.data.decode('utf-8')
                    print(f"Detected Barcode: {barcode_data}")
                    process_product(barcode_data)
            else:
                print("No barcode detected. Try again.")

        elif key == ord('q'):  # Quit the application
            break

    cap.release()
    cv2.destroyAllWindows()

# Switch-case simulation for user menu
def user_menu():
    while True:
        print("\nSelect an operation:")
        print("1. Scan a barcode")
        print("2. Archive and reset daily transactions")
        print("3. View archived data for a specific date")
        print("4. Quit")
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            detect_and_decode_barcode()
        elif choice == "2":
            archive_and_reset_transactions()
        elif choice == "3":
            date = input("Enter the date (YYYY_MM_DD) to retrieve data: ")
            retrieve_data_for_date(date)
        elif choice == "4":
            print("Exiting the application.")
            break
        else:
            print("Invalid choice. Please try again.")

# Main function
def main():
    user_menu()

if __name__ == "__main__":
    main()
