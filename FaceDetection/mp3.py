import asyncio
import edge_tts
import os

# 输出目录
output_dir = "FaceDetection/tts_mp3"
os.makedirs(output_dir, exist_ok=True)

# 需要生成的文本与文件名
tts_texts = {
    "biscuit": "识别到饼干。",
    "chip": "识别到薯片。",
    "lays": "识别到乐事薯片。",
    "cookie": "识别到曲奇。",
    "handwash": "识别到洗手液。",
    "dishsoap": "识别到洗洁精。",
    "shui": "识别到水。",
    "sprite": "识别到雪碧。",
    "cola": "识别到可乐。",
    "OrangeJuice": "识别到芬达。",
    "shampoo": "识别到洗发水。",


    # "cjxwelcome": "识别到主人，陈继新。",
    # "pzywelcome": "识别到客人，潘正杨。",
    # "dxswelcome": "识别到主人，狄兴淞。",
    # "zwlwelcome": "识别到客人，张文丽。",
    # "lqwelcome": "欢迎光临，吕侨。",
    # "ask": "您好，我是服务机器人。请问您需要什么物品？",
    # "answer": "对不起，我没听清，您可以再说一遍吗",
    # "bingan": "好的，我去给您拿饼干。",
    # "shupian": "好的，我去给您拿薯片。",
    # "leshi": "好的，我去给您拿乐事薯片。",
    # "quqi":"好的，我去给您拿曲奇",
    # "xishouye":"好的，我去给您拿洗手液",
    # "xijiejing": "好的，我去给您拿洗洁精。",
    # "watter": "好的，我去给您拿矿泉水。",
    # "xuebi": "好的，我去给您拿雪碧。",
    # "kele": "好的，我去给您拿可乐。",
    # "fenda": "好的，我去给您拿芬达。",
    # "xifashui": "好的，我去给您拿洗发水。",
    # "laji": "识别到垃圾。"
}


async def generate_tts():
    for filename, text in tts_texts.items():
        mp3_path = os.path.join(output_dir, f"{filename}.mp3")

        # edge-tts 中文女声
        communicate = edge_tts.Communicate(text, voice="zh-CN-XiaoxiaoNeural")

        # 保存 MP3
        await communicate.save(mp3_path)
        print(f"生成完成: {mp3_path}")


if __name__ == "__main__":
    asyncio.run(generate_tts())
