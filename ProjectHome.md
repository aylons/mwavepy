
---

# Deprecation Warning: ~~mwavepy~~  scikit-rf #
**mwavepy** is becoming a [scikit](http://scikits.appspot.com/). This means that this site, and the project named **mwavepy** is being moved and renamed. **mwavepy** is being re-named to **scikit-rf** with an import name of **skrf**. The code-base has moved to [github](https://github.com/scikit-rf/scikit-rf/wiki).

# --------------> [www.scikit-rf.org](http://www.scikit-rf.org) <-------------- #

---

# Description #

**mwavepy** is an object-oriented approach to rf/microwave engineering
implemented in the Python programming language. It provides a general set of
objects and features which can be used to construct solutions to
specific problems.



# Help #
  * ## Documentation ( [HTML](http://packages.python.org/mwavepy/#), [PDF](http://mwavepy.googlecode.com/files/mwavepy-1.51.pdf) ) ##
  * ## [Screencast Tutorials](http://code.google.com/p/mwavepy/wiki/Screencast_Tutorials) ##
  * ## [Installation Help](http://packages.python.org/mwavepy/installation.html) ##
  * ## Post an [Issue ](http://code.google.com/p/mwavepy/issues/list) ##

The author welcomes feedback of all kinds, and is open to new developers! Please contact me directly at
> arsenovic at virginia.edu



# Features #
  * load touchstone (.s2p, s?p) files for data processing
  * provides basic algebraic operations on networks' scattering parameters
  * connect n-port networks
  * de-embed 2-port networks
  * plot network's scattering parameter data (dB, Phase (unwrapped), Smith chart)
  * save plots in vector format for publication (a feature of matplotlib)
  * 1-port calibration, given any number of standards (least squares)
  * 2-port calibration with support for switch-terms.
  * can be used with pyvisa for instrument control of some VNA's ( partial support for HP8510, HP8720, and R&S ZVA40 )
  * circuit design
  * provide basic TEM transmission line models, and some non-TEM transmission lines


# Other Open-Source Microwave Software #
  * [qucs](http://qucs.sourceforge.net/): circuit simulator (ADS-like)
  * [dataplot](http://www.h-renrew.de/h/dataplot/dataplot.html): a graphical interface for making plots of touchstone files, among other common file formats
  * [Pythics](http://code.google.com/p/pythics): instrument control with gui creation
