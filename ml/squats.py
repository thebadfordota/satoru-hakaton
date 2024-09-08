import pickle
import logging

import pandas as pd
import numpy as np

import mediapipe as mp
import cv2

from landmarks import landmarks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_counter() -> None:
    global counter
    counter = 0


mp_draw = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_tracking_confidence=0.5, min_detection_confidence=0.5)

with open("squats.pkl", "rb") as f:
    model = pickle.load(f)

current_stage = ""
counter = 0
bodylang_prob = np.array([0, 0])
bodylang_class = ""


def detect_squats() -> None:
    global current_stage
    global counter
    global bodylang_class
    global bodylang_prob
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        _, image = cap.read()
        # image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        mp_draw.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_draw.DrawingSpec(color=(255, 0, 0), thickness=4, circle_radius=5),
            mp_draw.DrawingSpec(color=(0, 255, 0), thickness=5, circle_radius=10),
        )

        cv2.imshow("Squat Counter", image)
        if cv2.waitKey(10) & 0xFF == ord("q"):
            break

        try:
            row = (
                np.array(
                    [
                        [res.x, res.y, res.z, res.visibility]
                        for res in results.pose_landmarks.landmark
                    ]
                )
                .flatten()
                .tolist()
            )
            X = pd.DataFrame([row], columns=landmarks)
            bodylang_prob = model.predict_proba(X)[0]
            bodylang_class = model.predict(X)[0]

            if bodylang_class == "down" and bodylang_prob[bodylang_prob.argmax()] > 0.75:
                current_stage = "down"
            elif (
                current_stage == "down"
                and bodylang_class == "up"
                and bodylang_prob[bodylang_prob.argmax()] > 0.75
            ):
                current_stage = "up"
                counter += 1
            
            logging.info(f"Squat Count: {counter}")

        except Exception as e:
            logging.error(e)
  

    cap.release()
    cv2.destroyAllWindows()
