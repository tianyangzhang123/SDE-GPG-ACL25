import random
from itertools import combinations

import problem as pr
import dataset
import graph as gh
import ddar
import trace_back as tb
import pretty_o as pt
import geometry as gm
import numericals as nm


class GeoProblemCreator:

    def __init__(self):
        self.setter = dataset.MyDataSet()
        self.topics = GeoProblemCreator.load_topic("topics.txt")

    @staticmethod
    def load_topic(file):
        with open(file, 'r') as t_file:
            lines = t_file.readlines()

        topic2defs = {}
        for line in lines:
            words = line.strip().split(" ")
            topic2defs[words[0]] = words[1:]
        return topic2defs

    @staticmethod
    def get_dep_proof_steps(
            g: gh.Graph, goal: pr.Dependency, idx: int, merge_trivials: bool = False, context=None
    ):
        # -> tuple[
        #     list[pr.Dependency],
        #     list[pr.Dependency],
        #     list[tuple[list[pr.Dependency], list[pr.Dependency]]],
        #     dict[tuple[str, ...], int],
        # ]
        """Extract proof steps from the built DAG."""

        # goal_args = g.names2nodes(goal.args)
        # query = Dependency(goal.name, goal_args, None, None)
        def to_premise(setup_or_aux):
            deps = []
            for plist, _ in setup_or_aux:
                deps += plist
            return deps

        def serialize(n: str, premise: list[pr.Dependency], goal: pr.Dependency,
                      proof: list[tuple[list[pr.Dependency], list[pr.Dependency]]], rules: list[str]):
            p_str = "; ".join([i.txt() for i in premise])
            g_str = goal.txt()
            pf_str = []
            for prev, clrd in proof:
                prs = ", ".join([i.txt() for i in prev])
                crs = ", ".join([i.txt() for i in clrd])
                pf_str.append("->".join([prs, crs]))
            rule_str = "; ".join(rules)
            return "<" + n + "><" + p_str + "><" + g_str + "><" + "; ".join(pf_str) + "><" + rule_str + ">", pf_str

        def check_log_contains_all_premises(premise, log):
            """
            检查 log 是否包含了 s_premise 中的所有 Dependency 对象。

            :param s_premise: 前置条件的依赖关系列表，包含 Dependency 对象。
            :param log: 推理步骤的详细记录，包含 Dependency 对象。
            :return: 如果 log 包含了 s_premise 中的所有 Dependency 对象，返回 True；否则返回 False。
            """
            # 将 s_premise 和 log 转换为集合
            re_premise = "; ".join([i.txt() for i in premise])
            premise_list = re_premise.split("; ")
            premise_set = set(premise_list)
            all_prems = []
            # re_prems = ""
            for prems, _ in log:
                re_prems = "; ".join([i.txt() for i in prems])
                all_prems += re_prems.split("; ")
            # all_prems_list = []
            # for i in all_prems:
            #     all_prems_list += change(i)
            # text = '"前提": "ED∥BA; EA∥DB",'
            letters = set()
            letters.update(*[item.split()[1:] for item in premise_list])
            letters.update(*[item.split()[1:] for item in all_prems])
            # letters = letters+re.findall(r"[a-z]", re_prems)
            # unique_letters = sorted(set(letters))
            # 检查 s_premise_set 是否是 log_set 的子集
            return premise_set.issubset(set(all_prems)), letters

        def extract_dependencies(log):
            """
            从嵌套结构中提取所有 problem.Dependency 对象。

            参数:
                log: 嵌套的结构，包含 problem.Dependency 对象。

            返回:
                dependencies: 包含所有 problem.Dependency 对象的列表。
            """
            dependencies = []  # 用于存储所有找到的 problem.Dependency 对象

            def traverse(item):
                """递归遍历嵌套结构"""
                if isinstance(item, pr.Dependency):
                    # 如果是 problem.Dependency 对象，添加到结果列表中
                    dependencies.append(item)
                elif isinstance(item, (list, tuple)):
                    # 如果是列表或元组，递归处理每个元素
                    for sub_item in item:
                        traverse(sub_item)

            # 遍历顶层结构
            for item in log:
                traverse(item)

            return dependencies

        def find_dependencies_with_r(log):
            """
            从嵌套结构中提取所有 rule_name 以 'r' 开头的 problem.Dependency 对象。

            参数:
                log: 嵌套的结构，包含 problem.Dependency 对象。

            返回:
                result: 包含符合条件的 rule_name 的列表。
            """
            # 提取所有 problem.Dependency 对象
            dependencies = extract_dependencies(log)

            # 根据 rule_name 找到对应的 problem.Theorem 对象
            theorem_set = set()  # 使用集合去重
            for dep in dependencies:
                if dep.rule_name and dep.rule_name.startswith('r'):
                    # theorem_name = dep.rule_name
                    th = context.setter.rules[dep.rule_name]
                    theorem_set.add(pr.Theorem.txt(th))

            # 返回唯一的 problem.Theorem 列表
            return list(theorem_set)

            # 筛选出 rule_name 以 'r' 开头的对象
            # result = [dep.rule_name for dep in dependencies if dep.rule_name and dep.rule_name.startswith('r')]

            # return set(result)

        setup, aux, log, setup_points = tb.get_logs(
            goal, g, merge_trivials=merge_trivials)

        used_rules = find_dependencies_with_r(log)

        refs = {}
        setup = tb.point_log(setup, refs, set())
        aux = tb.point_log(aux, refs, setup_points)

        setup = [(prems, [tuple(p)]) for p, prems in setup]
        aux = [(prems, [tuple(p)]) for p, prems in aux]

        # setup, aux, log, refs = MyDataSet.get_dep_proof_steps(g, s_add, merge_trivials=False)
        # setup, aux --> premise; s_add --> goal; step --> goal
        s_premise = to_premise(setup)
        a_premise = to_premise(aux)
        # flag, letters = check_log_contains_all_premises(s_premise + a_premise, log)
        # if flag:
        all_sample_str, pf_str = serialize(str(idx), s_premise + a_premise, goal, log, used_rules)

        # return setup, aux, log, refs
        return all_sample_str, pf_str
        # else:
        #     return None, None


