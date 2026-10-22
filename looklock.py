import os
import cv2
import time
from deepface import DeepFace
from playsound import playsound
import pywhatkit as kit
import threading


# =========================
# SETTINGS
# =========================

AUTHORIZED_FACE = "faces/my pic.jpg"

MATCH_THRESHOLD = 0.50
REQUIRED_MATCHES = 5
LOCK_COOLDOWN = 10  # seconds
# WhatsApp Alert Settings

WHATSAPP_NUMBER = "+91 62616 57598"  # Your number with country code

# =========================
# WEBCAM SETUP
# =========================

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Press Q to quit")

# =========================
# VARIABLES
# =========================

granted_count = 0
denied_count = 0

status = "CHECKING..."
color = (255, 255, 0)

last_lock_time = 0

prev_time = time.time()

# =========================
# MAIN LOOP
# =========================
def send_whatsapp_alert():

    try:
        kit.sendwhatmsg_instantly(
            WHATSAPP_NUMBER,
            "🚨 LOOKLOCK ALERT!\nIntruder detected on your system."
        )

    except Exception as e:
        print("WhatsApp Error:", e)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Resize for speed
    small_frame = cv2.resize(frame, (640, 480))

    try:

        result = DeepFace.verify(
            img1_path=small_frame,
            img2_path=AUTHORIZED_FACE,
            model_name="Facenet512",
            detector_backend="opencv",
            enforce_detection=False,
            silent=True

            
    )

        distance = result["distance"]

        # =========================
        # FACE MATCH LOGIC
        # =========================

        if distance < MATCH_THRESHOLD:

            granted_count += 1
            denied_count = 0

        else:

            denied_count += 1
            granted_count = 0

        # =========================
        # ACCESS GRANTED
        # =========================

        if granted_count >= REQUIRED_MATCHES:

            status = "ACCESS GRANTED"
            color = (0, 255, 0)

        # =========================
        # ACCESS DENIED
        # =========================

        elif denied_count >= REQUIRED_MATCHES:

            status = "ACCESS DENIED"
            color = (0, 0, 255)

            current_time = time.time()

            # Prevent repeated locking spam
            if current_time - last_lock_time > LOCK_COOLDOWN:

                # Save intruder image
                filename = f"intruder_{int(current_time)}.jpg"

                cv2.imwrite(filename, frame)

                print(f"[!] Intruder image saved: {filename}")
                # Send WhatsApp alert in background
                threading.Thread(
                    target=send_whatsapp_alert,
                    daemon=True
                ).start()

                # PLAY SOUND
                # PLAY SOUND
            #     threading.Thread(
            #         target=lambda: playsound("Alarm-Clock-Short-choice.mp3"),
            #   daemon=True
            # ).start()
            try:
                print("Playing alarm...")
                playsound("Alarm-Clock-Short-chosic.com_.mp3")
            except Exception as e:
                print("Alarm Error:", e)
                #Lock Windows
                os.system(
                    "rundll32.exe user32.dll,LockWorkStation"
                )

                last_lock_time = current_time

        # =========================
        # DISPLAY STATUS
        # =========================

        cv2.putText(
            frame,
            status,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            3
        )

        cv2.putText(
            frame,
            f"Distance: {distance:.2f}",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        # =========================
        # FPS COUNTER
        # =========================

        current_time = time.time()

        fps = 1 / (current_time - prev_time)

        prev_time = current_time

        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2
        )

    except Exception:
        continue    

    # =========================
    # SHOW WINDOW
    # =========================

    cv2.imshow(
        "LookLock AI Authentication",
        frame
    )

    # Quit with Q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# =========================
# Khatam
# =========================

cap.release()
cv2.destroyAllWindows()