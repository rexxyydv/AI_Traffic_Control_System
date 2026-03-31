🚦 AI Traffic Control System (YOLOv8 Backend)

An AI-powered traffic analysis backend that detects and counts vehicles using YOLOv8 and computer vision. Designed for smart traffic management using CCTV or video input.

⸻

📌 Features
	•	🚗 Vehicle detection using YOLOv8 (Ultralytics)
	•	🎥 Video-based traffic density analysis
	•	🖼️ Real-time frame analysis (live mode)
	•	📊 Median-based traffic density calculation (reduces noise)
	•	🎯 Supports multiple vehicle classes:
	•	Car
	•	Motorcycle
	•	Bus
	•	Truck
	•	Bicycle
	•	⚡ Optimized for overhead CCTV footage
	•	🔧 Image enhancement using CLAHE + sharpening

⸻

🛠️ Tech Stack
	•	Python
	•	OpenCV
	•	NumPy
	•	Flask (Backend API)
	•	YOLOv8 (Ultralytics)
	•	Threading

📂 Project Structure

TrafficControl/
│── traffic_server.py
│── traffic_dashboard.html
│── requirements.txt
│── README.md
│── START_COMMAND.command
│── yolov8m.pt

🚀 Installation

1. Clone repository

git clone https://github.com/rexxyydv/TrafficControl.git
cd TrafficControl

2. Install dependencies
pip install -r requirements.txt

3. Run the server
python traffic_server.py

Then click the traffic_dashboard.html file from your desktop

📡 API Endpoints

🔹 1. Health Check
GET /health
Response : 
{
  "status": "ok",
  "model": "yolov8m"
}

🔹 2. Analyze Video
POST /analyze

Response :
{
  "lane_id": 0,
  "density": 12,
  "counts": {
    "Car": 8,
    "Truck": 2
  }
}

🔹 3. Analyze Frame (Live)
POST /analyze_frame

Input : 
{
  "frame": "base64_encoded_image",
  "lane_id": 0
}

Response : 
{
  "frame": "base64_encoded_image",
  "lane_id": 0
}

🧠 How It Works
	1.	Video is split into multiple frames
	2.	Frames are enhanced using CLAHE + sharpening
	3.	YOLOv8 detects vehicles in each frame
	4.	Vehicle counts are collected
	5.	Median density is calculated (for stability)
	6.	Results are returned via API

📊 Key Concepts
	•	Computer Vision
	•	Object Detection (YOLOv8)
	•	Image Preprocessing
	•	REST API Development
	•	Multi-threading

⚙️ Configuration

CONFIDENCE = 0.15
IOU = 0.40
IMGSZ = 1280
NUM_FRAMES = 15

🎯 Use Cases
	•	Smart Traffic Signal Systems
	•	Traffic Monitoring & Analytics
	•	Urban Planning
	•	CCTV-based Vehicle Analysis

📌 Future Improvements
	•	Frontend dashboard (React)
	•	Real-time signal control system
	•	Cloud deployment (AWS/GCP)
	•	Multi-lane intelligent prioritization

👨‍💻 Author

Karanajit Sahoo

⭐ If you like this project, give it a star!

:::



