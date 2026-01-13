"""
tts_util.py - MP3 播放工具
使用 playsound 同步播放音频（播放完成后才返回）
"""
import os
os.environ["PATH"] += os.pathsep + r"D:/tools/ffmpeg/bin"
from pydub.playback import _play_with_simpleaudio
from pydub import AudioSegment
AudioSegment.converter = r"D:/tools/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffprobe   = r"D:/tools/ffmpeg/bin/ffprobe.exe"

def play_mp3(file_name):
    """
    播放本地 MP3 文件（同步阻塞，播完再继续）
    支持 Windows / Ubuntu / Python 3.6+
    依赖: pip install pydub simpleaudio && sudo apt install ffmpeg
    """
    # 构建完整路径
    mp3_path = os.path.join("D:/zuomian/faceDetection-main/FaceDetection/tts_mp3/", file_name)

    # 检查文件是否存在
    if not os.path.exists(mp3_path):
        print(f"❌ 找不到音频文件: {mp3_path}")
        print(f"   请确认文件名是否正确，且文件存在于 FaceDetection/tts_mp3/ 目录")
        return False

    try:
        print(f"▶️  正在播放: {file_name}")
        # 读取音频
        sound = AudioSegment.from_file(mp3_path, format="mp3")
        # 在开头加 50ms 静音，避免吞字
        sound = AudioSegment.silent(duration=500) + sound
        # 使用 simpleaudio 播放并阻塞直到结束
        play_obj = _play_with_simpleaudio(sound)
        play_obj.wait_done()  # 同步等待播放结束
        print(f"✓ 播放完成: {file_name}")
        return True
    except Exception as e:
        print(f"❌ 播放失败: {e}")
        return False


def test_audio_files():
    """测试所有音频文件是否存在"""
    audio_dir = "FaceDetection/tts_mp3/"

    print("\n" + "="*50)
    print("🔍 检查音频文件...")
    print("="*50)

    if not os.path.exists(audio_dir):
        print(f"❌ 音频目录不存在: {audio_dir}")
        return

    required_files = [
        "dxswelcome.mp3",  #欢迎词
        "zwlwelcome.mp3",   #欢迎词
        "lqwelcome.mp3",    #欢迎词
        "ask_item.mp3",     #询问客人需要哪些物品
        "answer.mp3",          #机器人回答没听清
        "bingan.mp3",   #机器人回答去拿饼干
        "shupian.mp3",
        "watter.mp3",
        "xuebi.mp3",
        "kele.mp3",
        "fenda.mp3",
        "quqi.mp3",
        "xishouye.mp3",
        "xijiejing.mp3",
        "xifashui.mp3",
        # "biscuit.mp3", #识别到饼干
        # "chip.mp3", #识别到薯片
        # "lays.mp3", #识别到乐事
        # "cookie.mp3", #识别到曲奇
        # "handwash.mp3", #识别到洗手液
        # "dishsoap.mp3", #识别到洗洁精
        # "shui.mp3", #识别到水
        # "sprite.mp3", #识别到雪碧
        # "cola.mp3", #识别到可乐
        # "OrangeJuice.mp3", #识别到橙汁
        # "shampoo.mp3", #识别到洗发水
    ]

    missing_files = []
    for filename in required_files:
        filepath = os.path.join(audio_dir, filename)
        if os.path.exists(filepath):
            size_kb = os.path.getsize(filepath) / 1024
            print(f"✓ {filename:20s} ({size_kb:.1f} KB)")
        else:
            print(f"✗ {filename:20s} [缺失]")
            missing_files.append(filename)

    print("="*50)
    if missing_files:
        print(f"⚠️  缺失 {len(missing_files)} 个文件:")
        for f in missing_files:
            print(f"   - {f}")
    else:
        print("✅ 所有音频文件完整！")
    print()


if __name__ == "__main__":
    # 测试所有音频文件
    test_audio_files()

    # 测试播放
    print("\n测试播放 'answer.mp3'...")
    play_mp3("")