from typing import List
import cv2
import time
import json
import os
import math
from datetime import datetime
from ultralytics import YOLO

ALERTS_FILE = "alerts.json"
SUSPICIOUS_THRESHOLD = 0.6


class SentinelDetector:
    def __init__(self):
        print("[SentinelAI] Loading YOLOv8 model...")
        self.model = YOLO("yolov8n.pt")  # auto-downloads on first run
        self.cap = None
        self.running = False
        self.latest_frame_data = {
            "people_count": 0,
            "suspicious_score": 0.0,
            "timestamp": None,
        }
        self.alerts = self._load_alerts()

    # ------------------------------------------------------------------ #
    #  Alert persistence                                                   #
    # ------------------------------------------------------------------ #

    def _load_alerts(self):
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, "r") as f:
                return json.load(f)
        return []

    def _save_alert(self, alert: dict):
        self.alerts.append(alert)
        with open(ALERTS_FILE, "w") as f:
            json.dump(self.alerts, f, indent=2)

    # ------------------------------------------------------------------ #
    #  Suspicious-score logic                                              #
    # ------------------------------------------------------------------ #

    def _compute_suspicious_score(
        self, people_count: int, confidences: List[float], frame_area: int, boxes: list
    ) -> float:
        """
        Heuristic score in [0, 1] based on:
        - Number of people detected
        - Average detection confidence
        - Proximity of detected persons (bounding-box overlap / crowding)
        """
        if people_count == 0:
            return 0.0

        # --- component 1: crowd factor (saturates at 5+ people) ----------
        crowd = min(people_count / 5.0, 1.0)

        # --- component 2: avg confidence of detections -------------------
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        # --- component 3: crowding / proximity ---------------------------
        # rough measure: total bbox area vs frame area
        total_box_area = sum((x2 - x1) * (y2 - y1) for x1, y1, x2, y2 in boxes)
        density = min(total_box_area / max(frame_area, 1), 1.0)

        score = 0.4 * crowd + 0.3 * avg_conf + 0.3 * density
        return round(min(score, 1.0), 3)

    # ------------------------------------------------------------------ #
    #  Main detection loop (runs in a background thread)                  #
    # ------------------------------------------------------------------ #

    def start(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open webcam. Check device index or permissions.")
        self.running = True
        print("[SentinelAI] Detection loop started.")
        self._loop()

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        print("[SentinelAI] Detection loop stopped.")

    def _loop(self):
        frame_h, frame_w = None, None

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("[SentinelAI] Failed to read frame — retrying...")
                time.sleep(0.1)
                continue

            if frame_h is None:
                frame_h, frame_w = frame.shape[:2]
                frame_area = frame_h * frame_w

            # Run YOLOv8 inference (only 'person' class = 0)
            results = self.model(frame, classes=[0], verbose=False)[0]

            boxes = []
            confidences = []

            for box in results.boxes:
                conf = float(box.conf[0])
                if conf < 0.4:
                    continue
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                boxes.append((x1, y1, x2, y2))
                confidences.append(conf)

            people_count = len(boxes)
            score = self._compute_suspicious_score(
                people_count, confidences, frame_area, boxes
            )

            now = datetime.utcnow().isoformat()
            self.latest_frame_data = {
                "people_count": people_count,
                "suspicious_score": score,
                "timestamp": now,
            }

            # Log alert if threshold exceeded
            if score >= SUSPICIOUS_THRESHOLD:
                alert = {
                    "id": len(self.alerts) + 1,
                    "timestamp": now,
                    "people_count": people_count,
                    "suspicious_score": score,
                    "severity": "HIGH" if score >= 0.8 else "MEDIUM",
                }
                self._save_alert(alert)
                print(
                    f"[ALERT] score={score} people={people_count} severity={alert['severity']}"
                )

            time.sleep(0.1)  # ~10 fps polling; adjust as needed