import sys
import problem_generating as pg
import random
import problem as pr
import graph as gh
import ddar
import trace_back as tb
import geometry as gm
import numericals as nm
import datetime
import json
import re

from pretty import cn_pretty


def parse_request(text, limit=4):
    knowledge_list = [i.strip() for i in text.split(";")]
    if len(knowledge_list) == 0:
        knowledge_list = ["三角形", "重心"]
    elif len(knowledge_list) >= limit:
        knowledge_list = knowledge_list[:limit]
    else:
        pass

    return knowledge_list


def merge_premise_combines(premise_list, context: pg.GeoProblemCreator, n_pure=1):
    # 暂不涉及参数合并问题
    split_list = []
    for item in premise_list:
        split_list += item.split("; ")
    premise_list = split_list
    if len(premise_list) <= 2:
        return premise_list

    exist_pts = set()
    for item in premise_list[:2]:
        exist_pts = exist_pts | set(item.split(" = ")[0].split(" "))

    p_set = set(premise_list[:2])
    new_list = premise_list[:2]
    mps = {}
    for p in premise_list[2:]:
        if p in p_set:
            continue
        else:
            points, args = p.split(" = ")
            pts, aks = points.split(" "), args.split(" ")
            key = aks[0]
            if key in context.setter.pure_defs:
                if len(set(pts) & exist_pts) == 0:
                    new_list.append(p)
                else:
                    nts = []
                    for k in range(len(pts)):
                        ki = 0
                        while chr(ord('a') + ki + k) in exist_pts:
                            ki += 1
                        nts.append(chr(ord('a') + ki + k))
                        exist_pts.add(chr(ord('a') + ki + k))
                    mps = dict(zip(pts, nts))
                    new_list.append(" ".join(nts + ["=", key] + nts))
                    exist_pts = exist_pts | set(nts)
            else:
                words = p.split(" ")
                ngs = [mps[wi] if wi in mps else wi for wi in words]
                mps = {}
                nts = []
                for k in range(len(pts)):
                    if pts[k] not in exist_pts:
                        nts.append(pts[k])
                    else:
                        ki = 0
                        while chr(ord('a') + ki + k) in exist_pts:
                            ki += 1
                        nts.append(chr(ord('a') + ki + k))
                        exist_pts.add(chr(ord('a') + ki + k))
                xps = dict(zip(pts, nts))
                ngs = [xps[i] if i in xps else i for i in ngs]
                new_list.append(" ".join(ngs))

    return new_list


def clauses_to_txt(problem: pr.Problem, context: pg.GeoProblemCreator = None):
    cls_text = []
    for clause in problem.clauses:
        points = clause.points
        pls = []
        for construct in clause.constructions:
            args = construct.args
            name = construct.name
            deft = context.setter.trans[name]
            p_args = deft.definition.construction.args
            p_map = {} if len(p_args) != len(args) else dict(zip(p_args, args))
            new_desc = "".join([p_map[i.lower()].upper() if i.lower() in p_map else i for i in deft.desc])
            pls.append(new_desc)

        u_text = "且".join(pls)
        cls_text.append(u_text)
    return cls_text


def cn_pretty_proof_step(proof_list):
    cn_proof = []
    for item in proof_list:
        premise, goal = item.split("->")
        premises = premise.split(", ")
        cn_premises = "，".join([cn_pretty(i) for i in premises]).upper()
        cn_goal = cn_pretty(goal).upper()
        cn_proof.append(" -> ".join([cn_premises, cn_goal]))
    return cn_proof


def translate_one_proof_sample2json(all_str, to_upper=True):
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

    n_tag, premise, goal, steps, knowledge = all_str.split("><")

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

    cn_premise = "; ".join([cn_pretty(k) for k in cons_list])
    cn_goal = cn_pretty(goal)
    cn_proof = []
    cn_know = []
    for prv, cld in step_tpl:
        cn_prev = ", ".join([cn_pretty(p) for p in prv])
        cn_ld = cn_pretty(cld)
        cn_proof.append(cn_prev + " => " + cn_ld)
    cn_pfs = "; ".join(cn_proof)
    for know in know_list:
        cn_know.append(result_dict[know])
    know_list_en = "; ".join(know_list)
    cn_knows = "; ".join(cn_know)

    # result_txt = f"原始题号:{n_tag}. 原题fl: {key_dict[int(n_tag)]}. 前提: {cn_premise}. 结论: {cn_goal}. 步骤: {cn_pfs}. 生成题目的fl: {premise}  ?  {goal}. 步骤长度:{len(cn_proof)}. 使用的知识点(英文):{know_list_en}. 使用的知识点(中文):{cn_knows}. 知识点数量:{len(know_list)}"
    result_txt = f"原始题号:{n_tag}. 原题fl: . 原题知识点: . 前提: {cn_premise}. 结论: {cn_goal}. 步骤: {cn_pfs}. 生成题目的fl: {premise}  ?  {goal}. 步骤长度:{len(cn_proof)}. 使用的知识点(英文):{know_list_en}. 使用的知识点(中文):{cn_knows}. 知识点数量:{len(know_list)}"
    result_json = {
        "原始题号": n_tag,
        # "原题fl": key_dict[int(n_tag)],
        "原题fl": "",
        "原题知识点": "",
        "que_text": "",
        "前提": cn_premise,
        "结论": cn_goal,
        "步骤": cn_pfs,
        "生成题目的fl": premise + " ? " + goal,
        "步骤长度": str(len(cn_proof)),
        "使用的知识点(英文)": know_list_en,
        "使用的知识点(中文)": cn_knows,
        "知识点数量": str(len(know_list)),
        "pic_name": ""
    }

    if to_upper:
        result_json = {k: v.upper() for k, v in result_json.items()}
        result_txt = result_txt.upper()

    # return json.dumps(result_json, ensure_ascii=False, indent=4), result_txt
    return result_json, result_txt


