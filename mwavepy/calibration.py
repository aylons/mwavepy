
'''
#       calibration.py
#       
#       
#       Copyright 2010 alex arsenovic <arsenovic@virginia.edu>
#       
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later versionpy.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
'''
class Calibration(object):
	
	calibration_algorithm_dict={'one port': one_port}
	
	def __init__(self,f , type, ideals, measured, **kwargs):
		self.f = f
		self.ideals = ideals
		self.measured = measured
		# a dictionary holding key word arguments to pass to whatever
		# calibration function we are going to call
		self.kwargs = kwargs
		self.type = type
	
	@property
	def type (self):
		return self._type
	@type.setter
	def type(self, input):
		if input not in self.calibration_algorithm_dict.keys():
			raise ValueError('incorrect calibration type')
	
	@property	
	def coefs(self):
		'''
		coefs: a dictionary holding the calibration coefficients
		'''
		
		try:
			return self._coefs
		except(AttributeError):
			self.run()
			return self._coefs
	
	def run(self):
		calibration_algorithm_dict[self.type](self.**kwargs)

def one_port(measured, ideals):
	
	'''
	standard algorithm for a one port calibration. If more than three 
	standards are supplied then a least square algorithm is applied.
	 
	takes: 
		measured - list of measured reflection coefficients. can be 
			lists of either a kxnxn numpy.ndarray, representing a 
			s-matrix or list of  1-port mwavepy.ntwk types. 
		ideals - list of assumed reflection coefficients. can be 
			lists of either a kxnxn numpy.ndarray, representing a 
			s-matrix or list of  1-port mwavepy.ntwk types. 
	
	returns:
		(abc, residues) - a tuple. abc is a Nx3 ndarray containing the
			complex calibrations coefficients,where N is the number 
			of frequency points in the standards that where given.
			
			abc: 
			the components of abc are 
				a = abc[:,0] = e01*e10 - e00*e11
				b = abc[:,1] = e00
				c = abc[:,2] = e11
			
			residuals: a matrix of residuals from the least squared 
				calculation. see numpy.linalg.lstsq() for more info	
	'''
	#make  copies so list entities are not changed, when we typecast 
	mList = copy(measured)
	iList = copy(ideals)
	
	numStds = len(mList)# find number of standards given, for dimensions
	numCoefs=3
	# try to access s-parameters, in case its a ntwk type, other wise 
	# just keep on rollin 
	try:
		for k in range(numStds):
			mList[k] = mList[k].s.reshape((-1,1))
			iList[k] = iList[k].s.reshape((-1,1))
	except:
		pass	
	
	# ASSERT: mList and aList are now kx1x1 matrices, where k in frequency
	fLength = len(mList[0])
	
	#initialize outputs 
	abc = npy.zeros(shape=(fLength,numCoefs),dtype=complex) 
	residuals = npy.zeros(shape=(fLength,numStds-numCoefs),dtype=complex) 
	
	# loop through frequencies and form m, a vectors and 
	# the matrix M. where M = 	i1, 1, i1*m1 
	#							i2, 1, i2*m2
	#									...etc
	for f in range(fLength):
		#create  m, i, and 1 vectors
		one = npy.ones(shape=(numStds,1))
		m = array([ mList[k][f] for k in range(numStds)]).reshape(-1,1)# m-vector at f
		i = array([ iList[k][f] for k in range(numStds)]).reshape(-1,1)# i-vector at f			
		
		# construct the matrix 
		Q = npy.hstack([i, one, i*m])
		# calculate least squares
		abcTmp, residualsTmp = npy.linalg.lstsq(Q,m)[0:2]
		if len (residualsTmp )==0:
			raise ValueError( 'matrix has singular values, check standards')
			
		abc[f,:] = abcTmp.flatten()
		residuals[f,:] = residualsTmp
		
	return abc, residuals