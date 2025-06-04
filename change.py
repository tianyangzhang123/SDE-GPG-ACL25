import json
def json_to_txt_type(json_data):
    """
    将 JSON 格式的数据转换为指定的 txt_type 格式。
    :param json_data: JSON 格式的数据（字典）
    :return: 转换后的 txt_type 格式的字符串
    """
    txt_type = (
        f"原始题号:{json_data.get('pic_name', '')}. "
        f"原题FL: {json_data.get('原题fl', '')}. "
        f"原题的知识点: {json_data.get('原题知识点', '')}. "
        # f"que_text: {json_data.get('que_text', '')}. "
        # f"{json_data.get('结论', '')}. "
        f"前提: {json_data.get('前提', '')}. "
        # f"结论: {json_data.get('结论', '')}. "
        f"步骤: {json_data.get('步骤', '')}. "
        f"生成题目的FL: {json_data.get('生成题目的fl', '')}. "
        # f"{json_data.get('结论', '')}. "
        f"步骤长度: {json_data.get('步骤长度', '')}. "
        f"使用的知识点(英文): {json_data.get('使用的知识点(英文)', '')}. "
        f"使用的知识点(中文): {json_data.get('使用的知识点(中文)', '')}. "
        f"知识点数量: {json_data.get('知识点数量', '')}"
    )
    return txt_type

def process_json_file(input_file, output_file):
    """
    从输入的 JSON 文件中读取数据，转换为 txt_type 格式，并保存到输出的文本文件中。
    :param input_file: 输入的 JSON 文件路径
    :param output_file: 输出的文本文件路径
    """
    with open(input_file, "r", encoding="utf-8") as infile:
        json_list = json.load(infile)  # 加载 JSON 文件内容为 Python 列表

    with open(output_file, "w", encoding="utf-8") as outfile:
        for json_data in json_list:
            if json_data:  # 确保数据块不为空
                txt_type = json_to_txt_type(json_data)  # 转换为 txt_type 格式
                outfile.write(txt_type + "\n")  # 写入到文本文件，每行一个数据块
# 示例 JSON 数据
# json_data = {
#     '原始题号': '18',
#     '原题fl': '',
#     '原题知识点': 'eqangle6_eqangle6_ncoll_cong_contri2; eqratio6_eqratio6_ncoll_simtri*',
#     'que_text': '构造五边形ABCDE; 将点I作为CAB的重心，CI,AI,BI分别和AB,CB,CA相交于点F,G,H; 将点J作为A、E、C的外接圆中心 求证: CH=FG',
#     '前提': 'B,A,F共线; FA=FB; B,C,G共线; GB=GC; C,A,H共线; HC=HA',
#     '结论': 'CH=FG',
#     '步骤': 'B,A,F共线, FA=FB => F是BA的中点; B,C,G共线, GB=GC => G是BC的中点; F是BA的中点, G是BC的中点 => FG∥AC; C,A,H共线, FG∥AC => CH∥FG; C,A,H共线, HC=HA => H是AC的中点; F是BA的中点, H是AC的中点 => FH∥BC; C,B,G共线, FH∥BC => CG∥FH; CH∥FG, CG∥FH => CH=FG',
#     '生成题目的fl': 'COLL B A F; CONG F A F B; COLL B C G; CONG G B G C; COLL C A H; CONG H C H A ? CONG C H F G',
#     '步骤长度': '8',
#     '使用的知识点(英文)': 'MIDP E A B, MIDP F A C => PARA E F B C; PARA A C B D, PARA A D B C => CONG A C B D',
#     '使用的知识点(中文)': '三角形的中位线平行于第三边【中位线定理】; 两组对边分别平行的四边形是平行四边形，若四边形ACBD为平行四边形，则AC=BD【平行四边形的对边相等】',
#     '知识点数量': '2',
#     'pic_name': 'pics/pic6_20250320-141956.png'
# }

# 转换为 txt_type 格式
# txt_type = json_to_txt_type(json_data)
# print(txt_type)

# input_file = "problems/output_1.json"  # 替换为你的输入 JSON 文件路径
# output_file = "merged_output.txt"  # 替换为你的输出文本文件路径

# process_json_file(input_file, output_file)

import os
import re


def extract_pic_names_from_txt(file_path):
    """
    从 txt 文件中提取每行中的图片地址。
    :param file_path: txt 文件路径
    :return: 包含图片地址的集合
    """
    pic_names = set()
    # pattern = re.compile(r"原始题号:(pics/[^.]+\.png)")
    pattern = re.compile(r"原始题号:pics/([^.\n]+\.png)")

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            match = pattern.search(line)
            if match:
                pic_names.add(match.group(1))

    return pic_names


def delete_unreferenced_pics(txt_file_path, pics_folder):
    """
    删除 pics 文件夹中未在 txt 文件中出现的图片。
    :param txt_file_path: txt 文件路径
    :param pics_folder: 包含图片的文件夹路径
    """
    # 提取 txt 文件中提到的图片地址
    referenced_pics = extract_pic_names_from_txt(txt_file_path)

    # 获取 pics 文件夹中的所有图片文件
    all_pics = set(os.listdir(pics_folder))

    # 比较并删除未在 txt 文件中出现的图片
    for pic in all_pics:
        if pic not in referenced_pics:
            os.remove(os.path.join(pics_folder, pic))
            print(f"Deleted: {pic}")


# 示例用法
txt_file_path = "geoqa_without_check/merged_output.txt"  # 替换为你的 txt 文件路径
pics_folder = "pics2"  # 替换为你的图片文件夹路径

delete_unreferenced_pics(txt_file_path, pics_folder)