def process(self, req, p_thr=2, a_thr=3):
    from dataset import get_next_ord, get_ncs, get_args

    def get_next_args(xeq, pts, nseq=3):
        """
        构造pts序列的所有可能顺序
        """
        if not xeq:
            xeq = [[i] for i in pts]
            nseq = nseq - 1

        for _ in range(nseq):
            new_seq = []
            for s in xeq:
                for p in pts:
                    nx = s + [p]
                    new_seq.append(nx)
            xeq = new_seq
        return xeq

    def check_ncs(key, args, pcs):
        """
        判断参数组合是否合法:
        1. args 不重复
        2. key不允许重复时, args不能重复
        3. args允许重复时, 对应的组合满足逻辑规则
        """
        if len(set(args)) == len(args):
            return True
        elif key in self.setter.arg_ndups:  # arg_ndups 不允许有重复参数
            return False
        else:
            for p in pcs:
                if len(set(args) - set(p[1:])) == 0:
                    if (p[0] not in self.setter.valid_combines) or (key not in self.setter.valid_combines[p[0]]):
                        continue
                    f_map = dict(zip(p[1:], self.setter.valid_combines[p[0]][key][0][0]))
                    f_args = tuple([f_map[c] for c in args])
                    vbs = [i[2] for i in self.setter.valid_combines[p[0]][key]]
                    if f_args not in vbs:  # 不合法的组合
                        return False
        return True

    def make_pure_clauses(p_keys: list[str]):
        sx_list = []
        prev_args = set(self.setter.pure_defs[p_keys[0]].points)
        cnt, bs = 0, max(prev_args)
        if len(p_keys) > 1:
            for kx in p_keys[1:]:
                points = self.setter.pure_defs[kx].points
                f_points, ts = [], bs
                for _ in range(len(points)):
                    ns = get_next_ord(ts)
                    f_points.append(ns)
                    ts = ns
                bs = ts
                ncx = get_ncs(f_points, kx, [])
                sx_list.append(ncx)
        else:
            f_points = self.setter.pure_defs[p_keys[0]].points
            sx_list.append(get_ncs(f_points, p_keys[0], []))
        return sx_list

    def make_next_arg_clause(sx, arg, exist_args=None):
        exist_args, exist_pts, px_clauses = set(), set(), []  # 已有的参数
        seq_als = []
        for clause in sx:
            points, a_args = clause.strip().split("=")
            points = points.strip().split(" ")
            a_args = a_args.strip().split(" ")
            exist_args = exist_args | set(points)
            if a_args[0] in self.setter.pure_defs:
                px_clauses.append(a_args)
            else:
                if len(points) == 1:
                    exist_pts = exist_pts | set(points)
                sgl = get_args(clause)
                seq_als.append([points, sgl])

        sx_list = []
        bs = max(exist_args)
        d = self.setter.defs[arg]
        f_points, ts = [], bs
        for _ in range(len(d.points)):
            ns = get_next_ord(ts)
            f_points.append(ns)
            ts = ns

        nf_list = get_next_args([], exist_args, len(d.args))
        for nf_points in nf_list:
            if check_ncs(arg, nf_points, px_clauses):
                ncs = get_ncs(points=f_points, key=arg, args=list(nf_points))
                sx_list.append(sx + [ncs])
        return sx_list

    def make_arg_clauses(sx, args):
        exist_args = set()  # 已有的参数
        for clause in sx:
            exist_args = exist_args | set(clause.split("=")[0].strip().split(" "))

        sx_list, limit = [], 3
        if args:
            all_seq = make_next_arg_clause(sx, args[0])
            sx_list.append(all_seq)
            for arg in args[1:limit]:
                new_seq = []
                for seq in sx_list[-1]:
                    tmp_seq = make_next_arg_clause(seq, arg)
                    new_seq += tmp_seq
                sx_list.append(new_seq)
        else:
            new_seq = []
            r_args = sorted(self.setter.arg_defs.keys())
            # random.shuffle(r_args)
            r_key = r_args[0]
            d = self.setter.defs[r_key]
            b_ord = ord(max(exist_args))
            c_args = self.setter.defs[r_key].args
            f_points = [chr(b_ord + i + 1) for i in range(len(d.points))]
            for nf_points in sorted(combinations(exist_args, len(c_args))):
                ncs = " ".join(f_points) + " = " + " ".join([r_key] + f_points + list(nf_points))
                new_seq.append(sx + [ncs])
            sx_list.append(new_seq)

        results = []
        for item in sx_list:
            results += item
        return results

    target_question = []
    q_type = req['type']
    info = req['extra_info']
    topics = info.get("topic", [])
    origin_que = info.get("origin_que", "")
    topic_def_names = [self.topics[i] for i in topics if i in self.topics]
    if q_type == 0:  # 指定topic命题
        pure_defs, arg_defs = [], []
        for names in topic_def_names:
            for name in names:
                if name in self.setter.defs:
                    if name in self.setter.pure_defs:
                        pure_defs.append(name)
                    if name in self.setter.arg_defs:
                        arg_defs.append(name)
        if not pure_defs:
            r_keys = sorted(self.setter.pure_defs.keys())
            # random.shuffle(r_keys)
            pure_defs = r_keys[:p_thr]
        if not arg_defs:
            a_keys = sorted(self.setter.arg_defs.keys())
            arg_defs = a_keys[:a_thr]

        pure_clauses = make_pure_clauses(pure_defs)
        questions = make_arg_clauses(pure_clauses, arg_defs)
        sample_question = None
        goal_txt = None
        if questions:
            questions.sort(key=lambda x: "".join(x))
            for que in questions:
                goal_info = self.get_one_goal("; ".join(que))
                if goal_info:
                    goal_txt = GeoProblemCreator.cn_pretty(goal_info[0].txt()).upper()
                    sample_question = que
                    break
                # goal_txt = pt.pretty(goal_info[0].txt())
        if sample_question and goal_txt:
            question_txt = []
            for ques in sample_question:
                question_txt.append(self.translate_clause(ques))
            # question_txt.append(goal_txt)
            # question_txt.append(self.translate_clause(goal_txt, True))
            return question_txt, goal_txt
    return target_question, []


