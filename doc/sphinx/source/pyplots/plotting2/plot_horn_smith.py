import pylab
import mwavepy as mv 

# create a Network type from a touchstone file of a horn antenna
horn = mv.Network('horn antenna.s1p')
pylab.title('Return Loss (Mag)')
horn.plot_s_smith(m=0,n=0) # m,n are S-Matrix indecies


# show the plots 
pylab.show()
