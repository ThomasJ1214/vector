"""The reported 25@25deg + 35@255deg session, using actual source routes.

These are source/command-domain checks, not calculator firmware execution.
"""
import math
import random
import unittest

from basic_harness import Machine


ENTRY = ['YES START', 'ADD VECTOR', 'MAG / ANGLE', 'STANDARD CCW +X',
         'ADD VECTOR', 'MAG / ANGLE', 'STANDARD CCW +X']
VALUES = ['25', '25', '35', '255']


class ReportedGraphError(unittest.TestCase):
    def assert_result(self, machine):
        self.assertAlmostEqual(machine.v['X'], 13.59902809732802, places=11)
        self.assertAlmostEqual(machine.v['Y'], -23.241947376599903, places=11)
        self.assertAlmostEqual(machine.v['R'], 26.92808353835371, places=11)
        self.assertAlmostEqual(machine.v['T'], 300.3322050940172, places=10)

    def test_reported_vectors_visit_every_graph_and_triangle(self):
        menus = [*ENTRY, 'GRAPHS', 'HEAD TO TAIL', 'COMMON ORIGIN',
                 'STEP THROUGH', 'INSPECT TRIANGLE', 'INSPECT TRIANGLE',
                 'INSPECT TRIANGLE', 'BACK', 'RESULTS', 'QUIT']
        keys = [45, 45, 26, 26, 24, 26, 45, 45, 45, 45, 45]
        machine = Machine(menus, [*VALUES, '0', '1', '2'], keys)
        machine.run('VECTORCE')
        self.assertFalse(machine.menus)
        self.assertFalse(machine.inputs)
        self.assertFalse(machine.keys)
        self.assertEqual(machine.v['N'], 2)
        self.assert_result(machine)
        self.assertTrue(any('LEFT UNDO' in line for line in machine.output))

    def test_graph_then_result_work_then_triangle_then_result_again(self):
        menus = [*ENTRY, 'GRAPHS', 'HEAD TO TAIL', 'BACK', 'RESULTS',
                 'MAG / DIRECTION', 'BACK', 'QUIT']
        machine = Machine(menus, VALUES, [45, 92, 105, 105, 105, 105, 93, 45, 45])
        machine.run('VECTORCE')
        self.assertFalse(machine.menus)
        self.assertFalse(machine.keys)
        self.assert_result(machine)
        self.assertTrue(any('DIRECTION DEG CCW' in line for line in machine.output))

    def test_graph_labels_stay_in_safe_rows_for_varied_data(self):
        rng = random.Random(25525)
        cases = [[(0, 0)], [(0, 4)], [(-4, 0)], [(1e-9, -1e-9)],
                 [(1e9, 1e9), (-1e9, -1e9)]]
        for _ in range(20):
            cases.append([(rng.uniform(-1, 1) * 10**rng.randint(-9, 9),
                           rng.uniform(-1, 1) * 10**rng.randint(-9, 9))
                          for _ in range(rng.randint(1, 20))])
        for vectors in cases:
            for mode in (1, 2, 3, 4):
                with self.subTest(vectors=vectors, mode=mode):
                    machine = Machine(keys=([26] * len(vectors) + [45]) if mode == 4 else [45])
                    machine.v.update(N=len(vectors), G=mode, L=0)
                    for row, (x, y) in zip(machine.m, vectors):
                        row[:5] = [x, y, math.hypot(x, y),
                                   math.degrees(math.atan2(y, x)) % 360, 2]
                    machine.run('VQGRAPH')
                    self.assertFalse(machine.keys)
                    for frame in machine.frames:
                        for command in frame:
                            if command[0] == 'Text':
                                row, col = command[2:4]
                                self.assertEqual(row, int(row))
                                self.assertEqual(col, int(col))
                                self.assertLessEqual(row, 150)
                                self.assertLessEqual(col, 264)


if __name__ == '__main__':
    unittest.main()
