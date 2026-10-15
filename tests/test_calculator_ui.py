"""Native TI-BASIC menu and screen regression tests, not browser tests."""
import unittest
from basic_harness import Machine

class CalculatorUI(unittest.TestCase):
    def test_splash_initializes_an_empty_session_after_consent(self):
        m=Machine(['YES START','QUIT'])
        m.m[0][:5]=[3,4,5,53,2]
        m.v['N']=1
        m.run('VECTORCE')
        self.assertEqual(m.v['N'],0)
        self.assertTrue(all(value==0 for row in m.m for value in row))
        splash=m.paused_graphs[1]
        self.assertTrue(any(cmd[0]=='Text' and cmd[2]==-1 and cmd[-1]=='VECTRA CE' for cmd in splash))
        self.assertTrue(any(cmd[0]=='Text' and cmd[-1]=='READY / ENTER TO BEGIN' for cmd in splash))

    def test_cancel_before_splash_keeps_workspace_and_graph_untouched(self):
        m=Machine(['CANCEL'])
        m.m[0][0]=123
        m.run('VECTORCE')
        self.assertEqual(m.m[0][0],123)
        self.assertEqual(m.graph,[])
        self.assertEqual(m.v['Xmax'],0)

    def run_app(self,tail,keys=(),xy=(3,4)):
        m=Machine(['YES START','ADD VECTOR','X / Y',*tail,'QUIT'],map(str,xy),keys)
        m.run('VECTORCE')
        self.assertFalse(m.menus);self.assertFalse(m.inputs);self.assertFalse(m.keys)
        return m

    def has(self,m,text):return any(text in line for line in m.output)

    def test_results_are_immediate_without_work_pages(self):
        m=self.run_app(['RESULTS'],[45])
        self.assertEqual((m.v['X'],m.v['Y'],m.v['R']),(3,4,5))
        self.assertTrue(self.has(m,'RESULTANT'))
        self.assertFalse(self.has(m,'MAGNITUDE / WORK'))
        self.assertTrue(any(('Output',6.,9.,5.) in page for page in m.pages))

    def test_main_work_short_route(self):
        m=self.run_app(['SHOW WORK','MAG / DIRECTION','BACK'],[105]*4)
        self.assertTrue(self.has(m,'MAGNITUDE / WORK'))
        self.assertTrue(self.has(m,'ANGLE / SUBSTITUTION'))
        self.assertTrue(self.has(m,'DIRECTION DEG CCW'))
        self.assertFalse(self.has(m,'VECTOR COMPONENTS'))

    def test_component_sums_return_to_work_topics(self):
        m=self.run_app(['SHOW WORK','COMPONENT SUMS','BACK'],[105]*4)
        self.assertTrue(self.has(m,'RUNNING SUM / X'))
        self.assertTrue(self.has(m,'RUNNING SUM / Y'))
        self.assertFalse(self.has(m,'MAGNITUDE / WORK'))

    def test_result_one_opens_work_and_returns_to_answer(self):
        m=self.run_app(['RESULTS','MAG / DIRECTION','BACK'],[92,*([105]*4),45])
        self.assertTrue(self.has(m,'MAGNITUDE / WORK'))
        self.assertEqual(sum('Output(1,1,"RESULTANT")'==line for line in m.output),2)

    def test_result_two_opens_triangle_directly(self):
        m=self.run_app(['RESULTS'],[93,45,45])
        self.assertTrue(self.has(m,'TRIANGLE'))
        self.assertFalse(self.has(m,'MAGNITUDE / WORK'))

    def test_individual_vector_triangle_needs_no_work_pages(self):
        m=self.run_app(['VECTORS','TRIANGLE','MAIN MENU'],[45])
        self.assertEqual(m.v['L'],1)
        self.assertTrue(self.has(m,'TRIANGLE'))
        self.assertFalse(self.has(m,'MAGNITUDE / WORK'))

    def test_graph_triangle_picker_opens_drawing_directly(self):
        m=Machine(['YES START','ADD VECTOR','X / Y','GRAPHS','INSPECT TRIANGLE','BACK','QUIT'],['3','4','1'],[45])
        m.run('VECTORCE');self.assertFalse(m.menus);self.assertFalse(m.inputs);self.assertFalse(m.keys)
        self.assertTrue(self.has(m,'TRIANGLE'));self.assertFalse(self.has(m,'MAGNITUDE / WORK'))

    def test_zero_answer_has_no_placeholder_direction(self):
        m=self.run_app(['RESULTS'],[45],xy=(0,0))
        self.assertTrue(any(('Output',7.,9.,'UNDEFINED') in page for page in m.pages))

    def test_work_can_be_reopened_and_canceled(self):
        m=self.run_app(['SHOW WORK','MAG / DIRECTION','VIEW AGAIN','COMPONENT SUMS'],[105]*4+[45])
        self.assertTrue(self.has(m,'MAGNITUDE / WORK'))
        self.assertTrue(self.has(m,'RESULTANT / COMPONENTS'))

    def test_large_list_can_view_result_work_without_all_terms(self):
        m=Machine(['MAG / DIRECTION','BACK'],keys=[105]*4);m.v.update(N=20,L=0)
        for i in range(20):m.m[i][:5]=[3,4,5,53.13010235415598,2]
        m.run('VQWORK');self.assertFalse(m.keys);self.assertFalse(m.menus)
        self.assertEqual(m.v['R'],100)
        self.assertFalse(self.has(m,'VECTOR COMPONENTS'))

if __name__=='__main__':unittest.main()