def select_que_goals(premise, context: pg.GeoProblemCreator = None):
    """不指定target时，推理寻找一个合适的结论，构造一道题"""
    if isinstance(premise, list):
        premise = "; ".join(premise)
    p = pr.Problem.from_txt(premise)
    clauses_text = clauses_to_txt(p, context)
    g, x_added = gh.Graph.build_problem(p, context.setter.defs)
    candidates = []
    if g:
        points = g.type2nodes[gm.Point]
        lines = g.type2nodes[gm.Line]
        circles = g.type2nodes[gm.Circle]
        segments = g.type2nodes[gm.Segment]
        elements = (points, lines, circles, segments)
        dervs, eq4, next_branches, sat_added, tset = ddar.saturate_or_goal(g, theorems=context.setter.rules,
                                                                           level_times=[], p=p, max_level=1000,
                                                                           timeout=60)
        if sat_added:
            for idx, t_goal in enumerate(sat_added):
                # goal_tuple = (t_goal.name, t_goal.args)
                # nm.draw(points, lines, circles, segments, goal_tuple, equals=None,
                #         save_to=save_to.replace(".png", str(idx)+".png"), theme="bright")
                # setup, aux, log, xa = tb.get_logs(t_goal, g, merge_trivials=False)
                s_string, proof_list = context.get_dep_proof_steps(g, t_goal, idx, merge_trivials=False,
                                                                   context=context)
                # if s_string and len(proof_list) >= 5 and len(proof_list) <= 20:
                # premises_str, goal_str, proof_str = s_string.split("><")
                result_json, result_txt = translate_one_proof_sample2json(s_string)
                goal_text = t_goal.txt()
                goal_cn_text = cn_pretty(goal_text).upper()
                que_text = "; ".join(clauses_text) + " 求证: " + goal_cn_text
                result_json["前提"] = que_text
                cn_proof = cn_pretty_proof_step(proof_list)
                candidates.append((que_text, t_goal, cn_proof, elements, result_json, result_txt))  # 题目/参考答案/图


    return candidates


