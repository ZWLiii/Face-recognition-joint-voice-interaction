import json
import cv2 as cv
import os
from PIL import Image
from io import BytesIO
from face_compare1 import face_compare_all
from voice import start_dialogue
import threading
from tts_util import play_mp3
import time


# 加载用户信息
with open("FaceDetection/users.json", "r", encoding="utf-8") as f:
    users_dict = json.load(f)

# 已触发交互的客人 (key: user_key, value: timestamp)
guest_triggered = {}
TRIGGER_COOLDOWN = 180 # 3分钟冷却时间

# 加载人脸识别分类器
face_cas = cv.CascadeClassifier('FaceDetection/lib/haarcascade_frontalface_alt2.xml')
side_face_cas = cv.CascadeClassifier('FaceDetection/lib/haarcascade_profileface.xml')


def draw_box(frame, title, x1, y1, x2, y2):
    """绘制识别框"""
    cv.putText(frame, title, (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    return cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


def compress_image(path, max_size=3 * 1024 * 1024, max_dim=800):
    """压缩图片到指定大小以下"""
    try:
        img = Image.open(path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        buf = BytesIO()
        quality = 85
        img.save(buf, format="JPEG", quality=quality)

        while buf.getbuffer().nbytes > max_size and quality > 20:
            buf.seek(0)
            buf.truncate(0)
            quality -= 5
            img.save(buf, format="JPEG", quality=quality)

        with open(path, 'wb') as f:
            f.write(buf.getvalue())

        print(f"✓ 压缩完成: {os.path.basename(path)}, {buf.getbuffer().nbytes / 1024:.2f} KB")

    except Exception as e:
        print(f"✗ 压缩失败 {path}: {e}")


def preprocess_user_images():
    """预处理所有用户图片"""
    user_dir = 'FaceDetection/images/users/'
    if not os.path.exists(user_dir):
        print(f"⚠️ 用户图片目录不存在: {user_dir}")
        return

    for filename in os.listdir(user_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join(user_dir, filename)
            file_size = os.path.getsize(filepath)

            if file_size > 3 * 1024 * 1024:
                print(f"⚙️ 压缩用户图片: {filename} ({file_size / 1024:.2f} KB)")
                compress_image(filepath)


def process_face(matched_user_key):
    """
    处理识别到的人脸

    流程：
    1. 识别人脸
    2. 播放欢迎语（主人和客人都播放）
    3. 判断身份：
       - 主人：播放完欢迎语后结束
       - 客人：播放完欢迎语后启动语音交互

    :param matched_user_key: 用户唯一标识（如 "dxs", "zwl", "lq"）
    """
    if not matched_user_key:
        return

    # ========== 1. 冷却时间检查 ==========
    current_time = time.time()
    if matched_user_key in guest_triggered:
        last_trigger_time = guest_triggered[matched_user_key]
        if current_time - last_trigger_time < TRIGGER_COOLDOWN:
            print(f"⏳ {matched_user_key} 在冷却中，跳过")
            return

    # ========== 2. 查找用户信息 ==========
    user_info = None
    for person_id, info in users_dict.items():
        if info.get("key") == matched_user_key:
            user_info = info
            break

    if not user_info:
        print(f"⚠️ 未找到 key={matched_user_key} 的用户")
        return

    print(f"\n{'=' * 50}")
    print(f"✅ 识别成功: {matched_user_key}")
    print(f"{'=' * 50}")

    # ========== 3. 播放欢迎语（主人和客人都播放）==========
    welcome_audio = user_info.get("text", "")

    if not welcome_audio:
        print(f"⚠️ 用户 {matched_user_key} 未配置欢迎语音")
        return

    print(f"🔊 播放欢迎语: {welcome_audio}")

    play_mp3(welcome_audio)  # 同步播放，等待播放完成

    # 更新触发时间
    guest_triggered[matched_user_key] = current_time

    # ========== 4. 判断身份，决定是否启动语音交互 ==========
    user_type = user_info.get('type', '')

    if user_type == 'owner':
        # 主人：播放完欢迎语后结束
        print("👋 主人欢迎流程完成\n")

    elif user_type == 'guest':
        # 客人：启动语音交互（不再传入 welcome_mp3，因为已经播放过了）
        print("🎤 启动语音交互...\n")
        t = threading.Thread(
            target=start_dialogue,
            kwargs={'welcome_mp3': None}  # 欢迎语已经播放过
        )
        t.start()
        t.join()  # 等待语音交互结束再继续

    else:
        print(f"⚠️ 未知用户类型: {user_type}\n")


def videoFace(url=0):
    preprocess_user_images()
    print("✓ 预处理完成\n")

    # 检查摄像头
    video = cv.VideoCapture(url)
    if not video.isOpened():
        print("❌ 无法打开摄像头！")
        return

    print("📹 摄像头已就绪")
    print("👀 开始人脸识别... (按 'q' 退出)\n")

    frame_count = 0
    detect_interval = 30  # 每30帧检测一次人脸
    face_detected = False  # ====== 改动部分：增加标志

    while video.isOpened() and not face_detected:  # ====== 改动部分：检测到人脸就退出循环
        ret, frame = video.read()
        if not ret:
            break

        frame_count += 1
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # 检测人脸的通用函数
        def detect_faces(cascade, face_type="Front"):
            nonlocal face_detected  # ====== 改动部分
            faces = cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(50, 50)  # 提高最小尺寸，减少误检
            )

            for (x, y, w, h) in faces:
                x2, y2 = x + w, y + h
                confidence = round(w * h / (frame.shape[0] * frame.shape[1]), 2)

                # 绘制识别框
                label = f'{face_type}:{confidence * 100:.1f}%'
                draw_box(frame, label, x, y, x2, y2)

                # 定期进行人脸比对（降低 API 调用频率）
                if confidence > 0.05 and frame_count % detect_interval == 0:
                    # 裁剪并保存人脸
                    face_crop = frame[y:y + h, x:x + w]
                    slice_dir = 'FaceDetection/images/slice'
                    os.makedirs(slice_dir, exist_ok=True)
                    slice_path = os.path.join(slice_dir, f'face-{time.time()}.jpg')
                    cv.imwrite(slice_path, face_crop)

                    print(f"\n🔍 检测到人脸 ({face_type}, {confidence * 100:.1f}%)")
                    print(f"💾 保存切片: {os.path.basename(slice_path)}")
                    print("🔄 调用人脸比对 API...")

                    # 调用人脸比对
                    try:
                        user_type, user_key, user_text = face_compare_all(slice_path)

                        if user_key:
                            print(f"✅ API 返回: type={user_type}, key={user_key}, audio={user_text}")
                            process_face(user_key)
                            face_detected= True
                            return True
                        else:
                            print("❌ 未匹配到注册用户\n")
                    except Exception as e:
                        print(f"❌ 人脸比对失败: {e}\n")
                    return False
        if detect_faces(face_cas, "Front"):
            break
        if detect_faces(side_face_cas, "Side"):
            break
        # # 前脸检测
        # detect_faces(face_cas, "Front")
        #
        # # 侧脸检测
        # detect_faces(side_face_cas, "Side")

        # 显示视频
        cv.imshow("Face Recognition System", frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            print("\n👋 用户退出")
            break

    video.release()
    cv.destroyAllWindows()
    print("✓ 系统已关闭")


if __name__ == "__main__":
    videoFace(0)