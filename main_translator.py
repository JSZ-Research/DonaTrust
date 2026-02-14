import cv2
import mediapipe as mp
import numpy as np
import json
import os
import time

# --- 配置 ---
DATA_FILE = "gestures.json"
MATCH_THRESHOLD = 0.25 

class SignLanguageTranslator:
    def __init__(self):
        print("📥 正在初始化 MediaPipe...")
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.templates = self.load_templates()

    def load_templates(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    return {k: np.array(v) for k, v in data.items()}
            except: pass
        return {}

    def save_templates(self):
        try:
            serializable_data = {k: v.tolist() for k, v in self.templates.items()}
            with open(DATA_FILE, 'w') as f:
                json.dump(serializable_data, f)
            print("💾 数据已保存")
        except Exception as e:
            print(f"保存失败: {e}")

    def normalize_landmarks(self, landmarks):
        points = np.array([[lm.x, lm.y] for lm in landmarks.landmark])
        center = np.mean(points, axis=0)
        points -= center
        max_dist = np.max(np.linalg.norm(points, axis=1))
        if max_dist > 0: points /= max_dist
        return points.flatten()

    def run(self):
        # 强制使用索引 0 (针对你的报错修正)
        print("🔍 正在打开摄像头 (Index 0)...")
        cap = cv2.VideoCapture(0)
        
        # 给摄像头一点预热时间
        time.sleep(1.0)

        if not cap.isOpened():
            print("❌ 无法打开摄像头！请检查隐私设置或是否被占用。")
            return

        print("\n" + "="*40)
        print("🟢 程序已启动！请看弹出的窗口！")
        print("⚠️  重要：请用鼠标点击一下【视频画面】")
        print("   然后按键盘数字键 [1] [2] [3] 录制")
        print("   按 [q] 退出")
        print("="*40 + "\n")

        while True:
            ret, frame = cap.read()
            
            # 修正：如果读不到帧，不要退出，而是重试（防止启动时黑屏导致闪退）
            if not ret:
                print("⚠️ 等待摄像头画面...")
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)
            
            status_text = "Waiting..."
            color = (200, 200, 200)

            # 绘制提示文字，提醒你点击窗口
            cv2.putText(frame, "CLICK THIS WINDOW FIRST!", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if results.multi_hand_landmarks:
                hand_lms = results.multi_hand_landmarks[0]
                self.mp_drawing.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)
                
                features = self.normalize_landmarks(hand_lms)
                
                min_dist = float('inf')
                best_match = "Unknown"
                
                for name, temp in self.templates.items():
                    dist = np.linalg.norm(features - temp)
                    if dist < min_dist:
                        min_dist = dist
                        best_match = name
                
                if min_dist < MATCH_THRESHOLD:
                    status_text = f"Sign: {best_match}"
                    color = (0, 255, 0)
                else:
                    status_text = "Unknown"
                    color = (0, 0, 255)

                # --- 极速录制逻辑 ---
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('1'):
                    self.templates["Gesture_1"] = features
                    self.save_templates()
                    print("✅ 动作 [1] 已录入！")
                    cv2.circle(frame, (50, 50), 40, (0, 255, 0), -1) # 视觉反馈
                
                elif key == ord('2'):
                    self.templates["Gesture_2"] = features
                    self.save_templates()
                    print("✅ 动作 [2] 已录入！")
                    cv2.circle(frame, (50, 50), 40, (0, 255, 0), -1)

                elif key == ord('3'):
                    self.templates["Gesture_3"] = features
                    self.save_templates()
                    print("✅ 动作 [3] 已录入！")
                    cv2.circle(frame, (50, 50), 40, (0, 255, 0), -1)
                
                elif key == ord('c'):
                    self.templates.clear()
                    self.save_templates()
                    print("🗑️ 已清空")
            
            # UI 显示
            h, w, _ = frame.shape
            cv2.rectangle(frame, (0, h-60), (w, h), (0, 0, 0), -1)
            cv2.putText(frame, status_text, (20, h-20), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            cv2.imshow('Sign Language (Click Me)', frame)

            # 退出逻辑
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = SignLanguageTranslator()
    app.run()