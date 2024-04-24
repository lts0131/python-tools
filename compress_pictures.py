"""
@File    : compress_pictures.py
@Date    : 2024-04-24
@Author  : LiuTianSheng
@Software : python-tools
"""
import os
from PIL import Image
import shutil

# 输入文件夹和输出文件夹路径
input_folder_path = ""
output_folder_path = ""


# 确保输出文件夹存在
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# 循环遍历输入文件夹中的所有文件
for filename in os.listdir(input_folder_path):
    input_file_path = os.path.join(input_folder_path, filename)

    # 检查文件是否为图片
    if input_file_path.endswith(".jpg") or input_file_path.endswith(".png"):
        # 压缩并保存图片到输出文件夹
        output_file_path = os.path.join(output_folder_path, filename)
        with Image.open(input_file_path) as image:
            # 逐步减小quality值，直到达到指定的压缩目标大小
            target_size_kb = 100  # 希望的压缩后文件大小，单位为KB
            quality = 20  # 初始的quality值
            while True:
                image.save(output_file_path, optimize=True, quality=quality)
                output_file_size = os.path.getsize(output_file_path) / 1024  # 将文件大小转换为KB
                if output_file_size <= target_size_kb or quality <= 15:
                    break
                quality -= 1

            print(f"压缩后文件 {filename} 的大小为: {output_file_size} KB")

print("图片压缩并保存完成！")

