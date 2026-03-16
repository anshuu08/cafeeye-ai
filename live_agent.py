# live_agent.py - CafeEye Live Voice Agent with Vision

import asyncio
import sounddevice as sd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
import os
import threading
import cv2

load_dotenv()


def capture_frame():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if ret:
        return frame
    return None


def frame_to_jpeg_bytes(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()


def get_context(tracker, format_duration):
    summary = tracker.get_summary()
    details = ""
    for name, table in tracker.tables.items():
        if table["occupied"]:
            dur = format_duration(table["duration"])
            details += f"{name}: occupied {dur}, {table['customer_count']} people. "
        else:
            details += f"{name}: empty. "
    return (
        f"You are CafeEye, a smart restaurant AI assistant watching through a camera. "
        f"Time: {datetime.now().strftime('%H:%M:%S')}. "
        f"Sensor data: {summary['occupied_tables']}/{summary['total_tables']} tables occupied, "
        f"{summary['empty_tables']} empty, {summary['total_visitors']} visitors today. "
        f"Table details: {details} "
        f"Use both sensor data AND camera image to answer. "
        f"Be specific about table numbers. Keep response under 2 sentences."
    )


async def _run_voice(tracker, format_duration):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    MODEL = "gemini-2.5-flash-native-audio-latest"

    print("Capturing camera frame...")
    frame = capture_frame()

    print("Listening for 5 seconds... speak now!")
    rec = sd.rec(int(5 * 16000), samplerate=16000, channels=1, dtype='int16')
    sd.wait()
    audio_data = rec.tobytes()
    print("Thinking...\n")

    config = types.LiveConnectConfig(response_modalities=["AUDIO"])

    async with client.aio.live.connect(model=MODEL, config=config) as session:
        if frame is not None:
            jpeg_bytes = frame_to_jpeg_bytes(frame)
            await session.send_client_content(
                turns=types.Content(
                    role="user",
                    parts=[
                        types.Part(inline_data=types.Blob(
                            data=jpeg_bytes, mime_type="image/jpeg")),
                        types.Part(text=get_context(tracker, format_duration))
                    ]
                ),
                turn_complete=False
            )
            await asyncio.sleep(0.3)

        for i in range(0, len(audio_data), 1024):
            await session.send_realtime_input(
                audio=types.Blob(
                    data=audio_data[i:i+1024],
                    mime_type="audio/pcm;rate=16000"
                )
            )
            await asyncio.sleep(0.01)

        await asyncio.sleep(0.5)

        await session.send_client_content(
            turns=types.Content(
                role="user",
                parts=[types.Part(text="Now respond to what I just asked.")]
            ),
            turn_complete=True
        )

        buf = b""
        async for r in session.receive():
            sc = r.server_content
            if sc and sc.model_turn:
                for p in sc.model_turn.parts:
                    if hasattr(p, 'inline_data') and p.inline_data and p.inline_data.data:
                        buf += p.inline_data.data
            if sc and sc.turn_complete:
                break

    print(f"Collected: {len(buf)} bytes")

    if buf:
        print("CafeEye speaking...\n")
        arr = np.frombuffer(buf, dtype=np.int16).astype(np.float32) / 32768.0
        sd.play(arr, samplerate=24000)
        sd.wait()
        print("Done!\n")
        return True
    return False


async def _say(text):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    MODEL = "gemini-2.5-flash-native-audio-latest"

    config = types.LiveConnectConfig(response_modalities=["AUDIO"])

    async with client.aio.live.connect(model=MODEL, config=config) as session:
        await session.send_client_content(
            turns=types.Content(
                role="user",
                parts=[types.Part(
                    text=f"Say exactly this naturally and warmly: {text}"
                )]
            ),
            turn_complete=True
        )
        buf = b""
        async for r in session.receive():
            sc = r.server_content
            if sc and sc.model_turn:
                for p in sc.model_turn.parts:
                    if hasattr(p, 'inline_data') and p.inline_data and p.inline_data.data:
                        buf += p.inline_data.data
            if sc and sc.turn_complete:
                break

        if buf:
            arr = np.frombuffer(buf, dtype=np.int16).astype(np.float32) / 32768.0
            sd.play(arr, samplerate=24000)
            sd.wait()
        await asyncio.sleep(0.1)


def _run_async(coro):
    """Run any async coroutine in a fresh thread safely"""
    error = [None]

    def run():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
            loop.run_until_complete(asyncio.sleep(0.1))
            loop.close()
        except Exception as e:
            error[0] = e
            print(f"Async error: {e}")

    t = threading.Thread(target=run)
    t.start()
    t.join()

    if error[0]:
        raise error[0]


def ask_voice(tracker, format_duration):
    """Record voice question and get spoken answer"""
    result = [False]
    error = [None]

    def run():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result[0] = loop.run_until_complete(
                _run_voice(tracker, format_duration)
            )
            loop.run_until_complete(asyncio.sleep(0.1))
            loop.close()
        except Exception as e:
            error[0] = e
            print(f"Voice error: {e}")

    t = threading.Thread(target=run)
    t.start()
    t.join()

    if error[0]:
        raise error[0]
    return result[0]


def say_text(text):
    """Speak any text using Gemini voice"""
    _run_async(_say(text))


def say_greeting():
    """Welcome greeting"""
    say_text(
        "Welcome to our restaurant! I am CafeEye, your AI assistant. "
        "I am happy to help you order today. "
        "Would you like vegetarian or non-vegetarian food? "
        "I can also give you some great recommendations!"
    )


def confirm_order(order_text):
    """Confirm order placed"""
    say_text(
        f"Thank you so much for your order! "
        f"You have ordered {order_text}. "
        f"Your food will be prepared fresh and served to you shortly. "
        f"Thank you for dining with us today!"
    )


if __name__ == "__main__":
    from detector import TableTracker, format_duration
    tracker = TableTracker()

    print("\n" + "=" * 60)
    print("  CafeEye Live Voice Agent with Vision")
    print("  Press ENTER -> speak 5 seconds -> hear answer")
    print("  Press Ctrl+C to quit")
    print("=" * 60 + "\n")

    while True:
        try:
            input("Press ENTER to ask CafeEye a question...")
            ask_voice(tracker, format_duration)
            print("-" * 40 + "\n")
        except KeyboardInterrupt:
            print("\nCafeEye stopped. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Try again...\n")