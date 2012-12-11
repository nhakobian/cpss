import MySQLdb

from mod_python import apache
cpss = apache.import_module("../cpss.py")

try:
    from string import Template
except ImportError:
    from stringtemplate import Template

PITemplate = Template("""    <PI>
      <name>${name}</name>
      <email>${email}</email>
      <affiliation>${affil}</affiliation>
      <US>${us}</US>
    </PI>
""")

CoITemplate = Template("""    <CoI>
      <name>${name}</name>
      <email>${email}</email>
      <affiliation>${affil}</affiliation>
      <US>${us}</US>
    </CoI>
""")

# Check recieverBand
# Why is isFlex filled with a variable called fill?
ObsblockTemplate = Template("""  <obsblock>
    <obsblockID>${obsblock}</obsblockID>
    <observationType>${observation_type}</observationType>
    <recieverBand>${frequency_band}</recieverBand>
    <restFrequency>${rest_frequency}</restFrequency>
    <arrayConfiguration>${array_config}</arrayConfiguration>
    <isFlex>${fill}</isFlex>
    <subObsblock>
      <trial>
        <numberOfPointings>${numb_fields}</numberOfPointings>
        <target>
          <molecule>${species}</molecule>
          <transition></transition>
        </target>
        <objects>
          <source>
            <sourceName>${name}</sourceName>
            <RA>${ra}</RA>
            <DEC>${dec}</DEC>
            <selfcalibratable>${self_cal}</selfcalibratable>
          </source>
        </objects>
        <constraints>
          <imgVsSnr value="${imgvssnr}"/>
        </constraints>
      </trial>
    </subObsblock>
  </obsblock>
""")

XMLTemplate = Template("""<project>
  <projectID>${carmaid}</projectID>
  <callForProposals term="${term}"/>
  <title>${title}</title>
  <investigators>
    <numberOfInvestigators>${nois}</numberOfInvestigators>
${PI}${CoIs}  </investigators>
  <targetOfOpportunity>${toe}</targetOfOpportunity>
  <keyProject>${key_project}</keyProject>
  <category>${scientific_category}</category>
  <abstract>${abstract}</abstract>
${Obsblocks}</project><time>${time}</time>
""")

ScriptTemplate = Template("""<pid>${carmaid}</pid>
<pi>${pi}</pi>
<email>${email}</email>
<obsblock>${obsblock}</obsblock>
<config>${config}</config>
<source>${source}</source>
<ra>${ra}</ra>
<dec>${dec}</dec>
<vlsr>${vlsr}</vlsr>
<restfreq>${freq}</restfreq>
<corrconfig>
${corrconfig}
</corrconfig>
<obsmode>${obsmode}</obsmode>
<mosaic>${mosaic}</mosaic>
""")

category_map = { 
    #'' : 'GALACTIC',
    'Cometary'                        : 'COMET',
    #'' : 'EXTRAGALACTIC'
    #'' : 'OTHER',
    'Planetary'                       : 'PLANET',
    'Solar'                           : 'SOLAR',
    'Stellar'                         : 'STELLAR',
    'High-mass Star Formation'        : 'HIGH_MASS_SFR',
    'Low-mass Star Formation'         : 'LOW_MASS_SFR',
    'Chemistry / Interstellar Medium' : 'CHEMISTRY-ISM',
    'Galaxies - Detection'            : 'GALAXY_DETECTION',
    'Galaxies - Mapping'              : 'GALAXY_MAPPING',
    'Cosmology'                       : 'COSMOLOGY',
    'Other Galactic'                  : 'OTHER_GALACTIC',
    'Other Extragalactic'             : 'OTHER_EXTRAGALACTIC',
    }

