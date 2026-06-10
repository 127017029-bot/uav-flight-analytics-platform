import requests
import time
import random
from datetime import datetime

API_URL = "http://127.0.0.1:8000/api/telemetry/ingest/"


while True:

    data = {
        "flight": 1,
        "timestamp": datetime.now().isoformat(),

        "latitude": 10.7905 + random.uniform(-0.001, 0.001),
        "longitude": 78.7047 + random.uniform(-0.001, 0.001),

        "altitude": random.uniform(80, 120),
        "speed": random.uniform(10, 20),

        "battery": random.uniform(70, 100),
        "motor_rpm": random.uniform(4000, 6000)
    }

    try:
        response = requests.post(API_URL, json=data)

        print(
            response.status_code,
            response.text
        )

    except Exception as e:
        print("Error:", e)

    time.sleep(2)