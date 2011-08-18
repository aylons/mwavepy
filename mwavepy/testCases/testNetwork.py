import unittest
import mwavepy as mv



		
class NetworkTestCase(unittest.TestCase):
	'''
	Network class operation test case. 
	
	 As tested by lihan in ADS the following is true:
		test 3 == test1 ** test2
	
	'''
	def setUp(self):
		'''
		this also tests the ability to read touchstone files
		without an error
		'''
		self.ntwk1 =mv.Network('ntwk1.s2p')
		self.ntwk2 =mv.Network('ntwk2.s2p')
		self.ntwk3 =mv.Network('ntwk3.s2p')
	
	
	def test_open_saved_touchstone(self):
		self.ntwk1.write_touchstone('ntwk1Saved')
		ntwk1Saved = mv.Network('ntwk1Saved.s2p')
		self.assertEqual(self.ntwk1, ntwk1Saved)
		
	def test_cascade(self):
		self.assertEqual(self.ntwk1**self.ntwk2, self.ntwk3)
		
	def test_connect(self):
		self.assertEqual(mv.connect(self.ntwk1,1,self.ntwk2,0), \
			self.ntwk3)

	def test_de_embed_by_inv(self):
		self.assertEqual(self.ntwk1.inv**self.ntwk3,self.ntwk2)
		self.assertEqual(self.ntwk3**self.ntwk2.inv,self.ntwk1)

	def test_plot_one_port_db(self):
		self.ntwk1.plot_s_db(0,0)
	def test_plot_one_port_deg(self):
		self.ntwk1.plot_s_deg(0,0)
	def test_plot_one_port_smith(self):
		self.ntwk1.plot_s_smith(0,0)
	
	def test_plot_two_port_db(self):
		self.ntwk1.plot_s_db()
	def test_plot_two_port_deg(self):
		self.ntwk1.plot_s_deg()
	def test_plot_two_port_smith(self):
		self.ntwk1.plot_s_smith()
		

suite = unittest.TestLoader().loadTestsFromTestCase(NetworkTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
