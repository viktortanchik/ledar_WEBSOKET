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
        <canvas id="canvas" width="1000" height="1000"></canvas>

        <script>
         function drawPoint(context, x, y, label, color, size) {
      	if (color == null) {
        	color = 'red';
        }
        if (size == null) {
            size = 5;
        }
      
      	var radius = 0.5 * size;

      	// to increase smoothing for numbers with decimal part
		var pointX = Math.round(x - radius);
        var pointY = Math.round(y - radius);
  
        context.beginPath();
        context.fillStyle = color;
      	context.fillRect(pointX, pointY, size, size);
        context.fill();
      
    
    }

            
            var ws = new WebSocket("ws://localhost:8000/ws");

            ws.onmessage = function(event) {
                let messages = document.getElementById('messages')
                let message = document.createElement('li')
                let content = document.createTextNode(JSON.parse(event.data).message+" - "+JSON.parse(event.data).time)
                messages.innerHTML = JSON.parse(event.data).XY+" -    "+JSON.parse(event.data).XYnex
                let Xnow = Number(JSON.parse(event.data).XY[0])
                let Ynow = Number(JSON.parse(event.data).XY[1])
                let Xnex = Number(JSON.parse(event.data).XYnex[0])
                let Ynex = Number(JSON.parse(event.data).XYnex[1])
                
                var canvas = document.querySelector('#canvas');
                var context = canvas.getContext('2d');
            
                drawPoint(context, Xnow+500, Ynow+500, 'red', 1);
                        
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
        XY=[]
        with open("XY.csv", "r") as file1:
            for line in file1:
                reader = csv.reader(file1)
                for row in reader:
                    XY.append(row)
        for i in range(len(XY)):
            data = await websocket.receive_text()
            #print(XY[i][0])
            await websocket.send_text(json.dumps({"message": data, "XY": XY[i],"XYnex":XY[i+1]}))
        XY=0


