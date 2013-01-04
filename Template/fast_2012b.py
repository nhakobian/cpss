from mod_python import apache
export = apache.import_module("fast_2012b_export")

class template:
    def __init__(self):
        self.export = export
        author = [{'name':'ProposalID',
                   'fieldname':'proposalid',
                   'fieldtype':'integer',
                   'section': False},
                  {'name' : 'Number',
                   'fieldname' : 'numb',
                   'fieldtype' : 'integer',
                   'section'   : 'author',
                   'shortname' : '#'},
                  {'name':'Name',
                   'fieldname':'name',
                   'fieldtype':'text',
                   'section':'author'},
                  {'name':'E-mail',
                   'fieldname':'email',
                   'fieldtype':'text',
                   'section':'author'},
                  {'name':'Phone',
                   'fieldname':'phone',
                   'fieldtype':'text',
                   'section':'author'},
                  {'name':'Institution',
                   'fieldname':'institution',
                   'fieldtype':'institution',
                   'section':'author'},
                  {'name':'Thesis',
                   'fieldname':'thesis',
                   'fieldtype':'bool',
                   'section':'author'},
                  {'name':'Graduate Student',
                   'fieldname':'grad',
                   'fieldtype':'bool',
                   'section':'author',
                   'shortname' : 'Grad'}]

        self.author_order = { 1 : 'numb',
                         2 : 'name',
                         3 : 'email',
                         4 : 'phone',
                         5 : 'institution',
                         6 : 'thesis',
                         7 : 'grad' }

        proposal = [{'name':'ProposalID',
                     'fieldname':'proposalid',
                     'fieldtype':'integer',
                     'section': False},
                    {'name':'User',
                     'fieldname':'user',
                     'fieldtype':'text',
                     'section': False},
                    {'name':'Title',
                     'fieldname':'title',
                     'fieldtype':'text',
                     'size':'250',
                     'section':'propinfo'},
                    {'name':'Scientific Category',
                     'fieldname':'scientific_category',
                     'fieldtype':['Cometary', 'Planetary', 'Solar', 'Stellar',
                                  'High-mass Star Formation',
                                  'Low-mass Star Formation', 
                                  'Chemistry / Interstellar Medium',
                                  'Other Galactic', 'Galaxies - Detection', 
                                  'Galaxies - Mapping',
                                  'Cosmology', 'Other Extragalactic'],
                     'section':'propinfo'},
                    {'name':'Date',
                     'fieldname':'date',
                     'fieldtype':'date',
                     'section':'propinfo',
                     'info' : 'YYYY-MM-DD',
                     'line' : 2},
                    {'shortname':'TOO/Time Critical',
                     'name':'Target of Opportunity/Time Critical',
                     'fieldname':'toe',
                     'fieldtype':'bool',
                     'section':'propinfo',
                     'line':2},
                    {'name':'Level of Help Required',
                     'fieldname':'help_required',
                     'fieldtype':['None', 'Consultation',
                                  'Request Collaborator'],
                     'section':'propinfo',
                     'line' : 2},
                    {'name':'1cm Project',
                     'fieldname':'1cm',
                     'fieldtype':'bool',
                     'section':'propinfo',
                     'line':2},
                    {'name':'3mm Project',
                     'fieldname':'3mm',
                     'fieldtype':'bool',
                     'section':'propinfo',
                     'line':2},
                    {'name':'1mm Project',
                     'fieldname':'1mm',
                     'fieldtype':'bool',
                     'section':'propinfo',
                     'line':2},
                    {'name':'Abstract',
                     'fieldname':'abstract',
                     'fieldtype':'longtext',
                     'section':'abstract'},
                    {'name':'Special Requirements',
                     'fieldname':'special_requirements',
                     'fieldtype':'longtext',
                     'section':'special_requirements',
                     'check':[]},]

        self.fast_modes = {
            'SCI1_3MM_SP_WB' : {
                'obsmode' : 'SINGLEPOL',
                'userBW' : False,
                'userFreq' : True,
                'freqRange' : [85.0, 116.0],
                'config' : (
"""
tuning = {
    'restfreq' : %(freq)s, # [GHz] Line rest frequency
    'sideband' : USB,  # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.5, # [GHz] IF frequency
}

def setCorrelator(tuning):
    # lo1 = %(freq)s - 2.5
    clearastroband(0)
    configwideastroband(conf='LL')
""")
                },
            'SCI1_3MM_SP_SL' : {
                'obsmode' : 'SINGLEPOL',
                'userBW' : True,
                'userFreq' : True,
                'freqRange' : [85.0, 116.0],
                'config' : (
"""
tuning = {
    'restfreq' : %(freq)s, # [GHz] Line rest frequency
    'sideband' : %(tune)s,  # Sideband for first LO (LSB or USB)
    'IFfreq'   : %(if_freq)s, # [GHz] IF frequency
}

def setCorrelator(tuning):
    # 1st LO set to: %(first_lo)s GHz (not including doppler corrections)
    # Requested spectral line will be in the %(tune)s window of Band %(corr_band)s.
    clearastroband(0)
    configwideastroband(conf='LL')
    configastroband(%(corr_band)s, 'LL', %(slbw)s, %(freq)s, AUTO, 'none', 'none', bits=CORR_2BIT) # Custom Spectral Line
"""),
                },
            'SCI1_3MM_SP_CO' : { 
                'obsmode' : 'SINGLEPOL',
                'userBW' : True,
                'userFreq' : False,
                'freq' : '110.556042',
                'config' : (
"""
tuning = {
    'restfreq' : 110.556042,  # [GHz] Line rest frequency
    'sideband' : USB,    # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.535,   # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # lo1 = 108.021042
    configastroband(1, 'LL', %(userBW)s, 109.78216, AUTO, 109.78216, 'none', bits=CORR_2BIT) # C18O (USB)
    configastroband(2, 'LL', %(userBW)s, 110.201353, AUTO, 110.201353, 'none', bits=CORR_2BIT) # 13CO (USB)
    configastroband(3, 'LL', BW500, 102.560475, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(4, 'LL', BW500, 104.254851, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(5, 'LL', BW500, 103.615539, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(6, 'LL', BW500, 101.906132, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(7, 'LL', BW500, 101.201919, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(8, 'LL', %(userBW)s, 115.271204, AUTO, 115.271204, 'none', bits=CORR_2BIT) # 12CO (USB)
""")
                },
            'SCI1_3MM_SP_HCO+' : {
                'obsmode' : 'SINGLEPOL',
                'userBW' : True,
                'userFreq' : False,
                'freq' : '93.0699',
                'config' : (
"""
tuning = {
    'restfreq' : 93.0699,  # [GHz] Line rest frequency
    'sideband' : USB,    # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.05,   # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # lo1 = 91.0199
    configastroband(1, 'LL', %(userBW)s, 93.173505, AUTO, 93.173505, 'none', bits=CORR_2BIT) # N2H+ (USB)
    configastroband(2, 'LL', %(userBW)s, 88.631847, AUTO, 88.631847, 'none', bits=CORR_2BIT) # HCN (LSB)
    configastroband(3, 'LL', %(userBW)s, 89.188518, AUTO, 89.188518, 'none', bits=CORR_2BIT) # HCO+ (LSB)
    configastroband(4, 'LL', %(userBW)s, 85.925684, AUTO, 85.925684, 'none', bits=CORR_2BIT) # NH2D (LSB)
    configastroband(5, 'LL', %(userBW)s, 86.754288, AUTO, 86.754288, 'none', bits=CORR_2BIT) # H13CO+ (LSB)
    configastroband(6, 'LL', %(userBW)s, 86.340176, AUTO, 86.340176, 'none', bits=CORR_2BIT) # H13CN (LSB)
    configastroband(7, 'LL', %(userBW)s, 97.980968, AUTO, 97.980968, 'none', bits=CORR_2BIT) # CS (USB)
    configastroband(8, 'LL', BW500, 88.002153, AUTO, 'none', 'none', bits=CORR_2BIT)
""")
                },
            
            'SCI1_3MM_C23_WB' : {
                'obsmode' : 'CARMA23',
                'userBW' : False,
                'userFreq' : True,
                'freqRange' : [85.0, 116.0],
                'config' : (
"""
tuning = {
    'restfreq' : %(freq)s, # [GHz] Line rest frequency
    'sideband' : USB,  # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.5, # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # lo1 = %(freq)s - 2.5
    configwideastroband(conf='CARMA23', bits=CORR_2BIT)
""")
                },
            'SCI1_3MM_C23_SL' : {
                'obsmode' : 'CARMA23',
                'userBW' : True,
                'userFreq' : True,
                'freqRange' : [85.0, 116.0],
                'config' : (
"""
tuning = {
    'restfreq' : %(freq)s, # [GHz] Line rest frequency
    'sideband' : %(tune)s,  # Sideband for first LO (LSB or USB)
    'IFfreq'   : %(if_freq)s, # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # 1st LO set to: %(first_lo)s GHz (not including doppler corrections)
    # Requested spectral line will be in the %(tune)s window of Band %(corr_band)s.
    configwideastroband(conf='MAXSENS_CARMA23')
    configastroband(%(corr_band)s, 'CARMA23', %(slbw)s, %(freq)s, AUTO, 'none', 'none', bits=CORR_2BIT) # Custom Spectral Line
""")
                },
            'SCI1_3MM_C23_CO' : { 
                'obsmode' : 'CARMA23',
                'userBW' : True,
                'userFreq' : False,
                'freq' : '110.556042',
                'config' : (
"""
tuning = {
    'restfreq' : 110.556042,  # [GHz] Line rest frequency
    'sideband' : USB,    # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.535,   # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # lo1 = 108.021042
    configwideastroband(conf='MAXSENS_CARMA23')
    configastroband(1, 'CARMA23', BW500, 101.201919, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(3, 'CARMA23', %(userBW)s, 109.78216, AUTO, 109.78216, 'none', bits=CORR_2BIT) # C18O (USB)
    configastroband(5, 'CARMA23', %(userBW)s, 110.201353, AUTO, 110.201353, 'none', bits=CORR_2BIT) # 13CO (USB)
    configastroband(7, 'CARMA23', %(userBW)s, 115.271204, AUTO, 115.271204, 'none', bits=CORR_2BIT) # 12CO (USB)
""")
                },
            'SCI1_3MM_C23_HCO+' : {
                'obsmode' : 'CARMA23',
                'userBW' : True,
                'userFreq' : False,
                'freq' : '87.5',
                'config' : (
"""
tuning = {
    'restfreq' : 87.5,  # [GHz] Line rest frequency
    'sideband' : USB,    # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.5,   # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # lo1 = 85
    configwideastroband(conf='MAXSENS_CARMA23')
    configastroband(1, 'CARMA23', BW500, 88.25, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(3, 'CARMA23', %(userBW)s, 88.631847, AUTO, 88.631847, 'none', bits=CORR_2BIT) # HCN
    configastroband(5, 'CARMA23', %(userBW)s, 89.188518, AUTO, 89.188518, 'none', bits=CORR_2BIT) # HCO+
    configastroband(7, 'CARMA23', %(userBW)s, 93.173505, AUTO, 93.173505, 'none', bits=CORR_2BIT) # N2H+
""")
                },
            
            'SCI1_1MM_SP_WB' : {
                'obsmode' : 'SINGLEPOL',
                'userBW' : False,
                'userFreq' : True,
                'freqRange' : [215.0, 270.0],
                'config' : (
"""
tuning = {
    'restfreq' : %(freq)s, # [GHz] Line rest frequency
    'sideband' : USB,  # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.5, # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # lo1 = %(freq)s - 2.5
    configwideastroband(conf='LL', bits=CORR_2BIT)
""")
                },
            'SCI1_1MM_SP_SL' : { 
                'obsmode' : 'SINGLEPOL',
                'userBW' : True,
                'userFreq' : True,
                'freqRange' : [215.0, 270.0],
                'config' : (
"""
tuning = {
    'restfreq' : %(freq)s,  # [GHz] Line rest frequency
    'sideband' : %(tune)s,  # Sideband for first LO (LSB or USB)
    'IFfreq'   : %(if_freq)s, # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # 1st LO set to: %(first_lo)s GHz (not including doppler corrections)
    # Requested spectral line will be in the %(tune)s window of Band %(corr_band)s.
    configwideastroband(conf='LL')
    configastroband(%(corr_band)s, 'LL', %(slbw)s, %(freq)s, AUTO, 'none', 'none', bits=CORR_2BIT) # Custom Spectral Line
"""),
                },
            'SCI1_1MM_SP_CO' : {
                'obsmode' : 'SINGLEPOL',
                'userBW' : True,
                'userFreq' : False,
                'freq' : '225',
                'config' : (
"""
tuning = {
    'restfreq' : 225,  # [GHz] Line rest frequency
    'sideband' : USB,    # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.75,   # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # lo1 = 222.25
    configastroband(1, 'LL', BW500, 221.00, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(2, 'LL', %(userBW)s, 219.560319, AUTO, 219.560319, 'none', bits=CORR_2BIT) # C18O (LSB)
    configastroband(3, 'LL', %(userBW)s, 220.398686, AUTO, 220.398686, 'none', bits=CORR_2BIT) # 13CO (LSB)
    configastroband(4, 'LL', %(userBW)s, 230.538, AUTO, 230.538, 'none', bits=CORR_2BIT) # 12CO (USB)
    configastroband(5, 'LL', BW500, 217.56, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(6, 'LL', BW500, 216.25, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(7, 'LL', BW500, 219.25, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(8, 'LL', BW500, 218.45, AUTO, 'none', 'none', bits=CORR_2BIT)
""")
                },
            
            'SCI1_1MM_DP_WB' : { 
                'obsmode' : 'DUALPOL',
                'userBW' : False,
                'userFreq' : True,
                'freqRange' : [215.0, 270.0],
                'config' : (
"""
tuning = {
    'restfreq' : %(freq)s, # [GHz] Line rest frequency
    'sideband' : USB,  # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.5, # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # lo1 = %(freq)s - 2.5
    configwideastroband(conf='DUALPOL', bits=CORR_2BIT)
""")
                },
            'SCI1_1MM_DP_SL' : { 
                'obsmode' : 'DUALPOL',
                'userBW' : True,
                'userFreq' : True,
                'freqRange' : [215.0, 270.0],
                'config' : (
"""
tuning = {
    'restfreq' : %(freq)s, # [GHz] Line rest frequency
    'sideband' : %(tune)s,  # Sideband for first LO (LSB or USB)
    'IFfreq'   : %(if_freq)s, # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # 1st LO set to: %(first_lo)s GHz (not including doppler corrections)
    # Requested spectral line will be in the %(tune)s window of Band %(corr_band)s.
    configwideastroband(conf='DUALPOL')
    configastroband(%(corr_band)s, 'DUALPOL', %(slbw)s, %(freq)s, AUTO, 'none', 'none', bits=CORR_2BIT) # Custom Spectral Line
"""),
                },

            'SCI1_1MM_DP_CO' : {
                'obsmode' : 'DUALPOL',
                'userBW' : True,
                'userFreq' : False,
                'freq' : '225',
                'config' : (
"""
tuning = {
    'restfreq' : 225,  # [GHz] Line rest frequency
    'sideband' : USB,    # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.75,   # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # lo1 = 222.25
    configastroband(1, 'DUALPOL', BW500, 221.00, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(3, 'DUALPOL', %(userBW)s, 219.560319, AUTO, 219.560319, 'none', bits=CORR_2BIT) # C18O (LSB)
    configastroband(5, 'DUALPOL', %(userBW)s, 220.398686, AUTO, 220.398686, 'none', bits=CORR_2BIT) # 13CO (LSB)
    configastroband(7, 'DUALPOL', %(userBW)s, 230.538, AUTO, 230.538, 'none', bits=CORR_2BIT) # 12CO (USB)
""")
                },
            
            'SCI1_1MM_FP_WB' : {
                'obsmode' : 'FULLPOL',
                'userBW' : False,
                'userFreq' : True,
                'freqRange' : [215.0, 270.0],
                'config' : (
"""
tuning = {
    'restfreq' : %(freq)s, # [GHz] Line rest frequency
    'sideband' : USB,  # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.5, # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # lo1 = %(freq)s - 2.5
    configwideastroband(conf='FULLPOL', bits=CORR_2BIT)
""")
                },
            'SCI1_1MM_FP_SL' : {
                'obsmode' : 'FULLPOL',
                'userBW' : True,
                'userFreq' : True,
                'freqRange' : [215.0, 270.0],
                'config' : (
"""
tuning = {
    'restfreq' : %(freq)s, # [GHz] Line rest frequency
    'sideband' : %(tune)s,  # Sideband for first LO (LSB or USB)
    'IFfreq'   : %(if_freq)s, # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # 1st LO set to: %(first_lo)s GHz (not including doppler corrections)
    # Requested spectral line will be in the %(tune)s window of Band %(corr_band)s.
    configwideastroband(conf='FULLSTOKES')
    configastroband(%(corr_band)s, 'FULLSTOKES', %(slbw)s, %(freq)s, AUTO, 'none', 'none', bits=CORR_2BIT) # Custom Spectral Line
"""),
                },
            'SCI1_1MM_FP_CO' : {
                'obsmode' : 'FULLPOL',
                'userBW' : True,
                'userFreq' : False,
                'freq' : '225',
                'config' : (
"""
tuning = {
    'restfreq' : 225,  # [GHz] Line rest frequency
    'sideband' : USB,    # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.75,   # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    # lo1 = 222.25
    configastroband(1, 'FULLSTOKES', BW500, 221.00, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(3, 'FULLSTOKES', %(userBW)s, 219.560319, AUTO, 219.560319, 'none', bits=CORR_2BIT) # C18O (LSB)
    configastroband(5, 'FULLSTOKES', %(userBW)s, 220.398686, AUTO, 220.398686, 'none', bits=CORR_2BIT) # 13CO (LSB)
    configastroband(7, 'FULLSTOKES', %(userBW)s, 230.538, AUTO, 230.538, 'none', bits=CORR_2BIT) # 12CO (USB)
""")
                    },
            
            'SCI2_1CM_SP_WB' : {
                'obsmode' : 'SINGLEPOL',
                'userBW' : False,
                'userFreq' : False,
                'freq' : '35.938',
                'config' : (
"""
tuning = {
    'restfreq' : 35.938, # [GHz] Line rest frequency
    'sideband' : LSB,  # Sideband for first LO (LSB or USB)
    'IFfreq'   : 0, # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    configwideastroband(conf='LL', bits=CORR_2BIT)
""")
                },
            'SCI2_3MM_SP_WB' : { 
                'obsmode' : 'SINGLEPOL',
                'userBW' : False,
                'userFreq' : True,
                'freqRange' : [85.0, 105.0],
                'config' : (
"""
tuning = {
    'restfreq' : %(freq)s, # [GHz] Line rest frequency
    'sideband' : LSB,  # Sideband for first LO (LSB or USB)
    'IFfreq'   : 0, # [GHz] IF frequency
}

def setCorrelator(tuning):
    clearastroband(0)
    configwideastroband(conf='LL', bits=CORR_2BIT)
""")
                },
            }

        source = [
            {
                'name':'ProposalID',
                'fieldname':'proposalid',
                'fieldtype':'integer',
                'section' :False
                },
            {
                'name' : 'Number',
                'shortname':'#',
                'fieldname' : 'numb',
                'fieldtype' : 'integer',
                'section'   : 'source',
                'line'      : 1
                },
            {
                'name':'Source Name',
                'shortname':'Source',
                'fieldname':'f_sourcename',
                'fieldtype':'text',
                'section':'source',
                'line' : 1
                },
            {
                'name':'Right Ascension',
                'shortname':'RA',
                'fieldname':'f_ra',
                'fieldtype':'text',
                'section':'source',
                'line' : 1,
                'info' : 'J2000',
                'check' : ['NoNull', 'NoSpaces', 'FastraCheck']
                },
            {
                'name':'Declination',
                'shortname':'DEC',
                'fieldname':'f_dec',
                'fieldtype':'text',
                'section':'source',
                'line' : 1,
                'info' : 'J2000',
                'check' : ['NoNull', 'NoSpaces', 'FastdecCheck']
                },
            {
                'name':'LSR Velocity',
                'shortname':'V_LSR',
                'fieldname' : 'f_vlsr',
                'fieldtype' : 'text',
                'section' : 'source',
                'line' : 1,
                'info' : 'km/s',
                'check' : ['NoNull', 'num_float'],
                },
            {
                'name':'Track Length',
                'shortname':'Length',
                'fieldname' : 'f_time',
                'fieldtype' : 'text',
                'section' : 'source',
                'line' : 1,
                #'info' : '',
                'check' : ['NoNull', 'Numeric', 'FastTrackLength'],
                },
            {
                'name':'Array Configuration',
                'shortname':'Array',
                'fieldname' : 'f_array',
                'fieldtype' : ['A', 'B', 'C', 'D', 'E', 'SH', 'SL'],
                'section' : 'source',
                'line' : 1,
                #'info' : '',
                'check' : ['NoNull', 'FastArrayConfig'],
                },
            {
                'name':'Correlator Mode',
                'shortname':'Mode',
                'fieldname' : 'f_corrconfig',
                'fieldtype' : sorted(self.fast_modes.keys()),
                'section' : 'source',
                'line' : 1,
                #'info' : '',
                'check' : ['NoNull'],
                },
            {
                'name':'Frequency',
                'shortname':'Freq',
                'fieldname' : 'f_freq',
                'fieldtype' : 'text',
                'section' : 'source',
                'line' : 1,
                #'info' : '',
                'check' : ['FastFreqCheck'],
                },
            {
                'name':'Spectral Line Bandwidth',
                'shortname':'BW',
                'fieldname' : 'f_slbw',
                'fieldtype' : ['BW250', 'BW125', 'BW62', 'BW31', 'BW8', 'BW2'],
                'section' : 'source',
                'line' : 1,
                #'info' : '',
                'check' : ['FastBWCheck'],
                },
            {
                'name':'Mosaic',
                'shortname':'Mosaic',
                'fieldname' : 'f_mosaic',
                'fieldtype' : ['7 Point'],
                'section' : 'source',
                'line' : 1,
                #'info' : '',
                'check' : [],
                },
            
            ]

        self.source_order = { 
            1 : 'numb',
            2 : 'f_sourcename',
            3 : 'f_ra',
            4 : 'f_dec',
            5 : 'f_vlsr',
            6 : 'f_time',
            7 : 'f_array',
            8 : 'f_corrconfig',
            9 : 'f_freq',
            10 : 'f_slbw',
            11 : 'f_mosaic',
            }
                              
       
        self.sections = [{'section' : 'propinfo',
                          'name'    : 'General Proposal Information',
                          'type'    : 'general',
                          'table'   : 'proposal'},
                         {'section' : 'author',
                          'name'    : 'Authors List',
                          'type'    : 'repeat',
                          'table'   : 'author'},
                         {'section' : 'abstract',
                          'name'    : 'Abstract',
                          'type'    : 'general',
                          'table'   : 'proposal'},
                         {'section' : 'source',
                          'name'    : 'Source Information',
                          'type'    : 'repeat',
                          'table'   : 'source'},
                         {'section' : 'special_requirements',
                          'name'    : 'Special Requirements',
                          'type'    : 'general',
                          'table'   : 'proposal'},]

        self.tables = {'proposal' : { 'value' : proposal,
                                      'type'  : 'single'},
                       'source'   : { 'value' : source,
                                      'type'  : 'repeat'},
                       'author'   : { 'value' : author,
                                      'type'  : 'repeat'}}
