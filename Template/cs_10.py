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
                     'section':'propinfo'},
                    {'name':'Date',
                     'fieldname':'date',
                     'fieldtype':'date',
                     'section':'propinfo',
                     'info' : 'YYYY-MM-DD'},
                    {'name':'Target Of Opportunity',
                     'fieldname':'toe',
                     'fieldtype':'bool',
                     'section':'propinfo'},
                    {'name':'Scientific Category',
                     'fieldname':'scientific_category',
                     'fieldtype':['Planetary', 'Solar', 'Stellar',
                                  'Galactic', 'Extragalactic', 'Comet'],
                     'section':'propinfo',
                     'line' : 2},
                    {'name':'Type Of Observation',
                     'fieldname':'type_of_observation',
                     'fieldtype': ['Continuum', 'Spectral Line', 'Both'],
                     'section':'propinfo',
                     'line' : 2},
                    {'name':'Frequency Band',
                     'fieldname':'frequency_band',
                     #'fieldtype':['3mm', '1mm', '1cm', '3mm & 1mm',
                     #             '1mm & 1cm', '3mm & 1cm', 'All'],
                     'fieldtype':['1mm', '3mm', '3mm & 1mm'],
                     'section':'propinfo',
                     'line' : 2},
                    {'name':'Level of Help Required',
                     'fieldname':'help_required',
                     'fieldtype':['None', 'Consultation',
                                  'Request Collaborator'],
                     'section':'propinfo',
                     'line' : 2},
                    {'name':'Abstract',
                     'fieldname':'abstract',
                     'fieldtype':'longtext',
                     'section':'abstract'},
                    {'name':'Special Requirements',
                     'fieldname':'special_requirements',
                     'fieldtype':'longtext',
                     'section':'special_requirements'},
                    {'name':'Scientific Justification',
                     'fieldname':'scientific_justification',
                     'fieldtype':'longtext',
                     'section':'scientific_justification'},
                    {'name':'Technical Justification',
                     'fieldname':'technical_justification',
                     'fieldtype':'longtext',
                     'section':'technical_justification'}]
         
        source = [{'name':'ProposalID',
                   'fieldname':'proposalid',
                   'fieldtype':'integer',
                   'section' :False},
                  {'name' : 'Number',
                   'shortname':'#',
                   'fieldname' : 'numb',
                   'fieldtype' : 'integer',
                   'section'   : 'source',
                   'line'      : 1},
                  {'name':'Obsblock Name',
                   'shortname':'Obsblk',
                   'fieldname':'obsblock',
                   'fieldtype':'text',
                   'section':'source',
                   'line' : 1,
                   'check': ['NoNull', 'obsblockCheck']},
                  {'name':'Array Configuration',
                   'shortname':'Array',
                   'fieldname':'array_config',
                   'fieldtype':['A', 'B', 'C', 'D', 'E'],
#                   'fieldtype':['B', 'C', 'D', 'E'],
                   'section':'source',
                   'line' : 1},
                  {'name':'Frequency of Observation',
                   'shortname':'Freq',
                   'fieldname':'corr_frequency',
                   'fieldtype':'text',
                   'section':'source',
                   'line' : 1,
                   'info' : 'GHz',
                   'check' : ['NoNull', 'Numeric']},
                  {'name':'Source Name',
                   'shortname':'Source',
                   'fieldname':'name',
                   'fieldtype':'text',
                   'section':'source',
                   'line' : 1},
                  {'name':'Right Ascension',
                   'shortname':'RA',
                   'fieldname':'ra',
                   'fieldtype':'text',
                   'section':'source',
                   'line' : 1,
                   'info' : 'J2000',
                   'check' : ['NoNull', 'raCheck']},
                  {'name':'Declination',
                   'shortname':'DEC',
                   'fieldname':'dec',
                   'fieldtype':'text',
                   'section':'source',
                   'line' : 1,
                   'info' : 'J2000',
                   'check' : ['NoNull', 'decCheck']},
                  {'name':'Number of Mosaic Fields',
                   'shortname':'# Fields',
                   'fieldname':'numb_fields',
                   'fieldtype':'text',
                   'section':'source',
                   'line' : 1,
                   'check': ['NoNull', 'Integer',
                             'NoZero']},
                  #Begin Correlator Stuff
                  {'name':'Species or Transition Name',
                   'shortname':'Species',
                   'fieldname':'species',
                   'fieldtype':'text',
                   'section':'source',
                   'line' : 1},
                  {'name':'Channel Width',
                   'shortname':'Width',
                   'fieldname':'channel_width',
                   'fieldtype':'text',
                   'section':'source',
                   'line' : 1,
                   'info' : 'MHz',
                   'check' : ['NoNull', 'Numeric']},
                  {'name':'Required RMS',
                   'shortname':'RMS',
                   'fieldname':'rms',
                   'fieldtype':'text',
                   'section':'source',
                   'line' : 1,
                   'info' : 'mJy/beam',
                   'check' : ['NoNull', 'Numeric']},
                  #Begin Optional A Array Info
                  #{'name':'Point Source',
                  # 'shortname':'Point',
                  # 'fieldname':'point',
                  # 'fieldtype':['Point Source', 'Extended Source'],
                  # 'section':'source',
                  # 'line' : 1},
                  {'name':'Can Self-Calibrate',
                   'shortname':'Self Cal',
                   'fieldname':'self_cal',
                   'fieldtype':'bool',
                   'section':'source',
                   'line' : 1,
                   'nosummary' : True},
                  #{'name':'Flux Density',
                  # 'shortname':'Flux',
                  # 'fieldname':'flux_density',
                  # 'fieldtype':'text',
                  # 'section':'source',
                  # 'line' : 1,
                  # 'info' : 'Jy/beam',
                  # 'check' : ['NoNull', 'Numeric']},
                  {'name':'Hours Requested',
                   'shortname':'Hrs Req',
                   'fieldname':'min_max',
                   'fieldtype':'text',
                   'section':'source',
                   'line' : 1,
                   'info' : 'Hours',
                   'check' : ['NoNull', 'Numeric']},
                  {'name':'Minimum Number of Antennas',
                   'shortname':'Min Ant',
                   'fieldname':'min_ant',
                   'fieldtype':'text',
                   'section':'source',
                   'line' : 1,
                   'info' : '# Antennas',
                   'check' : ['NoNull', 'Integer', 'antCheck']},
                  {'name':'Flexible Hour Angle?',
                   'shortname':'Flex.HA',
                   'fieldname':'fill',
                   'fieldtype':'bool',
                   'section':'source',
                   'line' : 1,
                   'info' : 'Check if yes'},
                  {'name':'Image/SNR',
                   'shortname':'Img/SNR',
                   'fieldname':'imaging',
                   'fieldtype':['Image', 'SNR'],
                   'section':'source',
                   'line' : 1}]
        
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
                          'table'   : 'proposal'}]
#                         {'section' : 'scientific_justification',
#                          'name'    : 'Scientific Justification',
#                          'type'    : 'general',
#                          'table'   : 'proposal'},
#                         {'section' : 'technical_justification',
#                          'name'    : 'Technical Justification',
#                          'type'    : 'general',
#                          'table'   : 'proposal'},
#                         {'section' : 'image',
#                          'name'    : 'Image Attachments',
#                          'type'    : 'image',
#                          'table'   : None}]

        self.tables = {'proposal' : { 'value' : proposal,
                                      'type'  : 'single'},
                       'source'   : { 'value' : source,
                                      'type'  : 'repeat'},
                       'author'   : { 'value' : author,
                                      'type'  : 'repeat'}}