def get_one_goal(self, seq_line):
    p = pr.Problem.from_txt(seq_line.strip())
    g, x_added = gh.Graph.build_problem(p, self.setter.defs)
    if g:
        dervs, eq4, next_branches, sat_added, _ = ddar.saturate_or_goal(
            g, theorems=self.setter.rules, level_times=[], p=p, max_level=1000, timeout=600)
        if sat_added:
            t_goal = sat_added[0]
            # t_goal = random.choice(sat_added)
            setup, aux, xa, xb = tb.get_logs(t_goal, g, merge_trivials=False)
            setup = [p.hashed() for p in setup]
            aux = [p.hashed() for p in aux]
            s_string, _ = GeoProblemCreator.get_dep_proof_steps(g, t_goal, merge_trivials=False)
            return t_goal, setup, aux, xa, xb, s_string
    return None


def translate_clause(self, word, norm_ds=None, is_goal=False):
    """利用模板翻译成中文"""
    if is_goal:
        return None
    else:
        points, p_args = word.split("=")
        # points = points.strip().split(" ")
        p_args_list = p_args.split(",")
        new_desc = []
        for p_args in p_args_list:
            p_args = p_args.strip().split(" ")
            k_def = self.setter.trans.get(p_args[0], None)
            if k_def:
                k_points = self.setter.trans[p_args[0]].definition.points
                k_args = self.setter.trans[p_args[0]].definition.args
                n_args = [norm_ds[i] if norm_ds and i in norm_ds else i for i in p_args[1:]]
                f_map = dict(zip(k_points + k_args, n_args))  # 原始点转成目标点
                desc = "".join(
                    [f_map[i.lower()].upper() if i.lower() in f_map else i
                     for i in self.setter.trans[p_args[0]].desc])
                new_desc.append(desc)
            # else:
            #    new_desc.append(word)
        if new_desc:
            return "且".join(new_desc)
        else:
            return word


