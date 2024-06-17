''' CNN BASED MODEL'''

import cv2
import numpy as np
import tensorflow as tf
import RPi.GPIO as GPIO
import time

# Load the TensorFlow Lite model for plant disease detection
interpreter = tf.lite.Interpreter('converted_model.tflite')
interpreter.allocate_tensors()

# Set up the camera
cap = cv2.VideoCapture(0)  # Use 0 for the default camera

# Set up the GPIO pin for the motor pump
PUMP_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(PUMP_PIN, GPIO.OUT)

# Define a function to preprocess the image
def preprocess_image(image):
    image = cv2.resize(image, (224, 224))
    image = image.astype(np.float32) / 255.0  # Normalize pixel values
    return np.expand_dims(image, axis=0)

# Function to start the motor pump
def start_motor_pump():
    GPIO.output(PUMP_PIN, GPIO.HIGH)  # Turn on the motor pump
    time.sleep(5)  # Spray for 5 seconds
    GPIO.output(PUMP_PIN, GPIO.LOW)  # Turn off the motor pump

# Main loop for live plant disease detection
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame from camera.")
        break

    # Preprocess the image
    input_data = preprocess_image(frame)

    # Set the input tensor
    input_details = interpreter.get_input_details()
    interpreter.set_tensor(input_details[0]['index'], input_data)

    # Run inference
    interpreter.invoke()

    # Get the output tensor
    output_details = interpreter.get_output_details()
    output_data = interpreter.get_tensor(output_details[0]['index'])

    # Get the class index with the highest probability
    max_index = np.argmax(output_data)

    # Get the corresponding class name
    class_name = {
    0: 'Apple___Apple_scab',
    1: 'Apple___Black_rot',
    2: 'Apple___Cedar_apple_rust',
    3: 'Apple___healthy',
    4: 'Blueberry___healthy',
    5: 'Cherry_(including_sour)___Powdery_mildew',
    6: 'Cherry_(including_sour)___healthy',
    7: 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    8: 'Corn_(maize)___Common_rust_',
    9: 'Corn_(maize)___Northern_Leaf_Blight',
    10: 'Corn_(maize)___healthy',
    11: 'Grape___Black_rot',
    12: 'Grape___Esca_(Black_Measles)',
    13: 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    14: 'Grape___healthy',
    15: 'Orange___Haunglongbing_(Citrus_greening)',
    16: 'Peach___Bacterial_spot',
    17: 'Peach___healthy',
    18: 'Pepper,_bell___Bacterial_spot',
    19: 'Pepper,_bell___healthy',
    20: 'Potato___Early_blight',
    21: 'Potato___Late_blight',
    22: 'Potato___healthy',
    23: 'Raspberry___healthy',
    24: 'Soybean___healthy',
    25: 'Squash___Powdery_mildew',
    26: 'Strawberry___Leaf_scorch',
    27: 'Strawberry___healthy',
    28: 'Tomato___Bacterial_spot',
    29: 'Tomato___Early_blight',
    30: 'Tomato___Late_blight',
    31: 'Tomato___Leaf_Mold',
    32: 'Tomato___Septoria_leaf_spot',
    33: 'Tomato___Spider_mites Two-spotted_spider_mite',
    34: 'Tomato___Target_Spot',
    35: 'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    36: 'Tomato___Tomato_mosaic_virus',
    37: 'Tomato___healthy'
}

    class_name = class_name[max_index]

    # Check if the class name includes "healthy"
    if "healthy" in class_name.lower():
        output = "healthy"
    else:
        output = "diseased"
        # Start the motor pump
        start_motor_pump()

    print("Output:", output)

    # Display the frame
    cv2.imshow('Plant Disease Detection', frame)

    # Check for key press to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()

