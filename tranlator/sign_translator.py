import cv2
import mediapipe as mp

# 初始化 MediaPipe 手部模型
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

def recognize_gesture(landmarks):
    """
    极简逻辑判断：根据手指指尖与关节的位置关系判断手势
    这里我们模拟识别一个“手掌张开（代表感谢/打招呼）”的手势
    """
    # 获取指尖的坐标索引
    finger_tips = [8, 12, 16, 20]
    finger_pip = [6, 10, 14, 18]
    
    count = 0
    for i in range(4):
        # 如果指尖的 Y 坐标小于 第二关节的 Y 坐标，说明手指是伸直的
        if landmarks[finger_tips[i]].y < landmarks[finger_pip[i]].y:
            count += 1

    # 拇指判断 (根据横向坐标)
    if landmarks[4].x < landmarks[3].x:
        count += 1

    if count == 5:
        return "THANK YOU / HELLO"
    else:
        return "Waiting for sign..."

# 打开摄像头
cap = cv2.VideoCapture(0)

print("Sign Language Detector Started...")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    # 镜像翻转并转为 RGB
    image = cv2.flip(image, 1)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 处理图像并找出手部关键点
    results = hands.process(rgb_image)

    gesture_text = "No Hand Detected"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 在画面上画出骨架
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # 识别逻辑
            gesture_text = recognize_gesture(hand_landmarks.landmark)

    # 在画面上显示识别到的文字
    cv2.putText(image, gesture_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (28, 180, 149), 2)
    
    cv2.imshow('DonaTrust Sign Translator', image)

    # 按下 'q' 键退出
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()