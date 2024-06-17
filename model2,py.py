import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import json

# Initialize GPIO for Ultrasonic Sensor
TRIG_PIN = 23
ECHO_PIN = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Initialize GPIO for Relay
RELAY_PIN = 17  # GPIO pin connected to the relay
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)  # Initially, turn off the relay

# Initialize OpenCV
cap = cv2.VideoCapture(0)
cap.set(3, 320)
cap.set(4, 240)

# MQTT setup
TOKEN = 'YOUR_DEVICE_TOKEN'
MQTT_BROKER = 'demo.thingsboard.io'
PORT = 1883

client = mqtt.Client()
client.username_pw_set(TOKEN)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

client.on_connect = on_connect
client.connect(MQTT_BROKER, PORT, 60)
client.loop_start()

def publish_status(status):
    data = {'leaf_status': status}
    client.publish('v1/devices/me/telemetry', json.dumps(data))

def detect_leaf(img):
    kernel = np.ones((7, 7), np.uint8)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define the range for brown color (disease)
    lower_brown = np.array([8, 60, 20])
    upper_brown = np.array([30, 255, 200])
    mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)

    # Define the range for green color (healthy)
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([90, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Combine masks for brown and green
    mask = cv2.bitwise_or(mask_brown, mask_green)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    return mask

def measure_distance():
    # Function to measure distance using ultrasonic sensor
    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(0.5)

    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    pulse_end = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

redCount = 0
greenCount = 0

try:
    while True:
        # Measure distance using ultrasonic sensor
        distance = measure_distance()

        # Check if object is within range (e.g., 10cm)
        if 2 < distance < 10:  # Adjust distance threshold as needed
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break

            mask = detect_leaf(frame)
            contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            output = frame

            if contours:
                c = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(c)
                crop_img = frame[y:y + h, x:x + w]

                # Determine dominant color (red or green) for disease detection
                green_value = np.mean(crop_img[:, :, 1])
                red_value = np.mean(crop_img[:, :, 2])
                if green_value > red_value:
                    greenCount += 1
                    redCount = 0
                    cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
                else:
                    redCount += 1
                    greenCount = 0
                    cv2.rectangle(output, (x, y), (x + w, y + h), (0, 0, 255), 2)

            if redCount > 10:
                redCount = 0
                greenCount = 0
                print('Diseased Leaf Detected')
                publish_status('Diseased')

                # Activate the motor pump
                GPIO.output(RELAY_PIN, GPIO.LOW)
                print('Relay ON - Spraying Pesticide')
                time.sleep(10)  # Spray for 10 seconds
                GPIO.output(RELAY_PIN, GPIO.HIGH)
                print('Relay OFF - Pesticide Spraying Complete')
            elif greenCount > 10:
                greenCount = 0
                redCount = 0
                print('Healthy Leaf Detected')
                publish_status('Healthy')

            cv2.imshow('frame', output)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            # If no object is detected within range, reset counts
            redCount = 0
            greenCount = 0

except KeyboardInterrupt:
    print("Keyboard interrupt detected. Cleaning up GPIO...")
    GPIO.cleanup()

finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()
