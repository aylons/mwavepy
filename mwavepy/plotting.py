'''
#       plotting.py
#       
#       Copyright 2010 alex arsenovic <arsenovic@virginia.edu>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
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
import numpy as npy
from matplotlib.patches import Circle 	# for drawing smith chart
#from matplotlib.lines import Line2D		# for drawing smith chart



def smith(smithR=1,ax=None):
	'''
	plots the smith chart of a given radius
	takes:
		smithR - radius of smith chart
		ax - matplotlib.axes instance 
	'''
	##TODO: fix this function so it doesnt suck
	if ax == None:
		ax1 = plb.gca()
	else:
		ax1 = ax

	# contour holds matplotlib instances of: pathes.Circle, and lines.Line2D, which 
	# are the contours on the smith chart 
	contour = []
	
	# these are hard-coded on purpose,as they should always be present
	rHeavyList = [0,1]
	xHeavyList = [1,-1]

	#TODO: fix this
	# these could be dynamically coded in the future, but work good'nuff for now 
	rLightList = plb.logspace(3,-5,9,base=.5)
	xLightList = plb.hstack([plb.logspace(2,-5,8,base=.5), -1*plb.logspace(2,-5,8,base=.5)]) 
	
	# cheap way to make a ok-looking smith chart at larger than 1 radii
	if smithR > 1:
		rMax = (1.+smithR)/(1.-smithR)
		rLightList = plb.hstack([ plb.linspace(0,rMax,11)  , rLightList ])
		
	
	# loops through Light and Heavy lists and draws circles using patches
	# for analysis of this see R.M. Weikles Microwave II notes (from uva)
	for r in rLightList:
		center = (r/(1.+r),0 )
		radius = 1./(1+r)
		contour.append( Circle( center, radius, ec='grey',fc = 'none'))
	for x in xLightList:
		center = (1,1./x)
		radius = 1./x
		contour.append( Circle( center, radius, ec='grey',fc = 'none'))
			
	for r in rHeavyList:
		center = (r/(1.+r),0 )
		radius = 1./(1+r)
		contour.append( Circle( center, radius, ec= 'black', fc = 'none'))	
	for x in xHeavyList:
		center = (1,1./x)
		radius = 1./x	
		contour.append( Circle( center, radius, ec='black',fc = 'none'))
	
	#draw x and y axis
	ax1.axhline(0, color='k')
	ax1.axvline(1, color='k')
	ax1.grid(0)
	#set axis limits
	ax1.axis('equal')
	ax1.axis(smithR*npy.array([-1., 1., -1., 1.]))
	
	# loop though contours and draw them on the given axes
	for currentContour in contour:
		ax1.add_patch(currentContour)




