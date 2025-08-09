import cv2
from pyzbar.pyzbar import decode
import numpy as np

# Function to detect and decode barcode from camera capture
def detect_barcode_from_camera():
    # Start the camera (0 is the default camera, change if you have multiple cameras)
    cap = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to capture image")
            break

        # Decode barcodes in the captured frame
        barcodes = decode(frame)
        
        for barcode in barcodes:
            # Get the barcode data (e.g., text or numbers) and the bounding box coordinates
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            
            # Draw a rectangle around the barcode
            rect_points = barcode.polygon
            if len(rect_points) == 4:
                pts = np.array(rect_points, dtype=np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 0, 255), 5)
            else:
                cv2.circle(frame, (barcode.rect[0], barcode.rect[1]), 5, (0, 0, 255), -1)
            
            # Display the barcode data and type on the frame
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, barcode_data, (barcode.rect[0], barcode.rect[1] - 10), font, 0.9, (0, 255, 0), 2)
            print(f"Barcode Data: {barcode_data} | Type: {barcode_type}")
        
        # Display the resulting frame with the barcode
        cv2.imshow("Barcode Detection - Press 'q' to quit", frame)
        
        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()

# Call the function to start barcode detection from the camera
detect_barcode_from_camera()
