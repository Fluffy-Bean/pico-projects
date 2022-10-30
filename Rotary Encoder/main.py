from machine import Pin
import time

button_pin = Pin(16, Pin.IN, Pin.PULL_UP)
direction_pin = Pin(17, Pin.IN, Pin.PULL_UP)
step_pin  = Pin(18, Pin.IN, Pin.PULL_UP)

previous_value = True
button_down = False

count = 0

while True:    
    #print(f"dir: {direction_pin.value()}, step: {step_pin.value()}, button: {button_pin.value()}")
    
    if previous_value != step_pin.value():
        if step_pin.value() == False:
            if direction_pin.value() == False:
                count += 1
                print(count)
                # Left
            else:
                count -= 1
                print(count)
                # Right
                
        previous_value = step_pin.value()   
    
    if button_pin.value() == False and not button_down:
        button_down = True
        count = 0
        print(count)
        # Button pressed
        
    if button_pin.value() == True and button_down:
        button_down = False
        time.sleep(0.02)
        # Delay to prevent double click