@staticmethod
def cn_pretty(txt: str) -> str:
    """Pretty formating a predicate string."""
    if isinstance(txt, str):
        txt = txt.split(' ')
    name, *args = txt
    if name == 'ind':
        return 'Y ' + ' '.join(args)
    if name in ['fixc', 'fixl', 'fixb', 'fixt', 'fixp']:
        return map_symbol_inv(name) + ' ' + ' '.join(args)
    if name == 'acompute':
        a, b, c, d = args
        # return 'A ' + ' '.join(args)
        al = [a, b, c, d]
        v1 = [i for i in al if al.count(i) > 1]
        if v1:
            e1 = [i for i in al if i != v1[0]]
            return f"\u2220{e1[0]}{v1[0]}{e1[1]}"
        else:
            return f''.join(args)
    if name == 'rcompute':
        a, b, c, d = args
        # return 'R ' + ' '.join(args)
        return f'{a}{b}:{c}{d}'
    if name == 'aconst':
        a, b, c, d, y = args
        al = f'{pretty2a(a, b, c, d)}'.split(" ")
        v1 = [i for i in al if al.count(i) > 1]
        if v1:
            e1 = [i for i in al if i != v1[0]]
            return f"\u2220{e1[0]}{v1[0]}{e1[1]} = {y}"
        else:
            return f"{al[0]}{al[1]}到{al[2]}{al[3]}所成的夹角 = {y}"
            # return f'^ {pretty2a(a, b, c, d)} {y}'
    if name == 'rconst':
        a, b, c, d, y = args
        r1 = f'{pretty2r(a, b, c, d)}'.split(" ")
        # return f'/ {pretty2r(a, b, c, d)} {y}'
        return "".join(r1[:2]) + "/" + "".join(r1[2:]) + " = " + y
    if name == 'coll':
        # return 'C ' + ' '.join(args)
        return ','.join(args) + "共线"
    if name == 'collx':
        # return 'X ' + ' '.join(args)
        return ','.join(args) + "共线"
    if name == 'cyclic':
        # return 'O ' + ' '.join(args)
        return ",".join(args) + "共圆"
    if name in ['midp', 'midpoint']:
        x, a, b = args
        # return f'M {x} {a} {b}'
        return f'{x}是{a}{b}的中点'
    if name == 'eqangle' or name[:7] == 'eqangle':
        a, b, c, d, e, f, g, h = args
        a1 = f'{pretty2a(a, b, c, d)}'.split(" ")
        a2 = f'{pretty2a(e, f, g, h)}'.split(" ")
        v1 = [i for i in a1 if a1.count(i) > 1]
        v2 = [i for i in a2 if a2.count(i) > 1]
        if v1 and v2:
            e1 = [i for i in a1 if i != v1[0]]
            e2 = [i for i in a2 if i != v2[0]]
            return f"\u2220{e1[0]}{v1[0]}{e1[1]}=\u2220{e2[0]}{v2[0]}{e2[1]}"
        elif v1:
            e1 = [i for i in a1 if i != v1[0]]
            return f'\u2220{e1[0]}{v1[0]}{e1[1]}={a2[0]}{a2[1]}到{a2[2]}{a2[3]}所成的夹角'
        elif v2:
            e2 = [i for i in a2 if i != v2[0]]
            return f'{a1[0]}{a1[1]}到{a1[2]}{a1[3]}所成的夹角=\u2220{e2[0]}{v2[0]}{e2[1]}'
        else:
            return f'{a1[0]}{a1[1]}到{a1[2]}{a1[3]}所成的夹角等于{a2[0]}{a2[1]}到{a2[2]}{a2[3]}所成的夹角'
    if name == 'eqratio':
        a, b, c, d, e, f, g, h = args
        r1 = f'{pretty2r(a, b, c, d)}'
        r2 = f'{pretty2r(e, f, g, h)}'
        # return f'/ {pretty2r(a, b, c, d)} {pretty2r(e, f, g, h)}'
        return "".join(r1.split(" ")[:2]) + "/" + "".join(r1.split(" ")[2:]) + " = " + "".join(
            r2.split(" ")[:2]) + "/" + "".join(r2.split(" ")[2:])
    if name == 'eqratio3':
        a, b, c, d, o, o = args  # pylint: disable=redeclared-assigned-name
        return f'\u0394{o}{a}{b}相似于\u0394{o}{c}{d}'
        # return f'S {o} {a} {b} {o} {c} {d}'
    if name == 'cong':
        a, b, c, d = args
        return f"{a}{b}={c}{d}"
        # return f'D {a} {b} {c} {d}'
    if name == 'perp':
        if len(args) == 2:  # this is algebraic derivation.
            ab, cd = args  # ab = 'd( ... )'
            return f'{ab}\u27c2{cd}'
            # return f'T {ab} {cd}'
        a, b, c, d = args
        return f'{a}{b}\u27c2{c}{d}'
    if name == 'para':
        if len(args) == 2:  # this is algebraic derivation.
            ab, cd = args  # ab = 'd( ... )'
            # return f'P {ab} {cd}'
            return f'{ab}\u2225{cd}'
        a, b, c, d = args
        # return f'P {a} {b} {c} {d}'
        return f'{a}{b}\u2225{c}{d}'
    if name in ['simtri2', 'simtri', 'simtri*']:
        a, b, c, x, y, z = args
        return f'\u0394{a}{b}{c}相似于\u0394{x}{y}{z}'
    if name in ['contri2', 'contri', 'contri*']:
        a, b, c, x, y, z = args
        # return f'{a}{b}{c}全等于{x}{y}{z}'
        return f'\u0394{a}{b}{c}全等于\u0394{x}{y}{z}'
    if name == 'circle':
        o, a, b, c = args
        return f'{o}是\u0394{a}{b}{c}的外接圆心'
    if name == 'foot':
        a, b, c, d = args
        return f'{a}{b}\u27c2{c}{d}垂足是{a}'
    return ' '.join(txt)


