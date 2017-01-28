import threading
import time

def key_logger(keystroke):
    input('Press enter to stop loop.\n')
    keystroke.set()  

def mainloop():
    keystroke = threading.Event()
    input_loop = threading.Thread(target=key_logger, args=(keystroke,))
    input_loop.start()
    number = 0
    while not keystroke.is_set():
        print(number)
        number += 1
        time.sleep(0.1)
    input('Now something else can happen if you input what you will.')
        

mainloop()
