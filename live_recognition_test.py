import cv2
import time

from database.employee_repo import get_all_employee_embeddings
from ai.face_recognizer import get_embedding_from_image, cosine_similarity, RECOGNITION_THRESHOLD

known = get_all_employee_embeddings()
print(f"Loaded {len(known)} enrolled employee(s) from database.")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERROR: Could not open webcam.")
    exit()

print("Webcam started. Press 'q' to quit.")

last_check = 0
CHECK_INTERVAL = 1.0  # seconds between recognition attempts (avoid checking every single frame)

while True:
    ret, frame = cap.read()
    if not ret:
        print("ERROR: Failed to grab frame.")
        break

    now = time.time()
    label = "..."

    if now - last_check >= CHECK_INTERVAL:
        last_check = now
        embedding, face_count = get_embedding_from_image(frame)

        if face_count == 0:
            label = "No face detected"
        else:
            best_match = None
            best_score = -1
            for emp_id, code, name, known_embedding in known:
                score = cosine_similarity(embedding, known_embedding)
                if score > best_score:
                    best_score = score
                    best_match = (code, name)

            if best_match and best_score >= RECOGNITION_THRESHOLD:
                label = f"MATCH: {best_match[1]} ({best_match[0]}) - {best_score:.2f}"
            else:
                label = f"UNKNOWN - {best_score:.2f}" if best_match else "UNKNOWN"

    cv2.putText(frame, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imshow("Live Recognition Test (press q to quit)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
