import cv2
import sqlite3
from pyzbar.pyzbar import decode

# Create the database and table if not exists
def create_database():
    conn = sqlite3.connect('product_database.db')
    cursor = conn.cursor()

    # Drop table if it exists for fresh testing (use cautiously)
    cursor.execute('DROP TABLE IF EXISTS products')

    # Create table with necessary columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            name TEXT,
            mrp INTEGER,
            packed_date TEXT,
            expiry_date TEXT,
            fssai_no TEXT,
            quantity INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()
    print("Database and table created successfully.")

# Insert product into database
def insert_product(barcode, name, mrp, packed_date, expiry_date, fssai_no):
    conn = sqlite3.connect('product_database.db')
    cursor = conn.cursor()

    # Insert product if not already present
    cursor.execute('''
        INSERT OR IGNORE INTO products (barcode, name, mrp, packed_date, expiry_date, fssai_no, quantity)
        VALUES (?, ?, ?, ?, ?, ?, 0)  -- Initialize quantity to 0
    ''', (barcode, name, mrp, packed_date, expiry_date, fssai_no))

    conn.commit()
    conn.close()
    print(f"Product with barcode {barcode} added to the database.")

# Fetch product data based on barcode
def fetch_product_data(barcode):
    conn = sqlite3.connect('product_database.db')
    cursor = conn.cursor()

    # Query for product with the given barcode
    cursor.execute('SELECT * FROM products WHERE barcode = ?', (barcode,))
    product = cursor.fetchone()

    conn.close()
    return product

# Update the product quantity in the database
def update_product_quantity(barcode, new_quantity):
    conn = sqlite3.connect('product_database.db')
    cursor = conn.cursor()

    # Update quantity for the given barcode
    cursor.execute('UPDATE products SET quantity = ? WHERE barcode = ?', (new_quantity, barcode))
    conn.commit()
    conn.close()

# Fetch and update product data based on barcode (incrementing quantity)
def fetch_and_update_product(barcode):
    product = fetch_product_data(barcode)

    if product:
        print(f"Product found: {product}")

        # Check if the product has the expected structure
        if len(product) < 8:
            print("Error: Product data is incomplete. Expected format: (id, barcode, name, mrp, packed_date, expiry_date, fssai_no, quantity)")
            return

        # Increment the quantity by 1
        new_quantity = product[7] + 1  # Increment the quantity (7th index corresponds to quantity)
        update_product_quantity(barcode, new_quantity)

        # Calculate total price based on updated quantity
        total_price = new_quantity * product[3]  # quantity * mrp
        print(f"Total Price: {total_price} | Quantity: {new_quantity}")
    else:
        print("Product not found.")

# Function to scan barcode and fetch product data when 's' is pressed
def scan_barcode_on_s_key():
    cap = cv2.VideoCapture(0)  # Use webcam for barcode scanning
    print("Press 's' to scan the barcode and increment quantity.")
    barcode_data = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image.")
            break

        # Only process barcode when 's' is pressed
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):  # Only when 's' is pressed, start scanning for barcode
            # Decode barcodes from the captured frame
            barcodes = decode(frame)

            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                print(f"Detected barcode: {barcode_data}")

            # If barcode is detected, fetch and update product details
            if barcode_data:
                print("Scanning for barcode...")
                fetch_and_update_product(barcode_data)
                barcode_data = None  # Reset barcode_data after processing

        elif key == ord('q'):  # Press 'q' to quit the loop
            break

        # Display the frame for the user to see
        cv2.imshow("Barcode Scanner", frame)

    cap.release()
    cv2.destroyAllWindows()

def main():
    # Create database and insert initial data
    create_database()

    # Insert initial product data (Example)
    insert_product('10035', 'Nattrinai Sivappu Rice 1/2 kg', 65, '20/11/2024', '19/05/2025', '12416003000312')
    insert_product('2135663', 'Components', 2000, '20/11/2024', '19/05/2025', '78037860876')
    # Start scanning barcodes when 's' is pressed
    scan_barcode_on_s_key()

if __name__ == '__main__':
    main()
