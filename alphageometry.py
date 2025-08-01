# Copyright 2023 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Run DD+AR or AlphaGeometry solver.

Please refer to README.md for detailed instructions.
"""

# 捕获和处理异常
import traceback
# 使用 absl 库的 app、flags 和 logging 模块，用于程序运行、参数解析和日志记录。
from absl import app
from absl import flags
from absl import logging
# 以下几个模块是自定义模块
# ddar：实现 DD+AR 模式的求解逻辑。
# graph：用于表示和操作几何问题的图结构。
# lm_inference：用于语言模型的推理。
# pretty：用于将逻辑语句转换为自然语言描述。
# problem：用于定义和解析几何问题。
import ddar
import graph as gh
import lm_inference as lm
import pretty_o as pt
import problem as pr


# 配置 Gin（一个用于配置模型的工具）的路径、文件和参数绑定
_GIN_SEARCH_PATHS = flags.DEFINE_list(
    'gin_search_paths',
    ['third_party/py/meliad/transformer/configs'],
    'List of paths where the Gin config files are located.',
)
_GIN_FILE = flags.DEFINE_multi_string(
    'gin_file', ['base_htrans.gin'], 'List of Gin config files.'
)
_GIN_PARAM = flags.DEFINE_multi_string(
    'gin_param', None, 'Newline separated list of Gin parameter bindings.'
)
# 定义问题文件路径、问题名称（必须在问题文件中定义）和运行模式
_PROBLEMS_FILE = flags.DEFINE_string(
    'problems_file',
    'imo_ag_30.txt',
    'text file contains the problem strings. See imo_ag_30.txt for example.',
)
_PROBLEM_NAME = flags.DEFINE_string(
    'problem_name',
    'imo_2000_p1',
    'name of the problem to solve, must be in the problem_file.',
)
_MODE = flags.DEFINE_string(
    'mode', 'ddar', 'either `ddar` (DD+AR) or `alphageometry`') # 运行模式为ddar或alphageometry
# 可用构造动作定义的文件路径
_DEFS_FILE = flags.DEFINE_string(
    'defs_file',
    'defs.txt',
    'definitions of available constructions to state a problem.',
)
# 推理规则文件路径
_RULES_FILE = flags.DEFINE_string(
    'rules_file', 'rules.txt', 'list of deduction rules used by DD.'
)
# 语言模型的检查点路径
_CKPT_PATH = flags.DEFINE_string('ckpt_path', '', 'checkpoint of the LM model.')
# 语言模型词汇表的路径
_VOCAB_PATH = flags.DEFINE_string(
    'vocab_path', '', 'path to the LM vocab file.'
)
# 解决方案的输出文件路径
_OUT_FILE = flags.DEFINE_string(
    'out_file', '', 'path to the solution output file.'
)  # pylint: disable=line-too-long

# 定义证明搜索的束大小（beam_size）和证明搜索的深度（search_depth）
_BEAM_SIZE = flags.DEFINE_integer(
    'beam_size', 1, 'beam size of the proof search.'
)  # pylint: disable=line-too-long
_SEARCH_DEPTH = flags.DEFINE_integer(
    'search_depth', 1, 'search depth of the proof search.'
)  # pylint: disable=line-too-long

# DEFINITIONS 存储几何构造动作的定义；RULES存储推理规则
DEFINITIONS = None  # contains definitions of construction actions
RULES = None  # contains rules of deductions


# 以上都是定义内容，没有文件读取等具体操作



# 将逻辑语句（pr.Dependency对象）转换为自然语言描述
def natural_language_statement(logical_statement: pr.Dependency) -> str:
  """Convert logical_statement to natural language.

  Args:
    logical_statement: pr.Dependency with .name and .args

  Returns:
    a string of (pseudo) natural language of the predicate for human reader.
  """
  names = [a.name.upper() for a in logical_statement.args]
  names = [(n[0] + '_' + n[1:]) if len(n) > 1 else n for n in names]
  return pt.pretty_nl(logical_statement.name, names)

# 将证明步骤转化自然语言
def proof_step_string(
    proof_step: pr.Dependency, refs: dict[tuple[str, ...], int], last_step: bool
) -> str:
  """Translate proof to natural language.

  Args:
    proof_step: pr.Dependency with .name and .args 证明步骤
    refs: dict(hash: int) to keep track of derived predicates 跟踪已经推导出的谓词
    last_step: boolean to keep track whether this is the last step. 存储是否是最后一步

  Returns:
    a string of (pseudo) natural language of the proof step for human reader.
  """
  premises, [conclusion] = proof_step

  premises_nl = ' & '.join(
      [
          natural_language_statement(p) + ' [{:02}]'.format(refs[p.hashed()])
          for p in premises
      ]
  )

  if not premises:
    premises_nl = 'similarly'

  refs[conclusion.hashed()] = len(refs)

  conclusion_nl = natural_language_statement(conclusion)
  if not last_step:
    conclusion_nl += ' [{:02}]'.format(refs[conclusion.hashed()])

  return f'{premises_nl} \u21d2 {conclusion_nl}'

# 求解结果写入指定的输出文件
def write_solution(g: gh.Graph, p: pr.Problem, out_file: str) -> None:
  """Output the solution to out_file.

  Args:
    g: gh.Graph object, containing the proof state. 图对象，包含证明状态。
    p: pr.Problem object, containing the theorem. 问题对象，包含定理。
    out_file: file to write to, empty string to skip writing to file. 输出文件路径。
  """
  setup, aux, proof_steps, refs = ddar.get_proof_steps(
      g, p.goal, merge_trivials=False
  )

  solution = '\n=========================='
  solution += '\n * From theorem premises:\n'
  premises_nl = []
  for premises, [points] in setup:
    solution += ' '.join([p.name.upper() for p in points]) + ' '
    if not premises:
      continue
    premises_nl += [
        natural_language_statement(p) + ' [{:02}]'.format(refs[p.hashed()])
        for p in premises
    ]
  solution += ': Points\n' + '\n'.join(premises_nl)

  solution += '\n\n * Auxiliary Constructions:\n'
  aux_premises_nl = []
  for premises, [points] in aux:
    solution += ' '.join([p.name.upper() for p in points]) + ' '
    aux_premises_nl += [
        natural_language_statement(p) + ' [{:02}]'.format(refs[p.hashed()])
        for p in premises
    ]
  solution += ': Points\n' + '\n'.join(aux_premises_nl)

  # some special case where the deduction rule has a well known name.
  r2name = {
      'r32': '(SSS)',
      'r33': '(SAS)',
      'r34': '(Similar Triangles)',
      'r35': '(Similar Triangles)',
      'r36': '(ASA)',
      'r37': '(ASA)',
      'r38': '(Similar Triangles)',
      'r39': '(Similar Triangles)',
      'r40': '(Congruent Triangles)',
      'a00': '(Distance chase)',
      'a01': '(Ratio chase)',
      'a02': '(Angle chase)',
  }

  solution += '\n\n * Proof steps:\n'
  for i, step in enumerate(proof_steps):
    _, [con] = step
    nl = proof_step_string(step, refs, last_step=i == len(proof_steps) - 1)
    rule_name = r2name.get(con.rule_name, '')
    nl = nl.replace('\u21d2', f'{rule_name}\u21d2 ')
    solution += '{:03}. '.format(i + 1) + nl + '\n'

  solution += '==========================\n'
  logging.info(solution)
  if out_file:
    with open(out_file, 'w') as f:
      f.write(solution)
    logging.info('Solution written to %s.', out_file)

# 初始化语言模型，用于 AlphaGeometry 模式
# ckpt_init：模型检查点路径。
# vocab_path：词汇表路径。
def get_lm(ckpt_init: str, vocab_path: str) -> lm.LanguageModelInference:
  lm.parse_gin_configuration(
      _GIN_FILE.value, _GIN_PARAM.value, gin_paths=_GIN_SEARCH_PATHS.value
  )

  return lm.LanguageModelInference(vocab_path, ckpt_init, mode='beam_search')


# ！以下是核心功能模块

# 运行 DD+AR 模式，尝试解决几何问题
def run_ddar(g: gh.Graph, p: pr.Problem, out_file: str) -> bool:
  """Run DD+AR.

  Args:
    g: gh.Graph object, containing the proof state.
    p: pr.Problem object, containing the problem statement.
    out_file: path to output file if solution is found.

  Returns:
    Boolean, whether DD+AR finishes successfully.
  """
  ddar.solve(g, RULES, p, max_level=1000)

  goal_args = g.names2nodes(p.goal.args)
  if not g.check(p.goal.name, goal_args):
    logging.info('DD+AR failed to solve the problem.')
    return False

  write_solution(g, p, out_file)
  return True


def translate_constrained_to_constructive(
    point: str, name: str, args: list[str]
) -> tuple[str, list[str]]:
  """Translate a predicate from constraint-based to construction-based.

  Args:
    point: str: name of the new point
    name: str: name of the predicate, e.g., perp, para, etc.
    args: list[str]: list of predicate args.

  Returns:
    (name, args): translated to constructive predicate.
  """
  if name in ['T', 'perp']:
    a, b, c, d = args
    if point in [c, d]:
      a, b, c, d = c, d, a, b
    if point == b:
      a, b = b, a
    if point == d:
      c, d = d, c
    if a == c and a == point:
      return 'on_dia', [a, b, d]
    return 'on_tline', [a, b, c, d]

  elif name in ['P', 'para']:
    a, b, c, d = args
    if point in [c, d]:
      a, b, c, d = c, d, a, b
    if point == b:
      a, b = b, a
    return 'on_pline', [a, b, c, d]

  elif name in ['D', 'cong']:
    a, b, c, d = args
    if point in [c, d]:
      a, b, c, d = c, d, a, b
    if point == b:
      a, b = b, a
    if point == d:
      c, d = d, c
    if a == c and a == point:
      return 'on_bline', [a, b, d]
    if b in [c, d]:
      if b == d:
        c, d = d, c  # pylint: disable=unused-variable
      return 'on_circle', [a, b, d]
    return 'eqdistance', [a, b, c, d]

  elif name in ['C', 'coll']:
    a, b, c = args
    if point == b:
      a, b = b, a
    if point == c:
      a, b, c = c, a, b
    return 'on_line', [a, b, c]

  elif name in ['^', 'eqangle']:
    a, b, c, d, e, f = args

    if point in [d, e, f]:
      a, b, c, d, e, f = d, e, f, a, b, c

    x, b, y, c, d = b, c, e, d, f
    if point == b:
      a, b, c, d = b, a, d, c

    if point == d and x == y:  # x p x b = x c x p
      return 'angle_bisector', [point, b, x, c]

    if point == x:
      return 'eqangle3', [x, a, b, y, c, d]

    return 'on_aline', [a, x, b, c, y, d]

  elif name in ['cyclic', 'O']:
    a, b, c = [x for x in args if x != point]
    return 'on_circum', [point, a, b, c]

  return name, args


def check_valid_args(name: str, args: list[str]) -> bool:
  """Check whether a predicate is grammarically correct.

  Args:
    name: str: name of the predicate
    args: list[str]: args of the predicate

  Returns:
    bool: whether the predicate arg count is valid.
  """
  if name == 'perp':
    if len(args) != 4:
      return False
    a, b, c, d = args
    if len({a, b}) < 2:
      return False
    if len({c, d}) < 2:
      return False
  elif name == 'para':
    if len(args) != 4:
      return False
    a, b, c, d = args
    if len({a, b, c, d}) < 4:
      return False
  elif name == 'cong':
    if len(args) != 4:
      return False
    a, b, c, d = args
    if len({a, b}) < 2:
      return False
    if len({c, d}) < 2:
      return False
  elif name == 'coll':
    if len(args) != 3:
      return False
    a, b, c = args
    if len({a, b, c}) < 3:
      return False
  elif name == 'cyclic':
    if len(args) != 4:
      return False
    a, b, c, d = args
    if len({a, b, c, d}) < 4:
      return False
  elif name == 'eqangle':
    if len(args) != 8:
      return False
    a, b, c, d, e, f, g, h = args
    if len({a, b, c, d}) < 3:
      return False
    if len({e, f, g, h}) < 3:
      return False
  return True


def try_translate_constrained_to_construct(string: str, g: gh.Graph) -> str:
  """Whether a string of aux construction can be constructed.

  Args:
    string: str: the string describing aux construction.
    g: gh.Graph: the current proof state.

  Returns:
    str: whether this construction is valid. If not, starts with "ERROR:".
  """
  if string[-1] != ';':
    return 'ERROR: must end with ;'

  head, prem_str = string.split(' : ')
  point = head.strip()

  if len(point) != 1 or point == ' ':
    return f'ERROR: invalid point name {point}'

  existing_points = [p.name for p in g.all_points()]
  if point in existing_points:
    return f'ERROR: point {point} already exists.'

  prem_toks = prem_str.split()[:-1]  # remove the EOS ' ;'
  prems = [[]]

  for i, tok in enumerate(prem_toks):
    if tok.isdigit():
      if i < len(prem_toks) - 1:
        prems.append([])
    else:
      prems[-1].append(tok)

  if len(prems) > 2:
    return 'ERROR: there cannot be more than two predicates.'

  clause_txt = point + ' = '
  constructions = []

  for prem in prems:
    name, *args = prem

    if point not in args:
      return f'ERROR: {point} not found in predicate args.'

    if not check_valid_args(pt.map_symbol(name), args):
      return 'ERROR: Invalid predicate ' + name + ' ' + ' '.join(args)

    for a in args:
      if a != point and a not in existing_points:
        return f'ERROR: point {a} does not exist.'

    try:
      name, args = translate_constrained_to_constructive(point, name, args)
    except:  # pylint: disable=bare-except
      return 'ERROR: Invalid predicate ' + name + ' ' + ' '.join(args)

    if name == 'on_aline':
      if args.count(point) > 1:
        return f'ERROR: on_aline involves twice {point}'

    constructions += [name + ' ' + ' '.join(args)]

  clause_txt += ', '.join(constructions)
  clause = pr.Clause.from_txt(clause_txt)

  try:
    g.copy().add_clause(clause, 0, DEFINITIONS)
  except:  # pylint: disable=bare-except
    return 'ERROR: ' + traceback.format_exc()

  return clause_txt


def insert_aux_to_premise(pstring: str, auxstring: str) -> str:
  """Insert auxiliary constructs from proof to premise.

  Args:
    pstring: str: describing the problem to solve.
    auxstring: str: describing the auxiliar construction.

  Returns:
    str: new pstring with auxstring inserted before the conclusion.
  """
  setup, goal = pstring.split(' ? ')
  return setup + '; ' + auxstring + ' ? ' + goal


class BeamQueue:
  """Keep only the top k objects according to their values."""

  def __init__(self, max_size: int = 512):
    self.queue = []
    self.max_size = max_size

  def add(self, node: object, val: float) -> None:
    """Add a new node to this queue."""

    if len(self.queue) < self.max_size:
      self.queue.append((val, node))
      return

    # Find the minimum node:
    min_idx, (min_val, _) = min(enumerate(self.queue), key=lambda x: x[1])

    # replace it if the new node has higher value.
    if val > min_val:
      self.queue[min_idx] = (val, node)

  def __iter__(self):
    for val, node in self.queue:
      yield val, node

  def __len__(self) -> int:
    return len(self.queue)


# 运行 AlphaGeometry 模式
# 通过语言模型生成辅助构造，并结合 DD+AR 模式进行证明搜索
def run_alphageometry(
    model: lm.LanguageModelInference,
    p: pr.Problem,
    search_depth: int,
    beam_size: int,
    out_file: str,
) -> bool:
  """Simplified code to run AlphaGeometry proof search.

  We removed all optimizations that are infrastructure-dependent, e.g.
  parallelized model inference on multi GPUs,
  parallelized DD+AR on multiple CPUs,
  parallel execution of LM and DD+AR,
  shared pool of CPU workers across different problem, etc.

  Many other speed optimizations and abstractions are also removed to
  better present the core structure of the proof search.

  将几何问题转换为语言模型（LM）可以处理的格式。
  使用符号引擎（DD+AR）尝试直接解决问题。
  如果符号引擎无法解决问题，则使用 beam search 结合 LM 逐步生成辅助点并更新证明状态。
  记录证明过程，并在找到解决方案时输出结果。

  Args:
    model: Interface with inference-related endpoints to JAX's model.
    p: pr.Problem object describing the problem to solve.
    search_depth: max proof search depth.
    beam_size: beam size of the proof search.
    out_file: path to output file if solution is found.

  Returns:
    boolean of whether this is solved.
  """
  # translate the problem to a string of grammar that the LM is trained on.
  # 将几何问题转换为语言模型可以处理的字符串格式。
  string = p.setup_str_from_problem(DEFINITIONS)
  # special tokens prompting the LM to generate auxiliary points.
  # {F1} x00 是一个特殊标记，提示 LM 生成辅助点。
  string += ' {F1} x00'
  # the graph to represent the proof state.
  g, _ = gh.Graph.build_problem(p, DEFINITIONS)

  # First we run the symbolic engine DD+AR: 调用 run_ddar 函数，尝试使用符号引擎直接解决问题
  if run_ddar(g, p, out_file):
    return True

  # beam search for the proof
  # each node in the search tree is a 3-tuple:
  # (<graph representation of proof state>,
  #  <string for LM to decode from>,
  #  <original problem string>)
  # 初始化 beam search 队列，g-图状态，string-LM 的输入字符串，p.txt()-原始问题字符串
  beam_queue = BeamQueue(max_size=beam_size)
  # originally the beam search tree starts with a single node (a 3-tuple):
  beam_queue.add(
      node=(g, string, p.txt()), val=0.0  # value of the root node is simply 0.
  )

  for depth in range(search_depth):
    logging.info(
        'Depth %s. There are %i nodes to expand:', depth, len(beam_queue)
    )
    for _, (_, string, _) in beam_queue:
      logging.info(string)

    new_queue = BeamQueue(max_size=beam_size)  # to replace beam_queue.

    for prev_score, (g, string, pstring) in beam_queue:
      logging.info('Decoding from %s', string)
      outputs = model.beam_decode(string, eos_tokens=[';'])

      # translate lm output to the constructive language.
      # so that we can update the graph representing proof states:
      translations = [
          try_translate_constrained_to_construct(o, g)
          for o in outputs['seqs_str']
      ]

      # couple the lm outputs with its translations
      candidates = zip(outputs['seqs_str'], translations, outputs['scores'])

      # bring the highest scoring candidate first
      candidates = reversed(list(candidates))

      for lm_out, translation, score in candidates:
        logging.info('LM output (score=%f): "%s"', score, lm_out)
        logging.info('Translation: "%s"\n', translation)

        if translation.startswith('ERROR:'):
          # the construction is invalid.
          continue

        # Update the constructive statement of the problem with the aux point:
        candidate_pstring = insert_aux_to_premise(pstring, translation)

        logging.info('Solving: "%s"', candidate_pstring)
        p_new = pr.Problem.from_txt(candidate_pstring)

        # This is the new proof state graph representation: 添加了辅助点的问题&图像成功解决，则证明搜索ok
        g_new, _ = gh.Graph.build_problem(p_new, DEFINITIONS)
        if run_ddar(g_new, p_new, out_file):
          logging.info('Solved.')
          return True

        # Add the candidate to the beam queue.
        new_queue.add(
            # The string for the new node is old_string + lm output +
            # the special token asking for a new auxiliary point ' x00':
            node=(g_new, string + ' ' + lm_out + ' x00', candidate_pstring),
            # the score of each node is sum of score of all nodes
            # on the path to itself. For beam search, there is no need to
            # normalize according to path length because all nodes in beam
            # is of the same path length.
            val=prev_score + score,
        )
        # Note that the queue only maintain at most beam_size nodes
        # so this new node might possibly be dropped depending on its value.

    # replace the old queue with new queue before the new proof search depth.
    beam_queue = new_queue

  return False


def main(_):
  global DEFINITIONS
  global RULES

  # definitions of terms used in our domain-specific language. defs.txt 生成data，其中包含多个Definition实例
  DEFINITIONS = pr.Definition.from_txt_file(_DEFS_FILE.value, to_dict=True)
  # load inference rules used in DD. 生成theorems，其中包含多个Theorem实例
  RULES = pr.Theorem.from_txt_file(_RULES_FILE.value, to_dict=True)

  # when using the language model,
  # point names will be renamed to alphabetical a, b, c, d, e, ...
  # instead of staying with their original names,
  # in order to match the synthetic training data generation.
  # 使用语言模型时，point names需要重命名为a，b，c。。。--以匹配合成训练数据的生成
  need_rename = _MODE.value != 'ddar'

  # load problem from the problems_file, 生成data，其中包含多个Problem实例
  problems = pr.Problem.from_txt_file(
      _PROBLEMS_FILE.value, to_dict=True, translate=need_rename
  )

  if _PROBLEM_NAME.value not in problems:
    raise ValueError(
        f'Problem name `{_PROBLEM_NAME.value}` '
        + f'not found in `{_PROBLEMS_FILE.value}`'
    )

  # this_problem = translated_imo_2000_p1对应的Problem实例
  this_problem = problems[_PROBLEM_NAME.value]

  if _MODE.value == 'ddar':
    g, _ = gh.Graph.build_problem(this_problem, DEFINITIONS)
    # ddar只包括推理辅助
    run_ddar(g, this_problem, _OUT_FILE.value)

  elif _MODE.value == 'alphageometry':
    # alphageometry包含模型的辅助点拓展
    model = get_lm(_CKPT_PATH.value, _VOCAB_PATH.value)
    run_alphageometry(
        model,
        this_problem,
        _SEARCH_DEPTH.value,
        _BEAM_SIZE.value,
        _OUT_FILE.value,
    )

  else:
    raise ValueError(f'Unknown FLAGS.mode: {_MODE.value}')


if __name__ == '__main__':
  app.run(main)
