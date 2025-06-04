from absl import app
from absl import flags
import problem as pr
from graph import Graph

# 定义标志
_PROBLEMS_FILE = flags.DEFINE_string(
    'problems_file',
    'imo_ag_30.txt',
    'text file contains the problem strings. See imo_ag_30.txt for example.',
)
_PROBLEM_NAME = flags.DEFINE_string(
    'problem_name',
    'translated_imo_2000_p1',
    'name of the problem to solve, must be in the problem_file.',
)

def main(argv):
    # 在标志解析后访问标志的值
    problems = pr.Problem.from_txt_file(
        _PROBLEMS_FILE.value, to_dict=True, translate=False
    )
    this_problem = problems[_PROBLEM_NAME.value]

    # 创建 Graph 实例
    g = Graph()
    a = lambda x: g.get(x, lambda: int(x))()
    # 处理 this_problem.goal.args
    args = list(map(lambda x: g.get(x, lambda: int(x))(), this_problem.goal.args))
    print(args)

if __name__ == '__main__':
    app.run(main)