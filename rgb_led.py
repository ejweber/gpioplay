# Either display color changing patter or user input color with RGB LED.

import RPi.GPIO as GPIO
import time
import threading

# establish pin number, pulses, cycle speed, and initial color globally
R = 16
G = 20
B = 21
pins = (R, G, B)
pulse = {}
col = 0x800000

def setup():
    GPIO.setmode(GPIO.BCM) # number pins by microcontroller identification
    GPIO.setup(pins, GPIO.OUT, initial=GPIO.HIGH) # set pins to output and off

    global pulse
    pulse['R'] = GPIO.PWM(R, 100)
    pulse['G'] = GPIO.PWM(G, 100)
    pulse['B']= GPIO.PWM(B, 100)

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

def color_cycle(col, keypress):
    values = parse_color(col)
    max_value = max(values)
    max_index = values.index(max_value)
    start_flag = False
    while not keypress.is_set():
        set_color(values)
        rising = (max_index + 1) % 3
        falling = (max_index + 2) % 3    
        if values[max_index] < 255:
            values[max_index] = values[max_index] + 1
        elif values[max_index] == 255:
            start_flag = True
        if values[rising] < 255:
            if start_flag == False and values[rising] > 0:
                values[rising] = values[rising] - 1
            if start_flag == True and values[falling] == 0:
                values[rising] = values[rising] + 1
        if values[falling] > 0:
            values[falling] = values[falling] - 1
        if values[max_index] == 255 and values[rising] == 255:
            max_index = rising
        time.sleep(0.01)
    return

def key_logger(keypress):
    print('Looping through colors...')
    input('Press enter to exit the color change loop.')
    keypress.set()

    
def mainloop():
    global col
    while True:
        keypress = threading.Event()
        loop = threading.Thread(target=key_logger, args=(keypress,))
        loop.start()
        color_cycle(col, keypress)
        col = input("Type 'exit' or a hex string of the format "
                     '0xrrggbb: ')
        if col == 'exit':
            return
        col = int(col, 16)
        values = parse_color(col)
        print(set_color(values))
        for t in range(0,10):
            print('Loop will start again in ' + str(10 - t) + ' seconds.')
            time.sleep(1)
     
if __name__ == '__main__':
    try:
        setup()
        mainloop()
        destroy()
    except KeyboardInterrupt:
        destroy()

