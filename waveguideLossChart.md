# !! THIS NO LONGER WORKS !! #
## I HAVE YET TO IMPLEMENT  SURFACE CONDUCTIVITY LOSS IN MWAVEPY-1.0 ##


# Introduction #
here is a waveguide loss chart, the code to produce such a chart using mwavepy follows. This example is distributed with mwavepy under the examples/ directory.o or [here](http://mwavepy.googlecode.com/svn/trunk/examples/waveguideLossChart.py)

![http://mwavepy.googlecode.com/svn/trunk/examples/waveguideLoss.png](http://mwavepy.googlecode.com/svn/trunk/examples/waveguideLoss.png)

```
import sys
sys.path.append('../')
import mwavepy as m
import pylab

# this should be accessed from some material database
conductivityCopper=5.7e7 #S/m

pylab.figure()

# loops through waveguide types, and plots the conductor loss (alphaC)
# vs frequency
listOfWaveguides = [ \
        m.wr(90,surfaceConductivity=conductivityCopper),\
        m.wr(62,surfaceConductivity=conductivityCopper),\
        m.wr(42,surfaceConductivity=conductivityCopper),\
        m.wr(28,surfaceConductivity=conductivityCopper),\
        m.wr(19,surfaceConductivity=conductivityCopper),\
        m.wr(15,surfaceConductivity=conductivityCopper),\
        m.wr(10,surfaceConductivity=conductivityCopper)\
        ]

for k in listOfWaveguides:
        loss = m.np2dB(k.alphaC(k.freqAxis*(2*pylab.pi))) # loss in dB/m
        freq = k.freqAxis/1e9 # frequency in GHz
        pylab.plot(freq, loss, label= k.name)

pylab.legend()
pylab.xlabel('Frequenc (GHz)')
pylab.ylabel ('Loss (dB/m)')
pylab.title('Waveguide Loss, for Copper ($\sigma=5.7E7$)')


pylab.savefig('waveguideLoss.eps',format='eps')
pylab.savefig('waveguideLoss.png',format='png')


pylab.show()

```