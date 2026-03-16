# app.py - Terminal runner for CafeEye AI

import cv2
import time
from datetime import datetime
from dotenv import load_dotenv
from detector import (
    TableTracker, TABLES,
    detect_people_in_zone,
    draw_tables, draw_summary,
    format_duration
)

load_dotenv()

tracker = TableTracker()

def print_dashboard(tracker):
    summary = tracker.get_summary()
    print("\n" + "=" * 60)
    print(f"  CafeEye AI  {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    print(f"  Tables: {summary['occupied_tables']}/{summary['total_tables']} occupied | {summary['empty_tables']} empty")
    print(f"  Total visitors: {summary['total_visitors']}")
    print("\n  TABLE STATUS:")
    for name, table in tracker.tables.items():
        if table["occupied"]:
            duration = format_duration(table["duration"])
            attention = " NEEDS ATTENTION!" if table["needs_attention"] else ""
            print(f"  OCCUPIED - {name}: {table['customer_count']} people | {duration}{attention}")
        else:
            print(f"  EMPTY    - {name}")
    print("=" * 60)

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 900)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 620)

    if not cap.isOpened():
        print("Cannot open camera!")
        return

    print("CafeEye AI started!")
    print("Press 'q' to quit | 'd' for dashboard | 'r' to reset")
    print("-" * 60)

    last_dashboard_print = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        now = time.time()

        for name, zone in TABLES.items():
            person_detected, count = detect_people_in_zone(frame, zone)
            tracker.update(name, person_detected, count)

        if now - last_dashboard_print > 10:
            print_dashboard(tracker)
            last_dashboard_print = now

        frame = draw_tables(frame, tracker)
        frame = draw_summary(frame, tracker)
        cv2.imshow("CafeEye AI", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('d'):
            print_dashboard(tracker)
        elif key == ord('r'):
            tracker.__init__()
            print("Tracker reset!")

    cap.release()
    cv2.destroyAllWindows()
    print("\nCafeEye AI stopped.")

if __name__ == "__main__":
    main()