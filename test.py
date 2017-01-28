# Either display color changing patter or user input color with RGB LED.

import RPi.GPIO as GPIO
import time
import threading

# establish pin numbers and pulses globally
R = 16
G = 20
B = 21
pins = (R, G, B)
pulse = {}

def setup():
    GPIO.setmode(GPIO.BCM) # number pins by microcontroller identification
    GPIO.setup(pins, GPIO.OUT, initial=GPIO.HIGH) # set pins to output and off

    global pulse
    pulse['R'] = GPIO.PWM(R, 2000)
    pulse['G'] = GPIO.PWM(G, 2000)
    pulse['B']= GPIO.PWM(B, 2000)

    for pin in pulse:
        pulse[pin].start(100)

def col_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def off():
    GPIO.output(pins, GPIO.HIGH)
    

def parse_color(col):
    R_val = col >> 16 # shift G and B values out of col
    G_val = (col & 0x00ff00) >> 8 # erase R values and shift G values out of col
    B_val = col & 0x0000ff # erase R and G values out of col
    return [R_val, G_val, B_val]

def set_color(values):
    # take numbers from 0-255 and convert to duty cycles from 0-100
    R_val = col_map(values[0], 0, 255, 0, 100)
    G_val = col_map(values[1], 0, 255, 0, 100)
    B_val = col_map(values[2], 0, 255, 0, 100)
    # change duty cycles appropriately
    pulse['R'].ChangeDutyCycle(100 - R_val)
    pulse['G'].ChangeDutyCycle(100 - G_val)
    pulse['B'].ChangeDutyCycle(100 - B_val)
    # create string of color values in understandable format
    col_string = ('Red: {:.2f}%, Green: {:.2f}%, '
                  'Blue: {:.2f}%'.format(R_val, G_val, B_val))
    return col_string

def destroy():
    for pin in pulse:
        pulse[pin].stop
    GPIO.output(pins, GPIO.HIGH)
    GPIO.cleanup()

def color_cycle(col):
    initial_values = parse_color(col)
    set_color(initial_values)
    R = (initial_values[0], 1)
    G = (initial_values[1], 2)
    B = (initial_values[2], 3)
    values = [R, G, B]
    keystroke = threading.Event()
    loop = threading.Thread(target=key_logger, args=(keystroke,))
    loop.start()
    while not keystroke.is_set():
        print(values)
        new_values = []
        for value in values:
            if 0 <= (value[0] + value[1]) <= 255:
                new_values.append((value[0] + value[1], value[1]))
            else:
                new_values.append((value[0] - value[1], -value[1]))
        values = new_values
        color_values = (values[0][0], values[1][0], values[2][0])
        set_color(color_values)
        time.sleep(0.1)

def key_logger(keystroke):
    try:
        input('Press enter to exit the color change loop.')
        keystroke.set()
    except KeyboardInterrupt:
        return
    
def mainloop():
    col = 0x000000
    while True:
        color_cycle(col)
        col = int(input('Enter a hex string of the format 0xrrggbb: '), 16)
        values = parse_color(col)
        print(set_color(values))
        for t in range(0,10):
            print('Loop will start again in ' + str(10 - t) + ' seconds.')
            time.sleep(1)
     
if __name__ == '__main__':
    try:
        setup()
        mainloop()
    except KeyboardInterrupt:
        destroy()

