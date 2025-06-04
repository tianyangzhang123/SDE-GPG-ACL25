import unittest
import problem_generating as pg
from absl.testing import absltest


import problem as pr
import graph as gh
import ddar
import trace_back as tb
import geometry as gm
import numericals as nm
import json


class PrGenerateTest(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     super().setUpClass()
    #     cls.defs = pr.Definition.from_txt_file('../defs.txt', to_dict=True)
    #     cls.rules = pr.Theorem.from_txt_file('../rules.txt', to_dict=True)

    def test_generate_problem_case(self):
        # 可能因为生成顺序不一致导致不通过
        creator = pg.GeoProblemCreator()
        test_req = {"type": 0,
                    "extra_info": {
                        "topic": ["等腰直角三角形", "垂直"],
                        "origin_que": ""
                    }}
        target, s_txt = creator.process(test_req)
        expect_target = ['构造等腰直角三角形ABC使得AB垂直AC', '构造D使得DAB为等腰直角三角形', '构造E使得EAC为等腰直角三角形']
        expect_goal = '∠CED=∠CBD'
        # self.assertEqual(s_txt, '∠ABC=∠BCA')
        # self.assertEqual(s_txt[1], 'd = nsquare d b a')
        self.assertEqual(target[0], expect_target[0])
        self.assertEqual(target[1], expect_target[1])
        # self.assertEqual(target[2], expect_target[2])
        # self.assertEqual(s_txt, expect_goal)

    def test_solve_que(self):
        # line = "a b c = triangle a b c; o = circle o a b c; h = midpoint h c b; d = on_line d o h, on_line d a b; e = on_tline e c c o, on_tline e a a o ? cyclic a o e d"
        # line = 'a b c d = eq_quadrangle a b c d; i j k l = cc_tangent i j k l a b b a'
        # line = 'a b c d = eq_quadrangle a b c d; i j k l = cc_tangent i j k l a b b a ? eqangle a i a k i j k l'
        # with open("jgex_ag_231.txt") as f:
        # line = 'a b c = iso_triangle a b c; x = foot x a b c'
        # line = 'a b c d = r_trapezoid a b c d; x = intersection_cc x b a d'
        # line = 'a b c d = rectangle a b c d; x = intersection_pp x a c d d a c'

        #
        # def recover(ds, xwords):
        #     return "".join([i if i not in ds else ds[i] for i in xwords])
        # rules = []
        # # rule_tag = 'geoQA_'
        # rule_tag = 'yalphageometry_'
        # creater = pg.GeoProblemCreator()
        # question_list = []
        # # for key, rls in rules:
        # for idx, rls in enumerate(rules):
        #
        #     ques_info = creater.generate_ques_with_rules_v2(rls, rule_tag+str(idx)+".png")
        #     # ques_info = creater.generate_ques_with_rules_v2(rls, rule_tag + key + ".png")
        #     qls = []
        #     for cur_info in ques_info:
        #         if len(cur_info[2]) < 3:
        #             continue
        #         for item in cur_info[2][:3]:
        #              qinfo = {'raw_premise': cur_info[0], 'ques_premises_nl': [i[1] for i in cur_info[1]],
        #                       'ques_premises_fl': [i[0] for i in cur_info[1]],
        #                       'conclusion_nl': item[-2], 'conclusion_fl': item[-3],
        #                       'conclusion_pic': item[-1], 'reference': item[-4]}
        #              qls.append(qinfo)
        #     question_list.append(qls)
        #     print("processed key: ", idx)
        #
        # jds = {'rules': rules, 'question_list': question_list}
        # # with open("geoQA_fl_samples.json", "w") as f:
        # with open("yalphageometry_fl_samples.json", "w") as f:
        #     json.dump(jds, f, ensure_ascii=False, indent=4)
        # with open('test_fl_set.txt') as f:
        #     lines = f.readlines()
        # for line in lines:
        #     all_sat_words, ques = creater.generate_ques_with_premise(line)
        # print("debug")
        r2ds = {'perp_perp_ncoll_para': 'r00',
                 'cong_cong_cong_cyclic': 'r01',
                 'eqangle_para': 'r02',
                 'cyclic_eqangle': 'r03',
                 'eqangle6_ncoll_cyclic': 'r04',
                 'cyclic_eqangle_cong': 'r05',
                 'midp_midp_para_1': 'r06',
                 'para_coll_coll_eqratio3': 'r07',
                 'perp_perp_npara_eqangle': 'r08',
                 'eqangle_eqangle_eqangle': 'r09',
                 'eqratio_eqratio_eqratio': 'r10',
                 'eqratio6_coll_ncoll_eqangle6': 'r11',
                 'eqangle6_coll_ncoll_eqratio6': 'r12',
                 'cong_ncoll_eqangle': 'r13',
                 'eqangle6_ncoll_cong': 'r14',
                 'circle_perp_eqangle': 'r15',
                 'circle_eqangle_perp': 'r16',
                 'circle_midp_eqangle': 'r17',
                 'circle_coll_eqangle_midp': 'r18',
                 'perp_midp_cong': 'r19',
                 'circle_coll_perp': 'r20',
                 'cyclic_para_eqangle': 'r21',
                 'midp_perp_cong': 'r22',
                 'cong_cong_perp': 'r23',
                 'cong_cong_cyclic_perp': 'r24',
                 'midp_midp_para_2': 'r25',
                 'midp_para_para_midp': 'r26',
                 'eqratio_coll_coll_ncoll_sameside_para': 'r27',
                 'para_coll': 'r28',
                 'midp_midp_eqratio': 'r29',
                 'eqangle_perp_perp': 'r30',
                 'eqratio_cong_cong': 'r31',
                 'cong_cong_cong_ncoll_contri*': 'r32',
                 'cong_cong_eqangle6_ncoll_contri*': 'r33',
                 'eqangle6_eqangle6_ncoll_simtri': 'r34',
                 'eqangle6_eqangle6_ncoll_simtri2': 'r35',
                 'eqangle6_eqangle6_ncoll_cong_contri': 'r36',
                 'eqangle6_eqangle6_ncoll_cong_contri2': 'r37',
                 'eqratio6_eqratio6_ncoll_simtri*': 'r38',
                 'eqratio6_eqangle6_ncoll_simtri*': 'r39',
                 'eqratio6_eqratio6_ncoll_cong_contri*': 'r40',
                 'para_coll_coll_eqratio6_sameside_para': 'r41',
                 'para_coll_coll_para_eqratio6': 'r42'}
        all_lines = ['a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? para b f f h',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqangle b g f g e h a h',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqangle f g b g a h e h',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio b d g d a h h g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio g d b d h g a h',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio e h h g f g g d',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i j k l = cc_tangent i j k l a b b a ? eqangle b k b h a l e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i j k l = cc_tangent i j k l a b b a ? eqangle b h b k e g a l',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i j k l = cc_tangent i j k l a b b a ? eqangle b k e g a l b h',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle a e a c a c c e',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle a c a e c e a c',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle a e a b a b b e',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle a e b e a e a c',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle b e a e a c a e',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle a e d e d e a d',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle a e a c a e b e',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle a c a e b e a e',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle a d d e d e a e',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle c e a c a c a e',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle a c c e a e a c',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle b e b c b c c e',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio h a g h b d g d',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio g h h a g d b d',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio g h h e g d g f',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = cc_tangent f g h i a b b a ? eqratio a i f h a b a i',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = cc_tangent f g h i a b b a ? eqratio f h a i a i a b',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = cc_tangent f g h i a b b a ? eqangle b h g h f i a i',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle a e b e a e a c',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle b e a e a c a e',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle a e d e d e a d',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle a e d e d e a d',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle d e a e a d d e',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle b c a c a e b e',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqratio b a h a h a e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqratio h a b a e g h a',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqangle b g f g e h a h',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i = circle i a b c ? eqangle a h f g e g b h',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i = circle i a b c ? eqangle f g a h b h e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i = circle i a b c ? eqangle e f a h e h e g',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c; f = circle f a b c ? eqangle a e d e d e a d',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c; f = circle f a b c ? eqangle d e a e a d d e',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c; f = circle f a b c ? eqangle a f a c a c c f',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i j k l = r_trapezoid i j k l; i j k l = centroid i j k l a b d ? eqangle a d e g f h b h',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i j k l = r_trapezoid i j k l; i j k l = centroid i j k l a b d ? eqangle e g a d b h f h',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i j k l = r_trapezoid i j k l; i j k l = centroid i j k l a b d ? eqangle a d a h d h e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle d h f g e g g h',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle f g d h g h e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle d h b d f g b h',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio b d d g h a h g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d g b d h g h a',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio h a e d h d d g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio b d d g h a h g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d g b d h g h a',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d h h a d g f g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle e f a h e h e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle a h e f e g e h',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle f h b h a d e g',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle a d d e d e a e',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle d e a d a e d e',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle a e b e b c a c',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? eqangle b e a b a b a e',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? eqangle a b b e a e a b',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? eqangle a f a c a c c f',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? eqangle c f a c a c a f',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? eqangle a c c f a f a c',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? perp a b e f',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? eqangle b e a b a b a e',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? eqangle a b b e a e a b',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? eqangle a f a c a c c f',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i = circle i a b c; j k l m = r_trapezoid j k l m; j k l m = centroid j k l m a b d ? eqangle d h f g e g i l',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i = circle i a b c; j k l m = r_trapezoid j k l m; j k l m = centroid j k l m a b d ? eqangle f g d h i l e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i = circle i a b c; j k l m = r_trapezoid j k l m; j k l m = centroid j k l m a b d ? eqangle f g a h b h e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i j k l = r_trapezoid i j k l; i j k l = centroid i j k l a b d ? eqangle f h b h a d e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i j k l = r_trapezoid i j k l; i j k l = centroid i j k l a b d ? eqangle b h f h e g a d',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i j k l = r_trapezoid i j k l; i j k l = centroid i j k l a b d ? eqangle a d a h d h e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqratio b a b g b g h f',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqratio b g b a h f b g',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqangle a h e h f g b g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle f g a h b h e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle a h f g e g b h',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle a h e f e g e h',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = r_trapezoid f g h i; j k l m = centroid j k l m a b d ? eqratio b d m d j d m l',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = r_trapezoid f g h i; j k l m = centroid j k l m a b d ? eqratio m d b d m l j d',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = r_trapezoid f g h i; j k l m = centroid j k l m a b d ? eqratio b d j d m d m l',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle e f e h a h e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle e h e f e g a h',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle e f a h e h e g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio a h h g d b d g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio h g a h d g d b',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d h d g a h d e',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle a h f g e g b h',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle f g a h b h e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle e f a h e h e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqratio a b f a f a g e',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqratio f a a b g e f a',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqangle b e e h f g a f',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio b d g d h a h g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio g d b d h g h a',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio h a h d g f g d',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i = eq_triangle i a b; j = circle j a b c ? eqratio f i b a b a h i',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i = eq_triangle i a b; j = circle j a b c ? eqratio b a f i h i b a',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i = eq_triangle i a b; j = circle j a b c ? eqangle e g g i a i a f',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i = circle i a b c; j k l m = r_trapezoid j k l m; j k l m = centroid j k l m a b d; n o = square a b n o ? eqangle b h b o e g a n',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i = circle i a b c; j k l m = r_trapezoid j k l m; j k l m = centroid j k l m a b d; n o = square a b n o ? eqangle b o b h a n e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i = circle i a b c; j k l m = r_trapezoid j k l m; j k l m = centroid j k l m a b d; n o = square a b n o ? eqangle b h a n e g b o',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i j k l = centroid i j k l a b c ? eqratio j i k l a b c l',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i j k l = centroid i j k l a b c ? eqratio k l j i c l a b',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d; i j k l = centroid i j k l a b c ? eqratio c l k c l b j b',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = incenter2 f g h i a b d; j k l m = r_trapezoid j k l m; j k l m = centroid j k l m a b d ? eqratio b c a k m d l m',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = incenter2 f g h i a b d; j k l m = r_trapezoid j k l m; j k l m = centroid j k l m a b d ? eqratio a k b c l m m d',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = incenter2 f g h i a b d; j k l m = r_trapezoid j k l m; j k l m = centroid j k l m a b d ? eqangle a i g h f h b i',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio b d d g a h g h',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d g b d g h a h',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d h a h d g g f',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio b d g d h a h g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio g d b d h g h a',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio h g h e g d f g',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqratio a b a f a f g e',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqratio a f a b g e a f',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqangle e h a h b g f g',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqratio b a b g b g g e',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqratio b g b a g e b g',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a ? eqangle a h e h f g b g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d b d g a h h g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d g d b h g a h',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio e h h g f g d g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio a h h g b d g d',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio h g a h g d b d',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio h g g d h e d e',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d b d g h a h g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d g d b h g h a',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio h g h e d g f g',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle a e a c a c c e',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle a c a e c e a c',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle b e a b a b a e',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio f e g h b a c h',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio g h f e c h b a',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio g h c g e h a e',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c; i = eq_triangle i a b ? eqratio c h c g h a e a',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c; i = eq_triangle i a b ? eqratio c g c h e a h a',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c; i = eq_triangle i a b ? eqratio c h h a c g e a',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio b c e c h c g h',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio e c b c g h h c',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio a h a e h c g c',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle c e a c a c a e',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle a c c e a e a c',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle c e b c b c b e',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio c h c g a h e a',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio c g c h e a a h',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio c h a h c g e a',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle a e b e a e a c',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle b e a e a c a e',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c ? eqangle a e d e d e a d',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b ? eqangle a b b e b e a e',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b ? eqangle b e a b a e b e',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b ? eqangle a b a e a e b e',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c; f = circle f a b c ? eqangle a e d e d e a d',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c; f = circle f a b c ? eqangle d e a e a d d e',
                     'a b c d = eq_quadrangle a b c d; e = shift e a b c; f = circle f a b c ? eqangle a f a c a c c f',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i j k l = rectangle i j k l; i j k l = centroid i j k l a b c ? eqratio e h l c k h k l',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i j k l = rectangle i j k l; i j k l = centroid i j k l a b c ? eqratio l c e h k l k h',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i j k l = rectangle i j k l; i j k l = centroid i j k l a b c ? eqratio j l b a l b f h',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio h e a e h g c g',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio a e h e c g h g',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio h e h g a e c g',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio e h e a g h g c',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio e a e h g c g h',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio e h g h e a g c',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c; i = eq_triangle i a b; j = circle j a b c ? eqratio c e h g c b c h',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c; i = eq_triangle i a b; j = circle j a b c ? eqratio h g c e c h c b',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c; i = eq_triangle i a b; j = circle j a b c ? eqratio h g h f c h h b',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? eqangle b e a b a b a e',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? eqangle a b b e a e a b',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? eqangle c f a c a c a f',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? eqangle b e a b a b a e',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? eqangle a b b e a e a b',
                     'a b c d = eq_quadrangle a b c d; e = eq_triangle e a b; f = circle f a b c ? eqangle a f a c a c c f',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i = eq_triangle i a b; j = circle j a b c ? eqratio b a e i g i b a',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i = eq_triangle i a b; j = circle j a b c ? eqratio e i b a b a g i',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i = eq_triangle i a b; j = circle j a b c ? eqangle h i a f a b b i',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = r_trapezoid f g h i; j k l m = centroid j k l m a b d ? eqratio j l m l c b m d',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = r_trapezoid f g h i; j k l m = centroid j k l m a b d ? eqratio m l j l m d c b',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = r_trapezoid f g h i; j k l m = centroid j k l m a b d ? eqratio j d b d m l m d',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d b d g a h h g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d g d b h g a h',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d h a h d g g f',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = r_trapezoid f g h i; j k l m = centroid j k l m a b d ? eqratio j d l m b d d m',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = r_trapezoid f g h i; j k l m = centroid j k l m a b d ? eqratio l m j d d m b d',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c; f g h i = r_trapezoid f g h i; j k l m = centroid j k l m a b d ? eqratio j d b d l m d m',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d; i j k l = eq_quadrangle i j k l; i j k l = incenter2 i j k l a b d ? eqratio b d d g a h h g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d; i j k l = eq_quadrangle i j k l; i j k l = incenter2 i j k l a b d ? eqratio d g b d h g a h',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d; i j k l = eq_quadrangle i j k l; i j k l = incenter2 i j k l a b d ? eqangle j k a l i k b l',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio b d g d a h g h',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio g d b d g h a h',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio a h d e h d g d',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle c e a c a c a e',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle a c c e a e a c',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle b e b c b c c e',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle c e a c a c a e',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle a c c e a e a c',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle b e b c b c c e',
                     'a b c d = rectangle a b c d; e f g h = centroid e f g h a b c ? eqratio h c c g h d c a',
                     'a b c d = rectangle a b c d; e f g h = centroid e f g h a b c ? eqratio c g h c c a h d',
                     'a b c d = rectangle a b c d; e f g h = centroid e f g h a b c ? eqratio h c h d c g c a',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i j k l = rectangle i j k l; i j k l = centroid i j k l a b c ? eqratio f h c l a b l k',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i j k l = rectangle i j k l; i j k l = centroid i j k l a b c ? eqratio c l f h l k a b',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i j k l = rectangle i j k l; i j k l = centroid i j k l a b c ? eqratio a l f h i l a b',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle c e a c a c a e',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle a c c e a e a c',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle b e b c b c c e',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle a e a c a c c e',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle a c a e c e a c',
                     'a b c d = eq_quadrangle a b c d; e = circle e a b c ? eqangle b e a b a b a e',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i j k l = rectangle i j k l; i j k l = centroid i j k l a b c ? eqratio f g c l e k l k',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i j k l = rectangle i j k l; i j k l = centroid i j k l a b c ? eqratio c l f g l k e k',
                     'a b c d = eq_quadrangle a b c d; e f g h = cc_tangent e f g h a b b a; i j k l = rectangle i j k l; i j k l = centroid i j k l a b c ? eqratio a b k i g e c a',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio g b g h b a c h',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio g h g b c h b a',
                     'a b c d = eq_quadrangle a b c d; e f g h = centroid e f g h a b c ? eqratio c h g c h a e a',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d b d g h a g h',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d g d b g h h a',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio d h d g h a d e',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle a h f g e g b h',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle f g a h b h e g',
                     'a b c d = eq_quadrangle a b c d; e f g h = incenter2 e f g h a b d ? eqangle f g d h g h e g',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio b d g d a h g h',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio g d b d g h a h',
                     'a b c d = r_trapezoid a b c d; e f g h = centroid e f g h a b d ? eqratio a h h d g f g d']
        select_rules = ['midp_perp_cong',
                         'midp_perp_cong',
                         'midp_perp_cong',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'cyclic_eqangle; circle_coll_perp',
                         'cyclic_eqangle; circle_coll_perp',
                         'cyclic_eqangle; circle_coll_perp',
                         'cong_ncoll_eqangle',
                         'cong_ncoll_eqangle',
                         'cong_ncoll_eqangle',
                         'eqangle_para',
                         'eqangle_para',
                         'eqangle_para',
                         'eqangle_para',
                         'eqangle_para',
                         'eqangle_para',
                         'eqratio6_eqratio6_ncoll_simtri*',
                         'eqratio6_eqratio6_ncoll_simtri*',
                         'eqratio6_eqratio6_ncoll_simtri*',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'cong_ncoll_eqangle; midp_perp_cong',
                         'cong_ncoll_eqangle; midp_perp_cong',
                         'cong_ncoll_eqangle; midp_perp_cong',
                         'eqangle_para',
                         'eqangle_para',
                         'eqangle_para',
                         'eqangle_para',
                         'eqangle_para',
                         'eqangle_para',
                         'circle_coll_perp',
                         'circle_coll_perp',
                         'circle_coll_perp',
                         'cyclic_eqangle; cong_ncoll_eqangle',
                         'cyclic_eqangle; cong_ncoll_eqangle',
                         'cyclic_eqangle; cong_ncoll_eqangle',
                         'eqangle_para; cong_ncoll_eqangle',
                         'eqangle_para; cong_ncoll_eqangle',
                         'eqangle_para; cong_ncoll_eqangle',
                         'cyclic_eqangle; circle_midp_eqangle',
                         'cyclic_eqangle; circle_midp_eqangle',
                         'cyclic_eqangle; circle_midp_eqangle',
                         'cyclic_eqangle',
                         'cyclic_eqangle',
                         'cyclic_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'cyclic_eqangle',
                         'cyclic_eqangle',
                         'cyclic_eqangle',
                         'eqangle_para',
                         'eqangle_para',
                         'eqangle_para',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'cyclic_eqangle; cong_ncoll_eqangle; circle_midp_eqangle',
                         'cyclic_eqangle; cong_ncoll_eqangle; circle_midp_eqangle',
                         'cyclic_eqangle; cong_ncoll_eqangle; circle_midp_eqangle',
                         'perp_perp_npara_eqangle; circle_midp_eqangle',
                         'perp_perp_npara_eqangle; circle_midp_eqangle',
                         'perp_perp_npara_eqangle; circle_midp_eqangle',
                         'perp_midp_cong',
                         'perp_midp_cong',
                         'perp_midp_cong',
                         'cyclic_eqangle',
                         'cyclic_eqangle',
                         'cyclic_eqangle',
                         'cong_ncoll_eqangle; circle_midp_eqangle',
                         'cong_ncoll_eqangle; circle_midp_eqangle',
                         'cong_ncoll_eqangle; circle_midp_eqangle',
                         'cyclic_eqangle',
                         'cyclic_eqangle',
                         'cyclic_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'cyclic_eqangle',
                         'cyclic_eqangle',
                         'cyclic_eqangle',
                         'circle_coll_perp',
                         'circle_coll_perp',
                         'circle_coll_perp',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_coll_perp; eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'circle_coll_perp; eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'circle_coll_perp; eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'cyclic_eqangle; cong_ncoll_eqangle; circle_coll_eqangle_midp; cyclic_para_eqangle',
                         'cyclic_eqangle; cong_ncoll_eqangle; circle_coll_eqangle_midp; cyclic_para_eqangle',
                         'cyclic_eqangle; cong_ncoll_eqangle; circle_coll_eqangle_midp; cyclic_para_eqangle',
                         'cyclic_eqangle; para_coll',
                         'cyclic_eqangle; para_coll',
                         'cyclic_eqangle; para_coll',
                         'cong_ncoll_eqangle; circle_perp_eqangle; circle_midp_eqangle',
                         'cong_ncoll_eqangle; circle_perp_eqangle; circle_midp_eqangle',
                         'cong_ncoll_eqangle; circle_perp_eqangle; circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_coll_perp',
                         'circle_coll_perp',
                         'circle_coll_perp',
                         'midp_perp_cong',
                         'midp_perp_cong',
                         'midp_perp_cong',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'cong_ncoll_eqangle',
                         'cong_ncoll_eqangle',
                         'cong_ncoll_eqangle',
                         'para_coll_coll_eqratio3',
                         'para_coll_coll_eqratio3',
                         'para_coll_coll_eqratio3',
                         'para_coll_coll_eqratio3; eqangle6_eqangle6_ncoll_simtri',
                         'para_coll_coll_eqratio3; eqangle6_eqangle6_ncoll_simtri',
                         'para_coll_coll_eqratio3; eqangle6_eqangle6_ncoll_simtri',
                         'para_coll_coll_eqratio3',
                         'para_coll_coll_eqratio3',
                         'para_coll_coll_eqratio3',
                         'eqratio6_eqratio6_ncoll_simtri*',
                         'eqratio6_eqratio6_ncoll_simtri*',
                         'eqratio6_eqratio6_ncoll_simtri*',
                         'midp_midp_para_1',
                         'midp_midp_para_1',
                         'midp_midp_para_1',
                         'eqangle_para',
                         'eqangle_para',
                         'eqangle_para',
                         'eqangle6_eqangle6_ncoll_simtri',
                         'eqangle6_eqangle6_ncoll_simtri',
                         'eqangle6_eqangle6_ncoll_simtri',
                         'eqangle_para; cong_ncoll_eqangle',
                         'eqangle_para; cong_ncoll_eqangle',
                         'eqangle_para; cong_ncoll_eqangle',
                         'midp_perp_cong; midp_para_para_midp',
                         'midp_perp_cong; midp_para_para_midp',
                         'midp_perp_cong; midp_para_para_midp',
                         'midp_midp_para_1',
                         'midp_midp_para_1',
                         'midp_midp_para_1',
                         'midp_midp_para_1',
                         'midp_midp_para_1',
                         'midp_midp_para_1',
                         'para_coll_coll_eqratio3; eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'para_coll_coll_eqratio3; eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'para_coll_coll_eqratio3; eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'midp_midp_eqratio; eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'midp_midp_eqratio; eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'midp_midp_eqratio; eqangle6_eqangle6_ncoll_simtri; eqratio6_eqratio6_ncoll_simtri*',
                         'cong_ncoll_eqangle; circle_midp_eqangle',
                         'cong_ncoll_eqangle; circle_midp_eqangle',
                         'cong_ncoll_eqangle; circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'cong_ncoll_eqangle; circle_midp_eqangle',
                         'cong_ncoll_eqangle; circle_midp_eqangle',
                         'cong_ncoll_eqangle; circle_midp_eqangle',
                         'circle_midp_eqangle; cong_cong_perp',
                         'circle_midp_eqangle; cong_cong_perp',
                         'circle_midp_eqangle; cong_cong_perp',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'cong_ncoll_eqangle',
                         'cong_ncoll_eqangle',
                         'cong_ncoll_eqangle',
                         'cong_ncoll_eqangle',
                         'cong_ncoll_eqangle',
                         'cong_ncoll_eqangle',
                         'midp_para_para_midp',
                         'midp_para_para_midp',
                         'midp_para_para_midp',
                         'midp_perp_cong; midp_para_para_midp',
                         'midp_perp_cong; midp_para_para_midp',
                         'midp_perp_cong; midp_para_para_midp',
                         'eqangle6_ncoll_cong',
                         'eqangle6_ncoll_cong',
                         'eqangle6_ncoll_cong',
                         'eqangle6_ncoll_cong',
                         'eqangle6_ncoll_cong',
                         'eqangle6_ncoll_cong',
                         'midp_perp_cong; midp_para_para_midp',
                         'midp_perp_cong; midp_para_para_midp',
                         'midp_perp_cong; midp_para_para_midp',
                         'eqratio_eqratio_eqratio',
                         'eqratio_eqratio_eqratio',
                         'eqratio_eqratio_eqratio',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'cyclic_eqangle',
                         'cyclic_eqangle',
                         'cyclic_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle',
                         'circle_midp_eqangle']
        all_sat_words = []
        creater = pg.GeoProblemCreator()
        defs = pr.Definition.from_txt_file('defs.txt', to_dict=True)
        rules = pr.Theorem.from_txt_file('rules.txt', to_dict=True)
        # for line in all_lines:
        for i in range(100):
            line = all_lines[i]
            print("debug: ", i, line)
            srls = select_rules[i].split("; ")
            sds = [r2ds[ts] for ts in srls]
            p_args = [i.split(" = ")[0].split(" ") for i in line.split(" ? ")[0].split("; ")]
            p = pr.Problem.from_txt(line.strip())
            # pds = dict([(v, k) for k, v in p.mapping.items()])
            # ques = []
            # for q in line.split("?")[0].split("; "):
            #     ques.append(creater.translate_clause(q, p.mapping))
            g, x_added = gh.Graph.build_problem(p, defs)
            if g:
                # points = g.type2nodes[gm.Point]
                # lines = g.type2nodes[gm.Line]
                # circles = g.type2nodes[gm.Circle]
                # segments = g.type2nodes[gm.Segment]
                # save_to = "example.png"
                # nm.draw(points, lines, circles, segments, equals=None, save_to=save_to, theme="bright")
                dervs, eq4, next_branches, sat_added, tset = ddar.saturate_or_goal(g, theorems=rules, level_times=[],
                                                                                   p=p, max_level=1000, timeout=60)
                if sat_added:
                    sat_ls = [t for t in sat_added if t.name == p.goal.name and
                              [ti.name for ti in t.args] == p.goal.args]
                    # print("debug")
                    for idx, t_goal in enumerate(sat_ls):
                        # t_goal = sat_added[0]
                        # t_goal = random.choice(sat_added)
                        # goal_tuple = (t_goal.name, t_goal.args)
                        # nm.draw(points, lines, circles, segments, goal_tuple, equals=None,
                        #         save_to=save_to.replace(".png", str(idx)+".png"), theme="bright")
                        # if t_goal.name != p.goal.name
                        setup, aux, log, xa = tb.get_logs(t_goal, g, merge_trivials=False)
                        # setup, aux_setup, log, setup_points
                        # setup = [p.hashed() for p in setup]
                        # aux = [p.hashed() for p in aux]
                        # s_string, proof_list = creater.get_dep_proof_steps(g, t_goal, merge_trivials=False)
                        # premises_str, goal_str, proof_str = s_string.split("><")
                        # premises_str = premises_str[1:]
                        # proof_str = proof_str[:-1]

                        theorems = [fi[1][0].rule_name for fi in log]
                        tls = [fi for fi in theorems if len(fi) > 0]
                        pxs = [[[pt.name for pt in pi.args] for pi in pi[0]] for pi in log]
                        pns = set()
                        for fi in pxs:
                            for fj in fi:
                                for fk in fj:
                                    pns.add(fk)
                        xn, xm = 0, len(p_args)
                        yn, ym = len(set(tls) & set(sds)), len(set(sds))
                        for ptx in p_args:
                            if any(pti in pns for pti in ptx):
                                xn += 1
                        all_sat_words.append((i, xn/xm, yn/ym))

                        # steps = []
                        # for proof in proof_list:
                        #     premise, conclusion = proof.split("->")
                        #     premise = premise.split(';')
                        #     new_premise = ";".join([creater.cn_pretty(i.strip()).upper() for i in premise])
                        #     new_conclusion = creater.cn_pretty(conclusion).upper()
                        #     steps.append((new_premise, new_conclusion))
                        # t_txt = t_goal.txt()
                        # goal_txt = creater.cn_pretty(t_txt).upper()
                    #     sat_words.append([setup, aux, log, xa, s_string, steps, goal_txt])
                    # all_sat_words.append(sat_words)

        return all_sat_words

    # def get_one_goal(self, seq_line):
    #     p = pr.Problem.from_txt(seq_line.strip())
    #     g, x_added = gh.Graph.build_problem(p, self.setter.defs)
    #     if g:
    #         dervs, eq4, next_branches, sat_added = ddar.saturate_or_goal(
    #             g, theorems=self.setter.rules, level_times=[], p=p, max_level=1000, timeout=600)
            # if sat_added:
            #     t_goal = sat_added[0]
            #     # t_goal = random.choice(sat_added)
            #     setup, aux, xa, xb = tb.get_logs(t_goal, g, merge_trivials=False)
            #     setup = [p.hashed() for p in setup]
            #     aux = [p.hashed() for p in aux]
            #     s_string = GeoProblemCreator.get_dep_proof_steps(g, t_goal, merge_trivials=False)
            #     return t_goal, setup, aux, xa, xb, s_string
        return None


if __name__ == '__main__':
    absltest.main()

