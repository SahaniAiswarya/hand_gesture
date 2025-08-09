import cv2
import mediapipe as mp
import pyautogui
import webbrowser
from datetime import datetime

# Initialize MediaPipe and webcam
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

# Finger tip landmark IDs
tip_ids = [4, 8, 12, 16, 20]

# Gesture state
prev_gesture = ""
gesture_delay = 20
counter = 0

# Log file
log_file = open("gesture_log.txt", "a")

# Get finger status
def get_finger_status(hand_landmarks):
    finger_status = []

    # Thumb (x-axis)
    if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0] - 1].x:
        finger_status.append(1)
    else:
        finger_status.append(0)

    # Other fingers (y-axis)
    for i in range(1, 5):
        if hand_landmarks.landmark[tip_ids[i]].y < hand_landmarks.landmark[tip_ids[i] - 2].y:
            finger_status.append(1)
        else:
            finger_status.append(0)

    return finger_status

# Detect gesture from finger status
def detect_gesture(finger_status):
    if finger_status == [1, 1, 1, 1, 1]: #all fingers open
        return "Play"
    elif finger_status == [0, 0, 0, 0, 0]:  #all fingers close
        return "Pause"
    elif finger_status == [0, 0, 0, 0, 1]: #little finger
        return "Next"
    elif finger_status == [1, 0, 0, 0, 0]: #thumb finger
        return "Previous"
    elif finger_status == [1, 0, 0, 0, 1]: #thumb + little finger
        return "OpenYouTube"
    elif finger_status == [0, 1, 1, 0, 0]: #index + middle finger
        return "VolumeUp"
    elif finger_status == [0, 0, 0, 1, 1]:
        return "VolumeDown"
    elif finger_status == [0, 0, 1, 1, 1]:  # middle + ring + pinky finger
        return "ScrollDown"
    elif finger_status == [0, 1, 1, 1, 0]:  # index + middle + ring finger
        return "ScrollUp"


    else:
        return "None"

# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    gesture = "None"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            finger_status = get_finger_status(hand_landmarks)
            gesture = detect_gesture(finger_status)

            if gesture != prev_gesture:
                counter = 0
                prev_gesture = gesture
            else:
                counter += 1

            if counter == gesture_delay:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_file.write(f"{timestamp} - Gesture: {gesture}\n")
                log_file.flush()

                if gesture == "Play":
                    pyautogui.press("playpause")
                elif gesture == "Pause":
                    pyautogui.press("playpause")
                elif gesture == "Next":
                    pyautogui.press("nexttrack")
                elif gesture == "Previous":
                    pyautogui.press("prevtrack")
                elif gesture == "OpenYouTube":
                    webbrowser.open("https://www.youtube.com")
                elif gesture == "VolumeUp":
                    pyautogui.press("volumeup")
                elif gesture == "VolumeDown":
                    pyautogui.press("volumedown")
                
                elif gesture == "ScrollDown":
                    pyautogui.scroll(-500)
                elif gesture == "ScrollUp":
                    pyautogui.scroll(500)


                counter = 0

    # Display the gesture
    cv2.putText(frame, f"Gesture: {gesture}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),2)

    cv2.imshow("🖐 Gesture Controlled Media Player", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
log_file.close()
cap.release()
cv2.destroyAllWindows()
