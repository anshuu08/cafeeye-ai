# detector.py - The eyes of CafeEye AI

import cv2
import time
import numpy as np
from datetime import datetime

yolo_model = None

def get_yolo():
    global yolo_model
    if yolo_model is None:
        from ultralytics import YOLO
        yolo_model = YOLO("yolo11n.pt")
    return yolo_model

TABLES = {
    "Table 1": (50, 50, 300, 300),
    "Table 2": (320, 50, 570, 300),
    "Table 3": (590, 50, 840, 300),
    "Table 4": (50, 320, 300, 570),
    "Table 5": (320, 320, 570, 570),
    "Table 6": (590, 320, 840, 570),
}

class TableTracker:
    def __init__(self):
        self.tables = {}
        for name in TABLES:
            self.tables[name] = {
                "occupied": False,
                "start_time": None,
                "duration": 0,
                "customer_count": 0,
                "needs_attention": False,
            }
        self.total_visitors = 0
        self.peak_hour_log = {}

    def update(self, table_name, person_detected, person_count=0):
        table = self.tables[table_name]
        now = time.time()
        current_hour = datetime.now().strftime("%H:00")
        if person_detected:
            if not table["occupied"]:
                table["occupied"] = True
                table["start_time"] = now
                table["customer_count"] = person_count
                table["needs_attention"] = False
                self.total_visitors += person_count
                self.peak_hour_log[current_hour] = self.peak_hour_log.get(current_hour, 0) + 1
            table["duration"] = int(now - table["start_time"])
            if table["duration"] > 1800:
                table["needs_attention"] = True
        else:
            if table["occupied"]:
                table["occupied"] = False
                table["duration"] = 0
                table["start_time"] = None
                table["needs_attention"] = False
                table["customer_count"] = 0
        return table

    def get_summary(self):
        occupied = sum(1 for t in self.tables.values() if t["occupied"])
        empty = len(self.tables) - occupied
        attention_needed = [n for n, t in self.tables.items() if t["needs_attention"]]
        return {
            "occupied_tables": occupied,
            "empty_tables": empty,
            "total_tables": len(self.tables),
            "total_visitors": self.total_visitors,
            "attention_needed": attention_needed,
            "peak_hours": self.peak_hour_log
        }

def format_duration(seconds):
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"

def detect_people_in_zone(frame, zone):
    x1, y1, x2, y2 = zone
    results = get_yolo()(frame, verbose=False)[0]
    person_count = 0
    for box in results.boxes:
        if int(box.cls[0]) == 0 and float(box.conf[0]) > 0.4:
            bx1, by1, bx2, by2 = map(int, box.xyxy[0])
            center_x = (bx1 + bx2) // 2
            center_y = (by1 + by2) // 2
            if x1 < center_x < x2 and y1 < center_y < y2:
                person_count += 1
                cv2.rectangle(frame, (bx1, by1), (bx2, by2), (255, 0, 0), 2)
                cv2.putText(frame, f"Person {float(box.conf[0]):.0%}",
                            (bx1, by1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
    return person_count > 0, person_count

def draw_tables(frame, tracker):
    for name, zone in TABLES.items():
        x1, y1, x2, y2 = zone
        table = tracker.tables[name]
        if table["needs_attention"]:
            color = (0, 165, 255)
        elif table["occupied"]:
            color = (0, 0, 255)
        else:
            color = (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, name, (x1 + 5, y1 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        if table["occupied"]:
            duration_str = format_duration(table["duration"])
            cv2.putText(frame, f"Occupied: {duration_str}", (x1 + 5, y1 + 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            cv2.putText(frame, f"People: {table['customer_count']}", (x1 + 5, y1 + 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            if table["needs_attention"]:
                cv2.putText(frame, "NEEDS ATTENTION", (x1 + 5, y1 + 85),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 165, 255), 1)
        else:
            cv2.putText(frame, "EMPTY", (x1 + 5, y1 + 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return frame

def draw_summary(frame, tracker):
    summary = tracker.get_summary()
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 40), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    cv2.putText(frame,
        f"CafeEye AI  |  Tables: {summary['occupied_tables']}/{summary['total_tables']} Occupied  |  Empty: {summary['empty_tables']}  |  Visitors: {summary['total_visitors']}",
        (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return frame