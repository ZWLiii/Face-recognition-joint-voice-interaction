"""
face_compare1.py - 人脸比对逻辑
修复：正确返回用户的 key 值（如 "dxs", "zwl", "lq"）
"""
import json
import time
from face_compare_python3_demo import run as face_run


def face_compare(face_path: str, user_image_path: str, max_retries=3) -> bool:
    """
    调用人脸比对 API，带重试机制
    :param face_path: 检测到的人脸图片路径
    :param user_image_path: 注册用户图片路径
    :param max_retries: 最大重试次数
    :return: True-匹配，False-不匹配
    """
    for attempt in range(max_retries):
        try:
            result = face_run(
                appid='ce3cff88',
                apisecret='NWM2Y2Y3OWI2YWNhZGU3ZGMyMTUyNjdh',
                apikey='0b08851356d9bf23e4a10c2f5cb56a6c',
                img1_path=face_path,
                img2_path=user_image_path,
            )
            return result

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # 递增等待时间
                print(f"⚠️  API 调用失败 (尝试 {attempt + 1}/{max_retries}): {str(e)[:50]}")
                print(f"   等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"❌ 人脸比对接口异常 ({user_image_path}): {e}")
                return False

    return False


def face_compare_all(face_path: str):
    """
    将检测到的人脸与所有注册用户进行比对

    ⚠️ 关键修复：返回 value["key"] 而不是字典的 key

    :param face_path: 检测到的人脸图片路径
    :return: (user_type, user_key, welcome_audio)
             例如：("guest", "zwl", "zwlwelcome.mp3")
    """
    try:
        with open('FaceDetection/users.json', "r", encoding='utf-8') as f:
            people_data = json.load(f)
    except FileNotFoundError:
        print("❌ 找不到 users.json 文件")
        return None, None, None
    except json.JSONDecodeError as e:
        print(f"❌ users.json 格式错误: {e}")
        return None, None, None

    # 遍历所有注册用户
    for person_id, value in people_data.items():
        # person_id: "person1", "person2", "person3"
        # value["key"]: "dxs", "zwl", "lq"  ← 这才是我们需要的

        user_key = value.get("key")
        user_image = value.get("image")

        if not user_key or not user_image:
            print(f"⚠️  用户 {person_id} 配置不完整，跳过")
            continue

        print(f"   正在比对: {person_id} (key={user_key})...", end=" ")

        # 调用人脸比对
        if face_compare(face_path, user_image):
            print("✅ 匹配成功！")
            return (
                value.get("type"),  # "owner" 或 "guest"
                user_key,  # "dxs", "zwl", "lq" ← 修复点
                value.get("text")  # "dxswelcome.mp3"
            )
        else:
            print("❌")

    # 未匹配到任何用户
    return None, None, None


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 测试人脸比对功能")
    print("=" * 60 + "\n")

    # 测试用例：使用一个人脸切片
    test_face = "FaceDetection/images/slice/test_face.jpg"

    user_type, user_key, audio_file = face_compare_all(test_face)

    print("\n" + "=" * 60)
    if user_key:
        print(f"✅ 识别结果:")
        print(f"   用户标识: {user_key}")
        print(f"   用户类型: {user_type}")
        print(f"   欢迎语音: {audio_file}")
    else:
        print("❌ 未匹配到注册用户")
    print("=" * 60)