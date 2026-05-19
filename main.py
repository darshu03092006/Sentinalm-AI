from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import cv2
from ultralytics import YOLO

app = FastAPI()

# Load YOLO model
model = YOLO("yolov8n.pt")

# Open video file
video = cv2.VideoCapture("store.mp4")


def generate_frames():

    while True:

        success, frame = video.read()

        # Restart video when video ends
        if not success:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # YOLO detection
        results = model.predict(frame, verbose=False)

        # Draw custom boxes
        for box in results[0].boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            confidence = float(box.conf[0])

            cls = int(box.cls[0])

            label = model.names[cls]

            # Detect only people
            if label == "person":

                # Suspicious logic
                if confidence > 0.75:
                    color = (0, 0, 255)  # RED
                    status = "Suspicious"
                else:
                    color = (0, 255, 0)  # GREEN
                    status = "Normal"

                # Draw rectangle
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    color,
                    3
                )

                # Put label
                cv2.putText(
                    frame,
                    status,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    color,
                    2
                )

        # Convert frame
        _, buffer = cv2.imencode('.jpg', frame)

        frame = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        )


@app.get("/")
def home():
    return {"status": "SentinelAI running"}


@app.get("/video_feed")
def video_feed():

    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )