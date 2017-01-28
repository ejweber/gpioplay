# Change color of red/green LED based on user's hex input.

import RPi.GPIO as GPIO
import time

pins = (17, 18)

GPIO.setmode(GPIO.BCM) # number pins by physical location
GPIO.setup(pins, GPIO.OUT, initial=GPIO.LOW) # set pins to output and off

p_R = GPIO.PWM(pins[0], 2000)
p_G = GPIO.PWM(pins[1], 2000)

p_R.start(0)
p_G.start(0)

def col_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setColor(col):
    R_val = col >> 8 # shift col 8 bits right (to get at intended red value)
    G_val = col & 0x00FF # overwrite red bits (to get at intended green value)
    # take numbers from 0-255 and convert to duty cycles from 0-100
    R_val = col_map(R_val, 0, 255, 0, 100)
    G_val = col_map(G_val, 0, 255, 0, 100)
    # change duty cycles appropriately
    p_R.ChangeDutyCycle(R_val)
    p_G.ChangeDutyCycle(G_val)
    # create string of color values in understandable format
    string = 'Red: {:.2f}%, Green: {:.2f}%'.format(R_val, G_val)
    return string

def destroy():
    p_R.stop()
    p_G.stop()
    GPIO.output(pins, GPIO.LOW)
    GPIO.cleanup()

def mainloop():
    while True:
        col = int(input('Enter a hex string of the format 0xRRGG: '), 16)
        print(setColor(col))
        
if __name__ == '__main__':
    try:
        mainloop()
    except KeyboardInterrupt:
        destroy()
    

