import math
import unittest
from basic_harness import Machine, ROOT

class SourceTests(unittest.TestCase):
    def entry(self, vectors):
        menus=['YES START']; inputs=[]
        for style,values,choices in vectors:
            menus+=['ADD VECTOR',style]+choices
            inputs+=list(map(str,values))
        menus+=['QUIT']
        m=Machine(menus,inputs); m.run('VECTORCE')
        self.assertFalse(m.menus); self.assertFalse(m.inputs)
        return m

    def test_components_quadrants_and_axes(self):
        for x,y,t in [(3,4,53.13010235415598),(-3,4,126.86989764584402),
                      (-3,-4,233.13010235415598),(3,-4,306.869897645844),
                      (0,2,90),(0,-2,270),(2,0,0),(-2,0,180),(0,0,0)]:
            with self.subTest(x=x,y=y):
                m=Machine(); m.v.update(A=x,B=y);m.run('VQMATH')
                self.assertAlmostEqual(m.v['R'],math.hypot(x,y))
                self.assertAlmostEqual(m.v['T'],t)

    def test_compass_24_30_east_of_north(self):
        m=self.entry([('MAG / ANGLE',[24,30],['COMPASS WORDS','NORTH','EAST OF NORTH'])])
        self.assertAlmostEqual(m.m[0][0],12)
        self.assertAlmostEqual(m.m[0][1],12*math.sqrt(3))
        self.assertEqual(m.m[0][3],60)

    def test_all_compass_forms(self):
        for axis,phrase,expected in [('NORTH','EAST OF NORTH',60),('NORTH','WEST OF NORTH',120),
                 ('SOUTH','EAST OF SOUTH',300),('SOUTH','WEST OF SOUTH',240),
                 ('EAST','NORTH OF EAST',30),('EAST','SOUTH OF EAST',330),
                 ('WEST','NORTH OF WEST',150),('WEST','SOUTH OF WEST',210)]:
            with self.subTest(phrase=phrase):
                m=self.entry([('MAG / ANGLE',[24,30],['COMPASS WORDS',axis,phrase])])
                self.assertEqual(m.m[0][3],expected)

    def test_perpendicular_mixed_and_cancel(self):
        m=self.entry([('MAG / ANGLE',[3,0],['STANDARD CCW +X']),('X / Y',[0,4],[])])
        m.stopped=False;m.run('VQSUM')
        self.assertEqual((m.v['X'],m.v['Y'],m.v['R']),(3,4,5))
        m=self.entry([('MAG / ANGLE',[24,-330],['STANDARD CCW +X']),
                      ('MAG / ANGLE',[24,210],['STANDARD CCW +X'])])
        m.stopped=False;m.run('VQSUM');self.assertEqual(m.v['Z'],1)

    def test_axis_snap_and_exact_zero(self):
        m=self.entry([('MAG / ANGLE',[10,0],['STANDARD CCW +X']),
                      ('MAG / ANGLE',[10,180],['STANDARD CCW +X'])])
        m.stopped=False;m.run('VQSUM')
        self.assertEqual((m.v['X'],m.v['Y'],m.v['R'],m.v['Z']),(0,0,0,1))

    def test_numeric_validation(self):
        for good,value in [('0',0),('⁻3.5',-3.5),('-30',-30),('.000000001',1e-9),('1000000000',1e9)]:
            m=Machine(inputs=[good]);m.run('VQNUM');self.assertEqual(m.v['F'],1)
            self.assertAlmostEqual(m.v['V'],value)
        for bad in ['.','-','1..2','2+3','1E9','ABC','1000000001','.0000000001','1'*19]:
            m=Machine(inputs=[bad,'Q']);m.run('VQNUM');self.assertEqual(m.v['F'],0)

    def test_cancel_edit_and_delete(self):
        menus=['YES START','ADD VECTOR','X / Y','VECTORS','EDIT','X / Y',
               'VECTORS','DELETE','YES','QUIT']
        m=Machine(menus,['3','4','Q']);m.run('VECTORCE');self.assertEqual(m.v['N'],0)
        # Deletion shifts all data, and canceled edit never commits partial data.
        menus=['YES START','ADD VECTOR','X / Y','VECTORS','EDIT','X / Y','QUIT']
        m=Machine(menus,['3','4','9','Q']);m.run('VECTORCE');self.assertEqual(m.m[0][:2],[3,4])

    def test_large_small_and_graph_modes(self):
        m=self.entry([('X / Y',[1e9,1e9],[])])
        # Input uses decimal, never scientific notation.
        # str(1e9) is decimal, so above is valid.
        for g in [1,2,3,4]:
            m.stopped=False;m.v.update(G=g,L=1);m.keys.extend([26,24,45] if g==4 else [45])
            m.run('VQGRAPH');self.assertGreater(m.v['S'],1e9)
        m=Machine();m.v.update(A=1e-18,B=-1e-18);m.run('VQMATH')
        self.assertAlmostEqual(m.v['T'],315)
        self.assertTrue(math.isclose(m.v['R'],math.sqrt(2)*1e-18,rel_tol=1e-14))

    def test_result_pages_and_triangle(self):
        m=self.entry([('X / Y',[-3,4],[])])
        m.stopped=False;m.v['L']=0;m.menus.extend(['FULL WORK','TRIANGLE']);m.keys.extend([105]*8+[45]);m.run('VQWORK')
        self.assertTrue(any('DIRECTION DEG CCW' in s for s in m.output))
        self.assertTrue(any('NORTH OF WEST' in s for s in m.output))

    def test_near_cancellation_is_not_forced_to_zero(self):
        m=Machine(); m.v['N']=2
        m.m[0][:3]=[1e9,0,1e9]
        m.m[1][:3]=[-1e9+.001,0,1e9-.001]
        m.run('VQSUM')
        self.assertGreater(m.v['R'],0)
        self.assertEqual(m.v['Z'],2)
        m.v['L']=0;m.menus.append('FULL WORK');m.keys.extend([45]);m.run('VQWORK')
        self.assertFalse(any('DIRECTION UNDEFINED' in s for s in m.output))

    def test_zero_result_has_no_angle(self):
        m=Machine(menus=['FULL WORK','BACK'],keys=[105]*4);m.v['L']=0
        m.run('VQWORK')
        self.assertTrue(any('DIRECTION UNDEFINED' in s for s in m.output))
        self.assertFalse(any('DIRECTION DEG CCW' in s for s in m.output))

    def test_capacity_and_delete_shifts(self):
        menus=['YES START'];inputs=[]
        for i in range(20):
            menus+=['ADD VECTOR','X / Y'];inputs += [str(i),'0']
        menus+=['ADD VECTOR','VECTORS','DELETE','YES','MAIN MENU','QUIT']
        m=Machine(menus,inputs);m.run('VECTORCE')
        self.assertEqual(m.v['N'],19)
        self.assertEqual([r[0] for r in m.m[:19]],list(range(1,20)))

    def test_labels_and_calls(self):
        for path in (ROOT/'src').glob('*.txt'):
            lines=path.read_text(encoding="utf-8").splitlines()
            labels=[s[4:] for s in lines if s.startswith('Lbl ')]
            self.assertEqual(len(labels),len(set(labels)),path.name)
            for label in labels:self.assertLessEqual(len(label),2)
            for s in lines:
                if s.startswith('Goto '):self.assertIn(s[5:],labels)
                if s.startswith('prgm'):self.assertTrue((ROOT/'src'/f'{s[4:]}.txt').exists())

if __name__=='__main__': unittest.main()