def generate_question_from_theorems(request_kg=None, context: pg.GeoProblemCreator = None,
                                    save_pic="pics/pic.png", batch=2, limit=20):
    def make_patches(xds):
        c_len, c_patch, x_patch = len(xds[0][1]), [xds[0]], []
        if len(xds) <= 1:
            return x_patch
        for xi in xds[1:]:
            if len(xi[1]) == c_len:
                c_patch.append(xi)
            else:
                x_patch.append(c_patch)
                c_patch = [xi]
                c_len = len(xi[1])
        x_patch.append(c_patch)
        return x_patch

    def stack_hashes(x_hash):
        xs = {}
        for item in x_hash:
            xk = int(item[0] / 100)
            xs.setdefault(xk, []).append(item)
        return xs

    kgs = set(request_kg)
    rule2premise = {}
    premise_rules = {}
    for rule in kgs:
        # premise_hash
        p_hash = set([i['premise_hash'] for i in context.setter.r2p[rule]])
        rule2premise[rule] = p_hash
        for p in p_hash:
            premise_rules.setdefault(p, set()).add(rule)
    hks = sorted(premise_rules.items(), key=lambda x: len(x[1]), reverse=True)
    kps = make_patches(hks)
    select_premises = []
    for k, v in stack_hashes(kps[0]).items():
        select_premises += v[:batch]
    if len(kps) > 1:
        for k, v in stack_hashes(kps[1]).items():
            select_premises += v[: batch - 1]
    candidate_premises = []
    # for p_key, rls in select_premises:
    for p_key, rls in select_premises[::-1]:
        u_hashes = []
        for r in kgs - rls:
            u_hashes.append(rule2premise[r])
        um_hashes = [[j for j in i if int(j / 100) == int(p_key / 100)] for i in u_hashes]
        # merge_premise_combines(premise_list, context: pg.GeoProblemCreator, n_pure=1)
        support_ps = []
        for i in range(len(um_hashes)):
            if len(um_hashes[i]) > 0:
                support_ps.append(list(set(um_hashes[i][:2] + [um_hashes[i][-1]])))
            else:
                uxs = list(u_hashes[i])
                support_ps.append([uxs[0], uxs[-1]] if len(uxs) > 1 else [uxs[0]])
        cps = [[p_key]]
        for item in support_ps:
            new_cps = []
            for i in item:
                new_cps += [j + [i] for j in cps]
            cps = new_cps
        candidate_premises += cps

    all_candidates = []
    for candidate in candidate_premises:
        pxs = context.setter.p2t[str(candidate[0])]
        pls = pxs[:2] if len(pxs) <= 2 else pxs[:2] + [pxs[-1]]
        pls = [[i] for i in pls]
        if len(candidate) > 1:
            for psh in candidate[1:]:
                clause = context.setter.p2t[str(psh)]
                cps = clause[:2] if len(clause) <= 2 else clause[:2] + [clause[-1]]
                new_pls = [i + [j] for i in pls for j in cps]
                pls = new_pls
        all_candidates += pls

    all_premises = [merge_premise_combines(c, context) for c in all_candidates]
    my_questions = []
    for item in all_premises[:limit]:
        print(item)
        candidates = select_que_goals(item, context)
        candidates.sort(key=lambda x: len(x[-3]), reverse=True)
        new_candidates = [candidates[0], candidates[int(len(candidates) / 2)]] if len(candidates) > 2 else candidates
        # new_candidates = (que_text, t_goal, cn_proof, elements,result_json,result_txt)
        my_questions += new_candidates

    uds = []
    for ti, item in enumerate(my_questions):
        que_text, t_goal, cn_proof, elements, result_json, result_txt = item
        time_string = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        goal_tuple = (t_goal.name, t_goal.args)
        points, lines, circles, segments = elements
        pic_name = save_pic.replace(".png", str(ti) + "_" + time_string + ".png")
        try:
            nm.draw(points, lines, circles, segments, goal_tuple, equals=None, save_to=pic_name, theme="bright")  # 画图
            result_json["pic_name"] = pic_name
            result_json["原题知识点"] = "; ".join(kgs)
            # uds.append({"que_text": que_text, "cn_proof": cn_proof, "pic_name": pic_name})
            uds.append(result_json)
        except:
            continue

    return uds


