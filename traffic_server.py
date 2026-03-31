import cv2
import base64
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import threading
import os
import tempfile

app = Flask(__name__)
CORS(app)

# ── MODEL ─────────────────────────────────────────────────────────────────────
print("Loading YOLOv8m model (~52MB — downloads on first run)...")
model = YOLO("yolov8m.pt")
print("Model ready!\n")

# ── TUNING ────────────────────────────────────────────────────────────────────
CONFIDENCE = 0.15
IOU        = 0.40
IMGSZ      = 320   
NUM_FRAMES = 15

VEHICLE_CLASSES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck",
    1: "Bicycle",
}

lock = threading.Lock()


def preprocess_frame(frame):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    return cv2.filter2D(enhanced, -1, kernel)


def detect_vehicles_in_frame(frame_bgr):
    frame = preprocess_frame(frame_bgr)
    with lock:
        results = model(frame, verbose=False, conf=CONFIDENCE, iou=IOU, imgsz=IMGSZ)[0]

    counts = {name: 0 for name in VEHICLE_CLASSES.values()}
    boxes_out = []

    for box in results.boxes:
        cls_id = int(box.cls[0])
        if cls_id in VEHICLE_CLASSES:
            label = VEHICLE_CLASSES[cls_id]
            counts[label] += 1
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            boxes_out.append({
                "label": label,
                "conf":  round(conf, 2),
                "x1": round(x1), "y1": round(y1),
                "x2": round(x2), "y2": round(y2),
            })

    return sum(counts.values()), counts, boxes_out


def extract_frames(video_path, num_frames=NUM_FRAMES):
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total == 0:
        cap.release()
        return []
    indices = [int((i + 0.5) * total / num_frames) for i in range(num_frames)]
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()
    return frames


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "yolov8m", "conf": CONFIDENCE, "imgsz": IMGSZ})


@app.route("/analyze", methods=["POST"])
def analyze():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    lane_id    = int(request.form.get("lane_id", 0))
    video_file = request.files["video"]

    suffix = os.path.splitext(video_file.filename)[-1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        video_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        frames = extract_frames(tmp_path, num_frames=NUM_FRAMES)
        if not frames:
            return jsonify({"error": "Could not read video frames"}), 400

        print(f"Lane {lane_id+1}: analysing {len(frames)} frames...")

        all_totals = []
        all_counts = {}
        for frame in frames:
            total, counts, _ = detect_vehicles_in_frame(frame)
            all_totals.append(total)
            for k, v in counts.items():
                all_counts[k] = all_counts.get(k, 0) + v

        all_totals.sort()
        median_density = all_totals[len(all_totals) // 2]
        avg_counts = {k: round(v / len(frames), 1) for k, v in all_counts.items()}

        print(f"Lane {lane_id+1}: {median_density} vehicles | {avg_counts}")

        return jsonify({
            "lane_id":       lane_id,
            "density":       median_density,
            "counts":        avg_counts,
            "sample_frames": len(frames),
        })
    finally:
        os.unlink(tmp_path)


@app.route("/analyze_frame", methods=["POST"])
def analyze_frame():
    """
    Fast single-frame inference — called continuously for live box tracking.
    Accepts base64 JPEG, returns boxes + counts immediately.
    """
    data = request.get_json()
    if not data or "frame" not in data:
        return jsonify({"error": "No frame data"}), 400

    lane_id   = int(data.get("lane_id", 0))
    img_bytes = base64.b64decode(data["frame"])
    nparr     = np.frombuffer(img_bytes, np.uint8)
    frame     = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "Invalid image data"}), 400

    total, counts, boxes = detect_vehicles_in_frame(frame)

    return jsonify({
        "lane_id": lane_id,
        "density": total,
        "counts":  counts,
        "boxes":   boxes,
    })


if __name__ == "__main__":
    print("\n" + "=" * 52)
    print("  AI Traffic Control - YOLO Backend  v3")
    print("  Model      : YOLOv8m")
    print("  Confidence : 0.15  (overhead CCTV)")
    print("  Live track : imgsz=320 for fast inference")
    print("  Running at : http://localhost:5050")
    print("=" * 52 + "\n")
    app.run(host="0.0.0.0", port=5050, debug=False, threaded=True)