# List of universities that are definitely in the US.
US_inst = [ 
    'AFRL',
    'Arizona',
    'Boston University',
    'Cal State Los Angeles',
    'Caltech',
    'Caltech/JPL',
    'Caltech/OVRO',
    'Colorado',
    'Carnegie',
    'Carnegie Institution for Science',
    'Center for Astrophysics and Space Astronomy, University of Colorado',
    'Columbia University',
    'Cornell',
    'Cornell University',
    'CfA',
    'CfA/NJU',
    'Cfa Harvard',
    'CfA, Harvard University',
    'CfA, Harvard University - Peking University',
    'Emory University',
    'Georgia Institute of Technology',
    'Georgia Southern University',
    'Harvard',
    'Harvard ',
    'Harvard University',
    'Harvard-CfA',
    'Harvard-CFA',
    'Harvard-Smithsonian',
    'Harvard-Smithsonian CfA',
    'Harvard Smithsonian Center for Astrophysics (CfA)',
    'Havard-Smithsonian Center for Astrophysics',
    'Hawaii',
    'Hawaii IfA',
    'IfA Hawaii',
    "Institute for Astronomy, Hawai'i", 
    'IPAC',
    'Johns Hopkins',
    'Johns Hopkins University',
    'Johns Hopkins University ',
    'JPL',
    'JPL (NASA, Caltech)',
    'JPL, Caltech',
    'LBL',
    'Lawrence Berkeley Lab',
    'MIT Kavli Institute',
    'NASA GSFC',
    'NASA/GSFC',
    'NASA Goddard',
    'NASA Herschel Science Center',
    'NASA Herschel Science Center/Caltech',
    'New Mexico Tech',
    'NOAO USA',
    'Northwestern University',
    'NRAO',
    'NRAO, Charlottesville',
    'National Radio Astronomy Observatory',
    'National Radio Astronomy Observatory/University of Virginia',
    'NJIT',
    'OVRO',
    'Penn State',
    'Penn State University',
    'Princeton',
    'Princeton University',
    'Purdue University',
    'Rutgers',
    'Rutgers University',
    'SAO CfA/Taiwan University',
    'SAO CfA/ASIAA',
    'SAO CfA',
    'SETI',
    'SMA',
    'SOFIA/USRA',
    'Space Telescope Science Institute',
    'SSC',
    'Stanford',
    'Stanford University',
    'Stony Brook University',
    'Stony Brook Univ.',
    'Stony Brook Univ',
    'Texas A\&M',
    'UC Berkeley',
    'UC - Berkeley, MPE Garching',
    'UC Davis',
    'UC Irvine',
    'UC Santa Cruz',
    'U of Wisconsin',
    'UArizona',
    'UAH',
    'UChicago',
    'UCLA',
    'UFlorida',
    'UH IfA',
    'UIUC',
    'UMASS',
    'UMass',
    'UMD',
    'UMichigan Ann Arbor, Observatorio Nacional Brazil',
    'UMissouri-Kansas City',
    'University of Alabama, Huntsville',
    'University of Arizona',
    'University of Florida',
    'University of Hawaii',
    'University of Massachusetts',
    'University of Michigan',
    'University of Minnesota',
    'University of Pennsylvania',
    'University of Rochester',
    'University of Texas',
    'University of Toledo',
    'University of Virginia',
    'University of Wisconsin',
    'Univ. of Washington',
    'Univ. of Wisconsin Milwaukee',
    'UPenn',
    'USRA - SOFIA',
    'UT Austin',
    'UvA',
    'West Virginia University',
    'Williams College',
    'Yale',
]

