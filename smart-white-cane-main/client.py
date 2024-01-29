import RPi.GPIO as GPIO
import time
import socket
import geopy
import geocoder


PORT = 8080
SERVER_ADDRESS = "192.168.43.140"
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((SERVER_ADDRESS, PORT))


GPIO.setmode(GPIO.BCM)

TRIG = 17
ECHO = 18

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

try:
    while True:
        GPIO.output(TRIG, False)
        time.sleep(2)

        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)

        print("Distance:", distance, "cm")
        msg=str(distance)+" "+str(geocoder.ip('me').latlng[0])+" "+str(geocoder.ip('me').latlng[1])
        client_socket.sendall(msg.encode())

        time.sleep(1)

except KeyboardInterrupt:
    client_socket.close()
    GPIO.cleanup()



