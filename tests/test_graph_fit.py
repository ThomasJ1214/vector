"""Behavioral checks for the native calculator's data-focused graph windows.

These exercise TI-BASIC source with the project harness, not a TI emulator.
Pixel positions are calculated independently from the resulting WINDOW values.
"""
from collections import deque
import math
import unittest

from basic_harness import Machine


class WindowKeys(deque):
    """Record the actual window whenever the program waits for a key."""

    def __init__(self, machine, keys):
        super().__init__(keys)
        self.machine = machine
        self.windows = []

    def popleft(self):
        self.windows.append(tuple(self.machine.v[name] for name in
                                  ('Xmin', 'Xmax', 'Ymin', 'Ymax')))
        return super().popleft()


class GraphFit(unittest.TestCase):
    def graph(self, vectors, mode=1, selected=1, keys=None):
        machine = Machine()
        machine.v.update(N=len(vectors), G=mode, L=selected)
        for row, (x, y) in zip(machine.m, vectors):
            row[:5] = [x, y, math.hypot(x, y),
                       math.degrees(math.atan2(y, x)) % 360, 2]
        machine.keys = WindowKeys(machine, [45] if keys is None else keys)
        machine.run('VQGRAPH')
        self.assertFalse(machine.keys)
        return machine

    def points(self, vectors, mode, selected=1):
        points = [(0, 0)]
        x = y = 0
        for dx, dy in vectors:
            x += dx
            y += dy
            if mode in (1, 4):
                points.append((x, y))
        if mode == 2:
            points.extend(vectors)
            points.append((x, y))  # The common-origin view also draws the sum.
        if mode == 3:
            endpoint = (x, y) if selected == 0 else vectors[selected - 1]
            points.extend([endpoint, (endpoint[0], 0)])
        return points

    def pixels(self, machine, points):
        v = machine.v
        return [((x - v['Xmin']) * 264 / (v['Xmax'] - v['Xmin']),
                 (v['Ymax'] - y) * 164 / (v['Ymax'] - v['Ymin']))
                for x, y in points]

    def check_fit(self, machine, points, require_dense=True):
        v = machine.v
        horizontal_unit = (v['Xmax'] - v['Xmin']) / 264
        vertical_unit = (v['Ymax'] - v['Ymin']) / 164
        self.assertGreater(horizontal_unit, 0)
        self.assertTrue(math.isclose(horizontal_unit, vertical_unit,
                                     rel_tol=1e-12))
        pixels = self.pixels(machine, points)
        for x, y in pixels:
            self.assertTrue(math.isfinite(x) and math.isfinite(y))
            self.assertGreaterEqual(x, 12 - 1e-7)
            self.assertLessEqual(x, 252 + 1e-7)
            self.assertGreaterEqual(y, 32 - 1e-7)
            self.assertLessEqual(y, 130 + 1e-7)
        left, right = min(x for x, _ in pixels), max(x for x, _ in pixels)
        top, bottom = min(y for _, y in pixels), max(y for _, y in pixels)
        self.assertAlmostEqual((left + right) / 2, 132, places=6)
        self.assertAlmostEqual((top + bottom) / 2, 81, places=6)
        if require_dense:
            # A constrained dimension should use most of the plot, with room
            # for arrowheads. This catches the former large symmetric window.
            self.assertGreater(max((right - left) / 240,
                                   (bottom - top) / 98), .80)

    def test_positive_and_negative_data_are_centered_and_fill_the_plot(self):
        for vectors in [[(3, 1), (4, 2)], [(-3, -1), (-4, -2)]]:
            for mode in (1, 2, 3, 4):
                with self.subTest(vectors=vectors, mode=mode):
                    machine = self.graph(vectors, mode)
                    self.check_fit(machine, self.points(vectors, mode))

    def test_common_origin_includes_resultant_beyond_individual_vectors(self):
        vectors = [(3, 2)] * 10
        machine = self.graph(vectors, 2)
        self.check_fit(machine, self.points(vectors, 2))
        self.assertEqual((machine.v['X'], machine.v['Y']), (30, 20))

    def test_cancelled_path_keeps_all_intermediate_endpoints_visible(self):
        vectors = [(10, 0)] * 9 + [(-10, 0)] * 9
        for mode in (1, 4):
            with self.subTest(mode=mode):
                machine = self.graph(vectors, mode)
                self.check_fit(machine, self.points(vectors, mode))
                self.assertEqual((machine.v['X'], machine.v['Y']), (0, 0))

    def test_common_origin_ignores_unrelated_cumulative_path_extents(self):
        vectors = [(10, 0)] * 9 + [(-10, 0)] * 9
        origin = self.graph(vectors, 2)
        path = self.graph(vectors, 1)
        self.check_fit(origin, self.points(vectors, 2))
        self.assertLess(origin.v['Xmax'] - origin.v['Xmin'],
                        (path.v['Xmax'] - path.v['Xmin']) / 4)

    def test_selected_triangle_is_independent_of_other_vectors(self):
        endpoint = (0, -1e-9)
        isolated = self.graph([endpoint], 3)
        mixed = self.graph([(1e9, 1e9), endpoint], 3, selected=2)
        self.check_fit(mixed, self.points([(1e9, 1e9), endpoint], 3, 2))
        for name in ('Xmin', 'Xmax', 'Ymin', 'Ymax'):
            self.assertEqual(isolated.v[name], mixed.v[name])

    def test_resultant_triangle_fits_result_instead_of_individual_extremes(self):
        vectors = [(1e9, 0), (-1e9, 1e-9)]
        machine = self.graph(vectors, 3, selected=0)
        self.check_fit(machine, self.points(vectors, 3, 0))
        self.assertLess(machine.v['Ymax'] - machine.v['Ymin'], 1e-8)

    def test_horizontal_vertical_and_extreme_values(self):
        cases = [[(4, 0)], [(0, -4)], [(1e-9, -1e-9)],
                 [(1e9, 1e9), (-1e9, 0)], [(1e-9, 1e9)]]
        for vectors in cases:
            for mode in (1, 2, 3, 4):
                with self.subTest(vectors=vectors, mode=mode):
                    machine = self.graph(vectors, mode)
                    self.check_fit(machine, self.points(vectors, mode))

    def test_zero_vectors_have_finite_nonempty_windows(self):
        for mode in (1, 2, 3, 4):
            with self.subTest(mode=mode):
                machine = self.graph([(0, 0)] * 3, mode)
                self.check_fit(machine, [(0, 0)], require_dense=False)
                self.assertTrue(all(math.isfinite(machine.v[name]) for name in
                                    ('Xmin', 'Xmax', 'Ymin', 'Ymax')))

    def test_step_window_stays_stable_through_additions_and_undo(self):
        vectors = [(10, 2), (-3, -8), (-7, 6)]
        machine = self.graph(vectors, 4, keys=[26, 105, 26, 24, 24, 26, 45])
        self.assertEqual(len(machine.keys.windows), 7)
        self.assertTrue(all(window == machine.keys.windows[0]
                            for window in machine.keys.windows))
        self.check_fit(machine, self.points(vectors, 4))
        self.assertEqual(machine.v['M'], 2)


if __name__ == '__main__':
    unittest.main()
