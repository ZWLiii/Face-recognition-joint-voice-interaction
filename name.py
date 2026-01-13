import os
import zipfile

# -------- 配置参数 --------
# 文件夹列表及对应的前缀
folders = [
    # (r"D:\zuomian\orange_juice", "orange_juice"),
    # (r"D:\zuomian\lays", "lays"),
    # (r"D:\zuomian\dishsoap", "dishsoap"),
    # (r"D:\zuomian\chip", "chip"),
    # (r"D:\zuomian\handwash", "handwash"),
    # (r"D:\zuomian\shampoo", "shampoo"),
    # (r"D:\zuomian\sprite", "sprite"),
    # (r"D:\zuomian\water", "water"),
    (r"D:\zuomian\aoliao", "biscuit"),
    # 如果还有其他文件夹，继续添加：
    # (r"D:\zuomian\another_folder", "another_prefix")
]
# 图片扩展名（支持多种格式）
exts = ('.jpg', '.png')
# -------------------------

for folder_path, prefix in folders:
    if not os.path.isdir(folder_path):
        print(f"⚠️ 文件夹不存在: {folder_path}, 跳过")
        continue

    folder_name = os.path.basename(folder_path)
    print(f"🔹 处理文件夹: {folder_name}，前缀: {prefix}")

    # 获取图片文件并排序
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(exts)]
    files.sort()

    # 1️⃣ 重命名
    for idx, filename in enumerate(files):
        old_path = os.path.join(folder_path, filename)
        ext = os.path.splitext(filename)[1]  # 保留原后缀
        new_name = f"{prefix}{idx}{ext}"
        new_path = os.path.join(folder_path, new_name)
        os.rename(old_path, new_path)
    print(f"✅ 已完成重命名 {len(files)} 张图片")

    # 2️⃣ 压缩成 zip
    zip_path = os.path.join(os.path.dirname(folder_path), f"{folder_name}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            zipf.write(file_path, arcname=filename)  # 压缩包内只保留文件名
    print(f"✅ 已压缩为 {zip_path}\n")

print("🎉 所有文件夹处理完成！")
