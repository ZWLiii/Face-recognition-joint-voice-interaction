#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从多个视频中依次截取帧，并统一命名保存到同一文件夹下
示例：
python pic.py --videos mp4/aoliao1.mp4 mp4/aoliao2.mp4 --out data/aoliao --num 1000 --mode uniform
"""
import os
import cv2
import argparse
import numpy as np

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def extract_uniform(video_path, out_dir, start_idx, target_num, prefix="frame", ext="jpg"):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频文件: {video_path}")
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        raise RuntimeError(f"视频帧数未知或无法读取: {video_path}")
    pick_idx = np.linspace(0, total - 1, num=target_num, dtype=int)
    pick_set = set(pick_idx.tolist())

    saved = 0
    idx = 0
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx in pick_set:
            global_idx = start_idx + saved  # 保证连续编号
            filename = os.path.join(out_dir, f"{prefix}_{global_idx:06d}.{ext}")
            cv2.imwrite(filename, frame)
            saved += 1
            if saved % 100 == 0:
                print(f"[{os.path.basename(video_path)}] 已保存 {saved}/{target_num}")
            if saved >= target_num:
                break
        idx += 1
    cap.release()
    print(f"完成 {video_path}：共保存 {saved} 帧。")
    return start_idx + saved

def main():
    parser = argparse.ArgumentParser(description="从多个视频中依次截取帧并统一编号")
    parser.add_argument("--videos", nargs="+", required=True, help="输入视频路径列表，用空格分隔")
    parser.add_argument("--out", required=True, help="输出文件夹，会自动创建")
    parser.add_argument("--num", type=int, default=1000, help="每个视频截取的帧数")
    parser.add_argument("--mode", choices=["uniform"], default="uniform", help="目前仅支持均匀采样")
    parser.add_argument("--prefix", default="frame", help="输出文件名前缀")
    parser.add_argument("--ext", default="jpg", help="图片格式扩展名（jpg/png）")
    args = parser.parse_args()

    ensure_dir(args.out)
    next_start = 0
    for video_path in args.videos:
        next_start = extract_uniform(video_path, args.out, next_start, args.num, args.prefix, args.ext)
    print(f"全部完成，总共保存 {next_start} 张图片 -> {args.out}")

if __name__ == "__main__":
    main()
