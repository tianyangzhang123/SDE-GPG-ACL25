import json
import problem_generating as pg
from generate import generate_question

def read_input_rules_from_file(file_path):
    """
    从文件中逐行读取数据，每行数据作为一个 input_rules 列表。
    :param file_path: 文件路径
    :return: 包含所有 input_rules 的列表
    """
    input_rules_list = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            # 去除首尾空格，并按分号分割
            rules = line.strip().split(";")
            # 去除每个规则的首尾空格
            rules = [rule.strip() for rule in rules]
            input_rules_list.append(rules)
    return input_rules_list

def generate_problems_from_rules(input_rules_list, context, step=3, batch=8, input_type="theorem"):
    """
    对每个 input_rules 运行 generate_question 函数，并将结果收集到一个总列表中。
    :param input_rules_list: 包含所有 input_rules 的列表
    :param context: GeoProblemCreator 对象
    :param step: 参数 step
    :param batch: 参数 batch
    :param input_type: 参数 input_type
    :return: 包含所有结果的总列表
    """
    all_results = []
    for input_rules in input_rules_list:
        result_json = generate_question(request_kg=input_rules, context=context, step=step, batch=batch, input_type=input_type)
        all_results.extend(result_json)  # 将结果添加到总列表中
    return all_results

def save_results_to_json(all_results, output_file_path):
    """
    将总结果列表保存到 JSON 文件中。
    :param all_results: 包含所有结果的总列表
    :param output_file_path: 输出文件路径
    """
    with open(output_file_path, "w", encoding="utf-8") as file:
        json.dump(all_results, file, ensure_ascii=False, indent=4)

# 文件路径
geoqa_file_path = "problems/geoqa_1.txt"  # 替换为你的 geoqa 文件路径
output_json_path = "problems/output_1.json"  # 替换为你的输出 JSON 文件路径

# 读取 input_rules
input_rules_list = read_input_rules_from_file(geoqa_file_path)

# 创建 GeoProblemCreator 对象
context = pg.GeoProblemCreator()

# 生成问题并收集结果
all_results = generate_problems_from_rules(input_rules_list, context)

# 保存结果到 JSON 文件
save_results_to_json(all_results, output_json_path)

print(f"所有结果已保存到 {output_json_path}")