# List of universities that are definitely NOT in the US.
NUS_inst = [
    'Acad. of Sciences, Prague',
    'Academia Sinica Institute of Astronomy and Astrophysics',
    'ALMA',
    'Argelander Institute for Astronomy, University of Bonn',
    'Argelander Institut fur Astronomie/Humboldt Fellow',
    'ASIAA',
    'Astrobiology Center (INTA, CSIC) - Spain',
    'ASTRON',
    'Australia Telescope National Facility',
    'Bonn',
    'Bristol University',
    'Cambridge U.',
    'Cambridge Univ.',
    'Cavendish Laboratory, University of Cambridge',
    'CEA',
    'CEA Saclay',
    'CEA-Saclay',
    'CESR',
    'Chalmers University of Technology',
    'CITA',
    'CRyA-UNAM',
    'CSIRO',
    'Curtin',
    'Durham',
    'Durham University',
    'Dublin Institute for Advanced Studies',
    'Edinburgh',
    'ESA',
    'ESA/ESTEC',
    'ESO',
    'ESO/Manchester',
    'European Southern Observatory',
    'Faculty of Science, Hong Kong University',
    'Hebrew University',
    'Herzberg Institute of Astrophysics',
    'Herzberg Institute of Astrophysics, Canada',
    'Hokkaido Univ.',
    'IA-UNAM',
    'IAA, Spain',
    'IAC',
    'IAP',
    'Ibaraki University',
    'ICATE, Universidade de Sao Paulo',
    'ICE (IEEC-CSIC)',
    'IFSI-INAF, Rome, Italy',
    'Imperial College',
    'INAF',
    'INAF-IASF',
    'INAF - Arcetri (Florence)',
    'INAF - Arcetri Observatory',
    'INAF - Osservatorio di Arcetri',
    'INAF - Osservatorio Astrofisico di Arcetri',
    'INAF-Osservatorio Astrofisico di Arcetri',
    'INAF - IAPS',
    'INAF - IFSI (Rome)',
    'INAF - IFSI',
    'INAF-IRA, Italy',
    'INAF-OAA, Italy',
    'INAF-Osservatorio Astrofisico di Arcetri',
    'INAOE',
    "Institut de Ciencies de l'Espai (CSIC)",
    'Institute of Physics, Vietnam',
    'Instituto de Astrofisica de Andalucia',
    "Institut d'Astrophysique de Paris, France",
    'INTA CSIC, Madrid',
    'IRAM',
    'ISAS/JAXA',
    'ITA, Uni Heidelberg',
    'JAXA',
    'Jodrell Bank Observatory',
    'Kapteyn Institute,Groningen',
    'Kapteyn Astronomical Inst.',
    'Keio University',
    'Kyoto University',
    'Laboratoire AIM, IRFU/SAp, CEA-Saclay, France',
    "Laboratoire d'Astrophysique de Bordeaux",
    "Laboratoire d'Astrophysique de Marseille",
    'Leiden',
    'Leiden Observatory',
    'Leiden Observatory, the Netherlands',
    'LERMA',
    'LERMA Paris',
    'LMU Munich',
    'Macquarie University',
    'Max Planck Institut fur Extraterrestrische Physik, Germany',
    'Max-Planck-Institut fuer Radioastronomie',
    'Max Planck Institute for Radioastronomy',
    'Max Planck Institute for Solar System Research',
    'Max Planck Institute for Solar System Research, Germany',
    'McGill',
    'McMaster University',
    'MPE',
    'MPE Garching',
    'MPI Garching',
    'MPIA',
    'MPIA, Heidelberg',
    'MPIA Heidelberg',
    'MPIfR',
    'MPirF',
    'MRAO',
    'NAOJ',
    'National Institute of Information and Communications Technology, Japan',
    'National Observatory, Rio de Janeiro',
    'National Observatory, Rio de Janeiro ', 
    'National Tsing Hua University',
    'NJU/SHAO',
    'Nobeyama Radio Observatory', 
    'Nobeyama Radio Observatory ',
    'Nottingham',
    'NRC-HIA',
    'NRO',
    'NRO/NAOJ',
    'OAN Madrid',
    'Obs. de Paris, France',
    "Observatoire de la Cote d'Azur",
    'Observatoire de la Cote d',
    'Observatorio Astronomico Nacional',
    'Observatorio Nacional, Brazil',
    'Open University',
    '1. Physikalisches Institut, Uni Koeln',
    'Pontificia Universidad Catolica de Chile',
    'Purple Mountain Observatory, CAS, China',
    'Royal Military College of Canada',
    'Sussex',
    'SRON, Groningen',
    'SRON \& Univ Groningen, the Netherlands',
    'St Petersburg Univ.',
    'Tel Aviv University',
    'Tianjin Astrophysics Center, Tianjin Normal University, China',
    'TIFR, India',
    'Tokyo Univ.',
    'Trinity College Dublin, Dublin',
    'U-PSUD',
    'UIO',
    'UBC',
    'UNAM',
    'Universidad Catolica de Chile',
    'Universidad Nacional Autonoma de Mexico',
    'Universidad Nacional Autonoma de Mexico,  Institute of Astronomy:Ensenada BC',
    'Universidade de Sao Paulo',
    'Univ. of Cologne - Germany',
    'Univ. of Leicester, UK',
    'Univ. of Sao Paulo',
    'Univ-Paris',
    'University of Bonn',
    'University of Bristol',
    'University of Cambridge',
    'The University of Cambridge',
    'University of Chile',
    'University of Erlangen-Nuremberg',
    'University of KwaZulu-Natal',
    'University of Leeds',
    'University of Leeds, United Kingdom',
    'University of Manchester',
    'University of Manitoba',
    ' University of Portsmouth',
    'University of Southampton',
    'University of Sydney',
    'University of Tokyo/NAOJ',
    'University of Tokyo',
    'The university of Tokyo',
    'University of Victoria',
    'University of Western Ontario, Caltech',
    'UKZN',
    'Vienna',
    'Weizmann Institute',
]