def generate_ques_with_rules(self, rules, save_to="", top_k=1):
    r2p = self.setter.r2p  # pr.Theorem.from_txt_file('rules.txt', to_dict=True)
    defs = self.setter.defs
    rule_list = []
    for r in rules:
        rule_list += r2p[r]
    sorted_list = sorted(rule_list, key=lambda x: len(set(x['rules']) & set(rules)), reverse=True)
    top_k = sorted_list[:top_k]

    all_sat_words = []
    for item in top_k:
        item_premise = item['premise']
        pure_args = item_premise.split(" = ")[0].split(" ")
        p = pr.Problem.from_txt(item_premise.strip())
        ques = []
        for q in item_premise.split("?")[0].split("; "):
            cn_mapping = self.translate_clause(q, p.mapping)
            args, cons = q.split(" = ")
            nargs = " ".join([p.mapping[i] for i in args.split(" ")])
            ncons = " ".join([cons.split(" ")[0]] + [p.mapping[i] for i in cons.split(" ")[1:]])
            fl_mapping = " = ".join([nargs, ncons])
            ques.append((fl_mapping, cn_mapping))

        g, x_added = gh.Graph.build_problem(p, defs)
        if g:
            points = g.type2nodes[gm.Point]
            lines = g.type2nodes[gm.Line]
            circles = g.type2nodes[gm.Circle]
            segments = g.type2nodes[gm.Segment]
            # save_to = "example.png"
            # nm.draw(points, lines, circles, segments, equals=None, save_to=save_to, theme="bright")
            dervs, eq4, next_branches, sat_added, tset = ddar.saturate_or_goal(
                g, theorems=self.setter.rules, level_times=[], p=p, max_level=1000, timeout=600)
            if sat_added:
                sat_words = []
                for idx, t_goal in enumerate(sat_added):
                    goal_tuple = (t_goal.name, t_goal.args)
                    if all(t.name in pure_args for t in t_goal.args):
                        continue
                    save_name = save_to.replace(".png", "_" + str(idx) + ".png")
                    try:
                        nm.draw(points, lines, circles, segments, goal_tuple, equals=None,
                                save_to=save_name, theme="bright")
                    except:
                        continue
                    setup, aux, log, xa = tb.get_logs(t_goal, g, merge_trivials=False)
                    setup = [p.hashed() for p in setup]
                    aux = [p.hashed() for p in aux]
                    s_string, proof_list = self.get_dep_proof_steps(g, t_goal, merge_trivials=False)
                    steps = []
                    for proof in proof_list:
                        premise, conclusion = proof.split("->")
                        premise = premise.split(';')
                        new_premise = ";".join([self.cn_pretty(i.strip()).upper() for i in premise])
                        new_conclusion = self.cn_pretty(conclusion).upper()
                        steps.append((new_premise, new_conclusion))
                    t_txt = t_goal.txt()
                    goal_txt = self.cn_pretty(t_txt).upper()
                    sat_words.append([setup, aux, log, xa, s_string, steps, t_txt, goal_txt, save_name])
                sat_words.sort(key=lambda x: len(x[-4]), reverse=True)
                all_sat_words.append((item_premise, ques, sat_words))

    return all_sat_words


