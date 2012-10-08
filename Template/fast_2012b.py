class template:
    def __init__(self):
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

        fast_modes = {
            'SCI1_3MM_SP_WB' : {
                restFreq = True,
                userWB = False,
                userFreq = False,
                config = (
"""
tuning = {
    'restfreq' : %s # [GHz] Line rest frequency
    'sideband' : 'USB',  # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.5, # [GHz] IF frequency

def setCorrelator(tuning):
#    lo1 = %s - 2.5 = %s
    configwideastroband('LL', bits=CORR_2BIT)
""")
                },
            'SCI1_3MM_SP_SL' : {
                config = (
"""
tuning = {
    'restfreq' : %s # [GHz] Line rest frequency
    'sideband' : 'USB',  # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.5, # [GHz] IF frequency

def setCorrelator(tuning):
#    lo1 = %s - 2.5 = %s
    if (tuning['restfreq'] > 92.0) and (tuning['restfreq'] < 113.0):
        slband = 2
    else:
        slband = 7

    configwideastroband('LL')
    configastroband(slband, "LL", %s, AUTO, %s, 'none', bits=CORR_2BIT) # Custom Spectral Line
""")
                },
            'SCI1_3MM_SP_CO' : { 
                config = (
"""
tuning = {
    'restfreq' : 110.556042,  # [GHz] Line rest frequency
    'sideband' : USB,    # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.535,   # [GHz] IF frequency
}
def setCorrelator(tuning):
#    lo1 = 108.021042
    configastroband(1, "LL", BW31, 109.78216, AUTO, 109.78216, 'none', bits=CORR_2BIT) # C18O (USB)
    configastroband(2, "LL", BW31, 110.201353, AUTO, 110.201353, 'none', bits=CORR_2BIT) # 13CO (USB)
    configastroband(3, "LL", BW500, 102.560475, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(4, "LL", BW500, 104.254851, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(5, "LL", BW500, 103.615539, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(6, "LL", BW500, 101.906132, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(7, "LL", BW500, 101.201919, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(8, "LL", BW31, 115.271204, AUTO, 115.271204, 'none', bits=CORR_2BIT) # 12CO (USB)
""")
                },
            'SCI1_3MM_SP_HCO+' : {
                config = (
"""
tuning = {
    'restfreq' : 93.0699,  # [GHz] Line rest frequency
    'sideband' : USB,    # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.05,   # [GHz] IF frequency
}
def setCorrelator(tuning):
#    lo1 = 91.0199
    configastroband(1, "LL", BW8, 93.173505, AUTO, 93.173505, 'none', bits=CORR_2BIT) # N2H+ (USB)
    configastroband(2, "LL", BW8, 88.631847, AUTO, 88.631847, 'none', bits=CORR_2BIT) # HCN (LSB)
    configastroband(3, "LL", BW8, 89.188518, AUTO, 89.188518, 'none', bits=CORR_2BIT) # HCO+ (LSB)
    configastroband(4, "LL", BW8, 85.925684, AUTO, 85.925684, 'none', bits=CORR_2BIT) # NH2D (LSB)
    configastroband(5, "LL", BW8, 86.754288, AUTO, 86.754288, 'none', bits=CORR_2BIT) # H13CO+ (LSB)
    configastroband(6, "LL", BW8, 86.340176, AUTO, 86.340176, 'none', bits=CORR_2BIT) # H13CN (LSB)
    configastroband(7, "LL", BW8, 97.980968, AUTO, 97.980968, 'none', bits=CORR_2BIT) # CS (USB)
    configastroband(8, "LL", BW500, 88.002153, AUTO, 'none', 'none', bits=CORR_2BIT)
""")
                },
            
            'SCI1_3MM_C23_WB' : { },
            'SCI1_3MM_C23_SL' : { },
            'SCI1_3MM_C23_CO' : { 
                    config = (
"""
tuning = {
    'restfreq' : 110.556042,  # [GHz] Line rest frequency
    'sideband' : USB,    # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.535,   # [GHz] IF frequency
}
def setCorrelator(tuning):
#    lo1 = 108.021042
    configwideastroband(conf="MAXSENS_CARMA23")
    configastroband(1, "CARMA23", BW500, 101.201919, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(3, "CARMA23", BW31, 109.78216, AUTO, 109.78216, 'none', bits=CORR_2BIT) # C18O (USB)
    configastroband(5, "CARMA23", BW31, 110.201353, AUTO, 110.201353, 'none', bits=CORR_2BIT) # 13CO (USB)
    configastroband(7, "CARMA23", BW31, 115.271204, AUTO, 115.271204, 'none', bits=CORR_2BIT) # 12CO (USB)
""")
                    },
            'SCI1_3MM_C23_HCO+' : {
                config = (
"""
tuning = {
    'restfreq' : 87.5,  # [GHz] Line rest frequency
    'sideband' : USB,    # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.5,   # [GHz] IF frequency
}
def setCorrelator(tuning):
#    lo1 = 85
    configwideastroband(conf="MAXSENS_CARMA23")
    configastroband(1, "CARMA23", BW500, 88.25, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(3, "CARMA23", BW31, 88.631847, AUTO, 88.631847, 'none', bits=CORR_2BIT) # HCN
    configastroband(5, "CARMA23", BW31, 89.188518, AUTO, 89.188518, 'none', bits=CORR_2BIT) # HCO+
    configastroband(7, "CARMA23", BW31, 93.173505, AUTO, 93.173505, 'none', bits=CORR_2BIT) # N2H+
""")
                },
            
            'SCI1_1MM_SP_WB' : { },
            'SCI1_1MM_SP_SL' : { },
            'SCI1_1MM_SP_CO' : {
                    config = (
"""
tuning = {
    'restfreq' : 225,  # [GHz] Line rest frequency
    'sideband' : USB,    # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.75,   # [GHz] IF frequency
}
def setCorrelator(tuning):
#    lo1 = 222.25
    configastroband(1, "LL", BW500, 221.00, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(2, "LL", BW31, 219.560319, AUTO, 219.560319, 'none', bits=CORR_2BIT) # C18O (LSB)
    configastroband(3, "LL", BW31, 220.398686, AUTO, 220.398686, 'none', bits=CORR_2BIT) # 13CO (LSB)
    configastroband(4, "LL", BW31, 230.538, AUTO, 230.538, 'none', bits=CORR_2BIT) # 12CO (USB)
    configastroband(5, "LL", BW500, 217.56, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(6, "LL", BW500, 216.25, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(7, "LL", BW500, 219.25, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(8, "LL", BW500, 218.45, AUTO, 'none', 'none', bits=CORR_2BIT)
""")
                    
                    },
            
            'SCI1_1MM_DP_WB' : { },
            'SCI1_1MM_DP_SL' : { },
            'SCI1_1MM_DP_CO' : {
                    config = (
"""
tuning = {
    'restfreq' : 225,  # [GHz] Line rest frequency
    'sideband' : USB,    # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.75,   # [GHz] IF frequency
}
def setCorrelator(tuning):
#    lo1 = 222.25
    configastroband(1, "DUALPOL", BW500, 221.00, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(3, "DUALPOL", BW31, 219.560319, AUTO, 219.560319, 'none', bits=CORR_2BIT) # C18O (LSB)
    configastroband(5, "DUALPOL", BW31, 220.398686, AUTO, 220.398686, 'none', bits=CORR_2BIT) # 13CO (LSB)
    configastroband(7, "DUALPOL", BW31, 230.538, AUTO, 230.538, 'none', bits=CORR_2BIT) # 12CO (USB)
""")
                    },
            
            'SCI1_1MM_FP_WB' : { },
            'SCI1_1MM_FP_SL' : { },
            'SCI1_1MM_FP_CO' : {
                    config = (
"""
tuning = {
    'restfreq' : 225,  # [GHz] Line rest frequency
    'sideband' : USB,    # Sideband for first LO (LSB or USB)
    'IFfreq'   : 2.75,   # [GHz] IF frequency
}
def setCorrelator(tuning):
#    lo1 = 222.25
    configastroband(1, "FULLSTOKES", BW500, 221.00, AUTO, 'none', 'none', bits=CORR_2BIT)
    configastroband(3, "FULLSTOKES", BW31, 219.560319, AUTO, 219.560319, 'none', bits=CORR_2BIT) # C18O (LSB)
    configastroband(5, "FULLSTOKES", BW31, 220.398686, AUTO, 220.398686, 'none', bits=CORR_2BIT) # 13CO (LSB)
    configastroband(7, "FULLSTOKES", BW31, 230.538, AUTO, 230.538, 'none', bits=CORR_2BIT) # 12CO (USB)
""")
                    },
            
            'SCI2_1CM_SP_WB' : { },
            'SCI2_3MM_SP_WB' : { },
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
                'check' : ['NoNull', 'NoSpaces', 'raCheck']
                },
            {
                'name':'Declination',
                'shortname':'DEC',
                'fieldname':'f_dec',
                'fieldtype':'text',
                'section':'source',
                'line' : 1,
                'info' : 'J2000',
                'check' : ['NoNull', 'NoSpaces', 'decCheck']
                },
            {
                'name':'LSR Velocity',
                'shortname':'V_LSR',
                'fieldname' : 'f_vlsr',
                'fieldtype' : 'text',
                'section' : 'source',
                'line' : 1,
                #'info' : '',
                #'check' : [],
                },
            {
                'name':'Track Length',
                'shortname':'Length',
                'fieldname' : 'f_time',
                'fieldtype' : 'text',
                'section' : 'source',
                'line' : 1,
                #'info' : '',
                #'check' : [],
                },
            {
                'name':'Correlator Mode',
                'shortname':'Mode',
                'fieldname' : 'f_corrconfig',
                'fieldtype' : fast_modes,
                'section' : 'source',
                'line' : 1,
                #'info' : '',
                #'check' : [],
                },
            {
                'name':'Frequency',
                'shortname':'Freq',
                'fieldname' : 'f_bfreq',
                'fieldtype' : 'text',
                'section' : 'source',
                'line' : 1,
                #'info' : '',
                #'check' : [],
                },
            {
                'name':'Spectral Line Frequency',
                'shortname':'Line Freq',
                'fieldname' : 'f_slfreq',
                'fieldtype' : 'text',
                'section' : 'source',
                'line' : 1,
                #'info' : '',
                #'check' : [],
                },
            {
                'name':'Spectral Line Bandwidth',
                'shortname':'BW',
                'fieldname' : 'f_slbw',
                'fieldtype' : ['62 MHz', '31 MHz', '8 MHz', '2 MHz'],
                'section' : 'source',
                'line' : 1,
                #'info' : '',
                #'check' : [],
                },
            {
                'name':'Mosaic',
                'shortname':'Mosaic',
                'fieldname' : 'f_mosaic',
                'fieldtype' : ['test'],
                'section' : 'source',
                'line' : 1,
                #'info' : '',
                #'check' : [],
                },
            
            ]

        self.source_order = { 
            1 : 'numb',
            2 : 'f_sourcename',
            3 : 'f_ra',
            4 : 'f_dec',
            5 : 'f_vlsr',
            6 : 'f_time',
            7 : 'f_corrconfig',
            8 : 'f_bfreq',
            9 : 'f_slfreq',
            10: 'f_slbw',
            11: 'f_mosaic',
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
