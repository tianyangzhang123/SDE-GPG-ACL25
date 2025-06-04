import os
import re

def extract_question_numbers(txt_file_path):
    """
    从txt文件中提取所有原始题号
    :param txt_file_path: txt文件的路径
    :return: 一个集合，包含所有原始题号
    """
    question_numbers = set()
    pattern = re.compile(r"原始题号:(\d+_\d+)")  # 正则表达式匹配原始题号

    with open(txt_file_path, "r", encoding="utf-8") as file:
        for line in file:
            match = pattern.search(line)
            if match:
                question_numbers.add(match.group(1))

    return question_numbers

def clean_up_images(pics_folder, question_numbers):
    """
    检查并删除没有对应题号的图片文件
    :param pics_folder: 包含图片的文件夹路径
    :param question_numbers: 从txt文件中提取的题号集合
    """
    for filename in os.listdir(pics_folder):
        if filename.startswith("output_") and filename.endswith(".png"):
            # 提取文件名中的题号部分
            question_number = filename[len("output_"):-len(".png")]
            if question_number not in question_numbers:
                # 如果题号不在txt文件中，删除该图片文件
                os.remove(os.path.join(pics_folder, filename))
                print(f"Deleted: {filename}")

# 示例用法
txt_file_path = "alphageometry_with_check/cn_proof.txt"  # 替换为你的txt文件路径
pics_folder = "geometry-pics-v2"  # 替换为你的图片文件夹路径

# 提取txt文件中的题号
question_numbers = extract_question_numbers(txt_file_path)

# 清理图片文件夹
clean_up_images(pics_folder, question_numbers)