def generate_ques_with_rules_v2(self, rules, save_to="", rand=False, rule_limit=3):
    def make_def_combine(xlist):
        flist = [i for i in xlist[0]]
        x_dfs = [(i.split(" = ")[1].split(" ")[0], i) for i in flist]
        p_dfs = [i for i in x_dfs if i[0] in self.setter.pure_defs]
        a_dfs = [i for i in x_dfs if i[0] not in self.setter.pure_defs]
        pure_points, arg_points = set(), set()
        for xt in p_dfs:
            pure_points = pure_points | (set(xt[1].split(" = ")[0].split(" ")))
        for xt in a_dfs:
            arg_points = arg_points | (set(xt[1].split(" = ")[0].split(" ")))

        for xt in xlist[1:]:
            p_map = {}
            xp_dfs, xa_dfs = [], []
            for xi in xt:
                key = xi.split(" = ")[1].split(" ")[0]
                ags = xi.split(" = ")[0].split(" ")
                if key in self.setter.pure_defs:
                    if any(x[0] == key for x in p_dfs):
                        pts = None
                        for px in p_dfs:
                            if px[0] == key:
                                pts = px[1].split(" = ")[0].split(" ")
                        p_map = dict(zip(ags, pts))
                        n_args = [p_map[a] for a in ags]
                    else:
                        if len(set(ags) & pure_points) == 0:
                            n_args = ags
                        else:
                            n_args = []
                            for xm in range(len(ags)):
                                for xj in range(26):
                                    xng = chr(ord('a') + xj)
                                    if xng not in pure_points | arg_points and xng not in n_args:
                                        n_args.append(xng)
                                        break
                    ndf = " = ".join([" ".join(n_args), " ".join([key] + n_args)])
                    xp_dfs.append(ndf)
                else:
                    if len(set(ags) & (pure_points | arg_points)) == 0:
                        ndf = " ".join([p_map[i] if i in p_map else i for i in xi.split(" ")])
                        xa_dfs.append(ndf)
                    else:
                        n_args = []
                        for xm in range(len(ags)):
                            for xj in range(26):
                                xng = chr(ord('a') + xj)
                                if xng not in pure_points | arg_points and xng not in n_args and \
                                        xng not in p_map.values():
                                    n_args.append(xng)
                                    break
                        n_map = dict(zip(ags, n_args))
                        ndf = " ".join([n_map[i] if i in n_map else i for i in xi.split(" ")])
                        xa_dfs.append(ndf)

            for xitem in xp_dfs + xa_dfs:
                if xitem not in flist:
                    flist.append(xitem)
            x_dfs = [(i.split(" = ")[1].split(" ")[0], i) for i in flist]
            p_dfs = [i for i in x_dfs if i[0] in self.setter.pure_defs]
            a_dfs = [i for i in x_dfs if i[0] not in self.setter.pure_defs]
            pure_points, arg_points = set(), set()
            for xit in p_dfs:
                pure_points = pure_points | (set(xit[1].split(" = ")[0].split(" ")))
            for xit in a_dfs:
                arg_points = arg_points | (set(xit[1].split(" = ")[0].split(" ")))
            # keys = [(i.split(" = ")[1].split(" ")[0], i) for i in xlist]
            # pkeys = [k for k in keys if k[0] in self.setter.pure_defs]
            # pset = set([i[0] for i in pkeys])
            # nkeys = [k for k in keys if k[0] in self.setter.arg_defs]
            # p_num = sum([len(self.setter.pure_defs[i].points) for i in pset])
        return "; ".join(flist)
        # if p_num <= 26:
        #     p_idx = 0
        #     # 构造pure_def
        #     p_defs, p_points, a_defs = [], [], []
        #     for k in pset:
        #         k_size = len(self.setter.pure_defs[k].points)
        #         points = [chr(ord('a')+p_idx+i) for i in range(k_size)]
        #         p_idx += k_size
        #         p_def = " ".join(points) + " = " + k + " " + " ".join(points)
        #         p_defs.append(p_def)
        #         p_points += points
        #     # 构造 arg_def
        #     if len(nkeys) > 1:
        #         print("debug")
        #     al_points = p_points
        #     for k in [i[0] for i in nkeys]:
        #         k_size = len(self.setter.arg_defs[k].points)
        #         a_points = [chr(ord('a')+p_idx+i) for i in range(k_size)]
        #         p_idx += k_size
        #         a_size = len(self.setter.defs[k].args)-1 if k == 's_angle' else len(self.setter.defs[k].args)
        #         nf_list = list(combinations(al_points, a_size))
        #         al_points += a_points
        #         if len(nf_list) > 3:
        #            xf_list = [nf_list[0], nf_list[-1], nf_list[int(len(nf_list)/2)-1]]
        #         else:
        #            xf_list = nf_list[:3]
        #         if len(a_defs) == 0:
        #             for xf in xf_list:
        #                 a_defs.append([get_ncs(a_points, k, list(xf), xs_key)])
        #         else:
        #             nfs = []
        #             for xt in a_defs:
        #                 for xf in xf_list:
        #                     nfs.append(xt+[get_ncs(a_points, k, list(xf), xs_key)])
        #             a_defs = nfs
        #
        #     candidates = [p_defs + xt for xt in a_defs]
        # else:
        #     candidates = []

    r2p = self.setter.r2p  # pr.Theorem.from_txt_file('rules.txt', to_dict=True)
    defs = self.setter.defs
    s_pool = [str(15 * (i + 1)) for i in range(11)] * 30 + [str(-15 * (i + 1)) for i in range(11)] * 30 + \
             [str(i * 2) for i in range(180)][1:] + [str(-i) for i in range(180)][1:]
    s_angle_key = random.choice(s_pool)
    # rule_list = []
    select_list = []
    for r in rules[-rule_limit:]:  # 限制包含某些rules
        if rand:
            select_list.append(random.choice(r2p[r]))
        else:
            select_list.append(r2p[r][0])

    s_defs = []
    for item in select_list:
        s_defs.append(item['premise'].split("; "))
    item_premise = make_def_combine(s_defs)
    all_sat_words = []

    pure_args = item_premise.split(" = ")[0].split(" ")
    p = pr.Problem.from_txt(item_premise.strip())
    ques = []
    for q in item_premise.split("?")[0].split("; "):
        cn_mapping = self.translate_clause(q, p.mapping)
        args, cons = q.split(" = ")
        nargs = " ".join([p.mapping[i] for i in args.split(" ")])
        ncons = " ".join([cons.split(" ")[0]] + [p.mapping[i] for i in cons.split(" ")[1:]])
        fl_mapping = " = ".join([nargs, ncons])
        ques.append((fl_mapping, cn_mapping))

    g, x_added = gh.Graph.build_problem(p, defs)
    if g:
        points = g.type2nodes[gm.Point]
        lines = g.type2nodes[gm.Line]
        circles = g.type2nodes[gm.Circle]
        segments = g.type2nodes[gm.Segment]
        # save_to = "example.png"
        # nm.draw(points, lines, circles, segments, equals=None, save_to=save_to, theme="bright")
        try:
            dervs, eq4, next_branches, sat_added, tset = ddar.saturate_or_goal(
                g, theorems=self.setter.rules, level_times=[], p=p, max_level=1000, timeout=600)
        except:
            return all_sat_words
        if sat_added:
            sat_words = []
            for idx, t_goal in enumerate(sat_added):
                if all(t.name in pure_args for t in t_goal.args):
                    continue
                goal_tuple = (t_goal.name, t_goal.args)
                save_name = save_to.replace(".png", "_" + str(idx) + ".png")
                setup, aux, log, xa = tb.get_logs(t_goal, g, merge_trivials=False)
                setup = [p.hashed() for p in setup]
                aux = [p.hashed() for p in aux]
                s_string, proof_list = self.get_dep_proof_steps(g, t_goal, merge_trivials=False)
                steps = []
                for proof in proof_list:
                    premise, conclusion = proof.split("->")
                    premise = premise.split(';')
                    new_premise = ";".join([self.cn_pretty(i.strip()).upper() for i in premise])
                    new_conclusion = self.cn_pretty(conclusion).upper()
                    steps.append((new_premise, new_conclusion))
                t_txt = t_goal.txt()
                goal_txt = self.cn_pretty(t_txt).upper()
                sat_words.append([setup, aux, log, xa, s_string, goal_tuple, steps, t_txt, goal_txt, save_name])
            sat_words.sort(key=lambda x: len(x[-4]), reverse=True)
            for s_item in sat_words[:3]:
                try:
                    nm.draw(points, lines, circles, segments, s_item[5], equals=None,
                            save_to=s_item[-1], theme="bright")
                except:
                    continue
            all_sat_words.append((item_premise, ques, sat_words))

    return all_sat_words


