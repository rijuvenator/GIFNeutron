''' Class for handling test beam measurements
'''
import os

class TBM(object):
    '''
    - GIFMeasurement class is designed to be a python class container for all relevant 
      meta data associated with a measurement: 
      - CSC  : chamber type (ME11 or ME21)
      - test : STEP Test type (27, 27s, 40)
      - HV   : Chamber high voltage (HV0V, 2900V, 3600V, etc.)
      - beam : Beam status (bOn, bOff)
      - uAtt : Upsteam source attenuation (u46, uOff, etc.)
      - dAtt : Downstream source attenuation (d15, dOff, etc.)
      - meas : Measurement number (m1966, m1977, etc.)
    '''
    def __init__(self, fn):
        self.fn = fn
        self.setInfo()
    def setInfo(self,ana_dataset=None):
        fileName  = os.path.basename(self.fn)
        nameList  = fileName.split('_')
        self.CSC  = nameList[0]
        self.test = nameList[1]
        self.HV   = nameList[2]
        self.beam = nameList[3]
        self.uAtt = nameList[4]
        self.dAtt = nameList[5]
        self.meas = nameList[6]
        self.time = nameList[7].strip('.root')
        self.ana_dataset = ana_dataset

#measDirMay16 = '/eos/cms/store/group/dpg_csc/comm_csc/gif/may16/'
measDirMay16 = '/store/group/dpg_csc/comm_csc/gif/may16/'
# Measurement instantiations
measurements = [

    TBM(measDirMay16+'ME11/sourceOFF/test27/ME11_Test27_HV0_bOn_uOff_dOff_m2250_t160508163702.root'),

    TBM(measDirMay16+'ME11/sourceOFF/test40/ME11_Test40_HV0_bOn_uOff_dOff_m1966_t160506015143.root'),

    TBM(measDirMay16+'ME11/d46/test27/ME11_Test27_HV0_bOn_u46_d46_m1977_t160506025710.root'),

    TBM(measDirMay16+'ME11/d46/test40/ME11_Test40_HV0_bOn_u46000_d46_m2040_t160506125054.root'),

    TBM(measDirMay16+'ME21/sourceOFF/test27/ME21_Test27_HV0_bOn_uOff_dOff_m2306_t160509094700.root'),

    TBM(measDirMay16+'ME21/sourceOFF/test40/ME21_Test40_HV0_bOn_uOff_dOff_m2312_t160509111100.root'),

    TBM(measDirMay16+'ME21/d15/test27/ME21_Test27_HV0_bOn_u46_d15_m2062_t160506220324.root'),

    TBM(measDirMay16+'ME21/d15/test40/ME21_Test40_HV0_bOn_u46_d15_m2064_t160506222510.root'),

]

for TBM in measurements:
    exec '%s = TBM' % TBM.meas

anaDatasetDir = '/afs/cern.ch/work/c/cschnaib/GIF/data/'
m2250.ana_dataset = anaDatasetDir + 'ana_ME21_Test27_HV0_bOn_uOff_dOff_m2306.root' 
m2312.ana_dataset = anaDatasetDir + 'ana_ME21_Test40_HV0_bOn_uOff_dOff_m2312.root'
m2062.ana_dataset = anaDatasetDir + 'ana_ME21_Test27_HV0_bOn_u46_d15_m2062.root'
m2064.ana_dataset = anaDatasetDir + 'ana_ME21_Test40_HV0_bOn_u46_d15_m2064.root'
m2250.ana_dataset = anaDatasetDir + 'ana_ME11_Test27_HV0_bOn_uOff_dOff_m2250.root'
m1966.ana_dataset = anaDatasetDir + 'ana_ME11_Test40_HV0_bOn_uOff_dOff_m1966.root'
m1977.ana_dataset = anaDatasetDir + 'ana_ME11_Test27_HV0_bOn_u46_d46_m1977.root'
m2040.ana_dataset = anaDatasetDir + 'ana_ME11_Test40_HV0_bOn_u46000_d46_m2040.root'


__all__ = ['measurements'] + [m.meas for m in measurements]


if __name__ == '__main__':
    for TBM in measurements:
        print TBM.CSC
        print TBM.test
        print TBM.HV
        print TBM.beam
        print TBM.uAtt
        print TBM.dAtt
        print TBM.meas
        print TBM.time
        print TBM.fn
        if m.ana_dataset: print m.ana_dataset
        print 
