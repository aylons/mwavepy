
#       network.py
#       
#       
#       Copyright 2010 alex arsenovic <arsenovic@virginia.edu>
#       Copyright 2010 lihan chen 
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
.. module:: mwavepy.network
========================================
network (:mod:`mwavepy.network`)
========================================


Provides a n-port network class and associated functions.  

Most of the functionality in this module is provided as methods and
properties of the :class:`Network` Class. 


Network Class
===============

.. autosummary::
   :toctree: generated/

   Network 
	

Functions On Networks
======================

.. autosummary::
   :toctree: generated/

   connect 
   innerconnect
   cascade
   de_embed
   average
   one_port_2_two_port

Supporting Functions 
=====================

.. autosummary::
   :toctree: generated/

   connect_s
   innerconnect_s
   s2t
   t2s
   inv
   flip
   
Misc Functions 
=====================
.. autosummary::
   :toctree: generated/
   
	impedance_mismatch
	load_all_touchstones
	write_dict_of_networks
	csv_2_touchstone
'''
from copy import deepcopy as copy
from copy import deepcopy
import os

import numpy as npy
import pylab as plb 
from scipy import stats		# for Network.add_noise_* 
from scipy.interpolate import interp1d # for Network.interpolate()

import  mathFunctions as mf
import touchstone
from frequency import Frequency
from plotting import smith
from tlineFunctions import zl_2_Gamma0

class Network(object):
	'''

	A n-port microwave network.
	
	A n-port microwave networks is defined by three quantities,
	 * scattering parameter matrix (s-matrix)
	 * port characteristic impedance matrix 
	 * frequency information
	
	The :class:`Network` class stores these data structures internally 
	in the form of complex numpy.ndarray's. These arrays are not 
	interfaced directly but instead through the use of the properties:

	=====================  =============================================
	Property               Quantity
	=====================  =============================================	
	:attr:`s`              scattering parameter matrix
	:attr:`z0`             characteristic impedancematrix
	:attr:`f`              frequency vector 
	=====================  =============================================	
	
	Individual components of the s-matrix are accesable through
	properties as well. These also return numpy.ndarray's.
	
	=====================  =============================================
	Property               Quantitiy
	=====================  =============================================	
	:attr:`s_re`           real part of the s-matrix
	:attr:`s_im`           imaginary part of the s-matrix
	:attr:`s_mag`          magnitude of the s-matrix
	:attr:`s_db`           magnitude in log scale of the s-matrix
	:attr:`s_deg`          phase of the s-matrix in degrees
	=====================  =============================================
	
	The following :class:`Network` operators are available:
	
	=====================  =============================================
	Operator               Function	
	=====================  =============================================	
	\+                     element-wise addition of the s-matrix
	\-                     element-wise difference of the s-matrix
	\*                     element-wise multiplication of the s-matrix
	\/                     element-wise division of the s-matrix
	\*\*                     cascading (only for 2-ports) 
	\//                    de-embedding (for 2-ports, see :attr:`inv`)
	=====================  =============================================	

	Different components of the :class:`Network` can be visualized
	through various plotting methods. These methods can be used to plot
	individual elements of the s-matrix or all at once. For more info
	about plotting see the :doc:`../tutorials/plotting` tutorial.
	
	=====================  =============================================
	Method                 Function	
	=====================  =============================================	
	:func:`plot_s_smith`   plot complex s-parameters on smith chart
	:func:`plot_s_re`      plot real part of s-parameters vs frequency
	:func:`plot_s_im`      plot imaginary part of s-parameters vs frequency
	:func:`plot_s_mag`     plot magnitude of s-parameters vs frequency
	:func:`plot_s_db`      plot magnitude (in dB) of s-parameters vs frequency
	:func:`plot_s_deg`     plot phase of s-parameters (in degrees) vs frequency
	=====================  =============================================	
	
	Generally, :class:`Network`  objects are created from touchstone 
	files upon initializtion  (see :func:`__init__`), or are created
	from a :class:`~media.media.Media` object. :class:`Network`  objects
	can be saved to disk in the form of touchstone files with the 
	:func:`write_touchstone` method.
	
	An exhaustive list of :class:`Network` Methods and Properties
	(Attributes) are given below
	'''
	global ALMOST_ZER0
	ALMOST_ZER0=1e-6 # used for testing s-parameter equivalencee

	## CONSTRUCTOR
	def __init__(self, touchstone_file = None, name = None ):
		'''
		constructor.
		
		Contructs a Network, and optionally populates the s-matrix 
		and frequency information from touchstone file.
		
		Parameters
		------------
		file: string
			if given will load information from touchstone file,optional
		name: string
			name of this network, optional 
		'''
		# although meaningless untill set with real values, this
		# needs this to exist for dependent properties
		#self.frequency = Frequency(0,0,0)
		
		if touchstone_file is not None:
			self.read_touchstone(touchstone_file)
			if name is not None:
				self.name = name
		
		else:
			self.name = name
			#self.s = None
			#self.z0 = 50 
		
		#convenience 
		#self.nports = self.number_of_ports
		

	## OPERATORS
	def __pow__(self,other):
		'''
		cascade this network with another network
		
		port 1 of this network is connected to port 0 or the other 
		network
		'''
		return connect(self,1,other,0)

	def __floordiv__(self,other):
		'''
		de-embeding another network[s], from this network

		See Also
		----------
		inv : inverse s-parameters
		'''
		try: 	
			# if they passed 1 ntwks and a tuple of ntwks, 
			# then deEmbed like A.inv*C*B.inv
			b = other[0]
			c = other[1]
			result =  copy (self)
			result.s =  (b.inv**self**c.inv).s
			#flip(de_embed( flip(de_embed(c.s,self.s)),b.s))
			return result
		except TypeError:
			pass
				
		if other.number_of_ports == 2:
			result = copy(self)
			result.s = (other.inv**self).s
			#de_embed(self.s,other.s)
			return result
		else:
			raise IndexError('Incorrect number of ports.')

	def __mul__(self,a):
		'''
		element-wise complex multiplication  of s-matrix
		'''
		result = copy(self)
		result.s = result.s * a.s
		return result

	def __add__(self,other):
		'''
		element-wise addition of s-matrix
		'''
		result = copy(self)
		result.s = result.s + other.s
		return result
		
	def __sub__(self,other):
		'''
		element-wise subtraction of s-matrix
		'''
		result = copy(self)
		result.s = result.s - other.s
		return result

	def __div__(self,other):
		'''
		element-wise division  of s-matrix
		'''
		if other.number_of_ports != self.number_of_ports:
			raise IndexError('Networks must have same number of ports.')
		else:
			result = copy(self)
			try:
				result.name = self.name+'/'+other.name
			except TypeError:
				pass
			result.s =(self.s/ other.s)
			
			return result

	def __eq__(self,other):
		if npy.mean(npy.abs(self.s - other.s)) < ALMOST_ZER0:
			return True
		else:
			return False
	def __ne__(self,other):
		return (not self.__eq__(other))
		
	def __getitem__(self,key):
		'''
		returns a Network object at a given single frequency
		'''
		a= self.z0# hack to force getter for z0 to re-shape it
		output = deepcopy(self)
		output.s = output.s[key,:,:]
		output.z0 = output.z0[key,:]
		output.frequency.f = npy.array(output.frequency.f[key]).reshape(-1)
		
		return output
	
	def __str__(self):
		'''
		'''
		f=self.frequency
		output =  \
			'%i-Port Network.  %i-%i %s.  %i points. z0='% \
			(self.number_of_ports,f.f_scaled[0],f.f_scaled[-1],f.unit, f.npoints)+str(self.z0[0,:])

		return output
	def __repr__(self):
		return self.__str__()
	
	## PRIMARY PROPERTIES
	# s-parameter matrix
	@property
	def s(self):
		'''
		the scattering parameter matrix.
		
		s-matrix is a 3 dimensional numpy.ndarray which has shape 
		`fxnxn`, where `f` is frequency axis and `n` is number of ports
		
		Returns
		---------
		s : complex numpy.ndarry of shape `fxnxn`
			the scattering parameter matrix.
		'''
		return self._s
	
	@s.setter
	def s(self, s):
		'''
		the input s-matrix should be of shape fxnxn, 
		where f is frequency axis and n is number of ports
		'''
		s_shape= npy.shape(s)
		if len(s_shape) <3:
			if len(s_shape)==2:
				# reshape to kx1x1, this simplifies indexing in function
				s = npy.reshape(s,(-1,s_shape[0],s_shape[0]))
			elif len(s_shape)==1:
				 s = npy.reshape(s,(-1,1,1))
		self._s = s
		#s.squeeze()
	@property
	def y(self):
		'''
		needs work
		'''
		if self.number_of_ports == 1:
			return (1-self.s)/(1+self.s)
		else:
			raise(NotImplementedError)
	
	# t-parameters
	@property
	def t(self):
		'''
		t-parameters, aka scattering transfer parameters
		
		this is also known or the wave cascading matrix, and is only 
		defined for a 2-port Network
		
		
		Returns
		--------
		t : complex numpy.ndarry of shape `fxnxn`
			t-parameters, aka scattering transfer parameters
			
		
		'''
		return s2t(self.s)
	@property
	def inv(self):
		'''
		a :class:`Network` object with 'inverse' s-parameters.
		
		This is used for de-embeding. It is defined so that the inverse
		of a Network cascaded with itself is unity.
		
		Returns
		---------
		inv : a :class:`Network` object
			a :class:`Network` object with 'inverse' s-parameters.
		
		See Also
		----------
			inv : function which implements the inverse s-matrix
		'''
		if self.number_of_ports <2:
			raise(TypeError('One-Port Networks dont have inverses'))
		out = copy(self)
		out.s = inv(self.s)
		return out
		
	# frequency information
	@property
	def frequency(self):
		'''
		frequency information for the network. 
		
		This property is a :class:`~mwavepy.frequency.Frequency` object.
		It holds the frequency vector, as well frequency unit, and 
		provides other properties related to frequency information, such 
		as start, stop, etc.
		
		Returns
		--------
		frequency :  :class:`~mwavepy.frequency.Frequency` object
			frequency information for the network. 
	
		
		See Also
		---------
			f : property holding frequency vector in Hz
			change_frequency : updates frequency property, and 
				interpolates s-parameters if needed
			interpolate : interpolate function based on new frequency 
				info
		'''
		try:
			return self._frequency
		except (AttributeError):
			self._frequency = Frequency(0,0,0)
			return self._frequency
	@frequency.setter
	def frequency(self, new_frequency):
		'''
		takes a Frequency object, see  frequency.py
		'''
		self._frequency= copy(new_frequency)

	
	@property
	def f(self):
		''' 
		the frequency vector for the network, in Hz. 
		
		Returns
		--------
		f : numpy.ndarray 
			frequency vector in Hz
		'''
		return self.frequency.f
		
	@f.setter
	def f(self,f):
		tmpUnit = self.frequency.unit
		self._frequency  = Frequency(f[0],f[-1],len(f),'hz')
		self._frequency.unit = tmpUnit
	

	
	# characteristic impedance
	@property
	def z0(self):
		'''
		the characteristic impedance[s] of the network ports.
		
		This property stores the  characteristic impedance of each port
		of the network. Because it is possible that each port has
		a different characteristic impedance, that is a function of 
		frequency, `z0` is stored internally as a `fxn` array.
		
		However because frequenty `z0` is simple (like 50ohm),it can 
		be set with just number as well. 
		
		Returns
		--------
		z0 : numpy.ndarray of shape fxn
			characteristic impedance for network
		
		'''
		# i hate this function
		# it was written this way because id like to allow the user to
		# set the z0 before the s-parameters are set. However, in this 
		# case we dont know how to re-shape the z0 to fxn. to solve this
		# i attempt to do the re-shaping when z0 is accessed, not when 
		# it is set. this is what makes this function confusing. 
		try:
			if len(npy.shape(self._z0)) ==0:
				try:
					#try and re-shape z0 to match s
					self._z0=self._z0*npy.ones(self.s.shape[:-1])
				except(AttributeError):
					print ('Warning: Network has improper \'z0\' shape.')
					#they have yet to set s .

			elif len(npy.shape(self._z0)) ==1:
				try:
					if len(self._z0) == self.frequency.npoints:
						# this z0 is frequency dependent but no port dependent
						self._z0 = \
							npy.repeat(npy.reshape(self._z0,(-1,1)),self.number_of_ports,1)

					elif len(self._z0) == self.number_of_ports:
						# this z0 is port dependent but not frequency dependent
						self._z0 = self._z0*npy.ones(\
							(self.frequency.npoints,self.number_of_ports))
						
					else:
						raise(IndexError('z0 has bad shape'))
						
				except(AttributeError):
					# there is no self.frequency, or self.number_of_ports
					raise(AttributeError('Error: i cant reshape z0 through inspection. you must provide correctly shaped z0, or s-matrix first.'))
			
			return self._z0
		
		except(AttributeError):
			print 'Warning: z0 is undefined. Defaulting to 50.'
			self.z0=50
			return self.z0 #this is not an error, its a recursive call
		
	@z0.setter
	def z0(self, z0):
		'''z0=npy.array(z0)
		if len(z0.shape) < 2:
			try:
				#try and re-shape z0 to match s
				z0=z0*npy.ones(self.s.shape[:-1])
			except(AttributeError):
				print ('Warning: you should store a Network\'s \'s\' matrix before its \'z0\'')
				#they have yet to set s .
				pass
		'''
		self._z0 = z0
	
## SECONDARY PROPERTIES

	# s-parameters convinience properties	
	@property
	def s_re(self):
		'''
		real part of the s-parameters.
		
		Returns
		--------
		s_re : numpy.ndarray of shape fxnxn
		
		'''
		return npy.real(self.s)
	
	@property
	def s_im(self):
		'''
		imaginary part of the s-parameters.
		
		Returns
		--------
		s_im : numpy.ndarray of shape fxnxn
		'''
		return npy.imag(self.s)
		
	@property
	def s_mag(self):
		'''
		magnitude of the s-parameters.
		
		Returns
		--------
		s_mag : numpy.ndarray of shape fxnxn
		'''
		return mf.complex_2_magnitude(self.s)
	@property
	def s_abs(self):
		'''
		see :attr:`s_mag`
		'''
		return self.s_mag
	
	@property
	def s_db(self):
		'''
		magnitude of the s-parameters, in dB
		
		this is calculated by 
		
		.. math::
			
			20\cdot \log_{10}(|s|)
		
		Returns
		--------
		s_db : numpy.ndarray of shape fxnxn
		
		
		
		'''
		return mf.complex_2_db(self.s)
		
	@property
	def s_deg(self):
		'''
		phase of the s-parameters, in degrees
		
		Returns
		--------
		s_deg : numpy.ndarray of shape fxnxn
		'''
		return mf.complex_2_degree(self.s)
	
	@property
	def s_angle(self):
		'''
		see :attr:`s_deg`
		'''
		return self.s_deg	
	@property
	def s_rad(self):
		'''
		phase of the s-parameters, in radians.
		
		Returns
		--------
		s_rad : numpy.ndarray of shape fxnxn
		'''
		return mf.complex_2_radian(self.s)
	
	@property
	def s_deg_unwrap(self):
		'''
		unwrapped phase of the s-paramerts, in degrees
		
		Returns
		--------
		s_deg_unwrap : numpy.ndarray of shape fxnxn
		
		
		'''
		return mf.radian_2_degree(self.s_rad_unwrap)
	
	@property
	def s_rad_unwrap(self):
		'''
		unwrapped phase of the s-parameters, in radians.
		
		Returns
		--------
		s_rad_unwrap : numpy.ndarray of shape fxnxn
		
		'''
		return mf.unwrap_rad(self.s_rad)
		
	@property
	def s_quad(self):
		'''
		see :attr:`s_arcl`
		'''
		return self.s_arcl
		
	@property
	def s_arcl(self):
		'''
		the arc-length of the s-parameters, given by  
			= s_rad * s_mag 
		
		used in calculating differences in phase, but in units of distance
		'''
		return self.s_rad * self.s_mag
	
	@property
	def s_arcl_unwrap(self):
		'''
		the unwrapped arc-length of the s-parameters, given by  
			= s_rad_unwrap * s_mag 
		
		used in calculating differences in phase, but in units of distance
		'''
		return self.s_rad_unwrap * self.s_mag
	
	@property
	def s11(self):
		result = Network()
		result.frequency = self.frequency
		result.s = self.s[:,0,0]
		return result
	@property
	def s22(self):
		if self.number_of_ports < 2:
			raise(IndexError('this network doesn have enough ports'))
		result = Network()
		result.frequency = self.frequency
		result.s = self.s[:,1,1]
		return result
	@property
	def s21(self):
		if self.number_of_ports < 2:
			raise(IndexError('this network doesn have enough ports'))
		result = Network()
		result.frequency = self.frequency
		result.s = self.s[:,1,0]
		return result
	@property
	def s12(self):
		if self.number_of_ports < 2:
			raise(IndexError('this network doesn have enough ports'))
		result = Network()
		result.frequency = self.frequency
		result.s = self.s[:,0,1]
		return result
	@property
	def number_of_ports(self):
		'''
		the number of ports the network has.
		'''
		return self.s.shape[1]
	@property
	def passivity(self):
		'''
		 passivity metric for a multi-port network. It returns
		a matrix who's diagonals are equal to the total power 
		received at all ports, normalized to the power at a single
		excitement  port.
		
		mathmatically, this is a test for unitary-ness of the 
		s-parameter matrix. 
		
		for two port this is 
			( |S11|^2 + |S21|^2, |S22|^2+|S12|^2)
		in general it is  
			S.H * S
		where H is conjugate transpose of S, and * is dot product
		
		note:
		see more at,
		http://en.wikipedia.org/wiki/Scattering_parameters#Lossless_networks
		'''
		if self.number_of_ports == 1:
			raise (ValueError('Doesnt exist for one ports'))
		
		pas_mat = copy(self.s)
		for f in range(len(self.s)):
			pas_mat[f,:,:] = npy.dot(self.s[f,:,:].conj().T, self.s[f,:,:])
		
		return pas_mat
	

	
## CLASS METHODS
	# touchstone file IO
	def read_touchstone(self, filename):
		'''
		loads  values from a touchstone file. 
		
		takes:
			filename - touchstone file name, string. 
		
		note: 
			ONLY 'S' FORMAT SUPORTED AT THE MOMENT 
			all work is tone in the touchstone class. 
		'''
		touchstoneFile = touchstone.touchstone(filename)
		
		if touchstoneFile.get_format().split()[1] != 's':
			raise NotImplementedError('only s-parameters supported for now.')
		
		
		self.f, self.s = touchstoneFile.get_sparameter_arrays() # note: freq in Hz
		self.z0 = float(touchstoneFile.resistance)
		self.frequency.unit = touchstoneFile.frequency_unit # for formatting plots
		self.name = os.path.basename( os.path.splitext(filename)[0])

	def write_touchstone(self, filename=None, dir = './'):
		'''
		write a touchstone file representing this network.  the only 
		format supported at the moment is :
			HZ S RI 
		
		takes: 
			filename: a string containing filename without 
				extension[None]. if 'None', then will use the network's 
				name. if this is empty, then throws an error.
			dir: the directory to save the file in. [string]. Defaults 
				to './'
			
		
		note:
			in the future could make possible use of the touchtone 
			class, but at the moment this would not provide any benefit 
			as it has not set_ functions. 
		'''
		if filename is None:
			if self.name is not None:
				filename= self.name
			else:
				raise ValueError('No filename given. Network must have a name, or you must provide a filename')
		
		extension = '.s%ip'%self.number_of_ports
		
		outputFile = open(dir+'/'+filename+extension,"w")
		
		# write header file. 
		# the '#'  line is NOT a comment it is essential and it must be 
		#exactly this format, to work
		# [HZ/KHZ/MHZ/GHZ] [S/Y/Z/G/H] [MA/DB/RI] [R n]
		outputFile.write('!Created with mwavepy.\n')
		outputFile.write('# ' + self.frequency.unit + ' S RI R ' + str(self.z0[0,0]) +" \n")
		
		#write comment line for users (optional)
		outputFile.write ("!freq\t")
		for n in range(self.number_of_ports):
			for m in range(self.number_of_ports):
				outputFile.write("Re" +'S'+`m+1`+ `n+1`+  "\tIm"+\
				'S'+`m+1`+ `n+1`+'\t')
		outputFile.write('\n')		
		
		# write out data, note: this could be done with matrix 
		#manipulations, but its more readable to me this way
		for f in range(len(self.f)):
			outputFile.write(str(self.frequency.f_scaled[f])+'\t')
			
			for n in range(self.number_of_ports):
				for m in range(self.number_of_ports):
					outputFile.write( str(npy.real(self.s[f,m,n])) + '\t'\
					 + str(npy.imag(self.s[f,m,n])) +'\t')
			
			outputFile.write('\n')
			outputFile.write('! Port Impedance\t' )
			for n in range(self.number_of_ports):
				outputFile.write('%.14f\t%.14f\t'%(self.z0[f,n].real, self.z0[f,n].imag))
			outputFile.write('\n')
		
		outputFile.close()


	# self-modifications
	def interpolate(self, new_frequency,**kwargs):
		'''
		calculates an interpolated network. defualt interpolation type
		is linear. see notes about other interpolation types

		takes:
			new_frequency:
			**kwargs: passed to scipy.interpolate.interp1d initializer.
				  
		returns:
			result: an interpolated Network

		note:
			usefule keyward for  scipy.interpolate.interp1d:
			 kind : str or int
				Specifies the kind of interpolation as a string ('linear',
				'nearest', 'zero', 'slinear', 'quadratic, 'cubic') or as an integer
				specifying the order of the spline interpolator to use.

			
		'''
		interpolation_s = interp1d(self.frequency.f,self.s,axis=0,**kwargs)
		interpolation_z0 = interp1d(self.frequency.f,self.z0,axis=0,**kwargs)
		result = deepcopy(self)
		result.frequency = new_frequency
		result.s = interpolation_s(new_frequency.f)
		result.z0 = interpolation_z0(new_frequency.f)
		return result

	def change_frequency(self, new_frequency, **kwargs):
		self.frequency.start = new_frequency.start
		self.frequency.stop = new_frequency.stop
		self = self.interpolate(new_frequency, **kwargs)
		
	def flip(self):
		'''
		swaps the ports of a two port 
		'''
		if self.number_of_ports == 2:
			self.s = flip(self.s)
		else:
			raise ValueError('you can only flip two-port Networks')


	# ploting

	def plot_vs_frequency_generic(self,attribute,y_label=None,\
		m=None,n=None, ax=None,show_legend=True,**kwargs):
		'''
		generic plotting function for plotting a Network's attribute
		vs frequency.
		

		takes:

		
		'''
		# get current axis if user doesnt supply and axis 
		if ax is None:
			ax = plb.gca()
		
		if m is None:
			M = range(self.number_of_ports)
		else:
			M = [m]
		if n is None:
			N = range(self.number_of_ports)
		else:
			N = [n]
		
		if 'label'  not in kwargs.keys():
			generate_label=True
		else:
			generate_label=False
		
		for m in M:
			for n in N:
				# set the legend label for this trace to the networks
				# name if it exists, and they didnt pass a name key in
				# the kwargs
				if generate_label: 
					if self.name is None:
						if plb.rcParams['text.usetex']:
							label_string = '$S_{'+repr(m+1) + \
								repr(n+1)+'}$'
						else:
							label_string = 'S'+repr(m+1) + repr(n+1)
					else:
						if plb.rcParams['text.usetex']:
							label_string = self.name+', $S_{'+repr(m+1)\
								+ repr(n+1)+'}$'
						else:
							label_string = self.name+', S'+repr(m+1) +\
								repr(n+1)
					kwargs['label'] = label_string
					
				# plot the desired attribute vs frequency 
				ax.plot(self.frequency.f_scaled, getattr(self,\
					attribute)[:,m,n], **kwargs)

		# label axis
		ax.set_xlabel('Frequency ['+ self.frequency.unit +']')
		ax.set_ylabel(y_label)
		ax.axis('tight')
		#draw legend
		if show_legend:
			ax.legend()
		plb.draw()
	def plot_polar_generic (self,attribute_r, attribute_theta,	m=0,n=0,\
		ax=None,show_legend=True,**kwargs):
		'''
		generic plotting function for plotting a Network's attribute
		in polar form
		

		takes:
			
		
		'''

		# get current axis if user doesnt supply and axis 
		if ax is None:
			ax = plb.gca(polar=True)
			
		# set the legend label for this trace to the networks name if it
		# exists, and they didnt pass a name key in the kwargs
		if 'label'  not in kwargs.keys(): 
			if self.name is None:
				if plb.rcParams['text.usetex']:
					label_string = '$S_{'+repr(m+1) + repr(n+1)+'}$'
				else:
					label_string = 'S'+repr(m+1) + repr(n+1)
			else:
				if plb.rcParams['text.usetex']:
					label_string = self.name+', $S_{'+repr(m+1) + \
						repr(n+1)+'}$'
				else:
					label_string = self.name+', S'+repr(m+1) + repr(n+1)

			kwargs['label'] = label_string
			
		#TODO: fix this to call from ax, if possible
		plb.polar(getattr(self, attribute_theta)[:,m,n],\
			getattr(self, attribute_r)[:,m,n],**kwargs)

		#draw legend
		if show_legend:
			plb.legend()	
		
	def plot_s_db(self,m=None, n=None, ax = None, show_legend=True,*args,**kwargs):
		'''
		plots the magnitude of the scattering parameters.
		
		plots indecies `m`, `n`, where `m` and `n` can be integers or 
		lists of integers.
		
		
		Parameters
		-----------
		m : int, optional
			first index
		n : int, optional
			second index
		ax : matplotlib.Axes object, optional
			axes to plot on. in case you want to update an existing 
			plot.
		show_legend : boolean, optional
			to turn legend show legend of not, optional
		*args : arguments, optional
			passed to the matplotlib.plot command
		**kwargs : keyword arguments, optional
			passed to the matplotlib.plot command
		
		
		See Also
		--------
		plot_vs_frequency_generic - generic plotting function
		
		
		Examples
		---------
		>>> myntwk.plot_s_db()
		>>> myntwk.plot_s_db(m=0,n=1,color='b', marker='x')
		'''
		self.plot_vs_frequency_generic(attribute= 's_db',\
			y_label='Magnitude [dB]', m=m,n=n, ax=ax,\
			show_legend = show_legend,*args,**kwargs)
	
	def plot_s_mag(self,m=None, n=None, ax = None, show_legend=True,*args,**kwargs):
		'''
		plots the magnitude of a scattering parameters.
		
		plots indecies `m`, `n`, where `m` and `n` can be integers or 
		lists of integers.
		
		
		Parameters
		-----------
		m : int, optional
			first index
		n : int, optional
			second index
		ax : matplotlib.Axes object, optional
			axes to plot on. in case you want to update an existing 
			plot.
		show_legend : boolean, optional
			to turn legend show legend of not, optional
		*args : arguments, optional
			passed to the matplotlib.plot command
		**kwargs : keyword arguments, optional
			passed to the matplotlib.plot command
		
		
		See Also
		--------
		plot_vs_frequency_generic - generic plotting function
		
		
		Examples
		---------
		>>> myntwk.plot_s_mag()
		>>> myntwk.plot_s_mag(m=0,n=1,color='b', marker='x')
		'''
		self.plot_vs_frequency_generic(attribute= 's_mag',\
			y_label='Magnitude [not dB]', m=m,n=n, ax=ax,\
			show_legend = show_legend,*args,**kwargs)
	
	def plot_s_re(self,m=None, n=None, ax = None, show_legend=True,*args,**kwargs):
		'''
		plots the real part of a scattering parameter of indecies m, n
		
		plots indecies `m`, `n`, where `m` and `n` can be integers or 
		lists of integers.
		
		
		Parameters
		-----------
		m : int, optional
			first index
		n : int, optional
			second index
		ax : matplotlib.Axes object, optional
			axes to plot on. in case you want to update an existing 
			plot.
		show_legend : boolean, optional
			to turn legend show legend of not, optional
		*args : arguments, optional
			passed to the matplotlib.plot command
		**kwargs : keyword arguments, optional
			passed to the matplotlib.plot command
		
		
		See Also
		--------
		plot_vs_frequency_generic - generic plotting function
		
		
		Examples
		---------
		>>> myntwk.plot_s_re()
		>>> myntwk.plot_s_re(m=0,n=1,color='b', marker='x')
		'''
		self.plot_vs_frequency_generic(attribute= 's_re',\
			y_label='Real Part', m=m,n=n, ax=ax,\
			show_legend = show_legend,*args,**kwargs)
			
	def plot_s_im(self,m=None, n=None, ax = None, show_legend=True,*args,**kwargs):
		'''
		plots the imaginary part of a scattering parameters.
		
		plots indecies `m`, `n`, where `m` and `n` can be integers or 
		lists of integers.
		
		
		Parameters
		-----------
		m : int, optional
			first index
		n : int, optional
			second index
		ax : matplotlib.Axes object, optional
			axes to plot on. in case you want to update an existing 
			plot.
		show_legend : boolean, optional
			to turn legend show legend of not, optional
		*args : arguments, optional
			passed to the matplotlib.plot command
		**kwargs : keyword arguments, optional
			passed to the matplotlib.plot command
		
		
		See Also
		--------
		plot_vs_frequency_generic - generic plotting function
		
		
		Examples
		---------
		>>> myntwk.plot_s_im()
		>>> myntwk.plot_s_im(m=0,n=1,color='b', marker='x')
		
		'''
		self.plot_vs_frequency_generic(attribute= 's_im',\
			y_label='Imaginary Part', m=m,n=n, ax=ax,\
			show_legend = show_legend,*args,**kwargs)
	
	def plot_s_deg(self,m=None, n=None, ax = None, show_legend=True,*args,**kwargs):
		'''
		plots the phase of a scattering parameters.
		
		plots indecies `m`, `n`, where `m` and `n` can be integers or 
		lists of integers.
		
		
		Parameters
		-----------
		m : int, optional
			first index
		n : int, optional
			second index
		ax : matplotlib.Axes object, optional
			axes to plot on. in case you want to update an existing 
			plot.
		show_legend : boolean, optional
			to turn legend show legend of not, optional
		*args : arguments, optional
			passed to the matplotlib.plot command
		**kwargs : keyword arguments, optional
			passed to the matplotlib.plot command
		
		
		See Also
		--------
		plot_vs_frequency_generic - generic plotting function
		
		
		Examples
		---------
		>>> myntwk.plot_s_deg()
		>>> myntwk.plot_s_deg(m=0,n=1,color='b', marker='x')
		
		'''
		self.plot_vs_frequency_generic(attribute= 's_deg',\
			y_label='Phase [deg]', m=m,n=n, ax=ax,\
			show_legend = show_legend,*args,**kwargs)
				
	def plot_s_deg_unwrapped(self,m=None, n=None, ax = None, show_legend=True,\
		*args,**kwargs):
		'''
		plots the phase of a scattering parameters.
		
		plots indecies `m`, `n`, where `m` and `n` can be integers or 
		lists of integers.
		
		
		Parameters
		-----------
		m : int, optional
			first index
		n : int, optional
			second index
		ax : matplotlib.Axes object, optional
			axes to plot on. in case you want to update an existing 
			plot.
		show_legend : boolean, optional
			to turn legend show legend of not, optional
		*args : arguments, optional
			passed to the matplotlib.plot command
		**kwargs : keyword arguments, optional
			passed to the matplotlib.plot command
		
		
		See Also
		--------
		plot_vs_frequency_generic - generic plotting function
		
		
		Examples
		---------
		>>> myntwk.plot_s_deg_unwrapped()
		>>> myntwk.plot_s_deg_unwrapped(m=0,n=1,color='b', marker='x')
		
		'''
		self.plot_vs_frequency_generic(attribute= 's_deg_unwrap',\
			y_label='Phase [deg]', m=m,n=n, ax=ax,\
			show_legend = show_legend,*args,**kwargs)
	
	plot_s_deg_unwrap = plot_s_deg_unwrapped
	
	def plot_s_rad(self,m=None, n=None, ax = None, show_legend=True,*args,**kwargs):
		'''
		plots the phase of a scattering parameters.
		
		plots indecies `m`, `n`, where `m` and `n` can be integers or 
		lists of integers.
		
		
		Parameters
		-----------
		m : int, optional
			first index
		n : int, optional
			second index
		ax : matplotlib.Axes object, optional
			axes to plot on. in case you want to update an existing 
			plot.
		show_legend : boolean, optional
			to turn legend show legend of not, optional
		*args : arguments, optional
			passed to the matplotlib.plot command
		**kwargs : keyword arguments, optional
			passed to the matplotlib.plot command
		
		
		See Also
		--------
		plot_vs_frequency_generic - generic plotting function
		
		
		Examples
		---------
		>>> myntwk.plot_s_rad()
		>>> myntwk.plot_s_rad(m=0,n=1,color='b', marker='x')
		
		'''
		self.plot_vs_frequency_generic(attribute= 's_rad',\
			y_label='Phase [rad]', m=m,n=n, ax=ax,\
			show_legend = show_legend,*args,**kwargs)
	def plot_s_quad(self,m=None, n=None, ax = None, show_legend=True,*args,**kwargs):
		'''
		plots the quadrature of a scattering parameters.
		
		quadrature is another name for arc-length. 
		plots indecies `m`, `n`, where `m` and `n` can be integers or 
		lists of integers.
		
		
		Parameters
		-----------
		m : int, optional
			first index
		n : int, optional
			second index
		ax : matplotlib.Axes object, optional
			axes to plot on. in case you want to update an existing 
			plot.
		show_legend : boolean, optional
			to turn legend show legend of not, optional
		*args : arguments, optional
			passed to the matplotlib.plot command
		**kwargs : keyword arguments, optional
			passed to the matplotlib.plot command
		
		
		See Also
		--------
		plot_vs_frequency_generic - generic plotting function
		
		
		Examples
		---------
		>>> myntwk.plot_s_quad()
		>>> myntwk.plot_s_quad(m=0,n=1,color='b', marker='x')
		'''
		self.plot_vs_frequency_generic(attribute= 's_quad',\
			y_label='Arc-Length [distance]', m=m,n=n, ax=ax,\
			show_legend = show_legend,*args,**kwargs)	
	def plot_s_rad_unwrapped(self,m=None, n=None, ax = None, show_legend=True,\
		*args,**kwargs):
		'''
		plots the phase of a scattering parameters, in unwrapped radians.
		
		plots indecies `m`, `n`, where `m` and `n` can be integers or 
		lists of integers.
		
		
		Parameters
		-----------
		m : int, optional
			first index
		n : int, optional
			second index
		ax : matplotlib.Axes object, optional
			axes to plot on. in case you want to update an existing 
			plot.
		show_legend : boolean, optional
			to turn legend show legend of not, optional
		*args : arguments, optional
			passed to the matplotlib.plot command
		**kwargs : keyword arguments, optional
			passed to the matplotlib.plot command
		
		
		See Also
		--------
		plot_vs_frequency_generic - generic plotting function
		
		
		Examples
		---------
		>>> myntwk.plot_s_rad_unwrap()
		>>> myntwk.plot_s_rad_unwrap(m=0,n=1,color='b', marker='x')
		'''
		self.plot_vs_frequency_generic(attribute= 's_rad_unwrap',\
			y_label='Phase [rad]', m=m,n=n, ax=ax,\
			show_legend = show_legend,*args,**kwargs)	

	def plot_s_polar(self,m=0, n=0, ax = None, show_legend=True,\
		*args,**kwargs):
		'''
		plots the scattering parameter in polar form.
		
		plots indecies `m`, `n`, where `m` and `n` can be integers or 
		lists of integers.
		
		
		Parameters
		-----------
		m : int, optional
			first index
		n : int, optional
			second index
		ax : matplotlib.Axes object, optional
			axes to plot on. in case you want to update an existing 
			plot.
		show_legend : boolean, optional
			to turn legend show legend of not, optional
		*args : arguments, optional
			passed to the matplotlib.plot command
		**kwargs : keyword arguments, optional
			passed to the matplotlib.plot command
		
		
		See Also
		--------
		plot_vs_frequency_generic - generic plotting function
		
		
		Examples
		---------
		>>> myntwk.plot_s_polar()
		>>> myntwk.plot_s_polar(m=0,n=1,color='b', marker='x')
		'''
		self.plot_polar_generic(attribute_r= 's_mag',attribute_theta='s_rad',\
			m=m,n=n, ax=ax,	show_legend = show_legend,*args,**kwargs)	

	def plot_s_smith(self,m=None, n=None,r=1,ax = None, show_legend=True,\
		chart_type='z', *args,**kwargs):
		'''
		plots the scattering parameter on a smith chart
		
		plots indecies `m`, `n`, where `m` and `n` can be integers or 
		lists of integers.
		
		
		Parameters
		-----------
		m : int, optional
			first index
		n : int, optional
			second index
		ax : matplotlib.Axes object, optional
			axes to plot on. in case you want to update an existing 
			plot.
		show_legend : boolean, optional
			to turn legend show legend of not, optional
		*args : arguments, optional
			passed to the matplotlib.plot command
		**kwargs : keyword arguments, optional
			passed to the matplotlib.plot command
		
		
		See Also
		--------
		plot_vs_frequency_generic - generic plotting function
		smith -  draws a smith chart
		
		Examples
		---------
		>>> myntwk.plot_s_smith()
		>>> myntwk.plot_s_smith(m=0,n=1,color='b', marker='x')
		'''
		# TODO: prevent this from re-drawing smith chart if one alread
		# exists on current set of axes

		# get current axis if user doesnt supply and axis 
		if ax is None:
			ax = plb.gca()
			
		
		if m is None:
			M = range(self.number_of_ports)
		else:
			M = [m]
		if n is None:
			N = range(self.number_of_ports)
		else:
			N = [n]
		
		if 'label'  not in kwargs.keys():
			generate_label=True
		else:
			generate_label=False
		
		for m in M:
			for n in N:
				# set the legend label for this trace to the networks name if it
				# exists, and they didnt pass a name key in the kwargs
				if generate_label: 
					if self.name is None:
						if plb.rcParams['text.usetex']:
							label_string = '$S_{'+repr(m+1) + repr(n+1)+'}$'
						else:
							label_string = 'S'+repr(m+1) + repr(n+1)
					else:
						if plb.rcParams['text.usetex']:
							label_string = self.name+', $S_{'+repr(m+1) + \
								repr(n+1)+'}$'
						else:
							label_string = self.name+', S'+repr(m+1) + repr(n+1)
		
					kwargs['label'] = label_string
					
				# plot the desired attribute vs frequency 
				if len (ax.patches) == 0:
					smith(ax=ax, smithR = r, chart_type=chart_type)
				ax.plot(self.s[:,m,n].real,  self.s[:,m,n].imag, *args,**kwargs)
		
		#draw legend
		if show_legend:
			ax.legend()
		ax.axis(npy.array([-1,1,-1,1])*r)
		ax.set_xlabel('Real')
		ax.set_ylabel('Imaginary')
	def plot_s_complex(self,m=None, n=None,ax = None, show_legend=True,\
		*args,**kwargs):
		'''
		plots the scattering parameter on complex plane
		
		plots indecies `m`, `n`, where `m` and `n` can be integers or 
		lists of integers.
		
		
		Parameters
		-----------
		m : int, optional
			first index
		n : int, optional
			second index
		ax : matplotlib.Axes object, optional
			axes to plot on. in case you want to update an existing 
			plot.
		show_legend : boolean, optional
			to turn legend show legend of not, optional
		*args : arguments, optional
			passed to the matplotlib.plot command
		**kwargs : keyword arguments, optional
			passed to the matplotlib.plot command
		
		
		See Also
		--------
		plot_vs_frequency_generic - generic plotting function
		
		
		Examples
		---------
		>>> myntwk.plot_s_rad()
		>>> myntwk.plot_s_rad(m=0,n=1,color='b', marker='x')
		'''
		# TODO: prevent this from re-drawing smith chart if one alread
		# exists on current set of axes

		# get current axis if user doesnt supply and axis 
		if ax is None:
			ax = plb.gca()
			
		
		if m is None:
			M = range(self.number_of_ports)
		else:
			M = [m]
		if n is None:
			N = range(self.number_of_ports)
		else:
			N = [n]
		
		if 'label'  not in kwargs.keys():
			generate_label=True
		else:
			generate_label=False
		
		for m in M:
			for n in N:
				# set the legend label for this trace to the networks name if it
				# exists, and they didnt pass a name key in the kwargs
				if generate_label: 
					if self.name is None:
						if plb.rcParams['text.usetex']:
							label_string = '$S_{'+repr(m+1) + repr(n+1)+'}$'
						else:
							label_string = 'S'+repr(m+1) + repr(n+1)
					else:
						if plb.rcParams['text.usetex']:
							label_string = self.name+', $S_{'+repr(m+1) + \
								repr(n+1)+'}$'
						else:
							label_string = self.name+', S'+repr(m+1) + repr(n+1)
		
					kwargs['label'] = label_string
					
				# plot the desired attribute vs frequency 
				ax.plot(self.s[:,m,n].real,  self.s[:,m,n].imag, *args,**kwargs)
		
		#draw legend
		if show_legend:
			ax.legend()
		ax.axis('equal')
		ax.set_xlabel('Real')
		ax.set_ylabel('Imaginary')
	def plot_s_all_db(self,ax = None, show_legend=True,*args,**kwargs):
		'''
		plots all s parameters in log magnitude

		takes:
			ax - matplotlib.axes object to plot on, used in case you
				want to update an existing plot.
			show_legend: boolean, to turn legend show legend of not
			*args,**kwargs - passed to the matplotlib.plot command
		'''
		for m in range(self.number_of_ports):
			for n in range(self.number_of_ports):
				self.plot_vs_frequency_generic(attribute= 's_db',\
					y_label='Magnitude [dB]', m=m,n=n, ax=ax,\
					show_legend = show_legend,*args,**kwargs)
	
	def plot_passivity(self,port=None, ax = None, show_legend=True,*args,**kwargs):
		'''
		plots the passivity of a network.
		possibly for a specific port. 
		
		
		Parameters
		-----------
		port: int
			calculate passivity of a given port
		ax : matplotlib.Axes object, optional
			axes to plot on. in case you want to update an existing 
			plot.
		show_legend : boolean, optional
			to turn legend show legend of not, optional
		*args : arguments, optional
			passed to the matplotlib.plot command
		**kwargs : keyword arguments, optional
			passed to the matplotlib.plot command
		
		
		See Also
		--------
		plot_vs_frequency_generic - generic plotting function
		passivity - passivity property
		
		Examples
		---------
		>>> myntwk.plot_s_rad()
		>>> myntwk.plot_s_rad(m=0,n=1,color='b', marker='x')
		'''
		if port is None:
			port = range(self.number_of_ports)
		
		for mn in list(port):	
			self.plot_vs_frequency_generic(attribute= 'passivity',\
				y_label='Passivity', m=mn,n=mn, ax=ax,\
				show_legend = show_legend,*args,**kwargs)
	
	
	# noise
	def add_noise_polar(self,mag_dev, phase_dev,**kwargs):
		'''
		adds a complex zero-mean gaussian white-noise signal of given
		standard deviations for magnitude and phase

		takes:
			mag_mag: standard deviation of magnitude
			phase_dev: standard deviation of phase [in degrees]
			n_ports: number of ports. defualt to 1
		returns:
			nothing
		'''
		phase_rv= stats.norm(loc=0, scale=phase_dev).rvs(size = self.s.shape)
		mag_rv = stats.norm(loc=0, scale=mag_dev).rvs(size = self.s.shape)
		phase = (self.s_deg+phase_rv)
		mag = self.s_mag + mag_rv 
		self.s = mag* npy.exp(1j*npy.pi/180.*phase)
	def add_noise_polar_flatband(self,mag_dev, phase_dev,**kwargs):
		'''
		adds a flatband complex zero-mean gaussian white-noise signal of
		given standard deviations for magnitude and phase

		takes:
			mag_mag: standard deviation of magnitude
			phase_dev: standard deviation of phase [in degrees]
			n_ports: number of ports. defualt to 1
		returns:
			nothing
		'''
		phase_rv= stats.norm(loc=0, scale=phase_dev).rvs(size = self.s[0].shape)
		mag_rv = stats.norm(loc=0, scale=mag_dev).rvs(size = self.s[0].shape)
		
		phase = (self.s_deg+phase_rv)
		mag = self.s_mag + mag_rv 
		self.s = mag* npy.exp(1j*npy.pi/180.*phase)
	
	def multiply_noise(self,mag_dev, phase_dev, **kwargs):
		'''
		multiplys a complex bivariate gaussian white-noise signal
		of given standard deviations for magnitude and phase. 	
		magnitude mean is 1, phase mean is 0 
		
		takes:
			mag_dev: standard deviation of magnitude
			phase_dev: standard deviation of phase [in degrees]
			n_ports: number of ports. defualt to 1
		returns:
			nothing
		'''
		phase_rv = stats.norm(loc=0, scale=phase_dev).rvs(\
			size = self.s.shape)
		mag_rv = stats.norm(loc=1, scale=mag_dev).rvs(\
			size = self.s.shape)
		self.s = mag_rv*npy.exp(1j*npy.pi/180.*phase_rv)*self.s
	
	def nudge(self, amount=1e-12):
		'''
		perturb s-parameters by small amount. this is usefule to work-around
		numerical bugs.
		takes:
			amount: amount to add to s parameters
		returns:
			na
		'''
		self.s = self.s + 1e-12

## Functions operating on Network[s]
def connect(ntwkA, k, ntwkB,l):
	'''
	connect two n-port networks together. 

	specifically, connect port `k` on `ntwkA` to port `l` on `ntwkB`. The 
	resultant network has (ntwkA.nports+ntwkB.nports-2) ports. The port
	index's ('k','l') start from 0. Port impedances **are** taken into 
	account.
	
	Parameters
	-----------
	ntwkA : :class:`Network` 
		network 'A'
	k : int
		port index on `ntwkA` ( port indecies start from 0 )
	ntwkB : :class:`Network` 
		network 'B'
	l : int
		port index on `ntwkB`
	
	
	
	Returns
	---------
	ntwkC : :class:`Network` 
		new network of rank (ntwkA.nports+ntwkB.nports -2)-ports
	
	
	See Also
	-----------
		connect_s : actual  S-parameter connection algorithm.
		innerconnect_s : actual S-parameter connection algorithm.
		
	Notes
	-------
		the effect of mis-matched port impedances is handled by inserting
		a 2-port 'mismatch' network between the two connected ports.
		This mismatch Network is calculated with the 
		:func:impedance_mismatch function.
	
	Examples
	---------
	To implement a *cascade* of two networks
	
	>>> ntwkA = mv.Network('ntwkA.s2p')
	>>> ntwkB = mv.Network('ntwkB.s2p')
	>>> ntwkC = mv.connect(ntwkA, 1, ntwkB,0)
	
	'''
	ntwkC = deepcopy(ntwkA)
	# account for port impedance mis-match by inserting a two-port 
	# network at the connection. if ports are matched this becomes a 
	# thru
	if not (ntwkA.z0[:,k] == ntwkB.z0[:,l]).all():
		ntwkC.s = connect_s(\
			ntwkA.s,k, \
			impedance_mismatch(ntwkA.z0[:,k],ntwkB.z0[:,l]),0)
			
	ntwkC.s = connect_s(ntwkC.s,k,ntwkB.s,l)
	ntwkC.z0=npy.hstack((npy.delete(ntwkA.z0,k,1),npy.delete(ntwkB.z0,l,1)))
	return ntwkC
	
def innerconnect(ntwkA, k, l):
	'''
	connect two ports of a single n-port network.
	
	this results in a (n-2)-port network. remember port indecies start
	from 0.
	
	Parameters
	-----------
	ntwkA : :class:`Network`  
		network 'A'
	k : int
		port index on ntwkA ( port indecies start from 0 )
	l : int
		port index on ntwkB
	
	
	
	Returns
	---------
	ntwkC : :class:`Network` 
		new network of rank (ntwkA.nports+ntwkB.nports -2)-ports
	
	
	See Also
	-----------
		connect_s : actual  S-parameter connection algorithm.
		innerconnect_s : actual S-parameter connection algorithm.
		
	Notes
	-------
		a 2-port 'mismatch' network between the two connected ports. 
	
	Examples
	---------
	To connect ports '0' and port '1' on ntwkA
	
	>>> ntwkA = mv.Network('ntwkA.s3p')
	>>> ntwkC = mv.innerconnect(ntwkA, 0,1)
	
	'''
	ntwkC = deepcopy(ntwkA)
	ntwkC.s = connect_s(\
		ntwkA.s,k, \
		impedance_mismatch(ntwkA.z0[:,k],ntwkA.z0[:,l]),0)
	ntwkC.s = innerconnect_s(ntwkC.s,k,l)
	ntwkC.z0=npy.delete(ntwkC.z0,[l,k],1)
	return ntwkC
	
def cascade(ntwkA,ntwkB):
	'''
	cascade two 2-port Networks together
	
	connects port 1 of `ntwkA` to port 0 of `ntwkB`. This calls 
	`connect(ntwkA,1, ntwkB,0)`
	
	Parameters
	-----------
	ntwkA : :class:`Network`
		network `ntwkA`
	ntwkB : Network
		network `ntwkB`
	
	Returns
	--------
	C : Network
		the resultant network of ntwkA cascaded with ntwkB	
	
	See Also
	---------
	connect : connects two Networks together at arbitrary ports.
	'''
	return connect(ntwkA,1, ntwkB,0)

def de_embed(ntwkA,ntwkB):	
	'''
	de-embed `ntwkA` from `ntwkB`. this calls `ntwkA.inv**ntwkB`. 
	the syntax of cascading an inverse is more explicit, it is 
	recomended that it be used instead of this function. 
	
	Parameters
	-----------
	ntwkA : :class:`Network`
		network `ntwkA`
	ntwkB : :class:`Network`
		network `ntwkB`
	
	Returns
	--------
	C : Network
		the resultant network of  ntwkB	de-embeded from ntwkA
	
	See Also
	---------
	connect : connects two Networks together at arbitrary ports.
	
	'''
	return ntwkA.inv ** ntwkB

def average(list_of_networks):
	'''
	calculates the average network from a list of Networks.
	 
	this is complex average of the s-parameters for a  list of Networks

	
	Parameters
	-----------
	list_of_networks: list
		a list of :class:`Network` objects
			
	Returns
	---------
	ntwk : :class:`Network` 
		the resultant averaged Network
	
	Notes
	------
	This same function can be accomplished with properties of a 
	:class:`NetworkSet` class.
	
	Examples
	---------
	
	>>> ntwk_list = [mv.Network('myntwk.s1p'), mv.Network('myntwk2.s1p')]
	>>> mean_ntwk = mv.average(ntwk_list)	
	'''
	out_ntwk = copy(list_of_networks[0])
	
	for a_ntwk in list_of_networks[1:]:
		out_ntwk += a_ntwk

	out_ntwk.s = out_ntwk.s/(len(list_of_networks))

	return out_ntwk

def one_port_2_two_port(ntwk):
	'''
	calculates the two-port network given a  symetric, reciprocal and 
	lossless one-port network.
	
	takes:
		ntwk: a symetric, reciprocal and lossless one-port network.
	returns:
		ntwk: the resultant two-port Network
	'''
	result = copy(ntwk)
	result.s = npy.zeros((result.frequency.npoints,2,2), dtype=complex) 
	s11 = ntwk.s[:,0,0]
	result.s[:,0,0] = s11
	result.s[:,1,1] = s11
	## HACK: TODO: verify this mathematically
	result.s[:,0,1] = npy.sqrt(1- npy.abs(s11)**2)*\
		npy.exp(1j*(npy.angle(s11)+npy.pi/2.*(npy.angle(s11)<0) -npy.pi/2*(npy.angle(s11)>0)))
	result.s[:,1,0] = result.s[:,0,1]
	return result
	

## Functions operating on s-parameter matrices
def connect_s(A,k,B,l):
	'''
	connect two n-port networks' s-matricies together. 
	
	specifically, connect port `k` on network `A` to port `l` on network
	`B`. The resultant network has nports = (A.rank + B.rank-2). This
	function operates on, and returns s-matricies. The function 
	:func:`connect` operates on :class:`Network` types.
	
	Parameters
	-----------
	A : numpy.ndarray
		S-parameter matrix of `A`, shape is fxnxn
	k : int
		port index on `A` (port indecies start from 0)
	B : numpy.ndarray
		S-parameter matrix of `B`, shape is fxnxn
	l : int
		port index on `B`
		
	Returns
	-------
	C : numpy.ndarray
		new S-parameter matrix 
		
	
	Notes
	-------
	internally, this function creates a larger composite network 
	and calls the  :func:`innerconnect_s` function. see that function for more 
	details about the implementation
	
	See Also
	--------
		connect : operates on :class:`Network` types
		innerconnect_s : function which implements the connection 
			connection algorithm
		

	'''
	if k > A.shape[-1]-1 or l>B.shape[-1]-1:
		raise(ValueError('port indecies are out of range'))
	
	if len (A.shape) > 2:
		# assume this is a kxnxn matrix
		n = A.shape[-1]+B.shape[-1]-2 # nports of output Matrix
		C = npy.zeros((A.shape[0], n,n), dtype='complex')
		
		for f in range(A.shape[0]):
			C[f,:,:] = connect_s(A[f,:,:],k,B[f,:,:],l)
		return C
	else:		
		filler = npy.zeros((A.shape[0],B.shape[1]))
		#create composite matrix, appending each sub-matrix diagonally
		C= npy.vstack( [npy.hstack([A,filler]),npy.hstack([filler.T,B])])
		
		return innerconnect_s(C, k,A.shape[-1]+l)
		
def innerconnect_s(A, k, l):
	'''
	connect two ports of a single n-port network's s-matrix.
	
	Specifically, connect port `k`  to port `l` on `A`. This results in
	a (n-2)-port network.  This	function operates on, and returns 
	s-matricies. The function :func:`innerconnect` operates on 
	:class:`Network` types.
	
	Parameters
	-----------
	A : numpy.ndarray
		S-parameter matrix of `A`, shape is fxnxn
	k : int
		port index on `A` (port indecies start from 0)
	l : int
		port index on `A`
		
	Returns
	-------
	C : numpy.ndarray
		new S-parameter matrix 
	
	Notes
	-----
	The algorithm used to calculate the resultant network is called a 
	'sub-network growth',  can be found in [#]_. The original paper 
	describing the  algorithm is given in [#]_.
	
	References
	----------	
	.. [#] Compton, R.C.; , "Perspectives in microwave circuit analysis," Circuits and Systems, 1989., Proceedings of the 32nd Midwest Symposium on , vol., no., pp.716-718 vol.2, 14-16 Aug 1989. URL: http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=101955&isnumber=3167

	.. [#] Filipsson, Gunnar; , "A New General Computer Algorithm for S-Matrix Calculation of Interconnected Multiports," Microwave Conference, 1981. 11th European , vol., no., pp.700-704, 7-11 Sept. 1981. URL: http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4131699&isnumber=4131585


	'''
	
	# TODO: this algorithm is a bit wasteful in that it calculates the 
	# scattering parameters for a network of rank S.rank+T.rank and 
	# then deletes the ports which are 'connected' 
	if k > A.shape[-1] -1 or l>A.shape[-1]-1:
		raise(ValueError('port indecies are out of range'))
	
	if len (A.shape) > 2:
		# assume this is a kxnxn matrix
		n = A.shape[-1]-2 # nports of output Matrix
		C = npy.zeros((A.shape[0], n,n), dtype='complex')
		
		for f in range(A.shape[0]):
			C[f,:,:] = innerconnect_s(A[f,:,:],k,l)
		return C
	else:
		n = A.shape[0]
		C = npy.zeros([n,n],dtype='complex')
		for i in range(n):
			for j in range(n):
				C[i,j] = A[i,j] +  \
					( A[k,j]*A[i,l]*(1-A[l,k]) + A[l,j]*A[i,k]*(1-A[k,l]) +\
					A[k,j]*A[l,l]*A[i,k] + A[l,j]*A[k,k]*A[i,l])/\
					( (1-A[k,l])*(1-A[l,k]) - A[k,k]*A[l,l] )
		C = npy.delete(C,(k,l),0)
		C = npy.delete(C,(k,l),1)
		return C

def s2t(s):
	'''
	converts scattering parameters to scattering transfer parameters. 
	
	transfer parameters [#]_ are also refered to as 
	'wave cascading matrix', this function only operates on 2-port
	networks.
	
	Parameters
	-----------
	s : numpy.ndarray
		scattering parameter matrix. shape should be should be 2x2, or
		fx2x2
	
	Returns
	-------
	t : numpy.ndarray
		scattering transfer parameters (aka wave cascading matrix)
		
	See Also
	---------
	t2s : converts scattering transfer parameters to scattering 
		parameters
	inv : calculates inverse s-parameters
	
	References
	-----------
	.. [#] http://en.wikipedia.org/wiki/Scattering_transfer_parameters#Scattering_transfer_parameters
	'''
	t = npy.copy(s)

	if len (s.shape) > 2 :
		for f in range(s.shape[0]):
			t[f,:,:] = s2t(s[f,:,:])
	elif s.shape == (2,2):
		t = npy.array([[-1*npy.linalg.det(s),	s[0,0]],\
					[-s[1,1],1]]) / s[1,0]
	else:
		raise IndexError('matrix should be 2x2, or kx2x2')
	return t        
        
def t2s(t):
	'''
	converts scattering transfer parameters to scattering parameters 
	
	transfer parameters [#]_ are also refered to as 
	'wave cascading matrix', this function only operates on 2-port
	networks. this function only operates on 2-port scattering 
	parameters.
	
	Parameters
	-----------
	t : numpy.ndarray
		scattering transfer parameters, shape should be should be 2x2, or
		fx2x2
	
	Returns
	-------
	s : numpy.ndarray
		scattering parameter matrix.
		
	See Also
	---------
	t2s : converts scattering transfer parameters to scattering parameters
	inv : calculates inverse s-parameters
	
	References
	-----------
	.. [#] http://en.wikipedia.org/wiki/Scattering_transfer_parameters#Scattering_transfer_parameters
	'''
	s = npy.copy(t)
	if len (t.shape) > 2 :
		for f in range(t.shape[0]):
			s[f,:,:] = t2s(s[f,:,:])
	
	elif t.shape== (2,2):
		s = npy.array([[t[0,1],npy.linalg.det(t)],\
			[1,-t[1,0]]])/t[1,1]
	else:
		raise IndexError('matrix should be 2x2, or kx2x2')
	return s
	
def inv(s):
	'''
	calculates 'inverse' s-parameter matrix, used for de-embeding
	
	this is not literally the inverse of the s-parameter matrix. it 
	is defined such that the inverse of the s-matrix cascaded 
	with itself is unity. 
	
	.. math::
	
		inv(s) = t2s({s2t(s)}^{-1})
		
	where :math:`x^{-1}` is the matrix inverse. in other words this 
	is the inverse of the scattering transfer parameters matrix 
	transformed into a scattering parameters matrix.
	
	Parameters
	-----------
	s : numpy.ndarray
		scattering parameter matrix. shape should be should be 2x2, or
		fx2x2
	
	Returns
	-------
	s' : numpy.ndarray
		inverse scattering parameter matrix.
	
	See Also
	---------
	t2s : converts scattering transfer parameters to scattering parameters
	s2t : converts scattering parameters to scattering transfer parameters 
		
		
	'''
	# this idea is from lihan
	i = npy.copy(s)
	if len (s.shape) > 2 :
		for f in range(len(s)):
			i[f,:,:] = inv(s[f,:,:])
	elif s.shape == (2,2):
		i = t2s(npy.linalg.inv(s2t(s)))
	else:
		raise IndexError('matrix should be 2x2, or kx2x2')
	return i

def flip(a):
	'''
	invert the ports of a networks s-matrix, 'flipping' it over
	
	Parameters
	-----------
	a : numpy.ndarray
		scattering parameter matrix. shape should be should be 2x2, or
		fx2x2
	
	Returns
	-------
	a' : numpy.ndarray
		flipped scattering parameter matrix, ie interchange of port 0 
		and port 1
	
	Note
	-----
			only works for 2-ports at the moment
	'''
	c = copy(a)
	
	if len (a.shape) > 2 :
		for f in range(a.shape[0]):
			c[f,:,:] = flip(a[f,:,:])
	elif a.shape == (2,2):
		c[0,0] = a[1,1]
		c[1,1] = a[0,0]
		c[0,1] = a[1,0]
		c[1,0] = a[0,1]
	else:
		raise IndexError('matricies should be 2x2, or kx2x2')
	return c




## Other	
# dont belong here, but i needed them quickly
# this is needed for port impedance mismatches 
def impedance_mismatch(z1, z2):
	'''
	creates a two-port network for a impedance mis-match
	
	Parameters
	-----------
	z1 : number or array-like
		complex impedance of port 1
	z2 : number or array-like
		complex impedance of port 2
	
	Returns
	---------
	s' : 2-port s-matrix for the impedance mis-match
	'''	
	gamma = zl_2_Gamma0(z1,z2)
	result = npy.zeros(shape=(len(gamma),2,2), dtype='complex')
	
	result[:,0,0] = gamma
	result[:,1,1] = -gamma
	result[:,1,0] = 1+gamma
	result[:,0,1] = 1-gamma
	return result


# Touchstone manipulation	
def load_all_touchstones(dir = '.', contains=None, f_unit=None):
	'''
	loads all touchtone files in a given dir into a dictionary. 
	
	Parameters
	-----------
	dir :	string
		the path 
	contains :	string 
		a string the filenames must contain to be loaded.
	f_unit 	: ['hz','mhz','ghz']
		the frequency unit to assign all loaded networks. see 
		:attr:`frequency.Frequency.unit`.
		
	Returns
	---------
	ntwkDict : a dictonary with keys equal to the file name (without
		a suffix), and values equal to the corresponding ntwk types
	
	Examples
	----------
	>>> ntwk_dict = mv.load_all_touchstones('.', contains ='20v')
		
	'''
	ntwkDict = {}

	for f in os.listdir (dir):
		if contains is not None and contains not in f:
			continue
			
		# TODO: make this s?p with reg ex
		if( f.lower().endswith ('.s1p') or f.lower().endswith ('.s2p') ):
			name = f[:-4]
			ntwkDict[name]=(Network(dir +'/'+f))
			if f_unit is not None: ntwkDict[name].frequency.unit=f_unit
		
	return ntwkDict	

def write_dict_of_networks(ntwkDict, dir='.'):
	'''
	saves a dictionary of networks touchstone files in a given directory
	
	The filenames assigned to the touchstone files are taken from 
	the keys of the dictionary. 
	
	Parameters
	-----------
	ntwkDict : dictionary 
		dictionary of :class:`Network` objects
	dir : string
		directory to write touchstone file to 

		
	'''
	for ntwkKey in ntwkDict:
		ntwkDict[ntwkKey].write_touchstone(filename = dir+'/'+ntwkKey)

def csv_2_touchstone(filename):
	'''
	converts a csv file to a :class:`Network`
	
	specifically, this converts csv files saved from a Rohde Shcwarz 
	ZVA-40, and possibly other network analyzers, into a :class:`Network`
	object. 
	
	Parameters
	------------
	filename : string
		name of file
	
	Returns
	--------
	ntwk : :class:`Network` object
		the network representing data in the csv file
	'''
		
	ntwk = Network(name=filename[:-4])
	try: 
		data = npy.loadtxt(filename, skiprows=3,delimiter=',',\
			usecols=range(9))
		s11 = data[:,1] +1j*data[:,2]	
		s21 = data[:,3] +1j*data[:,4]	
		s12 = data[:,5] +1j*data[:,6]	
		s22 = data[:,7] +1j*data[:,8]	
		ntwk.s = npy.array([[s11, s21],[s12,s22]]).transpose().reshape(-1,2,2)
	except(IndexError):
		data = npy.loadtxt(filename, skiprows=3,delimiter=',',\
			usecols=range(3))		
		ntwk.s = data[:,1] +1j*data[:,2]
	
	ntwk.frequency.f = data[:,0]
	ntwk.frequency.unit='ghz'
	
	return ntwk




