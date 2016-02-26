

# Introduction #

Add your content here.


# Quick Intro #

# Class Structure #

This class can support two models for TEM transmission lines:

1)simple media: in which the distributed circuit quantities are
NOT functions of frequency,
2)not-simple media:  in which the distributed circuit quantities
ART functions of frequency

## Simple vs Not-Simple Media ##
1) The simple media can be constructed with scalar values for the
distributed circuit quantities. then all methods for transmission
line properties( Z0, gamma) will take frequency as an argument.


2) The not-simple media must be constructed with array's for
distributed circuit quanties and a frequency array. alternativly,
you can construct this type of tline from propagation constant,
characterisitc impedance, and frequency information, through use of
the class method; from\_gamma\_Z0().

## Physics ##
A TEM transmission line can be described by a characterisitc
impedance and propagation constant, or by distributed impedance and
admittance. This description will be in terms of distributed
circuit quantities, given:

distributed Capacitance, C
distributed Inductance, I
distributed Resistance, R
distributed Conductance, G

from these the following quantities may be calculated, which
are functions of angular frequency (w):

distributed Impedance,  Z(w) = wR + jwI
distributed Admittance, Y'(w) = wG + jwC

from these we can calculate properties which define their wave
behavior:

characteristic Impedance, Z0(w) = sqrt(Z(w)/Y'(w))		[ohms](ohms.md)
propagation Constant,	gamma(w) = sqrt(Z(w)**Y'(w))	[none](none.md)**

given the following definitions, the components of propagation
constant are interpreted as follows:

positive real(gamma) = attenuation
positive imag(gamma) = forward propagation

this sign convention means that the transmission gain through a
distance, d, is given by,

S21 = exp(-gamma\*d)

and then finally these all produce methods which we use

electrical Length (theta)
input Impedance
relfection Coefficient