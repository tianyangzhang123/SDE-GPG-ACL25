import random
import os
import datetime
import json
from itertools import combinations, permutations

from absl import app
from absl import flags
from absl import logging

import problem as pr
import graph as gh
import dd
import ddar
import trace_back as tb
import pretty
import geometry as gm
import numericals_update as nup
import re


class MyDataSet:

    def __init__(self) -> None:
        self.defs = pr.Definition.from_txt_file('defs.txt', to_dict=True)
        self.rules = pr.Theorem.from_txt_file('rules_o.txt', to_dict=True)
        self.trans = pr.Translation.from_txt_file('translate_defs.txt', to_dict=True)
        self.valid_combines, self.args_dup_tags = self.get_valid_combines('valid_combine_0816.txt')
        self.r2p = MyDataSet.load_r2p('rules_with_premises.json')

        self.pure_defs, self.arg_defs = {}, {}  # 不同类型的clause
        for d in self.defs:
            definition = self.defs.get(d, None)
            if definition:
                if definition.args:
                    self.arg_defs[definition.construction.name] = definition
                else:
                    self.pure_defs[definition.construction.name] = definition

        self.arg_cls = {}  # 带重复参数的arg_defs, some may be invalid
        for xd in self.arg_defs:
            d = self.arg_defs[xd]
            pset, d_size = list(sorted(set(d.args))), len(d.args)
            target_set = set()
            for ni in range(d_size):
                n_args = pset[:ni + 1]  # 限定在ni个arg 假设等于[a,b,c]
                d_set, all_set = set(n_args), set([" ".join(n_args)])  # d_set = {a,b,c}  all_set = {a b c}
                for _ in range(d_size - ni - 1):  # 每次增加一个长度
                    cur_set = set()
                    for als in all_set:
                        # 将集合 words 中的每个单词插入到字符串 seq 的每个可能位置，生成所有可能的新序列，并将结果存储在一个集合中。
                        # 集合中的每个元素都是一个字符串，表示插入单词后的新序列。cur_set存储所有可能的新序列
                        cur_set = cur_set | MyDataSet.update_next_pos(als, d_set)
                    all_set = cur_set
                target_set = target_set | all_set  # 并集操作 将合并后的集合存储到target_set
            for ts in target_set:
                if len(set(ts.split(" "))) == d_size:  # 去重复 如果去重后的字母与原先的字母一致则继续， 如果不一致，则创建新的clause条件
                    continue
                new_clause = " ".join(d.points) + " = " + " ".join(
                    [d.construction.name] + d.points + list(ts.split(" ")))
                self.arg_cls.setdefault(d.construction.name, []).append(new_clause)

        self.arg_ndups = {"angle_bisector", "angle_mirror", "circle", "circumcenter", "eq_triangle", "eqangle2", "foot",
                          "incenter", "incenter2", "excenter",
                          "excenter2", "centroid", "ninepoints", "intersection_cc", "lc_tangent", "midpoint", "mirror",
                          "nsquare", "on_bline", "on_circle",
                          "on_line", "on_pline", "orthocenter", "parallelogram", "psquare", "reflect", "s_angle",
                          "square", "e5128", "3peq",
                          "trisect", "trisegment", "on_dia", "on_opline", 'tangent', "on_circum",
                          "intersection_ll"}  # 无重复点的def
        self.arg_dups = {
            "eqdistance": ["x = eqdistance x a b c", 'x = eqdistance x b a b', 'x = eqdistance x a b a',
                           'x = eqdistance x a a b'],
            "intersection_lc": ['x = intersection_lc x a b o', 'x = intersection_lc x a a b'],
            "intersection_lp": ['x = intersection_lp x a b c m b', 'x = intersection_lp x m a b c m',
                                'x = intersection_lp x a b c a m', 'x = intersection_lp x a c b c m',
                                'x = intersection_lp x a b c m a', 'x = intersection_lp x a b c m n',
                                'x = intersection_lp x a b c b m', 'x = intersection_lp x a m b c m',
                                'x = intersection_lp x c a b c m'],
            "intersection_lt": ['x = intersection_lt x a c b a c', 'x = intersection_lt x a c b c b',
                                'x = intersection_lt x a b c c d', 'x = intersection_lt x a c b b c',
                                'x = intersection_lt x c a b c d', 'x = intersection_lt x a b c d e',
                                'x = intersection_lt x c b a b c', 'x = intersection_lt x c a b c b',
                                'x = intersection_lt x c a b b c', 'x = intersection_lt x a d b c d',
                                'x = intersection_lt x a b c c b', 'x = intersection_lt x a b c c a',
                                'x = intersection_lt x a b c d b', 'x = intersection_lt x a b c a b',
                                'x = intersection_lt x a b c b d', 'x = intersection_lt x b a c b c',
                                'x = intersection_lt x a b c d c', 'x = intersection_lt x a b c b a',
                                'x = intersection_lt x a b c d a', 'x = intersection_lt x a b c a c',
                                'x = intersection_lt x a b c b c', 'x = intersection_lt x a b c a d',
                                'x = intersection_lt x c a b c a', 'x = intersection_lt x a c b c a',
                                'x = intersection_lt x d a b c d', 'x = intersection_lt x a b d c d',
                                'x = intersection_lt x b c a b c', 'x = intersection_lt x c a b a c',
                                'x = intersection_lt x a c b c d'],
            "intersection_pp": ['x = intersection_pp x a b c b c a', 'x = intersection_pp x c a b b a c',
                                'x = intersection_pp x a b c c b d',
                                'x = intersection_pp x e a b c d e', 'x = intersection_pp x a c b c b a',
                                'x = intersection_pp x d c a b c d',
                                'x = intersection_pp x a d b b c d', 'x = intersection_pp x a b c c a d',
                                'x = intersection_pp x a b c d e c',
                                'x = intersection_pp x d a c b c d', 'x = intersection_pp x d b a b c d',
                                'x = intersection_pp x a b c c d b',
                                'x = intersection_pp x a e b c d e', 'x = intersection_pp x a b c d a c',
                                'x = intersection_pp x a c b b a c',
                                'x = intersection_pp x c a d b c d', 'x = intersection_pp x c b a b c d',
                                'x = intersection_pp x a b c c b a',
                                'x = intersection_pp x a c b c d e', 'x = intersection_pp x a c b c d b',
                                'x = intersection_pp x c a b b c a',
                                'x = intersection_pp x a b d d c d'],
            "intersection_tt": ['x = intersection_tt x a b c b c a', 'x = intersection_tt x c a b b a c',
                                'x = intersection_tt x a b c c b d',
                                'x = intersection_tt x e a b c d e', 'x = intersection_tt x a c b c b a',
                                'x = intersection_tt x d c a b c d',
                                'x = intersection_tt x a d b b c d', 'x = intersection_tt x a b c c a d',
                                'x = intersection_tt x a b c d e c',
                                'x = intersection_tt x d a c b c d', 'x = intersection_tt x d b a b c d',
                                'x = intersection_tt x a b c c d b',
                                'x = intersection_tt x a e b c d e', 'x = intersection_tt x a b c d a c',
                                'x = intersection_tt x a c b b a c',
                                'x = intersection_tt x c a d b c d', 'x = intersection_tt x c b a b c d',
                                'x = intersection_tt x a b c c b a',
                                'x = intersection_tt x a c b c d e', 'x = intersection_tt x a c b c d b',
                                'x = intersection_tt x c a b b c a',
                                'x = intersection_tt x a b d d c d'],
            "on_aline": ['x = on_aline x a c b a c', 'x = on_aline x a b b c a', 'x = on_aline x a b a b c',
                         'x = on_aline x c a b c d', 'x = on_aline x a b c d e',
                         'x = on_aline x a b b a c', 'x = on_aline x c a a b c', 'x = on_aline x c b a b c',
                         'x = on_aline x b a a b c', 'x = on_aline x a c a b c',
                         'x = on_aline x a d b c d', 'x = on_aline x a b a c d', 'x = on_aline x b a b c d',
                         'x = on_aline x b a b a c', 'x = on_aline x a b c d b',
                         'x = on_aline x a b c a b', 'x = on_aline x a b c b d', 'x = on_aline x b a b c a',
                         'x = on_aline x a b c b a', 'x = on_aline x a b b c d',
                         'x = on_aline x a b c d a', 'x = on_aline x a b c a d', 'x = on_aline x c a b c a',
                         'x = on_aline x a c b c a', 'x = on_aline x d a b c d',
                         'x = on_aline x b c a b c', 'x = on_aline x c a b a c', 'x = on_aline x a b a c b',
                         'x = on_aline x a c b c d'],
            "on_aline2": ['x = on_aline2 x a c b a c', 'x = on_aline2 x a b b c a', 'x = on_aline2 x a b a b c',
                          'x = on_aline2 x c a b c d', 'x = on_aline2 x a b c d e',
                          'x = on_aline2 x a b b a c', 'x = on_aline2 x c a a b c', 'x = on_aline2 x c b a b c',
                          'x = on_aline2 x b a a b c', 'x = on_aline2 x a c a b c',
                          'x = on_aline2 x a d b c d', 'x = on_aline2 x a b a c d', 'x = on_aline2 x b a b c d',
                          'x = on_aline2 x b a b a c', 'x = on_aline2 x a b c d b',
                          'x = on_aline2 x a b c a b', 'x = on_aline2 x a b c b d', 'x = on_aline2 x b a b c a',
                          'x = on_aline2 x a b c b a', 'x = on_aline2 x a b b c d',
                          'x = on_aline2 x a b c d a', 'x = on_aline2 x a b c a d', 'x = on_aline2 x c a b c a',
                          'x = on_aline2 x a c b c a', 'x = on_aline2 x d a b c d',
                          'x = on_aline2 x b c a b c', 'x = on_aline2 x c a b a c', 'x = on_aline2 x a b a c b',
                          'x = on_aline2 x a c b c d'],
            "on_tline": ['x = on_tline x a b c', 'x = on_tline x b a b', 'x = on_tline x a b a',
                         'x = on_tline x a a b'],
            "shift": ['x = shift x b b c', 'x = shift x b c d'],
            "2l1c": ['x y z i = 2l1c x y z i a b c o', 'x y z i = 2l1c x y z i a b c c'],
            "cc_tangent0": ['x y = cc_tangent0 x y a b o b', 'x y = cc_tangent0 x y a b b o',
                            'x y = cc_tangent0 x y a b o a', 'x y = cc_tangent0 x y a b b a',
                            'x y = cc_tangent0 x y a o b o', 'x y = cc_tangent0 x y a b o w',
                            'x y = cc_tangent0 x y b a a b', 'x y = cc_tangent0 x y o a b o'],
            "cc_tangent": ['x y = cc_tangent x y a b o b', 'x y = cc_tangent x y a b b o',
                           'x y = cc_tangent x y a b o a', 'x y = cc_tangent x y a b b a',
                           'x y = cc_tangent x y a o b o', 'x y = cc_tangent x y a b o w',
                           'x y = cc_tangent x y b a a b', 'x y = cc_tangent x y o a b o'],
            "eqangle3": ['x = eqangle3 x a b a d e', 'x = eqangle3 x d a b a d', 'x = eqangle3 x b a b d a',
                         'x = eqangle3 x a e b d e', 'x = eqangle3 x b a b a d',
                         'x = eqangle3 x d a b d a', 'x = eqangle3 x a b d e b', 'x = eqangle3 x a b d b e',
                         'x = eqangle3 x b d a b d', 'x = eqangle3 x a d a b d',
                         'x = eqangle3 x a b d a e', 'x = eqangle3 x a d b d e', 'x = eqangle3 x a b d e a',
                         'x = eqangle3 x a d b a d', 'x = eqangle3 x a b b a d',
                         'x = eqangle3 x a b a d b', 'x = eqangle3 x a b a b d', 'x = eqangle3 x a b b d e',
                         'x = eqangle3 x a b d e f', 'x = eqangle3 x b a a b d',
                         'x = eqangle3 x b a b d e', 'x = eqangle3 x a b b d a', 'x = eqangle3 x d a b d e',
                         'x = eqangle3 x a b d b a', 'x = eqangle3 x a b d a b',
                         'x = eqangle3 x d a a b d', 'x = eqangle3 x a d b d a', 'x = eqangle3 x d b a b d',
                         'x = eqangle3 x e a b d e'],
        }

    @staticmethod
    def load_r2p(fname="rules_with_premises.json"):
        with open(fname) as f:
            jds = json.load(f)
        return jds

    # 将集合 words 中的每个单词插入到字符串 seq 的每个可能位置，生成所有可能的新序列，并将结果存储在一个集合中。
    # 集合中的每个元素都是一个字符串，表示插入单词后的新序列。
    @staticmethod
    def update_next_pos(seq, words):
        sls = seq.split(" ")
        new_seq = set()
        for word in words:
            for i in range(len(seq)):
                new_seq.add(" ".join(sls[:i] + [word] + sls[i:]))
            new_seq.add(" ".join(sls + [word]))
        return new_seq

    def add_next_arg_clause(self, seq, same_args=False, same_points=False, merge="combine", mode="all", limit=None):
        """"
        給seq 添加一个 arg 类的成员
        same_args: 添加允许重复参数的类型
        same_points: 允许一个参数多个clause
        merge: 组合的方式: combine, permute
        mode: all; full_random
        """
        exist_args, exist_pts, pure_clauses = set(), set(), []  # 已有的参数
        for clause in seq:
            points, a_args = clause.strip().split("=")
            points = points.strip().split(" ")
            a_args = a_args.strip().split(" ")

            exist_args = exist_args | points
            if a_args[0] in self.pure_defs:
                pure_clauses.append(a_args)
            else:
                if len(points) == 1:
                    exist_pts = exist_pts | set(points)

        n_dups, a_dups = list(self.arg_ndups), list(self.arg_dups.keys())
        if mode == "full_random":
            random.shuffle(n_dups)
            random.shuffle(a_dups)
            if random.random() <= 0.72:  # len(arg_ndups)/(len(arg_ndups)+len(arg_dups))
                n_dups = n_dups[:1]
                a_dups = []
            else:
                a_dups = a_dups[:1]
                n_dups = []

        seq_list, bs = [], max(exist_args)
        if not same_args:
            # for k in self.arg_defs:
            for k in n_dups + a_dups:
                d, f_points, ts = self.defs[k], [], bs
                if len(d.args) > len(exist_args):
                    continue
                for i in range(len(d.points)):
                    ns = get_next_ord(ts)
                    f_points.append(ns)
                    ts = ns

                if merge == 'combine':
                    nf_list = list(combinations(exist_args, len(d.args)))
                else:
                    nf_list = list(permutations(exist_args, len(d.args)))
                for nf_points in nf_list:
                    ncs = get_ncs(points=f_points, key=k, args=list(nf_points))
                    seq_list.append(seq + [ncs])

                if same_points:
                    if len(d.points) > 1:
                        continue
                    for dp in exist_pts:
                        new_args = exist_args - {dp}  # todo: 顺序问题
                        if len(d.args) > len(new_args):
                            continue
                        if merge == 'combine':
                            nf_list = list(combinations(new_args, len(d.args)))
                        else:  # permute
                            nf_list = list(permutations(new_args, len(d.args)))
                        for nf_points in nf_list:
                            ncs = get_ncs(points=[dp], key=k, args=list(nf_points))
                            seq_list.append(seq + [ncs])
        else:
            # for k in self.arg_ndups:
            for k in n_dups + a_dups:
                d, f_points, ts = self.defs[k], [], bs
                if len(d.args) > len(exist_args):
                    continue
                for _ in range(len(d.points)):
                    ns = get_next_ord(ts)
                    f_points.append(ns)
                    ts = ns

                if merge == 'combine':
                    nf_list = list(combinations(exist_args, len(d.args)))
                else:
                    nf_list = list(permutations(exist_args, len(d.args)))
                for nf_points in nf_list:
                    ncs = get_ncs(points=f_points, key=k, args=list(nf_points))
                    seq_list.append(seq + [ncs])

                if same_points:
                    if len(d.points) > 1:
                        continue
                    for dp in exist_pts:
                        new_args = exist_args - {dp}  # todo: 顺序问题
                        if len(d.args) > len(new_args):
                            continue
                        if merge == 'combine':
                            nf_list = list(combinations(new_args, len(d.args)))
                        else:  # permute
                            nf_list = list(permutations(new_args, len(d.args)))
                        for nf_points in nf_list:
                            ncs = get_ncs(points=[dp], key=k, args=list(nf_points))
                            seq_list.append(seq + [ncs])

            for k in a_dups:
                d, f_points, ts = self.defs[k], [], bs
                for _ in range(len(d.points)):
                    ns = get_next_ord(ts)
                    f_points.append(ns)
                    ts = ns

                for word in self.arg_dups[k]:
                    pts, agl = word.strip().split("=")
                    pts = pts.strip().split(" ")
                    args = agl.strip().split(" ")[len(pts) + 1:]
                    arg_set = set(args)
                    if len(arg_set) > len(exist_args):
                        continue
                    if merge == "combine":
                        nf_list = list(combinations(exist_args, len(arg_set)))
                    else:
                        nf_list = list(permutations(exist_args, len(arg_set)))
                    for nf_points in nf_list:
                        f_map = dict(zip(arg_set, nf_points))
                        n_args = [f_map[a] for a in args]
                        ncs = get_ncs(points=f_points, key=k, args=n_args)
                        seq_list.append(seq + [ncs])

                if same_points:
                    if len(d.points) > 1:
                        continue
                    for dp in exist_pts:
                        new_args = exist_args - {dp}
                        for word in self.arg_dups[k]:
                            pts, agl = word.strip().split("=")
                            pts = pts.strip().split(" ")
                            args = agl.strip().split(" ")[len(pts) + 1:]
                            arg_set = set(args)
                            if len(arg_set) > len(new_args):
                                continue
                            if merge == "combine":
                                nf_list = list(combinations(new_args, len(arg_set)))
                            else:
                                nf_list = list(permutations(new_args, len(arg_set)))
                            for nf_points in nf_list:
                                f_map = dict(zip(arg_set, nf_points))
                                n_args = [f_map[a] for a in args]
                                ncs = get_ncs(points=f_points, key=k, args=n_args)
                                seq_list.append(seq + [ncs])

        if mode == "full_random":
            random.shuffle(seq_list)
        if limit:
            seq_list = seq_list[:limit]
        return seq_list

    # 最终返回指定百分比的推理构造 list[list[str 构造语句]]
    def add_next_arg_clause2(self, seq, merge="all", limit=None, percent=None, percent_thr=2):
        """"
        給seq 添加一个 arg 类的成员
        same_args: 添加允许重复参数的类型
        same_points: 允许一个参数多个clause
        merge: 组合的方式: combine, permute, all 指定组合参数的方式，可以是 "combine"（组合）、"permute"（排列）或 "all"（所有可能的组合）
        mode: all; full_random
        percent_thr：当生成的序列数量小于这个阈值时，直接返回所有序列
        """

        # 生成所有可能的参数组合。pts 是可用的点集合，nseq 是组合的长度
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

        # 验证参数组合是否合法 如果参数不重复则合法，参数重复但key允许重复则验证组合是否满足逻辑规则，否则就是不合法 返回bool
        def check_ncs(key, args, pcs):
            """
            判断参数组合是否合法:
            1. args 不重复
            2. key不允许重复时, args不能重复
            3. args允许重复时, 对应的组合满足逻辑规则
            """
            if len(set(args)) == len(args):
                return True
            elif key in self.arg_ndups:  # arg_ndups 不允许有重复参数
                return False
            else:
                for p in pcs:
                    if len(set(args) - set(p[1:])) == 0:
                        if (p[0] not in self.valid_combines) or (key not in self.valid_combines[p[0]]):
                            continue
                        f_map = dict(zip(p[1:], self.valid_combines[p[0]][key][0][0]))
                        f_args = tuple([f_map[c] for c in args])
                        vbs = [i[2] for i in self.valid_combines[p[0]][key]]
                        if f_args not in vbs:  # 不合法的组合
                            return False
            return True

        # 递归地找到某个几何对象的所有依赖参数，找到所有直接或间接依赖xg的点
        def get_support_arg(xg, xseq):
            """
            找到完全覆盖arg的所有依赖
            """
            x_args = set()
            for xs in xseq:
                if xg in xs[1]:
                    x_args = x_args | set(xs[0])
                    for x_arg in xs[0]:
                        x_args = x_args | get_support_arg(x_arg, xseq)
            return x_args

        exist_args, exist_pts, pure_clauses = set(), set(), []  # 已有的参数
        seq_als = []
        for clause in seq:  # clause为str
            points, a_args = clause.strip().split("=")
            points = points.strip().split(" ")
            a_args = a_args.strip().split(" ")
            exist_args = exist_args | set(points)
            if a_args[0] in self.pure_defs:
                # 纯几何构造的子句列表
                pure_clauses.append(a_args)
            else:
                if len(points) == 1:
                    exist_pts = exist_pts | set(points)
                sgl = get_args(clause)  # 返回除point外的不重复的arg点列表
                # 解析后的子句列表，包含点和参数
                seq_als.append([points, sgl])

        seq_list, bs = [], max(exist_args)  # 找到集合中的最大元素点
        for k in self.arg_defs:
            # 相当于每一个arg_defs都跟当前的子句进行比较和点的生成
            d, f_points, ts = self.defs[k], [], bs
            # 根据d的points数量生成最大元素点的后len个点，存储到f_points中
            for _ in range(len(d.points)):
                ns = get_next_ord(ts)
                f_points.append(ns)
                ts = ns
            if merge == 'combine' and len(d.args) <= len(exist_args):
                # 返回一个列表list[tuple]，包含所有随机组合的可能 C(m n)——元素顺序不重要
                nf_list = list(combinations(exist_args, len(d.args)))
            elif merge == 'permute' and len(d.args) <= len(exist_args):
                # 返回一个列表list[tuple]，包含所有随机排列的可能P(m n) ——元素顺序重要
                nf_list = list(permutations(exist_args, len(d.args)))
            else:
                # nf_list存储exist_args中所有可能的组合，组合长度固定为d.args——所有节能的组合包括元素的重复
                nf_list = get_next_args([], exist_args, len(d.args))
            for nf_points in nf_list:
                if check_ncs(k, nf_points, pure_clauses):
                    # 返回一个新的构造语句
                    ncs = get_ncs(points=f_points, key=k, args=list(nf_points))
                    seq_list.append(seq + [ncs])

            if len(d.points) == 1:
                for dp in exist_pts:
                    # 一个集合，包含dp及其所有依赖参数
                    s_args = get_support_arg(dp, seq_als) | {dp}
                    new_args = exist_args - s_args  # 获取差集 再对这些差集中的点重新组合
                    if merge == 'combine' and len(d.args) <= len(new_args):
                        nf_list = list(combinations(new_args, len(d.args)))
                    elif merge == 'permute' and len(d.args) <= len(new_args):
                        nf_list = list(permutations(new_args, len(d.args)))
                    else:
                        nf_list = get_next_args([], new_args, len(d.args))
                    for nf_points in nf_list:
                        if check_ncs(k, nf_points, pure_clauses):
                            # 返回一个新的构造语句
                            ncs = get_ncs(points=[dp], key=k, args=list(nf_points))
                            seq_list.append(seq + [ncs])

        if limit:
            # 如果指定，表示限制生成的序列数量为 limit
            random.seed(10)
            random.shuffle(seq_list)
            seq_list = seq_list[:limit]
        elif percent:
            random.seed(5)
            # 随机打乱seq_list序列
            random.shuffle(seq_list)
            # 根据指定的百分比 percent 选择前若干个序列
            thr = max(percent_thr, int(len(seq_list) * percent))
            seq_list = seq_list[:thr]
        return seq_list

    def add_next_pure_clause(self, seq, exist_args=None):
        """构造不带arg的def"""
        if not exist_args:
            exist_args = set()
            for clause in seq:
                exist_args = exist_args | set(clause.split("=")[0].strip().split(" "))

        new_seq_list = []
        # b_ord = ord(max(exist_args))
        bs = max(exist_args)
        for k in self.pure_defs:
            d = self.pure_defs[k]
            f_points = []
            ts = bs
            for i in range(len(d.points)):
                ns = get_next_ord(ts)
                f_points.append(ns)
                ts = ns
            # f_points = [chr(b_ord+i+1) for i in range(len(d.points))] # 只允许用新的点生成条件，且没有重复的点
            ncs = " ".join(f_points + ["=", k] + f_points)
            new_seq_list.append(seq + [ncs])
        return new_seq_list

    def get_valid_combines(self, file="valid_combine_0816.txt"):
        def get_a_args(akey, words, la):
            if akey in {'parallelogram', 'square'}:
                return words[:-la]
            elif akey == 's_angle':
                return words[:-la - 1]
            else:
                return words[la:]

        with open(file) as fi:
            lines = fi.readlines()
        pds = {}
        n_tags = {}
        for line in lines:
            pure_part, arg_part = line.strip().split(";")
            p_pts, p_args = pure_part.strip().split("=")
            a_pts, a_args = arg_part.strip().split("=")
            p_pts = p_pts.strip().split(" ")
            p_args = p_args.strip().split(" ")
            a_pts = a_pts.strip().split(" ")
            a_args = a_args.strip().split(" ")
            p_key = p_args[0]
            a_key = a_args[0]
            pds.setdefault(p_key, {})
            a_words = get_a_args(a_key, a_args[1:], len(a_pts))
            pds[p_key].setdefault(a_key, []).append((tuple(p_pts), tuple(a_pts), tuple(a_words)))
        for d in pds:
            for n in pds[d]:
                n_tags.setdefault(n, {})
                n_tags[n][d] = all(len(set(c[2])) == len(c[2]) for c in pds[d][n])

        return pds, n_tags

    def make_pure_clause(self, d_max=5):
        """
        n_1+n_2+...+n_k=N
        k: 不同pure def的个数
        N: 序列长度
        * 用动态规划的方法得到不同组合的总数,
        pure clause 不需要以其它点存在为前提
        """

        # 根据num大小生成一组点名
        def get_num_points(nums):
            all_keys = []
            for i in range(nums):
                na = i % 26
                nb = int(i / 26)
                id_key = str(nb) if nb > 0 else ""
                all_keys.append(chr(ord('a') + na) + id_key)
            return all_keys

        # 通过递归的方式生成不同大小的子句组合（用元组存储），并确保组合中的子句是唯一的
        def gen_clause_keys(size, prev_clauses=None):
            if size <= 1:
                return [[i] for i in self.pure_defs]
            elif size == 2:
                sorted_keys = sorted(self.pure_defs.keys())
                combines = []
                for k in sorted_keys:
                    for nk in sorted_keys:
                        if nk >= k:
                            break
                        else:
                            combines.append((nk, k))
                return [(i, i) for i in self.pure_defs] + combines
            else:
                if not prev_clauses:  # 避免重复生成
                    prev_clauses = gen_clause_keys(size - 1)
                new_clauses, n_set = [], set()
                for pcl in prev_clauses:
                    for di in self.pure_defs:
                        tmp_clause = tuple(sorted(list(pcl) + [di]))
                        if tmp_clause not in n_set:
                            n_set.add(tmp_clause)
                            new_clauses.append(tmp_clause)
                return new_clauses

        # 返回所有生成的几何子句
        def generate_clause(k_seq):
            seq_list = []
            cnt, f_name = 0, "a"
            # 计算 k_seq 中所有几何构造涉及的点的总数
            num_points = sum(len(self.pure_defs[k].points) for k in k_seq)
            keys = get_num_points(num_points)
            for k in range(len(k_seq)):
                # 计算当前几何构造的起始点索引
                begin = sum(len(self.pure_defs[k_seq[i]].points) for i in range(k)) if k >= 1 else 0
                # 从 keys 中提取当前几何构造所需的点
                points = keys[begin: begin + len(self.pure_defs[k_seq[k]].points)]
                # new_points = [chr(ord(f_name)+cnt+ni) for ni in range(len(points))]
                # cnt += len(points)
                # 生成几何子句，格式为 points = construction_name points
                ncs = " ".join(points) + " = " + k_seq[k] + " " + " ".join(points)
                seq_list.append(ncs)
            return seq_list

        all_keys, all_seq = {}, {}
        # 生成大小不同的子句合集 从1～d_max大小的都有，包括所有组合方式
        for i in range(d_max):
            # 随机组合还是用pure_clause组合的
            all_keys[i + 1] = gen_clause_keys(i + 1, all_keys[i] if i > 0 else None)
        for ak in all_keys:
            for seq in all_keys[ak]:
                # 本来gen_clause_keys使all_keys中的组合是构造名称组合，现在把组合后的几何子句再次存储到all_seq字典中
                all_seq.setdefault(ak, []).append(generate_clause(seq))
        return all_seq

    def make_basic_combine(self):
        def get_next_args(seq, pts, nseq=3):
            if not seq:
                seq = [[i] for i in pts]
                nseq = nseq - 1

            for i in range(nseq):
                new_seq = []
                for s in seq:
                    for p in pts:
                        ns = s + [p]
                        new_seq.append(ns)
                seq = new_seq
            return seq

        seq_list = []
        for p in self.pure_defs:
            p_points = self.pure_defs[p].points
            p_ncs = " ".join(p_points + ["=", p] + p_points)
            for a in self.arg_defs:
                da = self.arg_defs[a]
                a_points = da.points
                n_args = len(da.args) if a != 's_angle' else len(da.args) - 1
                ncb = get_next_args([], p_points, n_args)
                for nb in ncb:
                    ncs = get_ncs(a_points, a, nb)
                    seq_list.append([p_ncs, ncs])
        return seq_list

    def select_basic_combines(self):
        cbs = self.make_basic_combine()
        valid_cbs, invalid_cbs = [], []
        for seq in cbs:
            line = "; ".join(seq)
            try:
                # print("processing: ", line)
                p = pr.Problem.from_txt(line.strip())  # revise 修正参数位置错误问题
                g, x_added = gh.Graph.build_problem(p, self.defs, no_goal=True)
                if g:  # 题目有问题
                    dervs, eq4, next_branches, sat_added, _ = ddar.saturate_or_goal(g, theorems=self.rules,
                                                                                    level_times=[],
                                                                                    p=p, max_level=1000, timeout=600)
                    valid_cbs.append(line)
                else:
                    invalid_cbs.append(line)
            except:
                invalid_cbs.append(line)
        return valid_cbs, invalid_cbs

    def select_valid_problem_combines(self, file="", wfile=""):
        with open(file) as fi:
            lines = fi.readlines()

        vlines = []
        for line in lines:
            seq = line.strip().split("; ")
            kls, pfs, others = {}, [], []
            for ns in seq:
                pts, ags = ns.split("=")
                pts = pts.strip().split(" ")
                ags = ags.strip().split(" ")
                if len(pts) != len(ags) - 1:  # 如果等式前后点数一致
                    if len(pts) == 1:
                        # 添加到键值对中
                        kls.setdefault(pts[0], []).append(ags)
                    else:
                        others.append(ns)  # 包含最终问题和结论 放在最后面
                else:
                    pfs.append(ns)  # 多半是先决条件-比如构造三角形。。
            # 把原先的kls等式再次拼回成字符串 但是格式略有变化
            kns = [" ".join([k, "=", ", ".join([" ".join(ki) for ki in kls[k]])]) for k in kls]  # 多半是推导的内容 因此要放在构造之后
            nline = "; ".join(pfs + kns + others)  # 相当于把原题的等式顺序重组

            # 自己写的部分，自动添加结论部分
            # if others:
            #     nline += " ? " + others[-1]

            try:
                p = pr.Problem.from_txt(nline)  # 由上述内容构造的问题【但是不存在题号url】 同时 由于大部分行不包括？无法生成符合要求的问答结果，因此也不会输出内容
                g, x_added = gh.Graph.build_problem(p, self.defs, no_goal=True if not others else False)
                if g:
                    vlines.append(line)
            except:
                continue

        with open(wfile, "w") as wfi:
            for line in vlines:
                wfi.write(line)
        return vlines

    @staticmethod
    def translate_one_proof_sample(proof_str, to_upper=True):
        n_tag, premise, goal, steps, knowledge = proof_str.split("><")

        n_tag = n_tag[1:]
        cons_list = premise.strip().split("; ")
        know_list = knowledge.strip()[:-1]
        step_tpl = []
        step_list = steps.strip().split("; ")
        for i in range(len(step_list)):
            prev = step_list[i].split("->")[0].split(", ")
            ccld = step_list[i].split("->")[1]
            step_tpl.append((prev, ccld))

        cn_premise = "; ".join([pretty.cn_pretty(k) for k in cons_list])
        cn_goal = pretty.cn_pretty(goal)
        cn_proof = []
        for prv, cld in step_tpl:
            cn_prev = ", ".join([pretty.cn_pretty(p) for p in prv])
            cn_ld = pretty.cn_pretty(cld)
            cn_proof.append(cn_prev + " => " + cn_ld)
        cn_pfs = "; ".join(cn_proof)

        result = f"原始题号:{n_tag}. 前提: {cn_premise}. 结论: {cn_goal}. 步骤: {cn_pfs}. 使用的知识点:{know_list}."
        if to_upper:
            result = result.upper()
        return result

    @staticmethod
    def translate_one_proof_sample2json(proof_str, key_dict, to_upper=True):

        file_path = "rules_translate_save.txt"
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # 初始化一个空字典来存储键值对
        result_dict = {}

        # 遍历文件中的每一行
        for i in range(0, len(lines), 2):
            # 获取偶数行（键）和奇数行（值）
            key = lines[i].strip()
            value = lines[i + 1].strip() if i + 1 < len(lines) else None

            # 将键值对添加到字典中
            result_dict[key] = value

        n_tag, premise, goal, steps, knowledge = proof_str.split("><")

        n_tag = n_tag[1:]
        # n = n_tag.split("_")[0]
        cons_list = premise.strip().split("; ")
        know_list = knowledge.strip()[:-1].split("; ")
        step_tpl = []
        step_list = steps.strip().split("; ")
        for i in range(len(step_list)):
            prev = step_list[i].split("->")[0].split(", ")
            ccld = step_list[i].split("->")[1]
            step_tpl.append((prev, ccld))

        cn_premise = "; ".join([pretty.cn_pretty(k) for k in cons_list])
        cn_goal = pretty.cn_pretty(goal)
        cn_proof = []
        cn_know = []
        for prv, cld in step_tpl:
            cn_prev = ", ".join([pretty.cn_pretty(p) for p in prv])
            cn_ld = pretty.cn_pretty(cld)
            cn_proof.append(cn_prev + " => " + cn_ld)
        cn_pfs = "; ".join(cn_proof)
        for know in know_list:
            cn_know.append(result_dict[know])
        know_list_en = "; ".join(know_list)
        cn_knows = "; ".join(cn_know)

        result_txt = f"原始题号:{n_tag}. 原题fl: {key_dict[int(n_tag)]}. 前提: {cn_premise}. 结论: {cn_goal}. 步骤: {cn_pfs}. 生成题目的fl: {premise}  ?  {goal}. 步骤长度:{len(cn_proof)}. 使用的知识点(英文):{know_list_en}. 使用的知识点(中文):{cn_knows}. 知识点数量:{len(know_list)}"
        result_json = {
            "原始题号": n_tag,
            "原题fl": key_dict[int(n_tag)],
            "前提": cn_premise,
            "结论": cn_goal,
            "步骤": cn_pfs,
            "生成题目的fl": premise + " ? " + goal,
            "步骤长度": str(len(cn_proof)),
            "使用的知识点(英文)": know_list_en,
            "使用的知识点(中文)": cn_knows,
            "知识点数量": str(len(know_list))
        }

        if to_upper:
            result_json = {k: v.upper() for k, v in result_json.items()}
            result_txt = result_txt.upper()

        return json.dumps(result_json, ensure_ascii=False, indent=4), result_txt

    @staticmethod
    def get_dep_proof_steps(
            g: gh.Graph, goal: pr.Dependency, merge_trivials: bool = False
    ) -> tuple[
        list[pr.Dependency],
        list[pr.Dependency],
        list[tuple[list[pr.Dependency], list[pr.Dependency]]],
        dict[tuple[str, ...], int],
    ]:
        """Extract proof steps from the built DAG."""
        # goal_args = g.names2nodes(goal.args)
        # query = Dependency(goal.name, goal_args, None, None)

        # 从图 g 中提取前置条件（setup）、辅助构造（aux）、推理步骤（log）和前置条件中涉及的点（setup_points）
        setup, aux, log, setup_points = tb.get_logs(
            goal, g, merge_trivials=merge_trivials)

        refs = {}
        setup = tb.point_log(setup, refs, set())
        aux = tb.point_log(aux, refs, setup_points)

        setup = [(prems, [tuple(p)]) for p, prems in setup]
        aux = [(prems, [tuple(p)]) for p, prems in aux]

        return setup, aux, log, refs

    def get_dep_proof_steps_v2(
            g: gh.Graph, goal: pr.Dependency, p: pr.Problem, merge_trivials: bool = False
    ) -> tuple[
        list[pr.Dependency],
        list[pr.Dependency],
        list[tuple[list[pr.Dependency], list[pr.Dependency]]],
        dict[tuple[str, ...], int],
    ]:
        # setup：前置条件的依赖关系。
        # aux：辅助构造的依赖关系。
        # log：推理步骤的详细记录。
        # refs：引用关系的字典。
        # Extract logs from the graph
        setup, aux, log, setup_points = tb.get_logs(
            goal, g, merge_trivials=merge_trivials
        )

        # Initialize references and logs
        refs = {}
        setup = tb.point_log(setup, refs, set())
        aux = tb.point_log(aux, refs, setup_points)

        # Format setup and auxiliary constructions
        setup = [(prems, [tuple(p)]) for p, prems in setup]
        aux = [(prems, [tuple(p)]) for p, prems in aux]

        # TODO：如果证实是最短路径，且全部条件都使用了 则正常输出
        return setup, aux, log, refs

    @staticmethod
    def explain_log(log: list[tuple[list[pr.Dependency], list[pr.Dependency]]], upper=False):
        log_text = []
        log_cn_txt = []
        for support, dep in log:
            support_txt = [i.txt() for i in support]
            support_cn_txt = [pretty.cn_pretty(i) for i in support_txt]
            conclude_txt = [i.txt() for i in dep]
            conclude_cn_txt = [pretty.cn_pretty(i) for i in conclude_txt]
            step_text = "; ".join(support_txt) + " ==> " + "; ".join(conclude_txt)
            step_cn_text = "; ".join(support_cn_txt) + " ==> " + "; ".join(conclude_cn_txt)
            if upper:
                step_cn_text = step_cn_text.upper()
            log_text.append(step_text)
            log_cn_txt.append(step_cn_text)
        return log_text, log_cn_txt

    def generate_proof_samples(self, path, pr_file, sample_file, save_to="", n_thr=10000):
        # 假设已经得到了结论，利用结论构造样本
        # 将 setup_or_aux 中的依赖关系（plist）提取出来，返回一个包含所有依赖的列表
        def to_premise(setup_or_aux):
            deps = []
            for plist, _ in setup_or_aux:
                deps += plist
            return deps

        # 将前提（premise）、结论（goal）和推理步骤（proof）序列化为一个字符串，格式为：
        #       <premise><goal><proof_step1; proof_step2; ...><used_rule1; used_rule2; ...>
        # Theorem(
        #         premise=[Construction.from_txt(p) for p in premises],
        #         conclusion=[Construction.from_txt(c) for c in conclusion],
        #     )
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
            return "<" + n + "><" + p_str + "><" + g_str + "><" + "; ".join(pf_str) + "><" + rule_str + ">"

        # 不可以添加change 图像中点的顺序改变后题目可能出错
        def change(prem: str):
            result = []
            parts = prem.split()  # 将字符串按空格分割成列表
            if parts[0] in ["cong", "para", "perp"]:  # 检查首个单词是否为 'cong' 且总长度为5
                a, b, c, d = parts[1], parts[2], parts[3], parts[4]  # 提取四个点
                # 生成所有可能的互换组合
                permutations = [
                    f"{parts[0]} {a} {b} {c} {d}",  # 原始顺序
                    f"{parts[0]} {c} {d} {a} {b}",  # 12和34整体互换
                    f"{parts[0]} {b} {a} {c} {d}",  # 12互换
                    f"{parts[0]} {c} {d} {b} {a}",  # 12互换后整体互换
                    f"{parts[0]} {a} {b} {d} {c}",  # 34互换
                    f"{parts[0]} {d} {c} {a} {b}",  # 34互换后整体互换
                    f"{parts[0]} {b} {a} {d} {c}",  # 12互换且34互换
                    f"{parts[0]} {d} {c} {b} {a}"  # 12和34互换后整体互换
                ]
            elif parts[0] in ["coll"]:
                a, b, c = parts[1], parts[2], parts[3]
                permutations = [
                    f"{parts[0]} {a} {b} {c}",
                    # f"{parts[0]} {b} {a} {c}",
                    # f"{parts[0]} {a} {c} {b}",
                    # f"{parts[0]} {b} {c} {a}",
                    f"{parts[0]} {c} {b} {a}",
                    # f"{parts[0]} {c} {a} {b}"
                ]
            else:
                permutations = []
            result.extend(permutations)
            return result

        # 检查当前证明过程中是否用到了所有的条件【不同条件有些点可以互换 但是全部包含代码过于细碎 所以只将常用的条件点互换写入了】，如果没有则返回false
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
            return premise_set.issubset(set(all_prems)),letters

        def filter_theorems(theorems):
            from collections import defaultdict

            # Step 1: Group theorems by goal
            groups = defaultdict(list)
            for th in theorems:
                _, premise, goal, _, _ = th
                groups[goal].append(th)

            # Step 2: Process each group to remove redundant theorems
            filtered_theorems = []
            for goal, group in groups.items():
                # Create a list to mark which theorems to keep
                # 对于每个分组，使用一个布尔列表 keep 来标记哪些元素需要保留
                keep = [True] * len(group)

                for i, th1 in enumerate(group):
                    if not keep[i]:  # Skip if already marked to remove
                        continue
                    #     将 premise 转换为集合（set），然后检查是否存在包含关系
                    premise1 = set(th1[1])  # Convert premise to set for easy comparison

                    for j, th2 in enumerate(group):
                        if i == j or not keep[j]:  # Skip if same theorem or already marked to remove
                            continue
                        premise2 = set(th2[1])

                        # Check if th1's premise is fully contained in th2's premise
                        if premise1.issubset(premise2):
                            keep[j] = False  # Mark th2 to be removed

                # Add the theorems that should be kept to the filtered list
                filtered_theorems.extend([th for i, th in enumerate(group) if keep[i]])

            return filtered_theorems

        def parse_theorem_string(theorem_string):
            #       <ques_tag><premise><goal><proof_step1; proof_step2; ...><used_rule1; used_rule2; ...>
            theorems = []
            for theorem in theorem_string:
                parts = theorem.split("><")
                n = parts[0][1:]
                premise = parts[1]
                premise = premise.split("; ")  # 去掉开头的 '<'
                goal = parts[2]
                proof = parts[3]
                proof_len = proof.split("; ")
                if (len(proof_len) > 20) or (len(proof_len) < 5):
                    print(theorem + "---- 证明链路过短，已掠过")
                    continue
                used_rule = parts[4][:-1]  # 去掉结尾的 '>'
                th = [n, premise, goal, proof, used_rule]
                # th.proof = proof
                theorems.append(th)
            #     TODO:目前已经实现将每行数据存储成一个单独的元素，现在需要比较每行数据中是否有goal一致，premise为包含关系的内容，如果有则删除包含的那行数据仅保留被包含的
            filtered_theorems = filter_theorems(theorems)
            sample = []
            for fil in filtered_theorems:
                str = f"<{fil[0]}><{'; '.join(pre for pre in fil[1])}><{fil[2]}><{fil[3]}><{fil[4]}>"
                sample.append(str)
            return sample

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
                    th = self.rules[dep.rule_name]
                    theorem_set.add(pr.Theorem.txt(th))

            # 返回唯一的 problem.Theorem 列表
            return list(theorem_set)

            # 筛选出 rule_name 以 'r' 开头的对象
            # result = [dep.rule_name for dep in dependencies if dep.rule_name and dep.rule_name.startswith('r')]

            # return set(result)

        # pr_file是存储几何问题的文件，每行代表一个问题
        with open(pr_file, 'r') as pfi:
            lines = pfi.readlines()

        all_sample_str, n = [], 0
        for line in lines:
            try:
                # p = pr.Problem.from_txt(line.strip(), revise=True)  # revise 修正参数位置错误问题
                p = pr.Problem.from_txt(line.strip())  # revise 修正参数位置错误问题
                g, x_added = gh.Graph.build_problem(p, self.defs, no_goal=False)
                if g:
                    points = g.type2nodes[gm.Point]
                    points_name = {point.name for point in points}
                    lines = g.type2nodes[gm.Line]
                    circles = g.type2nodes[gm.Circle]
                    segments = g.type2nodes[gm.Segment]
                    # 使用 ddar.saturate_or_goal 生成推理步骤
                    # 在给定的几何图 g 中运行深度优先搜索（BFS）推理，直到达到饱和状态（即无法再推导出新的几何关系）或找到目标条件（p.goal）
                    # dervs每一层推理得到的几何关系，eq4每一层推理得到的等式，next_branches每层推理的分支数，sat_added所有添加到图中的新Dependency（几何对象及其依赖）
                    dervs, eq4, next_branches, sat_added, theorem_set = ddar.saturate_or_goal(g, theorems=self.rules,
                                                                                    level_times=[],
                                                                                    p=p, max_level=1000,
                                                                                    timeout=60)
                    '''
                    def find_dependencies_with_max_level(dependencies, target_name):
                        """
                        在依赖列表中找到与目标名称匹配且 level 最大的 Dependency 对象。
                        :param dependencies: 包含 Dependency 对象的列表
                        :param target_name: 目标名称
                        :return: 匹配的 Dependency 对象
                        """
                        matched_dependencies = [d for d in dependencies if d.name == target_name]
                        if not matched_dependencies:
                            return None
                        return max(matched_dependencies, key=lambda d: d.level)

                    def extract_rule_names(dependency):
                        """
                        递归提取 Dependency 对象的 rule_name 属性，并存储到集合中。
                        :param dependency: 当前的 Dependency 对象
                        :return: 包含所有 rule_name 的集合
                        """
                        rule_names = set()
                        if dependency.rule_name:
                            rule_names.add(dependency.rule_name)
                        for dep in dependency.why:
                            rule_names.update(extract_rule_names(dep))
                        return rule_names

                    # 示例输入
                    # added = [...]  # 你的 Dependency 对象列表
                    input_text = "cong"  # 替换为实际的输入文本

                    # 找到匹配且 level 最大的 Dependency 对象
                    selected_dependency = find_dependencies_with_max_level(sat_added, input_text)

                    if selected_dependency:
                        # 递归提取所有 rule_name
                        rule_names_set = extract_rule_names(selected_dependency)
                        print("提取的 rule_name 属性集合:", rule_names_set)
                    else:
                        print("没有找到匹配的 Dependency 对象")
                    '''
                    # g 图像元素中的clauses是存储初始条件的，check判断时需要考查clauses是否全部用上
                    # sat_added包含所有的完整的证明链路

                    for idx, s_add in enumerate(sat_added):
                        # setup：前置条件的依赖关系。
                        # aux：辅助构造的依赖关系。
                        # log：推理步骤的详细记录。
                        # refs：引用关系的字典。
                        goal_tuple = (s_add.name, s_add.args)
                        save_name = save_to.replace(".png", "_" + str(n) + "_" + str(idx) + ".png")
                        setup, aux, log, refs = MyDataSet.get_dep_proof_steps(g, s_add, merge_trivials=False)
                        used_rules = find_dependencies_with_r(log)
                        # setup, aux, log, refs = MyDataSet.get_dep_proof_steps_v2(g, s_add,p=p, merge_trivials=False)
                        # setup, aux --> premise; s_add --> goal; step --> goal
                        s_premise = to_premise(setup)
                        a_premise = to_premise(aux)
                        #       <premise><goal><proof_step1; proof_step2; ...>
                        # serialize(premise: list[pr.Dependency], goal: pr.Dependency,
                        #                       proof: list[tuple[list[pr.Dependency], list[pr.Dependency]]])
                        flag,letters = check_log_contains_all_premises(s_premise + a_premise, log)
                        if flag and letters==points_name:
                            if (s_premise or a_premise) and log and len(used_rules) > 0:
                                try:
                                    nup.draw(points, lines, circles, segments, goal_tuple, equals=None,
                                             save_to=save_name, theme="bright")
                                except:
                                    continue
                            all_sample_str.append(
                                serialize(str(n) + "_" + str(idx), s_premise + a_premise, s_add, log, used_rules))
                        # if (s_premise or a_premise) and log and len(used_rules) > 0:
                        #     try:
                        #         nup.draw(points, lines, circles, segments, goal_tuple, equals=None,
                        #                  save_to=save_name, theme="bright")
                        #     except:
                        #         continue
                        #     all_sample_str.append(serialize(n, s_premise + a_premise, s_add, log, used_rules))
                        # n += 1
                        # if n > 0 and n % n_thr == 0:
                        #   tag = str(int(n/n_thr))
                        #   with open(path + sample_file + "_" + tag, "w") as sfi:
                        #     for s in all_sample_str:
                        #       sfi.write(s+"\n")
                        #   all_sample_str = []
                n = n + 1
            except:
                print("\n" + str(n) + " error \n")
                n = n + 1
                continue
        # 获得所有证明链路，检查是否有相同结果步骤冗余的情况
        all_sample = parse_theorem_string(all_sample_str)
        # print()

        with open(path + sample_file + "_end", "w") as sfi:
            for s in all_sample:
                sfi.write(s + "\n")

    def build_sample_problems(self, func='v1'):
        """
        d_max: pure defs的最大个数
        max_args: 带arg的参数最大个数
        mode: 样本生成的方式:
          all, 全部生成;
          random_1: 随机
        """
        if func == "v1":
            return self.build_sample_v1()
        elif func == "v2":
            return self.build_sample_v2()

    def build_sample_v1(self, d_max=3, max_args=2, mode="all", to_file=True):
        MAX_SCALE_1 = 1000
        MAX_SEEDS_1 = 100000
        MAX_SCALE_2 = 100
        MAX_SEEDS_2 = 1000000
        MAX_SCALE_3 = 10
        MAX_SEEDS_3 = 10000000

        pure_clauses = self.make_pure_clause(d_max)
        arg_clauses = {0: pure_clauses}
        for n in range(max_args):
            arg_clauses.setdefault(n + 1, {})
            if mode == 'random_1':
                for d in arg_clauses[n]:
                    if d > 3:
                        break
                    for seq in arg_clauses[n][d]:
                        arg_clauses[n + 1].setdefault(d + 1, [])
                        new_seq_list = self.add_next_arg_clause(seq)
                        if len(arg_clauses[n][d]) > MAX_SEEDS_3 and len(new_seq_list) > MAX_SCALE_3:
                            random.shuffle(new_seq_list)
                            new_seq_list = new_seq_list[:MAX_SCALE_3]
                        elif len(arg_clauses[n][d]) > MAX_SEEDS_2 and len(new_seq_list) > MAX_SCALE_2:
                            random.shuffle(new_seq_list)
                            new_seq_list = new_seq_list[:MAX_SCALE_2]
                        elif len(arg_clauses[n][d]) > MAX_SEEDS_1 and len(new_seq_list) > MAX_SCALE_1:
                            random.shuffle(new_seq_list)
                            new_seq_list = new_seq_list[:MAX_SCALE_1]
                        arg_clauses[n + 1][d + 1] += new_seq_list

            elif mode == "all":
                for d in arg_clauses[n]:
                    for seq in arg_clauses[n][d]:
                        arg_clauses[n + 1].setdefault(d + 1, [])
                        new_seq_list = self.add_next_arg_clause(seq)
                        arg_clauses[n + 1][d + 1] += new_seq_list

        if to_file:
            cur_time = datetime.datetime.now()
            with open("test_generate_samples_{}.txt".format(cur_time.isoformat()[:19].replace(":", "-")),
                      "w") as out_fi:
                for slen in pure_clauses:
                    for seq in pure_clauses[slen]:
                        out_fi.write("; ".join(seq) + "\n")
                for n_arg in arg_clauses:
                    for d in arg_clauses[n_arg]:
                        for seq in arg_clauses[n_arg][d]:
                            out_fi.write("; ".join(seq) + "\n")

        return pure_clauses, arg_clauses

    def build_sample_v2(self, d_max=3, max_args=3, mode="all", to_file=True):
        def group_cons(seq_list):
            n_keys = {}
            for seq in seq_list:
                n_key = "_".join([ns.split("=")[1].strip().split(" ")[0] for ns in seq])
                n_keys.setdefault(n_key, []).append(seq)
            return n_keys

        num_sample = 1
        n_seq_sample = 2
        p_max = 1
        num_seqs_thr = [(1000000, 1), (100000, 10), (10000, 100), (1000, 1000)]
        pure_clauses = self.make_pure_clause(d_max)
        arg_clauses = {}
        for p_size in pure_clauses:
            if p_size > p_max:
                break
            arg_clauses.setdefault(p_size, {})
            for seq in pure_clauses[p_size]:
                arg_clauses[p_size].setdefault(1, [])
                nseq = self.add_next_arg_clause(seq, same_args=True, same_points=True, merge="permute")
                arg_clauses[p_size][1] += nseq

            for k in range(max_args - 1):
                arg_clauses[p_size].setdefault(k + 2, [])
                selected_list = arg_clauses[p_size][k + 1]
                mode = 'all'
                if len(selected_list) >= num_seqs_thr[0][0]:
                    random.shuffle(selected_list)
                    selected_list = selected_list[:num_seqs_thr[0][0]]
                    limit = num_seqs_thr[0][1]
                    mode = "full_random"
                elif len(selected_list) >= num_seqs_thr[1][0]:
                    random.shuffle(selected_list)
                    selected_list = selected_list[:num_seqs_thr[1][0]]
                    limit = num_seqs_thr[1][1]
                    mode = "full_random"
                elif len(selected_list) >= num_seqs_thr[2][0]:
                    random.shuffle(selected_list)
                    selected_list = selected_list[:num_seqs_thr[2][0]]
                    limit = num_seqs_thr[2][1]
                    mode = "full_random"
                elif len(selected_list) >= num_seqs_thr[3][0]:
                    random.shuffle(selected_list)
                    selected_list = selected_list[:num_seqs_thr[3][0]]
                    limit = num_seqs_thr[3][1]
                    mode = "all"

                for seq in selected_list:
                    nseq = self.add_next_arg_clause(seq, same_args=True, same_points=True, merge="combine",
                                                    mode=mode, limit=limit)
                    arg_clauses[p_size][k + 2] += nseq

                if to_file:
                    cur_time = datetime.datetime.now()
                    with open("test_generate_samples_{}.txt".format(cur_time.isoformat()[:19].replace(":", "-")),
                              "w") as out_fi:
                        # for slen in pure_clauses:
                        #   for seq in pure_clauses[slen]:
                        #     out_fi.write("; ".join(seq) + "\n")
                        # for n_arg in arg_clauses:
                        #   for d in arg_clauses[n_arg]:
                        for seq in arg_clauses[p_size][k + 2]:
                            out_fi.write("; ".join(seq) + "\n")

        return pure_clauses, arg_clauses

    def build_sample_v3(self, part=0, to_file=True, per_save=200000, path="", sfi="", partitions=5):
        bfi = "geoqa.txt"
        # bfi = "valid_combine_0816_test.txt" 自己定义的
        with open(bfi, 'r') as bfile:
            lines = bfile.readlines()
        unit = int(len(lines) / partitions)
        # 设置当前分区的开始行数和结束行数
        begin, end = part * unit, min((part + 1) * unit, len(lines))
        # 如果文件的剩余行数（len(lines) - end）小于一个分区的大小（unit），则将 end 设置为文件的总行数
        if len(lines) - end < unit:
            end = len(lines)
        # 整个分区的行
        target_lines = lines[begin: end]

        seq_list = []
        fi_prefix = path + sfi + "_P" + str(part) + "_"

        for line in target_lines:
            seq = line.strip().split(";")
            # 最终返回指定百分比的推理构造 list[list[str 构造语句]]
            seq_list += self.add_next_arg_clause2(seq, percent=0.004)
            # 避免内存中存储过多的序列，定期将生成的序列保存到文件中，释放内存
            if to_file and len(seq_list) >= per_save:
                ctime = datetime.datetime.now().isoformat()[:19].replace(":", "-")
                with open(fi_prefix + ctime + ".txt", "w") as ofi:
                    for line in seq_list:
                        ofi.write("; ".join(line) + "\n")
                seq_list = []

        # 处理完所有 target_lines 后，将剩余的 seq_list 写入文件
        if to_file:
            ctime = datetime.datetime.now().isoformat()[:19].replace(":", "-")
            with open(fi_prefix + ctime + ".txt", "w") as ofi:
                for line in seq_list:
                    ofi.write("; ".join(line) + "\n")
            seq_list = []
        return seq_list

    # 不包含分区处理 相当于直接从文件中创造p_clauses并进行下一步构造，但是有可能构造数量过多会超出内存，还是v3更好
    def build_sample_v4(self, part=0, to_file=True, per_save=100000, path="", sfi="", partitions=5):
        # 生成深度为2的几何子句，包括不同构造之间的组合结果
        p_clauses = self.make_pure_clause(d_max=2)
        # unit = int(len(p_clauses[2])/partitions)
        # begin, end = part * unit, min((part+1) * unit, len(p_clauses[2]))
        target_lines = p_clauses[2]

        seq_list, percent = [], 0.05
        # fi_prefix = path+sfi+"_P"+str(part)+"_"
        fi_prefix = path + sfi  # 输出文件路径
        for seq in target_lines:
            # add_next_arg_clause2最终返回指定百分比的推理构造 list[list[str 构造语句]]
            # 同时seq_list返回的也是 list[list[str 包含前后关系的构造语句]] 这种形态
            seq_list += self.add_next_arg_clause2(seq, percent=percent)
            # if to_file and len(seq_list) >= per_save:
            #   ctime = datetime.datetime.now().isoformat()[:19].replace(":", "-")
            #   with open(fi_prefix+ctime+".txt", "w") as ofi:
            #     for line in seq_list:
            #       ofi.write("; ".join(line)+"\n")
            #   seq_list = []

        if to_file:
            ctime = datetime.datetime.now().isoformat()[:19].replace(":", "-")
            with open(fi_prefix + ctime + ".txt", "w") as ofi:
                for line in seq_list:
                    ofi.write("; ".join(line) + "\n")
            seq_list = []

        return seq_list

    def build_proof_samples_v1(self, to_file=True, cn_prf_file="", json_prf_file=""):
        path = "without_check/"
        files = os.listdir(path)
        all_lines, all_cn_lines, all_json_lines = [], [], []
        for fi in files:
            with open(path + fi) as pfi:
                lines = pfi.readlines()

            for line in lines:
                try:
                    # cn_str = MyDataSet.translate_one_proof_sample(line.strip())
                    original_pr = "problems/test_fl_set_v.txt"
                    key_dict = {}
                    with open(original_pr, "r", encoding="utf-8") as file:
                        lines = file.readlines()
                        # 初始化一个空字典来存储键值对
                        for i in range(len(lines)):
                            key_dict[i] = lines[i].strip()
                    cn_json, cn_str = MyDataSet.translate_one_proof_sample2json(line.strip(), key_dict)
                    all_cn_lines.append(cn_str)
                    all_json_lines.append(cn_json)
                except:
                    print("ErrorProcessing: ", line.strip())
                    continue

        if to_file:
            with open(cn_prf_file, "w") as pfile:
                for line in all_cn_lines:
                    pfile.write(line + "\n")
            with open(json_prf_file, "w", encoding="utf-8") as json_file:
                # 将 JSON 数据写入文件，确保格式化输出
                json.dump(all_json_lines, json_file, ensure_ascii=False, indent=4)

        # return all_cn_lines


