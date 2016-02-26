
# Introduction #

This example is provided with mwavepy's package under the examples directory.  It demonstrates how to use mwavepy to load a touchstone file and plot the data in various formats. The output is then saved in png, and eps (vector) format.

note: your plots may look different than these, which is a result of your matplotlib setup. See the [formatPlots](http://code.google.com/p/mwavepy/wiki/formatPlots) page in the wiki to make yours look exactly like these.

## Import mwavepy ##
the first step is to import mwavepy and any other librarys you are going to need
```
import mwavepy as mv
import pylab
```
## load touchstone data ##
in mwavepy, touchstone file data is loaded into 'Network' type.
```
horn = mv.Network('horn.s2p')
```
## Plot Some Information ##



### Magnitude of Return loss ###
```
# plot magnitude of S11
pylab.figure(1)
pylab.title('Return Loss (Mag)')	
horn.plot_s_db(m=0,n=0)	# m,n are S-Matrix indecies
```

<img src='http://mwavepy.googlecode.com/svn/branches/mwavepy-1.0/examples/basicTouchstonePlotting/Return%20Loss%20(Mag).png' width='800px'>

<h3>Phase of Return loss</h3>
<pre><code># plot phase of S11<br>
pylab.figure(2)<br>
pylab.title('Return Loss (Phase)')<br>
# all keyword arguments are passed to matplotlib.plot command<br>
horn.plot_s_deg(0,0, label='Broadband Horn Antenna', color='r', linewidth=2)<br>
</code></pre>

<img src='http://mwavepy.googlecode.com/svn/branches/mwavepy-1.0/examples/basicTouchstonePlotting/Return%20Loss%20(Phase).png' width='800px'>


<h3>Unwrapped Phase of Return loss</h3>
<pre><code># plot unwrapped phase of S11<br>
pylab.figure(3)<br>
pylab.title('Return Loss (Unwrapped Phase)')<br>
horn.plot_s_deg_unwrapped(0,0)<br>
<br>
</code></pre>
<img src='http://mwavepy.googlecode.com/svn/branches/mwavepy-1.0/examples/basicTouchstonePlotting/Return%20Loss%20(Unwrapped Phase).png' width='800px'>

<h3>Plot on Smith Chart</h3>
<pre><code># plot complex S11 on smith chart<br>
pylab.figure(5)<br>
horn.plot_s_smith(0,0, show_legend=False)<br>
pylab.title('Return Loss, Smith')<br>
</code></pre>

<img src='http://mwavepy.googlecode.com/svn/trunk/examples/basicTouchstonePlotting/Return%20Loss%2C%20Smith.png' width='800px'>

<pre><code># plot complex S11 on polar grid<br>
pylab.figure(4)<br>
horn.plot_s_polar(0,0, show_legend=False)<br>
pylab.title('Return Loss')<br>
</code></pre>

<img src='http://mwavepy.googlecode.com/svn/branches/mwavepy-1.0/examples/basicTouchstonePlotting/Return%20Loss.png' width='800px'>
<pre><code># uncomment to save all figures, <br>
#mvy.save_all_figs('.', format = ['png'])<br>
<br>
# show the plots <br>
pylab.show()<br>
<br>
</code></pre>