def isus(inst):
    if inst in US_inst:
        return '1'
    elif inst in NUS_inst:
        return '0'
    else:
        print inst
        return 'N/A'

def obsblockgen(numb, array, freq, name):
    #filter out all non-alphanumeric characters from name
    filtername = ""
    for letter in name:
        if (letter.isalnum() == True):
            filtername = filtername + letter

    #filter out everything after the . in freq. max 3 chars
    filterfreq = ""
    for digit in freq:
        if (digit == "."):
            break
        else:
            filterfreq = filterfreq + digit
    filterfreq = filterfreq[0:3]

    obsblockname = str(numb) + array + "_" + filterfreq + filtername[0:6]
    return obsblockname

def export_xml(propinfo, template):
    fast_dir = cpss.config['data_directory'] + 'fast/'

    cursor = cpss.db.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    # Get proposal info

    cursor.execute("""SELECT * 
                      FROM proposals, %(prop_table)s as cyc
                      WHERE proposals.proposalid=cyc.proposalid
                           AND proposals.proposalid=%(propid)s
                           AND proposals.carmaid IS NOT NULL
                      LIMIT 1""" % { 'prop_table' : propinfo['proposal'],
                                     'propid' : propinfo['proposalid']})

    proposal = cursor.fetchone()

    # Get author info and populate templates
    
    cursor.execute("""SELECT * FROM %(aut_table)s 
                      WHERE `proposalid`=%(propid)s
                      ORDER BY numb""" % 
                   { 'aut_table' : propinfo['author'],
                     'propid' : propinfo['proposalid'] } )

    authors = cursor.fetchall()
    nois = len(authors)
    if (nois != 1):
        PIdata = authors[0]
        authors = authors[1:]
    else:
        PIdata = authors[0]
        authors = ()

    PI = PITemplate.substitute(name = PIdata['name'], email = PIdata['email'],
                               affil = PIdata['institution'], 
                               us = isus(PIdata['institution']))

    CoIs = ""
    for coi in authors:
        CoIs = CoIs + CoITemplate.substitute(name = coi['name'],
                                           email = coi['email'],
                                           affil = coi['institution'],
                                           us = isus(coi['institution']))

    # Get Source info and populate templates

    cursor.execute("""SELECT * 
                      FROM %(source_table)s 
                      WHERE `proposalid`=%(propid)s
                      ORDER BY numb
                      LIMIT 1""" % 
                   { 'source_table' : propinfo['source'],
                     'propid' : propinfo['proposalid']} )
    source = cursor.fetchone()

    Obsblocks = ""

    corr = source['f_corrconfig']
    freq = source['f_freq']
    bw = source['f_slbw']
    modes = template.tempclass.fast_modes
    mode = modes[corr]

    corrconfig_mode = template.fast_corrconfig(mode=corr, freq=freq, slbw=bw)

    if mode['userFreq'] == False:
        freq = mode['freq']

    obsblock_name = obsblockgen(source['numb'], source['f_array'],
                                freq, source['f_sourcename'])

    Obsblocks += ObsblockTemplate.substitute(
        obsblock = obsblock_name,
        frequency_band = '',
        array_config = source['f_array'],
        fill = '0',
        numb_fields = '',
        species = '',
        name = source['f_sourcename'],
        ra = source['f_ra'],
        dec = source['f_dec'],
        self_cal = '0',
        rest_frequency = freq,
        observation_type = mode['obsmode'],
        imgvssnr = '',
        )

    # Grab and filter the abstract
    proposal['abstract'] = proposal['abstract'].replace('\n', ' ')
    proposal['abstract'] = proposal['abstract'].replace('\r', '')
    proposal['abstract'] = proposal['abstract'].replace('\\', '\\\\')
    proposal['abstract'] = proposal['abstract'].replace('$', '\$')
    proposal['abstract'] = proposal['abstract'].replace('"', '\\"')
    proposal['abstract'] = proposal['abstract'].replace("'", "\\'")

    xml_proposal = XMLTemplate.substitute(
        carmaid = proposal['carmaid'],
        term = 'fast',
        title = proposal['title'],
        nois = nois,
        PI = PI,
        CoIs = CoIs,
        key_project = proposal['key_project'],
        toe = proposal['toe'],
        scientific_category =category_map[proposal['scientific_category']],
        abstract = proposal['abstract'],
        Obsblocks = Obsblocks,
        time = source['f_time']
        )
        
    xml_strip = xml_proposal.replace('\n', '')
    xml_strip = xml_strip.replace('>  <', '><')
    xml_strip = xml_strip.replace('>    <', '><')
    xml_strip = xml_strip.replace('>      <', '><')
    xml_strip = xml_strip.replace('>        <', '><')
    xml_strip = xml_strip.replace('>          <', '><')
    xml_strip = xml_strip.replace('>            <', '><')

    file_strip = open(fast_dir + propinfo['carmaid'] + '_export.xml', 'w')
    file_strip.write(xml_strip)
    file_strip.write('\n')

    script = ScriptTemplate.substitute(
        carmaid = proposal['carmaid'],
        pi = PIdata['name'],
        email = PIdata['email'],
        obsblock = obsblock_name,
        config = source['f_array'],
        source = source['f_sourcename'],
        ra = source['f_ra'],
        dec = source['f_dec'],
        vlsr = source['f_vlsr'],
        freq = freq,
        corrconfig = corrconfig_mode,
        obsmode = mode['obsmode'],
        mosaic = source['f_mosaic'],
        )

    script_file = open(fast_dir + propinfo['carmaid'] + '_script.xml', 'w')
    script_file.write(script)
    script_file.write('\n')

    cursor.close()
    file_strip.close()
    script_file.close()

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def fast_email(carmaid):
    fast_dir = cpss.config['data_directory'] + 'fast/'
    from_email = "Fast-track Robot <no-reply@carma-prop.astro.illinois.edu>"

    CS = ', '

    mail = MIMEMultipart()
    mail['Subject'] = carmaid
    mail['To'] = CS.join(cpss.config['fast_email'])
    mail['From'] = from_email

    export_name = carmaid + '_export.xml'
    export_file = open(fast_dir + export_name, 'r')
    export = MIMEText(export_file.read(), _subtype='plain')
    export_file.close()
    export.add_header('Content-Disposition', 'attachment', filename='export.xml')

    script_name = carmaid + '_script.xml'
    script_file = open(fast_dir + script_name, 'r')
    script = MIMEText(script_file.read(), _subtype='plain')
    script_file.close()
    script.add_header('Content-Disposition', 'attachment', filename='script.xml')

    mail.attach(export)
    mail.attach(script)

    sender = smtplib.SMTP()
    sender.connect()
    sender.sendmail(from_email, cpss.config['fast_email'], mail.as_string())
    sender.quit()

    debug = open(fast_dir + carmaid + '_email.txt', 'w')
    debug.write(mail.as_string())
    debug.close()
