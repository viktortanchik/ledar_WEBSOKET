# -*- coding: utf-8 -*-

import numpy as np
from collections import namedtuple
from itertools import chain
import sys

import serial  # For this one, you must install pyserial, not serial
from enum import Enum
import time
import math

# SERIAL_PORT = "/dev/ttyS5"   # for Orange Pi Zero 2's serial port
# SERIAL_PORT = "COM10"#/dev/ttyUSB0"  # for Other PC's USB to Serial module
SERIAL_PORT = "/dev/ttyUSB0"  # for Other PC's USB to Serial module


class State(Enum):
    START1 = 0
    START2 = 1
    HEADER = 2
    DATA = 3


def readbytes(file, count):
    data = ser.read(count)
    # data = f.read(count)
    if len(data) != count:
        print("End of file")
        return False
    return data


try:
    # f = open(file_name, "rb")
    ser = serial.Serial(SERIAL_PORT, 153600, timeout=0.1)
    time.sleep(1)
except:
    print("could not connect to device")
    exit()
step = (math.pi * 2)


###### Get Full Circle of Data
def GetDataFromOneFullCycle():
    counter = 0
    ThisRoundCount = 0  # counts within one round
    maxThisRound = 0  # Number of good numbers for this cycle
    global pos  # using globla pos array will ensure we as storing data in same spot
    global spots  # using globla spots array will ensure we as storing data in same spot
    run = True
    try:
        state = State.START1
        while run:
            if state == State.START1:
                data = ser.read(1)
                # data = readbytes(f, 1)
                if data[0] == 0xAA:
                    state = State.START2
                continue
            elif state == State.START2:
                data = ser.read(1)
                # data = readbytes(f, 1)
                if data[0] == 0x55:
                    state = State.HEADER
                else:
                    state = State.START1
                continue
            elif state == State.HEADER:
                data = ser.read(8)
                # data = readbytes(f, 8)
                pack_type = data[0]
                data_lenght = int(data[1])
                start_angle = int(data[3] << 8) + int(data[2])
                stop_angle = int(data[5] << 8) + int(data[4])
                # unknown = int(data[7] << 8) + int(data[6])
                diff = stop_angle - start_angle
                if stop_angle < start_angle:
                    diff = 0xB400 - start_angle + stop_angle
                angle_per_sample = 0
                if diff > 1 and (data_lenght - 1) > 0:
                    angle_per_sample = diff / (data_lenght - 1)
                counter += 1
                state = State.DATA
                continue

            elif state == State.DATA:
                setX =0
                setY =0
                setX=[]
                setY=[]
                state = State.START1
                # read data
                data = ser.read(data_lenght * 3)
                # data = readbytes(f, data_lenght * 3)
                if data == False:
                    break
                for i in range(0, data_lenght):
                    data0 = int(data[i * 3 + 0])
                    data1 = int(data[i * 3 + 1])
                    data2 = int(data[i * 3 + 2])
                    distance = (data2 << 8) + data1

                    angle = (start_angle + angle_per_sample * i)
                    anglef = step * (angle / 0xB400)
                    # print("[{}]\tangle:{},\tanglef {},\tdist: {}".format(i, data0, (anglef + anglePlus), (distance/1000)), end="\n")
                    distanceDivided = distance / 1000  # div to convert mm to meter
                    # if (data0 != 1) & (distanceDivided < 3) :
                    if (distanceDivided < 120):
                        distanceDivided = (distance / 5)  # Adjust distance ratio.  It is too large

                        x = distanceDivided * np.cos(anglef)
                        y = distanceDivided * np.sin(anglef)
                        setX.append(x)
                        setY.append(y)


                        # x = float('{:.10f}'.format(x))
                        # y = float('{:.10f}'.format(y))
                        # print(y)
                        ThisRoundCount += 1
                        if pack_type != 40:
                            ser.reset_input_buffer()
                            ThisRoundCount = 0
                            # print("END ROUND")

                        if len(setX) == 500:
                            return setX, setY



            else:
                print("error")

    except KeyboardInterrupt:
        run = False
        exit()


# ==================================================WEBSOKET==================================================
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json
from datetime import datetime
import csv

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>

        <a href="http://127.0.0.1:8000/FTSE%20100">STATISTIC</a>
        <h1>WebSocket Real Time Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>


        </form>
        <div id='messages'>
        </div>
        <canvas id="canvas" width="2000" height="2000"></canvas>

        <script>
        let cler = 0;

                     function drawPoint(context, X, Y, label, color, size)
                      {
                     for (let i =0; i < X.length; i++)
                     {
                     let x = 0
                     let y = 0
                     x=X[i]
                     y=Y[i]
            
                    if (color == null) {
                        color = 'red';
                    }
                    if (size == null) {
                        size = 5;
                    }
                    cler++;
                    if (cler ==360)
                    {
                        context.save();
                        context.setTransform(1, 0, 0, 1, 0, 0);
                        context.clearRect(0, 0, canvas.width, canvas.height);
                        context.restore();
                        cler=0;
                    }
                    let radius = 0.5 * 100;
            
                    // to increase smoothing for numbers with decimal part
                    let pointX = Math.round(x - radius);
                    let pointY = Math.round(y - radius);
            
                    context.beginPath();
            
                    context.fillStyle = "#FF0000";
                    context.fillRect(pointX, pointY, 10, 10);
                    context.fill();
                    context.arc(950, 950, 50, 0, Math.PI * 2, true); // Outer circle
                    context.arc(950, 950, 250, 0, Math.PI * 2, true); // Outer circle
                    context.arc(950, 950, 500, 0, Math.PI * 2, true); // Outer circle
                    context.arc(950, 950, 750, 0, Math.PI * 2, true); // Outer circle
                    context.arc(950, 950, 1000, 0, Math.PI * 2, true); // Outer circle
                    context.arc(950, 950, 1250, 0, Math.PI * 2, true); // Outer circle
                    context.arc(950, 950, 1500, 0, Math.PI * 2, true); // Outer circle
                    context.arc(950, 950, 1750, 0, Math.PI * 2, true); // Outer circle
                    context.arc(950, 950, 2000, 0, Math.PI * 2, true); // Outer circle
            
                    context.closePath();
                    context.stroke();
                    }
                }
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                let messages = document.getElementById('messages')
                let message = document.createElement('li')
                let content = document.createTextNode(JSON.parse(event.data).message+" - "+JSON.parse(event.data).time)
                messages.innerHTML = JSON.parse(event.data).X+" -    "+JSON.parse(event.data).Y
                let Xnow = JSON.parse(event.data).X
                let Ynow = JSON.parse(event.data).Y           
                let canvas = document.querySelector('#canvas');
                let context = canvas.getContext('2d');
                console.log("Xnow",Xnow);
                console.log("Ynow",Ynow);


               
               
                drawPoint(context, Xnow, Ynow, 'red', 1);
            };
            setInterval(()=>{
                ws.send('df')
            }, 0);
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        # print(XY[i][0])
        X, Y = GetDataFromOneFullCycle()
        await websocket.send_text(json.dumps({"message": data, "X": X, "Y": Y}))

# ============================================================================================================

