
import mwavepy as m	


from mwavepy.pythics_instruments import vna
from time import time

a=   time()
myvna = vna.vna_hp8720c("GPIB::16")

myvna.setDataFormatAscii()
print myvna.getError()

freqVector = myvna.getFrequencyAxis() # this may not work on other vna's
myvna.setS('s11') # this defaults to sending an OPC?, see help
s11 = myvna.getS(freqVector)	
myvna.setS('s21') # this defaults to sending an OPC?, see help
s21 = myvna.getS(freqVector)
myvna.setS('s12') # this defaults to sending an OPC?, see help
s12 = myvna.getS(freqVector)
myvna.setS('s22') # this defaults to sending an OPC?, see help
s22 = myvna.getS(freqVector)

myntwk = m.twoPort(s11,s21,s12,s22)
myntwk.writeTouchtone('c:\output.s2p')

b =  time() -a
print b
