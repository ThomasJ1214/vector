"""Boundary, randomized, workflow, layout and rendering-command regression checks."""
import math
import random
import unittest
from basic_harness import Machine, ROOT

class Scenarios(unittest.TestCase):
    def entry(self,menus=(),inputs=(),angle='Degree'):
        m=Machine(['YES START',*menus,'QUIT'],map(str,inputs),initial_angle=angle)
        m.run('VECTORCE');self.assertFalse(m.menus);self.assertFalse(m.inputs);return m

    def test_random_cartesian_reference(self):
        rng=random.Random(84)
        for _ in range(600):
            x,y=[rng.uniform(-1,1)*10**rng.randint(-18,9) for _ in range(2)]
            m=Machine();m.v.update(A=x,B=y);m.run('VQMATH')
            self.assertTrue(math.isclose(m.v['R'],math.hypot(x,y),rel_tol=2e-15))
            expected=math.degrees(math.atan2(y,x))%360
            self.assertLess(abs(((m.v['T']-expected+180)%360)-180),1e-10)

    def test_standard_angle_wrap_boundaries(self):
        for a in [-1000000000,-720,-450,-360,-270,-180,-90,0,90,180,270,360,450,720,1000000000]:
            m=self.entry(['ADD VECTOR','MAG / ANGLE','STANDARD CCW +X'],[24,a])
            self.assertEqual(m.m[0][3],a%360)
            self.assertTrue(math.isclose(m.m[0][0],24*math.cos(math.radians(a%360)),abs_tol=1e-12))
            self.assertTrue(math.isclose(m.m[0][1],24*math.sin(math.radians(a%360)),abs_tol=1e-12))

    def test_compass_endpoints_and_rejected_angles(self):
        options=[('NORTH','EAST OF NORTH',90,-1),('NORTH','WEST OF NORTH',90,1),('SOUTH','EAST OF SOUTH',270,1),('SOUTH','WEST OF SOUTH',270,-1),('EAST','NORTH OF EAST',0,1),('EAST','SOUTH OF EAST',0,-1),('WEST','NORTH OF WEST',180,-1),('WEST','SOUTH OF WEST',180,1)]
        for axis,phrase,base,sign in options:
            for a in [0,90]:
                m=self.entry(['ADD VECTOR','MAG / ANGLE','COMPASS WORDS',axis,phrase],[24,-1,91,a])
                self.assertEqual(m.m[0][3],(base+sign*a)%360)

    def test_negative_magnitude_retry(self):
        m=self.entry(['ADD VECTOR','MAG / ANGLE','STANDARD CCW +X'],[-2,5,90])
        self.assertEqual(m.m[0][:2],[0,5])

    def test_cancel_every_input_and_direction_menu(self):
        cases=[(['ADD VECTOR','CANCEL'],[]),(['ADD VECTOR','X / Y'],['Q']),(['ADD VECTOR','X / Y'],[3,'Q']),(['ADD VECTOR','MAG / ANGLE'],['Q']),(['ADD VECTOR','MAG / ANGLE','CANCEL'],[24]),(['ADD VECTOR','MAG / ANGLE','STANDARD CCW +X'],[24,'Q']),(['ADD VECTOR','MAG / ANGLE','COMPASS WORDS'],[24,'Q']),(['ADD VECTOR','MAG / ANGLE','COMPASS WORDS','CANCEL'],[24,30]),(['ADD VECTOR','MAG / ANGLE','COMPASS WORDS','NORTH','CANCEL'],[24,30])]
        for menus,inputs in cases:
            with self.subTest(menus=menus):self.assertEqual(self.entry(menus,inputs).v['N'],0)

    def test_startup_decline_preserves_matrix_and_angle(self):
        for angle in ['Degree','Radian']:
            m=Machine(['CANCEL'],initial_angle=angle);m.m[0][0]=984;m.run('VECTORCE')
            self.assertEqual(m.m[0][0],984);self.assertEqual(m.angle,angle)

    def test_normal_exit_restores_angle(self):
        self.assertEqual(self.entry(angle='Radian').angle,'Radian')
        self.assertEqual(self.entry(angle='Degree').angle,'Degree')

    def test_list_wrap_zero_and_declined_delete(self):
        m=self.entry(['ADD VECTOR','X / Y','LIST / EDIT','NEXT','PREVIOUS','DELETE','NO','MAIN MENU'],[0,0])
        self.assertEqual(m.v['N'],1);self.assertEqual(m.v['I'],1)
        self.assertTrue(any('UNDEFINED' in s for s in m.output))

    def test_edit_switches_representation(self):
        m=self.entry(['ADD VECTOR','X / Y','LIST / EDIT','EDIT','MAG / ANGLE','COMPASS WORDS','NORTH','EAST OF NORTH'],[3,4,24,30])
        self.assertEqual(m.v['N'],1);self.assertEqual(m.m[0][4],1);self.assertAlmostEqual(m.m[0][0],12)

    def test_empty_paths_controls(self):
        self.entry(['LIST / EDIT','RESULT / WORK','GRAPHS','CONTROLS'])

    def test_numeric_recovery_long_chain(self):
        invalid=['',' ','-','⁻','.','-.','..','⁻.','1.2.3','+1','1e3','1/2','(3)','QX','0'*19,'1000000000.1','0.0000000009']*5
        m=Machine(inputs=[*invalid,'-0.000000001']);m.run('VQNUM')
        self.assertEqual(m.v['F'],1);self.assertTrue(math.isclose(m.v['V'],-1e-9))
        self.assertFalse(m.inputs)

    def test_graph_bounds_equal_scale_and_finite_primitives(self):
        datasets=[[(0,0)],[(3,0),(0,4)],[(-3,-4)],[(1e9,1e9),(-1e9,-1e9)],[(1e-9,-1e-9)],[(1e9,0),(1e-9,1e-9)]]
        for vectors in datasets:
            for mode in [1,2,3,4]:
                m=Machine(keys=[26]*len(vectors)+[45] if mode==4 else [45]);m.v.update(N=len(vectors),G=mode,L=1)
                for i,(x,y) in enumerate(vectors):m.m[i][:5]=[x,y,math.hypot(x,y),0,2]
                m.run('VQGRAPH');v=m.v
                self.assertTrue(math.isclose((v['Xmax']-v['Xmin'])/264,(v['Ymax']-v['Ymin'])/164))
                for command in m.graph:
                    if command[0]=='Line':
                        _,x1,y1,x2,y2,color=command
                        for x,y in [(x1,y1),(x2,y2)]:
                            self.assertLessEqual(v['Xmin']-1e-10*max(1,v['S']),x)
                            self.assertGreaterEqual(v['Xmax']+1e-10*max(1,v['S']),x)
                            self.assertLessEqual(v['Ymin']-1e-10*max(1,v['S']),y)
                            self.assertGreaterEqual(v['Ymax']+1e-10*max(1,v['S']),y)

    def test_triangle_rescales_independently(self):
        m=Machine(keys=[45]);m.v.update(N=2,G=3,L=2)
        m.m[0][:3]=[1e9,0,1e9];m.m[1][:3]=[0,1e-9,1e-9]
        m.run('VQGRAPH');self.assertTrue(math.isclose(m.v['S'],1.75e-9))

    def test_step_limits_and_irrelevant_keys(self):
        m=Machine(keys=[24,24,9,26,26,26,105,24,24,24,45]);m.v.update(N=2,G=4,L=0)
        m.m[0][:3]=[3,0,3];m.m[1][:3]=[0,4,4];m.run('VQGRAPH')
        self.assertEqual(m.v['M'],0);self.assertFalse(m.keys)

    def test_back_from_every_work_page(self):
        for l,pages in [(0,8),(1,8)]:
            for back in range(pages):
                m=Machine(keys=[105]*back+[45]);m.v.update(N=1,L=l)
                m.m[0][:5]=[-3,4,5,126.869897645844,2];m.run('VQWORK')
                self.assertFalse(m.keys);self.assertFalse(m.menus)

    def test_menu_shape_and_home_text_fit(self):
        import re
        for src in (ROOT/'src').glob('*.txt'):
            for line in src.read_text(encoding="utf-8").splitlines():
                if line.startswith('Menu('):
                    args=Machine.split(line[5:-1]);self.assertLessEqual((len(args)-1)//2,7)
                match=re.fullmatch(r'Output\((\d+),(\d+),"([^"]*)"\)',line)
                if match:self.assertLessEqual(int(match[2])+len(match[3])-1,26,line)
