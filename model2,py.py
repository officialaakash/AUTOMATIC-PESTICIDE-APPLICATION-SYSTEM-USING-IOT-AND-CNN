import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

# Setup GPIO pins for relay control
RELAY_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Function to activate motor pump for spraying pesticide
def spray_pesticide():
    print("Spraying pesticide")
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    time.sleep(10)  # Run motor pump for 10 seconds
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("Pesticide sprayed")

# Your existing detect_leaf function and variables go here...

# Main loop for detecting diseased plants and controlling motor pump
while True:
    ret, frame = cap.read()
    # Your existing code for plant disease detection goes here...

    if redCount > 250:  # If diseased plant detected
        redCount = 0
        greenCount = 0
        print('Diseased Leaf')
        spray_pesticide()  # Activate motor pump for spraying pesticide
    elif greenCount > 5:  # If healthy plant detected
        greenCount = 0
        redCount = 0
        print('Healthy Leaf')

    # Display output frame
    cv2.imshow('frame', output)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup GPIO
GPIO.cleanup()
cap.release()
cv2.destroyAllWindows()
