from machine import Pin
import sys as Sys
import time as Time
import json as Json
#import uasyncio as asyncio


# SET UP THE PINS
LED         = Pin(25, Pin.OUT)
BTN         = Pin(16, Pin.IN, Pin.PULL_UP)
ROTARY_DIR  = Pin(17, Pin.IN, Pin.PULL_UP)
ROTARY_STP = Pin(18, Pin.IN, Pin.PULL_UP)

# SET UP THE VARIABLES
btn_down        = False
prev_step       = True
rotations       = 0
prev_pass       = 0

# SET UP DEFAULT VALUES
data            = {
    "volume": 50,
    "muted": False,
    #"playing": False,
    #"skip": False,
    #"track": "None",
    #"artist": "None"
}
tmp_data        = {}


def vol_update(rotation, prev_rotation, vol):
    if rotation > prev_rotation:
        vol += 1
    else:
        vol -= 1
    
    if vol <= 0:
        vol = 0
    elif vol >= 100:
        vol = 100

    return vol

def check_data(data, tmp):
    diff = 0
    
    for i in data:
        if data.get(i) != tmp.get(i):
            diff += 1
            tmp[i] = data[i]
    
    return diff

def request_track(data):
    try:
        query = {
            "music": ['track', 'artist']
        }
        
        print (Json.dumps(query).encode('utf-8'))
        
        recived = Sys.stdin.readline().strip()
        recived = Json.loads(recived.decode('utf-8'))
        
        data["track"]   = recived.get("track")
        data["artist"]  = recived.get("artist")
        
        return True
    except:
        data["track"]   = "None"
        data["artist"]  = "None"
        
        return False
    
def request_volume(data):
    try:
        query = {
            "get_volume": ['volume']
        }
        
        print (Json.dumps(query).encode('utf-8'))
        
        recived = Sys.stdin.readline().strip()
        recived = Json.loads(recived.decode('utf-8'))
        
        data["volume"]   = recived.get("volume")
        
        return True
    except:
        data["volume"] = 50
        
        return False


try:
    # REUEST INFO FROM THE HOST COMPUTER
    #if request_track(data):
    #    print ("Track recieved")
        
    #if request_volume(data):
    #    print ("Volume recieved")        
    
    while True:
        # READ ROTARY ENCODER
        if prev_step != ROTARY_STP.value():
            if ROTARY_STP.value() == False:
                if ROTARY_DIR.value() == False:     # Left
                    LED.toggle()
                    rotations += 1
                    LED.toggle()
                else:                               # Right
                    LED.toggle()
                    rotations -= 1
                    LED.toggle() 
            prev_step = ROTARY_STP.value()   
        
        # READ BUTTON
        if BTN.value() == False and not btn_down: # Button pressed
            LED.toggle()
            btn_down = True
            
            if data["muted"]:
                data["muted"] = False
            else:
                data["muted"] = True
            
            LED.toggle()
        if BTN.value() == True and btn_down: # Debouce
            btn_down = False
            Time.sleep(0.02)
            
        # PROCESS AUDIO DATA
        if rotations != prev_pass:
            data["volume"] = vol_update(rotations, prev_pass, data["volume"])
            prev_pass = rotations
        
        # SEND DATA TO PC IF CHANGED
        if (check_data(data, tmp_data) > 0):
            print(Json.dumps(data))
        
except KeyboardInterrupt:
    print("Exiting...")
    