def generate_ques_with_premise(self, line):
    # line = 'a b c d = rectangle a b c d; e = intersection_pp e a c d d a c '
    # pds = dict([(v, k) for k, v in p.mapping.items()])

    all_sat_words = []
    p = pr.Problem.from_txt(line.strip())
    ques = []
    for q in line.split("?")[0].split("; "):
        ques.append(self.translate_clause(q, p.mapping))
    rules = pr.Theorem.from_txt_file('rules.txt', to_dict=True)
    g, x_added = gh.Graph.build_problem(p, self.setter.defs)
    if g:
        points = g.type2nodes[gm.Point]
        lines = g.type2nodes[gm.Line]
        circles = g.type2nodes[gm.Circle]
        segments = g.type2nodes[gm.Segment]
        save_to = "example.png"
        # nm.draw(points, lines, circles, segments, equals=None, save_to=save_to, theme="bright")
        dervs, eq4, next_branches, sat_added, tset = ddar.saturate_or_goal(
            g, theorems=rules, level_times=[], p=p, max_level=1000, timeout=600)
        if sat_added:
            sat_words = []
            for idx, t_goal in enumerate(sat_added):
                goal_tuple = (t_goal.name, t_goal.args)
                nm.draw(points, lines, circles, segments, goal_tuple, equals=None,
                        save_to=save_to.replace(".png", str(idx) + ".png"), theme="bright")
                setup, aux, log, xa = tb.get_logs(t_goal, g, merge_trivials=False)
                setup = [p.hashed() for p in setup]
                aux = [p.hashed() for p in aux]
                s_string, proof_list = self.get_dep_proof_steps(g, t_goal, merge_trivials=False)
                steps = []
                for proof in proof_list:
                    premise, conclusion = proof.split("->")
                    premise = premise.split(';')
                    new_premise = ";".join([self.cn_pretty(i.strip()).upper() for i in premise])
                    new_conclusion = self.cn_pretty(conclusion).upper()
                    steps.append((new_premise, new_conclusion))
                t_txt = t_goal.txt()
                goal_txt = self.cn_pretty(t_txt).upper()
                sat_words.append([setup, aux, log, xa, s_string, steps, goal_txt])
            all_sat_words.append(sat_words)

    return all_sat_words, ques


