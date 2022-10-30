from machine import I2C, Pin
from pico_i2c_lcd import I2cLcd
import time
import math
import _thread

'''
Assign pins to the rotary encoder, button and LCD
'''
button_pin		= Pin(16, Pin.IN, Pin.PULL_UP)
direction_pin	= Pin(17, Pin.IN, Pin.PULL_UP)
step_pin		= Pin(18, Pin.IN, Pin.PULL_UP)

i2c				= I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
I2C_ADDR		= i2c.scan()[0]
lcd				= I2cLcd(i2c, I2C_ADDR, 2, 16)

'''
Create special characters for the LCD such as progress bar for volume
'''
prog_1 = ( 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111 );    lcd.custom_char(5, prog_1)
prog_2 = ( 0b11110, 0b11110, 0b11110, 0b11110, 0b11110, 0b11110, 0b11110, 0b11110 );    lcd.custom_char(4, prog_2)
prog_3 = ( 0b11100, 0b11100, 0b11100, 0b11100, 0b11100, 0b11100, 0b11100, 0b11100 );	lcd.custom_char(3, prog_3)
prog_4 = ( 0b11000, 0b11000, 0b11000, 0b11000, 0b11000, 0b11000, 0b11000, 0b11000 );	lcd.custom_char(2, prog_4)
prog_5 = ( 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000 );	lcd.custom_char(1, prog_5)
blank = ( 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000 );     lcd.custom_char(6, blank)

'''
Values for rotary encoder, button debounce and progress bar length
'''
previous_value	= True
button_down		= False
count           = 0

bar             = 12
seg             = 5

def update_screen():
    '''
    Initiate some values for the display
    '''
    last_update	= round(time.time())
    backlight	= True
    prev_count	= 1
    
    lcd.clear()
    lcd.hide_cursor()
    
    while True:
        if count != prev_count:
            prev_count  = count
            last_update = round(time.time())
            
            lcd.move_to(0,0)
            
            if not backlight:
                lcd.backlight_on()
                backlight = True
            
            if len(str(count)) == 1:
                lcd.putstr(f"  {count} ")
            elif len(str(count)) == 2:
                lcd.putstr(f" {count} ")
            else:
                lcd.putstr(f"{count} ")
                
            # If count is over of under the progress bar length
            # correct the value
            a = count
            if a < 0:
                a = 0
            elif a > 100:
                a = 100
            
            # Calculate value of one bar
            h = 100 / bar
            # Calculate value of one segment
            j = h / seg
            
            # Calculate number of bars
            k = int(math.floor(a / h))
            # Calculate number of segments
            y = int(math.floor((a - (k * h)) / j))
            
            #print (f"count: {count} k: {k} j: {j} h: {h} y: {y}")            
            
            # Display the progress bar
            lcd.putstr(chr(5)*k)
            if y >= 1:
                lcd.putstr(chr(y))
                lcd.putstr(chr(6)*((bar - 1) - k))
            else:
                lcd.putstr(chr(6)*(bar - k))
            
        else:
            if round(time.time()) > (last_update + 5) and backlight:
                lcd.backlight_off()
                backlight = False

_thread.start_new_thread(update_screen, ())

while True:
    if previous_value != step_pin.value():
        if step_pin.value() == False:
            if direction_pin.value() == False:
                count += 1
                # Left
            else:
                count -= 1
                # Right

        previous_value = step_pin.value()

    if button_pin.value() == False and not button_down:
        button_down = True
        count = 0
        # Button pressed

    if button_pin.value() == True and button_down:
        button_down = False
        time.sleep(0.02)
        # Delay to prevent double
    