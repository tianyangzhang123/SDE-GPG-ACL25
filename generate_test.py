import unittest

from absl.testing import absltest

# import problem as pr
# import graph as gh
# import ddar
# import trace_back as tb
from generate import generate_question
import problem_generating as pg


class GenerateTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # cls.defs = pr.Definition.from_txt_file('../defs.txt', to_dict=True)
        # cls.rules = pr.Theorem.from_txt_file('../rules.txt', to_dict=True)

    def test_sample_problem_case(self):
        # input_knowledge = ["圆，垂直平分，角相等"]
        # input_knowledge = ["圆", "垂直平分", "角相等"]
        # input_knowledge = ['平行四边形', '等分', '点在线上']
        # input_knowledge = ['垂心', '角相等', '等腰三角形']
        # input_knowledge = ['直线与圆相交', '共线', '相切']
        # input_knowledge = ["轴对称"]
        # input_knowledge = ['角平分线']
        input_knowledge = ["重心"]
        context = pg.GeoProblemCreator()
        result_json = generate_question(request_kg=input_knowledge, context=context, step=3, batch=8)
        ques_sample = {'que_text': '四边形ABCD满足AC=BD; 点E是D、A、B的外接圆中心; 点F在BD的垂直平分线上; ' +\
                                   '等腰三角形GHI满足GH=GI; 点J满足角GHJ等于角IGH 求证: ∠EAB=∠ABE',
                       'cn_proof': ['EA=EB -> ∠EAB=∠ABE'],
                       'pic_name': 'pics/pic0_20250226-102245.png'}  # 可能会因为筛选机制内容有变化
        self.assertTrue(len(result_json) >= 10)  # 返回的结果个数
        self.assertTrue(ques_sample.keys() == result_json[0].keys())
        # self.assertTrue(result_json[0]['que_text'] == ques_sample['que_text'])
        # self.assertTrue(result_json[0]['cn_proof'] == ques_sample['cn_proof'])
        self.assertTrue(result_json[0]['pic_name'][:9] == ques_sample['pic_name'][:9])

    def test_generate_problem_by_theorems(self):
        # input_rules = ["eqangle6_eqangle6_ncoll_cong_contri2"]
        input_rules = ['eqratio6_eqratio6_ncoll_simtri*', "eqangle6_eqangle6_ncoll_cong_contri2"]
        # input_rules = ['eqangle_perp_perp', 'eqratio6_eqratio6_ncoll_simtri*', "eqangle6_eqangle6_ncoll_cong_contri2",
        #                'cyclic_eqangle_cong', 'midp_midp_para_2', 'eqratio_eqratio_eqratio', 'cong_ncoll_eqangle',
        #                'circle_perp_eqangle', 'eqangle6_ncoll_cyclic', 'para_coll', 'midp_midp_para_1', 'eqangle_para',
        #                'cong_cong_cong_ncoll_contri*', 'midp_midp_eqratio']
        context = pg.GeoProblemCreator()
        result_json = generate_question(request_kg=input_rules, context=context, step=3, batch=8, input_type="theorem")
        print(result_json)
        ques_sample = {'que_text': '四边形ABCD满足AC=BD; 点E是D、A、B的外接圆中心; 点F在BD的垂直平分线上; ' +\
                                   '等腰三角形GHI满足GH=GI; 点J满足角GHJ等于角IGH 求证: ∠EAB=∠ABE',
                       'cn_proof': ['EA=EB -> ∠EAB=∠ABE'],
                       'pic_name': 'pics/pic0_20250226-102245.png'}  # 可能会因为筛选机制内容有变化
        # self.assertTrue(len(result_json) >= 10)  # 返回的结果个数
        # self.assertTrue(ques_sample.keys() == result_json[0].keys())
        # self.assertTrue(result_json[0]['que_text'] == ques_sample['que_text'])
        # self.assertTrue(result_json[0]['cn_proof'] == ques_sample['cn_proof'])
        # self.assertTrue(result_json[0]['pic_name'][:9] == ques_sample['pic_name'][:9])


if __name__ == '__main__':
    absltest.main()

