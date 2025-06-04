import unittest

from absl.testing import absltest

import problem as pr
import graph as gh
import ddar
import trace_back as tb


class DataSetTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.defs = pr.Definition.from_txt_file('../defs.txt', to_dict=True)
        cls.rules = pr.Theorem.from_txt_file('../rules.txt', to_dict=True)
  
    def test_sample_problem_case(self):
        pr_file = "../test_sample_v1.txt"
        with open(pr_file, 'r') as pfi:
            lines = pfi.readlines()
        all_problems = []
        for line in lines:
            p = pr.Problem.from_txt(line.strip())
            g, x_added = gh.Graph.build_problem(p, self.defs)
            all_problems.append((p, g, x_added))
        self.assertTrue(len(all_problems) < 20)
        all_deductions = []
        all_deps = []
        for p, g, _ in all_problems:
            dervs, eq4, next_branches, sat_added, tset = ddar.saturate_or_goal(
              g, theorems=self.rules, level_times=[], p=p, max_level=1000, timeout=600)

            for s_dep in sat_added:
                setup, aux, xa, xb = tb.get_logs(s_dep, g, merge_trivials=False)
                setup = [p.hashed() for p in setup]
                aux = [p.hashed() for p in aux]
                all_deps.append((p, s_dep, setup, aux, xa, xb))

            all_deductions.append((dervs, eq4, next_branches, sat_added, g))

        self.assertTrue(len(all_deductions) < 20)


if __name__ == '__main__':
    absltest.main()

