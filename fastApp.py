import uvicorn
from fastapi import FastAPI, File, UploadFile, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pathlib as pathlib
import os as os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://10.6.7.214:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
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


@app.get("/websocket")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.get("/formb", response_class=HTMLResponse)
async def read_items():
    return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Take a High Resolution Photo with WebRTC</title>
        <style>
        .home {
            display: flex;
            align-items: center;
            flex-direction: column;
        }
        #hiddenCanvas {
            display: none;
        }

        .camera {
            display: none;
            max-width: 100%;
        }

        #photoTaken {
            max-width: 100%;
        }

        #file {
            display: none;
        }
        </style>
        </head>
        <body>
        <div class="home">
            <h2>Take a Photo</h2>
            <label>
            Camera:
            <select id="cameraSelect"></select>
            </label>
            <br/>
            <label>
            Desired Resolution:
            <select id="resolutionSelect">
                <option value="640x480">640x480</option>
                <option value="1280x720">1280x720</option>
                <option value="1920x1080">1920x1080</option>
                <option value="3840x2160">3840x2160</option>
            </select>
            </label>
            <br/>
            <div>
            <button id="startCameraBtn">Start Camera</button>
            <button id="takePhotoBtn">Take Photo</button>
            <button id="loadFileBtn">
                Load File
            </button>
            <input type="file" id="file" onchange="loadImageFromFile();" accept=".jpg,.jpeg,.png,.bmp" />
            </div>
            <br/>
            <video class="camera" muted autoplay="autoplay" playsinline="playsinline" webkit-playsinline></video>
            <br/>
            <canvas id="hiddenCanvas"></canvas>
            <img id="photoTaken" />
            <div id="info"></div>
        </div>
        <script>
            const cameraSelect = document.getElementById("cameraSelect");
            const resolutionSelect = document.getElementById("resolutionSelect");
            const video = document.querySelector("video");
            const canvas = document.getElementById("hiddenCanvas");
            
            document.getElementById("startCameraBtn").addEventListener('click', (event) => {
                console.log("start camera");
                let options = {};
                if (cameraSelect.selectedIndex != -1) {
                options.deviceId = cameraSelect.selectedOptions[0].value;
                }
                if (resolutionSelect.selectedIndex != -1) {
                let width = parseInt(resolutionSelect.selectedOptions[0].value.split("x")[0]);
                let height = parseInt(resolutionSelect.selectedOptions[0].value.split("x")[1]);
                let res = {width:width,height:height};
                options.desiredResolution = res;
                }
                play(options);
            });
            
            document.getElementById("takePhotoBtn").addEventListener('click', async (event) => {
                let src;
                if (imageCapture) {
                try {
                    let blob = await imageCapture.takePhoto();
                    src = URL.createObjectURL(blob);
                }catch(e) {
                    src = captureFrame();
                }
                }else{
                src = captureFrame();
                }
                document.getElementById("photoTaken").src = src;
            });
            
            document.getElementById("loadFileBtn").addEventListener('click', async (event) => {
                document.getElementById("file").click();
            });
            
            document.getElementById("photoTaken").onload = function(){
                let img = document.getElementById("photoTaken");
                document.getElementById("info").innerText = "Image Width: " + img.naturalWidth + "Image Height: " + img.naturalHeight;
            }

            let imageCapture;
            let localStream;
            let cameraDevices = [];
            window.onload = async function() {
                await requestCameraPermission();
                await loadCameraDevices();
                loadCameraDevicesToSelect();
            }
            
            async function loadCameraDevices(){
                const constraints = {video: true, audio: false};
                const stream = await navigator.mediaDevices.getUserMedia(constraints);
                const devices = await navigator.mediaDevices.enumerateDevices();
                for (let i=0;i<devices.length;i++){
                let device = devices[i];
                if (device.kind == 'videoinput'){ // filter out audio devices
                    cameraDevices.push(device);
                }
                }
                const tracks = stream.getTracks(); // stop the camera to avoid the NotReadableError
                for (let i=0;i<tracks.length;i++) {
                const track = tracks[i];
                track.stop();
                }
            }
            
            function loadCameraDevicesToSelect(){
                for (let i=0;i<cameraDevices.length;i++){
                let device = cameraDevices[i];
                cameraSelect.appendChild(new Option(device.label,device.deviceId))
                }
            }
            
            
            async function requestCameraPermission() {
                const constraints = {video: true, audio: false};
                const stream = await navigator.mediaDevices.getUserMedia(constraints);
                const tracks = stream.getTracks();
                for (let i=0;i<tracks.length;i++) {
                const track = tracks[i];
                track.stop();  // stop the opened camera
                }
            }
            
            function play(options) {
                stop(); // close before play
                video.style.display = "block";
                let constraints = {};
            
                if (options.deviceId){
                constraints = {
                    video: {deviceId: options.deviceId},
                    audio: false
                }
                }else{
                constraints = {
                    video: {width:1280, height:720,facingMode: { exact: "environment" }},
                    audio: false
                }
                }

                if (options.desiredResolution) {
                constraints["video"]["width"] = options.desiredResolution.width;
                constraints["video"]["height"] = options.desiredResolution.height;
                }

                navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
                localStream = stream;
                // Attach local stream to video element      
                video.srcObject = stream;
                if ("ImageCapture" in window) {
                    const track = localStream.getVideoTracks()[0];
                    imageCapture = new ImageCapture(track);
                }
                }).catch(function(err) {
                console.error('getUserMediaError', err, err.stack);
                });
            }
            
            function stop() {
                try{
                if (localStream){
                    const tracks = localStream.getTracks();
                    for (let i=0;i<tracks.length;i++) {
                    const track = tracks[i];
                    track.stop();
                    }
                }
                } catch (e){
                alert(e.message);
                }
            };
            
            function captureFrame(){
                let w = video.videoWidth;
                let h = video.videoHeight;
                canvas.width  = w;
                canvas.height = h;
                let ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, w, h);
                return canvas.toDataURL("image/jpeg")
            }

            function loadImageFromFile(){
                let fileInput = document.getElementById("file");
                let files = fileInput.files;
                if (files.length == 0) {
                return;
                }
                let file = files[0];
                fileReader = new FileReader();
                fileReader.onload = function(e){
                document.getElementById("photoTaken").src = e.target.result;
                };
                fileReader.onerror = function () {
                console.warn('oops, something went wrong.');
                };
                fileReader.readAsDataURL(file);
            }
        </script>
        </body>
        </html>
    """

@app.get("/forma", response_class=HTMLResponse)
async def read_items():
    return """
    <html>
        <head>
            <title>Take a picture</title>
        </head>
        <body>
            <h1>Schick mir ein Bild</h1>

            <FORM id="theForm" name="theForm" action="/upload/" method="POST" enctype="multipart/form-data">
                <input type="button" value="click" onclick="doIt();" />
                <input id="file-upload" style="display:none;" type="file" name="file" accept="image/*" capture="camera">
                <button id="submit" type="submit">Submit</button>
            </FORM>

            <script>
                async function doIt(){
                    document.getElementById('file-upload').click();
                    await delay(5000);
                    var form = document.getElementById('theForm');
                    alert("hallo");
                    form.requestSubmit();    
                    return 1;
                }
            </script>

        </body>
    </html>
    """


uploads = 'uploads'
uploads_dir = pathlib.Path(os.getcwd(), uploads)

@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        file_name = pathlib.Path(uploads_dir, file.filename)
        with open(file_name, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}

#if __name__ == "__main__":
#   uvicorn.run("fastApp:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    #uvicorn.run("fastApp:app", host="0.0.0.0", port=8000, reload=True)
    uvicorn.run("fastApp:app", host="0.0.0.0", port=8000,  reload=True, ssl_keyfile="key.pem", ssl_certfile="cert.pem")