def get_ncs(points, key, args, s_angle_key) -> str:
    f_points = points
    if key in {'square', 'parallelogram'}:  # square a b x y; parallelogram a b c x
        ncs = " ".join(f_points + ["=", key] + args + f_points)
    elif key == 's_angle':  # s_angle a b x y --> y是数值
        ncs = " ".join(f_points + ["=", key] + args + f_points + [s_angle_key])
    else:
        ncs = " ".join(f_points + ["=", key] + f_points + args)
    return ncs


def pretty2r(a: str, b: str, c: str, d: str) -> str:
    if b in (c, d):
        a, b = b, a

    if a == d:
        c, d = d, c

    return f'{a} {b} {c} {d}'


def pretty2a(a: str, b: str, c: str, d: str) -> str:
    if b in (c, d):
        a, b = b, a

    if a == d:
        c, d = d, c

    return f'{a} {b} {c} {d}'


MAP_SYMBOL = {
    'T': 'perp',
    'P': 'para',
    'D': 'cong',
    'S': 'simtri',
    'I': 'circle',
    'M': 'midp',
    'O': 'cyclic',
    'C': 'coll',
    '^': 'eqangle',
    '/': 'eqratio',
    '%': 'eqratio',
    '=': 'contri',
    'X': 'collx',
    'A': 'acompute',
    'R': 'rcompute',
    'Q': 'fixc',
    'E': 'fixl',
    'V': 'fixb',
    'H': 'fixt',
    'Z': 'fixp',
    'Y': 'ind',
}


def map_symbol(c: str) -> str:
    return MAP_SYMBOL[c]


def map_symbol_inv(c: str) -> str:
    return {v: k for k, v in MAP_SYMBOL.items()}[c]
