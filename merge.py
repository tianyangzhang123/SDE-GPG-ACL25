import json
import os

def merge_json_files(input_folder, output_file):
    """
    合并指定文件夹中所有 JSON 文件的内容到一个 JSON 文件中。
    :param input_folder: 包含 JSON 文件的文件夹路径
    :param output_file: 输出的 JSON 文件路径
    """
    # 初始化一个空列表，用于存储所有合并后的数据
    merged_list = []

    # 遍历文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(input_folder, filename)
            # 打开并读取 JSON 文件
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                # 确保读取的内容是列表
                if isinstance(data, list):
                    merged_list.extend(data)
                else:
                    print(f"Warning: {filename} does not contain a list.")

    # 将合并后的列表保存到新的 JSON 文件中
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(merged_list, outfile, ensure_ascii=False, indent=4)

    print(f"All JSON files have been merged into {output_file}")

# 示例用法
input_folder = "output"  # 替换为你的 JSON 文件所在文件夹路径
output_file = "merged_output.json"  # 替换为你的输出文件路径

merge_json_files(input_folder, output_file)