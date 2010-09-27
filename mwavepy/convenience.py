'''
#       convenience.py
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

import pylab as plb
import os
from network import *

def save_all_figs(dir = './', format=['eps','pdf','png']):
	if dir[-1] != '/':
		dir = dir + '/'
	for fignum in plb.get_fignums():
		plb.figure(fignum)
		fileName = plb.gca().get_title()
		if fileName == '':
				fileName = 'unamedPlot'
		for fmt in format:
			plb.savefig(dir+fileName+'.'+fmt, format=fmt)
			print (dir+fileName+'.'+fmt)
		
def load_all_touchstones(dir = '.', contains=None, f_unit=None):
	'''
	loads all touchtone files in a given dir 
	
	takes:
		dir  - the path to the dir, passed as a string (defalut is cwd)
		contains - string which filename must contain to be loaded, not 
			used if None.(default None)
	returns:
		ntwkDict - a Dictonary with keys equal to the file name (without
			a suffix), and values equal to the corresponding ntwk types
	
		
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
	writes a dictionary of networks to a given directory
	'''
	for ntwkKey in ntwkDict:
		ntwkDict[ntwkKey].write_touchstone(filename = dir+'/'+ntwkKey)
