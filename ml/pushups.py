import math
import logging

import cv2
from cv2.typing import MatLike
import mediapipe as mp


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PoseDetector:
    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):

        self.mp_draw = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def find_pose(self, img: MatLike, draw=True) -> MatLike:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(img_rgb)

        if draw:
            self.mp_draw.draw_landmarks(
                img,
                self.results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_draw.DrawingSpec(
                    color=(106, 13, 173), thickness=4, circle_radius=5
                ),
                self.mp_draw.DrawingSpec(
                    color=(255, 102, 0), thickness=5, circle_radius=10
                ),
            )
        return img

    def find_position(self, img: MatLike, draw=True) -> list:
        self.lm_list = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, _ = img.shape
                # Determining the pixels of the landmarks
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lm_list.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.lm_list

    def find_angle(self, img: MatLike, p1: int, p2: int, p3: int, draw=True) -> float:
        # Get the landmarks
        x1, y1 = self.lm_list[p1][1:]
        x2, y2 = self.lm_list[p2][1:]
        x3, y3 = self.lm_list[p3][1:]

        # Calculate Angle
        angle = math.degrees(
            math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2)
        )
        if angle < 0:
            angle += 360
            if angle > 180:
                angle = 360 - angle
        elif angle > 180:
            angle = 360 - angle

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.line(img, (x3, y3), (x2, y2), (0, 255, 0), 3)

            cv2.circle(img, (x1, y1), 1, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x1, y1), 1, (255, 0, 0), 2)
            cv2.circle(img, (x2, y2), 1, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 1, (255, 0, 0), 2)
            cv2.circle(img, (x3, y3), 1, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x3, y3), 1, (255, 0, 0), 2)

            cv2.putText(
                img,
                str(int(angle)),
                (x2 - 50, y2 + 50),
                cv2.FONT_HERSHEY_PLAIN,
                2,
                (0, 0, 255),
                2,
            )
        return angle


def update_count(
    elbow: int, shoulder: int, hip: int, direction: int, count: float, form: int
) -> tuple[float, int, int]:
    """Updates the count based on the angles."""
    if elbow > 160 and shoulder > 40 and hip > 160:
        form = 1
    if form == 1:
        if elbow <= 90 and hip > 160:
            if direction == 0:
                count += 0.5
                direction = 1
        elif elbow > 160 and shoulder > 40 and hip > 160:
            if direction == 1:
                count += 0.5
                direction = 0
    return count, direction, form


def detect_pushups() -> None:
    cap = cv2.VideoCapture(0)
    detector = PoseDetector()
    count = 0
    direction = 0
    form = 0

    while cap.isOpened():
        _, img = cap.read()
        img = detector.find_pose(img, False)
        lm_list = detector.find_position(img, False)

        if len(lm_list) != 0:
            elbow = detector.find_angle(img, 11, 13, 15)
            shoulder = detector.find_angle(img, 13, 11, 23)
            hip = detector.find_angle(img, 11, 23, 25)
            count, direction, form = update_count(
                elbow, shoulder, hip, direction, count, form
            )
            logging.info(f"Push-Up Count: {count}")

        cv2.imshow("Push-Up Counter", img)
        if cv2.waitKey(10) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