def generate_question(request_kg=None, context: pg.GeoProblemCreator = None, step=3, batch=8,
                      save_pic="pics/pic.png", input_type="knowledge", save_file="saved_questions.json"):
    def lcs(str1, str2):
        m = len(str1)
        n = len(str2)
        # 选择较短的字符串作为列方向，优化空间
        if m < n:
            str1, str2 = str2, str1
            m, n = n, m
        # 创建一个长度为 n + 1 的一维数组 dp
        dp = [0] * (n + 1)

        for i in range(1, m + 1):
            # 保存上一行的前一个值
            prev = 0
            for j in range(1, n + 1):
                temp = dp[j]
                if str1[i - 1] == str2[j - 1]:
                    dp[j] = prev + 1
                else:
                    dp[j] = max(dp[j], dp[j - 1])
                prev = temp

        return dp[n]

    def get_lcs(xg: str, x_context: pg.GeoProblemCreator):
        all_lcs = [(k, lcs(xg, k)) for k in x_context.topics]
        all_lcs.sort(key=lambda x: x[1], reverse=True)
        return [i[0] for i in all_lcs]

    def make_patches(xds):
        c_len, c_patch, x_patch = len(xds[0][1]), [xds[0]], []
        if len(xds) <= 1:
            return x_patch
        for xi in xds[1:]:
            if len(xi[1]) == c_len:
                c_patch.append(xi)
            else:
                x_patch.append(c_patch)
                c_patch = [xi]
                c_len = len(xi[1])
        x_patch.append(c_patch)
        return x_patch

    if input_type != 'knowledge':
        return generate_question_from_theorems(request_kg, context, save_pic)

    kgs = ",".join([re.sub("[，；、。;]", ",", i) for i in request_kg]).split(",")
    p_hashes, hds, hks, u_set = [], {}, {}, set()
    for ki, kg in enumerate(kgs):
        tps = []
        u_set.add(ki)
        if kg in context.topics:
            topics = context.topics[kg]
        else:
            skg = get_lcs(kg, context)
            topics = context.topics[skg[0]]
        for t in topics:
            p_hash = context.setter.def_hash[t]
            if str(p_hash) in context.setter.d2p:
                tps += context.setter.d2p[str(p_hash)]
        p_hashes.append(tps)
        for ti in tps:
            pf, kf = int(ti / 100), ti % 100
            hds.setdefault(pf, set()).add(ki)
            hks.setdefault(ti, set()).add(ki)
    hks = sorted(hks.items(), key=lambda x: len(x[1]), reverse=True)
    kps = make_patches(hks)
    selected_premises, n_iter, ni = kps[0][:5], 50, 0
    while len(set(int(i[0] / 100) for i in selected_premises)) == 1 and ni < n_iter:
        selected_premises = selected_premises[:-1]
        selected_premises.append(kps[0][min(5 + ni, len(kps[0]) - 1)])
        ni += 1
    # 2. 合并不同的clause组合
    candidate_premises = []
    for p in selected_premises:
        hl = u_set - p[1]
        px_key = int(p[0] / 100)
        pfs = []
        if len(hl) == 0:
            candidate_premises.append(context.setter.p2t[str(p[0])])
            continue
        for hi in hl:
            if len(pfs) == 0:
                c_hashes = [px for px in p_hashes[hi] if int(px / 100) == px_key]
                if len(c_hashes) > 0:
                    pfs.append([c_hashes[0]])
                    if len(c_hashes) > 1:
                        pfs.append([c_hashes[-1]])
                else:
                    pfs.append([p_hashes[hi][0]])
                    if len(p_hashes[hi]) > 1:
                        pfs.append([p_hashes[hi][-1]])
            else:
                nfs = []
                for item in pfs:
                    c_hashes = [px for px in p_hashes[hi] if int(px / 100) == px_key]
                    if len(c_hashes) > 0:
                        nfs.append(item + [c_hashes[0]])
                        if len(c_hashes) > 1:
                            nfs.append(item + [c_hashes[-1]])
                    else:
                        nfs.append(item + [p_hashes[hi][0]])
                        if len(p_hashes[hi]) > 1:
                            nfs.append(item + [p_hashes[hi][-1]])

                pfs = nfs
        pfs = [[p[0]] + i for i in pfs]
        afs = []
        for fi in pfs:
            pls = []
            for ti in fi:
                if len(pls) == 0:
                    pls = [[context.setter.p2t[str(ti)][0]]]
                    if len(context.setter.p2t[str(ti)]) > 1:
                        pls.append([context.setter.p2t[str(ti)][-1]])
                else:
                    pns = []
                    for pni in pls:
                        pns.append(pni + [context.setter.p2t[str(ti)][0]])
                        if len(context.setter.p2t[str(ti)]) > 1:
                            pns.append(pni + [context.setter.p2t[str(ti)][-1]])
                    pls = pns
            afs += pls
        sfs = afs[:batch - 4] + afs[-4:]
        cfs = []
        for item in sfs:
            cfs.append(merge_premise_combines(item, context))
        candidate_premises.append(cfs)
    my_premises = []
    for ki, p in enumerate(candidate_premises):
        if len(p) <= step:
            my_premises = p
        elif (ki + 1) * step > len(p):
            my_premises += p[:2] + [p[-1]]
        else:
            my_premises += p[ki * step: (ki + 1) * step]

    # 3. premise组合构造前提/结论/参考答案等信息
    my_questions = []
    for item in my_premises:
        candidates = select_que_goals(item, context)
        candidates.sort(key=lambda x: len(x[-1]), reverse=True)
        new_candidates = [candidates[0], candidates[int(len(candidates) / 2)]] if len(candidates) > 2 else candidates
        my_questions += new_candidates

    uds = []
    for ti, item in enumerate(my_questions):
        que_text, t_goal, cn_proof, elements = item
        time_string = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        goal_tuple = (t_goal.name, t_goal.args)
        points, lines, circles, segments = elements
        pic_name = save_pic.replace(".png", str(ti) + "_" + time_string + ".png")
        try:
            nm.draw(points, lines, circles, segments, goal_tuple, equals=None, save_to=pic_name, theme="bright")  # 画图
            uds.append({"que_text": que_text, "cn_proof": cn_proof, "pic_name": pic_name})
        except:
            continue

    return uds
    # for item in uds:
    #     print(item)
    # with open(save_file, 'w') as fi:
    #     json.dump(uds, fi, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    creator = pg.GeoProblemCreator()

    if len(sys.argv) == 2:
        input_text = sys.argv[1]
    else:
        input_text = ""
    request = parse_request(input_text)
    result = generate_question(request, creator)
