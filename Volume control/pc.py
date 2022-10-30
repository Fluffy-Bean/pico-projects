import asyncio as Async
from subprocess import call
import serial as Serial
import time as Time
import json as Json


PORT    = '/dev/ttyACM0'
RATE    = 115200
#RATE    = 9600


is_connected = False


def connect(dev: str, rate: int):
    try:
        ser = Serial.Serial(dev, rate)
        return ser
    except Serial.SerialException as e:
        #print(f"Error: {e}")
        return None


try:
    while True:
        while not is_connected:
            dev = connect(PORT, RATE)
            
            if dev is not None:
                is_connected = True
                print("Pico connected!")
            else:
                is_connected = False
                print("Device unavailable, retrying in 5 seconds...")
                Time.sleep(5)
        
        try:
            while dev is not None:
                read = dev.readline().decode('utf-8').strip()
                #print (read)
                
                if read != "":
                    try:
                        data = Json.loads(read)
                    except Json.decoder.JSONDecodeError as e:
                        print (e)
                        #print (read)
                    
                    if data.get("get_volume") != None:
                        try:
                            tmp_vol = call(["awk -F\"[][]\" '/Left:/ { print $2 }' <(amixer sget Master) | tr -d '%'"])
                        except:
                            tmp_vol = 50
                        
                        return_data = {
                            "volume": tmp_vol
                        }
                        
                        Serial.write(Json.dumps(return_data).encode('utf-8'))
                        #print (return_data)
                    
                    elif data.get("get_music") != None:                  
                        for i in data["get_music"]:
                            if i == "track":
                                try:
                                    tmp_title = call(["playerctl", "-p %any -i firefox", "metadata", "--format {{title}}"])
                                except:
                                    tmp_title = "None"
                            elif i == "artist":
                                try:
                                    tmp_artist = call(["playerctl", "-p %any -i firefox", "metadata", "--format {{artist}}"])
                                except:
                                    tmp_artist = "None"
                        
                        return_data = {
                            "track": tmp_title,
                            "artist": tmp_artist
                        }
                        
                        Serial.write(Json.dumps(return_data).encode('utf-8'))
                        #print (return_data)
                        
                    else:
                        if data.get("muted") == True:
                            call(["amixer", "-D", "pulse", "sset", "Master", "off", "-q"])
                            print ("Muted")
                        elif data.get("muted") == False:
                            call(["amixer", "-D", "pulse", "sset", "Master", "on", "-q"])
                            print ("Unmuted")
                            
                        if data.get("volume") != None:
                            call(["amixer", "-D", "pulse", "sset", "Master", str(data["volume"])+"%", "-q"])
                            print (f"Volume set to {data['volume']}")
        except Serial.SerialException as e:
            is_connected = False
except KeyboardInterrupt:
    print("Exiting...")
    exit(0)