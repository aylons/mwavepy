
# Introduction #

This page describes how to use **mwavepy** to calibrate data taken from a VNA. The explanation of calibration theory and calibration kit design is beyond the scope of this wiki page. This page describes how to calibrate a device under test (DUT), assuming you have measured an acceptable set of standards.

**mwavepy**'s calibration algorithm is generic, in that it will work with any set of standards. If you supply more calibration standards than is needed, **mwavepy** will implement a simple least-squares solution.


Calibrations are performed through  a Calibration class, which makes creating and working with calibrations easy.
Since **mwavepy-1.2** the Calibration class only requires two pieces of  information:
  * a list of measured Networks
  * a list of ideal Networks

The Network elements in each list must all be similar, (same #ports, same frequency info, etc) and must be aligned to each other, meaning the first element of ideals list must correspond to the first element of measured list.

Optionally, other information can be  provided for explicitness, such as,
  * calibration type
  * frequency information
  * reciprocity of embedding networks
  * etc

When this information is not provided **mwavepy** will determine it through inspection.


# One-Port #
Below are (hopefully) self-explanatory examples of increasing complexity, which should illustrate, by example, how to make a calibration.

## Simple One-port ##
This example is written to be instructive, not concise.
```

import mwavepy as mv


## created necessary data for Calibration class

# a list of Network types, holding 'ideal' responses
my_ideals = [\
	mv.Network('ideal/short.s1p'),
	mv.Network('ideal/open.s1p'),
	mv.Network('ideal/load.s1p'),
	]

# a list of Network types, holding 'measured' responses
my_measured = [\
	mv.Network('measured/short.s1p'),
	mv.Network('measured/open.s1p'),
	mv.Network('measured/load.s1p'),
	]

## create a Calibration instance
cal = mv.Calibration(\
	ideals = my_ideals,
	measured = my_measured,
	)


## run, and apply calibration to a DUT

# run calibration algorithm
cal.run() 

# apply it to a dut
dut = mv.Network('my_dut.s1p')
dut_caled = cal.apply_cal(dut)

# plot results
dut_caled.plot_s_db()
# save results 
dut_caled.write_touchstone()
```


## Concise One-port ##
This example is meant to be the same as the first except more concise.
```
import mwavepy as mv

my_ideals = mv.load_all_touchstones_in_dir('ideals/')
my_measured = mv.load_all_touchstones_in_dir('measured/')


## create a Calibration instance
cal = mv.Calibration(\
	ideals = [my_ideals[k] for k in ['short','open','load']],
	measured = [my_measured[k] for k in ['short','open','load']],
	)

## what you do with 'cal' may  may be similar to above example
```




# Two-port #
Two-port calibration is more involved than one-port. **mwavepy** supports two-port calibration using a 8-term error model based on the algorithm described in "A Generalization of the TSD Network-Analyzer Calibration Procedure, Covering n-Port Scattering-Parameter Measurements, Affected by Leakage Errors" by R.A. Speciale [here](http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1129282).

Like the one-port algorithm, the two-port calibration can handle any number of standards, providing that some fundamental constraints are met. In short, you need three two-port standards; one must be transmissive, and one must provide a known impedance and be reflective.

One draw-back of using the 8-term error model formulation (which is the same formulation used in TRL) is that  switch-terms may need to be measured in order to achieve a high quality calibration (this was pointed out to me by Dylan Williams).

## A note on switch-terms ##
Switch-terms are explained in Roger Marks's paper titled 'Formulations of the Basic Vector Network Analyzer Error Model including Switch-Terms' [here](http://www.google.com/url?sa=t&source=web&cd=1&ved=0CBYQFjAA&url=http%3A%2F%2Fieeexplore.ieee.org%2Fiel5%2F4119930%2F4119931%2F04119948.pdf%3F...&rct=j&q=marks%20switch%20terms&ei=Yj_JTaK-EsHIgQeLxsyOBg&usg=AFQjCNHvady0wYHdJjRmNns33nUPC2b1LA&cad=rja). Basically,  switch-terms account for the fact that the error networks change slightly depending on which port is being excited. This is due to the hardware of the VNA.

So how do you measure switch terms? With a custom measurement configuration on the VNA itself. I have support for switch terms in my HP8510C class [here](http://code.google.com/p/mwavepy/source/browse/trunk/mwavepy/virtualInstruments/vna.py#532), which you can use or extend to different VNA. Without switch-term measurements, your calibration quality will vary depending on properties of you VNA.

## Simple Two Port ##

Two-port calibration is accomplished in an identical way to one-port, except all the standards are two-port networks. This is even true of reflective standards (S21=S12=0). So if you measure reflective standards you must measure two of them simultaneously, and store information in a two-port. For example, connect a short to port-1 and a load to port-2, and save a two-port measurement as 'short,load.s2p' or similar.



```

import mwavepy as mv


## created necessary data for Calibration class

# a list of Network types, holding 'ideal' responses
my_ideals = [\
	mv.Network('ideal/thru.s2p'),
	mv.Network('ideal/line.s2p'),
	mv.Network('ideal/short, short.s2p'),
	]

# a list of Network types, holding 'measured' responses
my_measured = [\
	mv.Network('measured/thru.s2p'),
	mv.Network('measured/line.s2p'),
	mv.Network('measured/short, short.s2p'),
	]


## create a Calibration instance
cal = mv.Calibration(\
	ideals = my_ideals,
	measured = my_measured,
	)


## run, and apply calibration to a DUT

# run calibration algorithm
cal.run() 

# apply it to a dut
dut = mv.Network('my_dut.s2p')
dut_caled = cal.apply_cal(dut)

# plot results
dut_caled.plot_s_db()
# save results 
dut_caled.write_touchstone()
```

## Using s1p ideals in two-port calibration ##
Commonly, you have data for ideal data for reflective standards in the form of one-port touchstone files (ie s1p). To use this with mwavepy's two-port calibration method you need to create a two-port network that is a composite of the two networks. There is a function in the WorkingBand Class which will do this for you, called two\_port\_reflect.
```
short = mv.Network('ideals/short.s1p')
load = mv.Network('ideals/load.s1p')
short_load = wb.two_port_reflect(short, load)

```

# Using mwavepy to create ideal responses #

**mavepy** also has basic support for creation of simple standards. This is accomplished through the sub-module transmissionLine.



# Parameterized Self-calibration #
## One-Port ##
## Two-Port ##