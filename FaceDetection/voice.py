"""
voice.py - Vosk 语音识别与交互
实现：客人语音点单，识别关键词后播放对应物品的语音，并写入txt文件供外部调用
"""
import queue
import sounddevice as sd
import vosk
import sys
import json
import time
import os
from tts_util import play_mp3


# === 修改 1: 查找 BT-BT 设备索引 ===
# def find_btbt_device():
#     """自动查找 BT-BT 设备的索引"""
#     devices = sd.query_devices()
#     btbt_input = None
#     btbt_output = None
#
#     print("\n🔍 正在查找 BT-BT 设备...")
#     for i, device in enumerate(devices):
#         device_name = device['name']
#         if 'BT-BT' in device_name or 'BTBT' in device_name:
#             if device['max_input_channels'] > 0:
#                 btbt_input = i
#                 print(f"✓ 找到 BT-BT 输入设备: [{i}] {device_name}")
#                 print(f"  - 输入通道: {device['max_input_channels']}")
#                 print(f"  - 默认采样率: {device['default_samplerate']}")
#             if device['max_output_channels'] > 0:
#                 btbt_output = i
#                 print(f"✓ 找到 BT-BT 输出设备: [{i}] {device_name}")
#                 print(f"  - 输出通道: {device['max_output_channels']}")
#
#     if btbt_input is None or btbt_output is None:
#         print("❌ 未找到 BT-BT 设备，请检查设备连接")
#         print("\n可用设备列表:")
#         print(sd.query_devices())
#         return None, None
#
#     return btbt_input, btbt_output
#
#
# # 获取 BT-BT 设备索引
# BTBT_INPUT, BTBT_OUTPUT = find_btbt_device()
#
# # === 修改 2: 设置默认设备为 BT-BT ===
# if BTBT_INPUT is not None and BTBT_OUTPUT is not None:
#     sd.default.device = (BTBT_INPUT, BTBT_OUTPUT)
#     prin(f"✓ 已设置默认设备: 输入={BTBT_INPUT}, 输出={BTBT_OUTPUT}\n")
# else:
#     print("⚠️  BT-BT 设备未找到，使用系统默认设备")

listening = True

# Vosk 配置
q = queue.Queue()
model = vosk.Model("FaceDetection/vosk-model-small-cn-0.22")
samplerate = 16000
blocksize = 8000

# 结果输出文件
RESULT_FILE = "FaceDetection/recognized_item.txt"


def save_result_to_txt(text):
    """将识别到的关键词写入txt文件"""
    try:
        os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            f.write(text.strip())
        print(f"📝 已将识别结果写入: {RESULT_FILE} → 「{text}」")
    except Exception as e:
        print(f"❌ 写入识别结果失败: {e}")


def callback(indata, frames, time_info, status):
    """音频流回调函数"""
    if status:
        print(status, file=sys.stderr)
    if listening:
        q.put(bytes(indata))


def start_dialogue(welcome_mp3):
    """
    启动 Vosk 语音交互
    流程：
    1. 播放欢迎语
    2. 播放 "请问您需要什么物品？"
    3. 识别关键词 → 播放语音 → 写入txt
    """
    print("\n" + "=" * 50)
    print("🎤 语音交互已启动")
    print("=" * 50)

    # 关键词映射表
    responses = {
        "水": "watter.mp3",
        "矿泉水": "watter.mp3",
        "可乐": "kele.mp3",
        "芬达": "fenda.mp3",
        "饼干": "bingan.mp3",
        "雪碧": "xuebi.mp3",
        "薯片": "shupian.mp3",
        "乐事": "leshi.mp3",
        "乐事薯片": "leshi.mp3",
        "曲奇": "quqi.mp3",
        "洗手液": "xishouye.mp3",
        "洗洁精": "xijiejing.mp3",
        "洗发水": "xifashui.mp3"
    }

    try:
        # === 修改 3: 显式指定 BT-BT 设备 ===
        with sd.RawInputStream(
                samplerate=samplerate,
                blocksize=blocksize,
                dtype='int16',
                channels=1,  # 单声道
                # device=BTBT_INPUT,  # 使用 BT-BT 输入设备
                callback=callback
        ):
            rec = vosk.KaldiRecognizer(model, samplerate)

            if welcome_mp3:
                print(f"🔊 播放客人欢迎语: {welcome_mp3}")
                global listening
                listening = False
                play_mp3(welcome_mp3)
                listening = True
                time.sleep(0.5)

            # 播放询问语音
            print("🔊 播放询问语音...")
            listening = False
            play_mp3("ask.mp3")
            listening = True
            time.sleep(0.5)

            print("👂 正在监听客人需求...")
            print("   (说出物品名称，如：水、可乐、饼干等)")
            print("   (识别到物品后自动结束)\n")

            dialogue_timeout = 30
            start_time = time.time()

            while True:
                if time.time() - start_time > dialogue_timeout:
                    print("\n⏱️  对话超时，结束交互")
                    break

                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").strip()

                    if text:
                        print(f"👂 识别到: 「{text}」")

                        matched = False
                        for keyword, mp3_file in responses.items():
                            if keyword in text:
                                print(f"✅ 匹配关键词: {keyword}")
                                print(f"🔊 播放回复语音: {mp3_file}")
                                play_mp3(mp3_file)
                                save_result_to_txt(keyword)
                                matched = True

                                print("✓ 语音交互完成\n")
                                return

                        if not matched:
                            print("❓ 未识别到有效物品，请重新说...")
                            play_mp3("answer.mp3")
                            start_time = time.time()

    except KeyboardInterrupt:
        print("\n⚠️  语音交互被中断")
    except Exception as e:
        print(f"❌ 语音识别错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("=" * 50)
        print("🎤 语音交互已结束")
        print("=" * 50 + "\n")


if __name__ == "__main__":
    print("🧪 测试模式：直接启动语音交互")
    # if BTBT_INPUT is None or BTBT_OUTPUT is None:
    #     print("❌ 无法启动：BT-BT 设备未找到")
    #     sys.exit(1)
    start_dialogue("welcome.mp3")