def get_ncs(points, key, args) -> str:
    f_points = points
    s_angle_key = "10"
    if key in {'square', 'parallelogram'}:  # square a b x y; parallelogram a b c x
        ncs = " ".join(f_points + ["=", key] + args + f_points)
    elif key == 's_angle':  # s_angle a b x y --> y是数值
        ncs = " ".join(f_points + ["=", key] + args + f_points + [s_angle_key])
    else:
        ncs = " ".join(f_points + ["=", key] + f_points + args)
    return ncs


def get_args(seq):
    points, args = seq.split("=")
    arl = args.strip().split(" ")
    pts = set(points.strip().split(" "))
    if arl[0] == 's_angle':
        return arl[1:3]
    else:
        return [i for i in arl[1:] if i not in pts]


# 生成递增的字符序列 比如输入a 输出b
def get_next_ord(word):
    if len(word) == 1:
        if ord(word) + 1 <= ord('z'):
            return chr(ord(word) + 1)
        else:
            return chr(ord(word) - 26 + 1) + "1"
    else:
        if ord(word[0]) + 1 <= ord('z'):
            return chr(ord(word[0]) + 1) + word[1]
        else:
            return chr(ord(word[0]) - 26 + 1) + str(int(word[1]) + 1)


def main(_):
    # 1. 生成 premise前提组合;
    # 2. 筛选 premise前提组合；
    # 3. 推理构造结论，输出推理序列
    # 4. 翻译成非形式语言

    # path = "samples/"
    # problem_file = "test_generate_samples_2024-08-12T16-33-12.txt"
    # sample_file = "test_proof_samples_2024-08-12T16-33-12.txt"

    # problem_file = "test_generate_samples_2024-08-19T20-23-29.txt" # "test_proof_h100000.txt"  # "test_proof_t50000.txt"  # "test_proof_h100000.txt"
    # sample_file = "test_proof_args_nums_four.txt" # "test_proof_h100000.txt"  # "test_proof_h100000.txt"
    # problem_file = "valid_combine_0816.txt" # "test_proof_h100000.txt"  # "test_proof_t50000.txt"  # "test_proof_h100000.txt"
    # sample_file = "valid_combine_0816_proof.txt" # "test_proof_h100000.txt"  # "test_proof_h100000.txt"

    def geoqa_data_gn(dataset, path):
        with open('problems/geoqa.txt', 'r') as m:
            lines = m.readlines()
            all_premises = []
            for line in lines:
                keys = line.strip().split("; ")
                premise = []
                for key in keys:
                    premise.append(random.choice(dataset.r2p[key])['premise'])
                premise = "; ".join(premise)
                all_premises.append(premise)
        with open(path + "geoqa" + "_end", "w") as sfi:
            for s in all_premises:
                sfi.write(s + "\n")

    dataset = MyDataSet()

    # step1:
    # sample_file = "alphageometry.txt"
    sample_file = "geoqa_with_check.txt"
    # 如果设置了输出文件，则将构造数列输出到文件中，如果没有设置输出文件，函数返回构造数组
    # dataset.build_sample_v4(sfi=sample_file)
    # fi_prefix = path + sfi  # 输出文件路径
    path = "problems/"
    # sample_file = "pxx_combine_0821"
    # dataset.build_sample_v3(sfi=sample_file)
    # part代表当前处理的分区（从0开始），partitions代表文件一共被分成几个分区
    output_file = "geoqa.txt_end"
    # dataset.build_sample_v3(part=0, path=path,sfi=output_file,partitions = 1)
    # fi_prefix = path + sfi + "_P" + str(part) + "_"
    # step2:
    '''fls = [("problem/pxx_combine_0821.txt_P0_2024-08-21T13-08-17.txt",
            "problem/pxx_combine_P0_2024-08-21T13-08-17_v.txt"),
           ("problem/pxx_combine_0821.txt_P0_2024-08-21T12-53-27.txt",
            "problem/pxx_combine_P0_2024-08-21T12-53-27_v.txt"),
           ("problem/pxx_combine_0821.txt_P0_2024-08-21T12-37-22.txt",
            "problem/pxx_combine_P0_2024-08-21T12-37-22_v.txt"),
           ("problem/pxx_combine_0821.txt_P0_2024-08-21T12-27-20.txt",
            "problem/pxx_combine_P0_2024-08-21T12-27-20_v.txt"),
           ("problem/pxx_combine_0821.txt_P0_2024-08-21T12-21-08.txt",
            "problem/pxx_combine_P0_2024-08-21T12-21-08_v.txt"),
           ("problem/pxx_combine_0821.txt_P0_2024-08-21T12-13-35.txt",
            "problem/pxx_combine_P0_2024-08-21T12-13-35_v.txt"),
           ("problem/pxx_combine_0821.txt_P0_2024-08-21T12-08-57.txt",
            "problem/pxx_combine_P0_2024-08-21T12-08-57_v.txt"),
           ("problem/pxx_combine_0821.txt_P0_2024-08-21T11-51-53.txt",
            "problem/pxx_combine_P0_2024-08-21T11-51-53_v.txt"),
           ("problem/pxx_combine_0821.txt_P0_2024-08-21T11-34-51.txt",
            "problem/pxx_combine_P0_2024-08-21T11-34-51_v.txt"),
           ("problem/pxx_combine_0821.txt_P0_2024-08-21T11-22-41.txt",
            "problem/pxx_combine_P0_2024-08-21T11-22-41_v.txt")
           ]
           '''
    # fls = [("problems/geoqa.txt",
    #         "problems/geoqa_v.txt")]
    # fls = [("test_fl_set.txt", "problems/test_fl_set_v.txt")]
    # for file, wfile in fls:
    #     _ = dataset.select_valid_problem_combines(file=file, wfile=wfile)

    # geoqa数据集生成
    # lines 存储当行信息
    # geoqa_data_gn(dataset, path)

    # step3:
    # problem_file = "problems/geoqa_end_0"
    problem_file = "problems/less_fl_set_v.txt"
    problem_file = "small.txt"
    dataset.generate_proof_samples(path, problem_file, sample_file, save_to="geometry-pics-v2/output.png")

    # step4:
    # proof_file = "alphageometry_without_check/cn_proof.txt"
    # json_file = "alphageometry_without_check/cn_proof.json"
    # 从指定路径（path）下的所有文件中读取几何证明样本，将这些样本转换为自然语言描述，并将结果保存到指定的文件中。
    # 这个函数主要用于处理和转换几何证明样本，以便后续的分析或展示
    dataset.build_proof_samples_v1(to_file=True, cn_prf_file=proof_file,json_prf_file=json_file)


if __name__ == '__main__':
    app.run(main)
