from mod_python import apache
import copy
import os
import os.path
from pyPdf import PdfFileWriter, PdfFileReader
from string import Template as baseTemplate

cpss = apache.import_module("../cpss.py")

template_list = [ 'main_10',
                  'main_2008b',
                  'main_2009a',
                  'main_2009b',
                  'main_2010a',
                  'main_2010b',
                  'main_2011a',
                  'main_2011b',
                  'main_2012a',
                  'main_2012b',
                  'main_2013a',
                  'main_2013b',
                  'ddt_2010a',
                  'ddt_2011',
                  'ddt_2012a',
                  'ddt_2012b',
                  'cs_10',
                  'cs_2011',
                  'cs_2012',
                  'cs_2013',
                  'fast_2012b',
                  ]

templates = {}

for i in template_list:
    templates[i] = apache.import_module(i)

class strTemplate(baseTemplate):
    idpattern = r'[_a-z0-9][_a-z0-9]*'

class Template:
    def __init__(self, cycleinfo, propid, view,
                 Fetch=True, justification=False):

        self.justification = justification
        
        if (Fetch == True):
            self.is_key_project = cpss.db.is_key_project(propid)

            if (self.is_key_project != cpss.db.justification_type_latex(propid)):
                cpss.db.justification_type_set(propid, 1)
                self.justification = True
 
        self.req = cpss.req
        # self.cyclename is no more. replaced with storing the cycleinfo
        self.cycleinfo = cycleinfo
        self.error = False
        self.propid = propid
        self.tmpLinescan = {} # For enhanced error checking routine.

        if view == True:
            self.view = True
            self.edit = False
        else:
            self.view = False
            self.edit = True
        
        template = self.cycleinfo['template']

        # Set self.template to the correct class loaded in the header of the
        # file.
        self.template = templates[template]

        self.template_name = template
        self.tempclass = self.template.template()
        self.sections = self.tempclass.sections
        self.tables = self.tempclass.tables

        if (Fetch == True):
            self.proposal = cpss.db.proposal_get(self.tempclass.tables,
                                                         cycleinfo, propid) 
            # Merge database data with template style
            self.data_merge()

    def unlocked(self):
        # Identical to unlocked in connector.py. Perhaps find a way to call
        # that code?
        propinfo = self.cycleinfo
        if 'lock' not in propinfo:
            return False

        if propinfo['lock'] == 1:
            return False
        elif propinfo['lock'] == 0:
            return True
        elif propinfo['lock'] == None:
            if propinfo['create'] == 1:
                return True
            else:
                return False

    def calc_hours(self):
        for section in self.sections:
            if section['name'] == 'Source Information':
                sources = section
        sources = sources['data']
        time = 0
        for source in (sources):
            hours = 0
            for field in source[1]:
                if ((field['fieldname'] == 'hrs_a') or
                    (field['fieldname'] == 'hrs_b') or
                    (field['fieldname'] == 'hrs_c') or
                    (field['fieldname'] == 'hrs_d') or
                    (field['fieldname'] == 'hrs_e') or
                    (field['fieldname'] == 'hrs_sh') or
                    (field['fieldname'] == 'hrs_sl')) :
                    if field['data'] == None:
                        continue
                    elif (field['data'].count('.') <= 1):
                        val = field['data'].replace('.', '')
                        if (val.isdigit() == False):
                            hours = -1
                        else:
                            hours += float(field['data'])
                    else:
                        hours = -1
            if (hours == -1):
                return -1
            time += hours
        return time
        
    def process_options(self, entry):
        #this function verifies the types of data in the structures, and if
        #an option is not set, it will set the default value.
        if (entry.__contains__('line') == False):
            entry['line'] = 1
        return entry
    
    def data_merge(self):
        for section in self.sections:
            if (section['table'] == None):
                continue
            section['data'] = []
            for dataline in self.proposal[section['table']]:
                section['data'].append({})
                data = section['data'][-1]

                # Pre-scan line for the C23 marker (if exists) and store
                # temporary value for the current line. This will allow
                # other fields to perform error checking on the presence of
                # the C23 field. This can be easily extended to other fields
                # if need be. This is kind of a rough "hack" since the error
                # checking system was never designed to need data from other
                # fields to calculate the error status of the current field.

                self.tmpLinescan = {} # Initialize it to be a persistant value
                                      # on this line ONLY, but must be available
                                      # from other functions (hence the class
                                      # scope. The error checking functions are
                                      # called during the self.element() call
                                      # below, so this variable should only
                                      # exist during its lifetime.
                for entry in self.tables[section['table']]['value']:
                    # This is the pre-scan for loop. It will only grab values
                    # that need to be checked from error checking functions on
                    # fields that are not its own (currently is the C23 status
                    # field).
                    if (entry['section'] != section['section']):
                        continue
                    
                    if entry['fieldname'] == 'observation_type':
                        self.tmpLinescan['observation_type'] = dataline['observation_type']
                    if entry['fieldname'] == 'corr_frequency':
                        self.tmpLinescan['corr_frequency'] = dataline['corr_frequency']
                    if entry['fieldname'] == 'f_corrconfig':
                        self.tmpLinescan['f_corrconfig'] = dataline['f_corrconfig']
                    # If more pre-scan values are needed add them here...
                # End pre-scan for loop, below continues normal processing.

                for entry in self.tables[section['table']]['value']:
                    if (entry['section'] != section['section']):
                        continue
                    #Process options and add defaults
                    entry = copy.deepcopy(entry)
                    entry = self.process_options(entry)
                    #Retrieve data from dataline and add to entry
                    entry['data'] = dataline[entry['fieldname']]
                    entry = self.element(entry, view=self.view, edit=self.edit)
                    #Add to the section list and sort by line number
                    if (data.__contains__(entry['line']) == False):
                        data[entry['line']] = [entry]
                    else:
                        data[entry['line']] += [entry]

                self.tmpLinescan = {} # Clear any values that might have been
                                      # temporarily stored here. This is a 
                                      # safety measure.

    def data_strip(self, data):
        #This function strips all misc info from the array, creating a
        #dictionary of fieldname : data. 
        buff = {}
        for num, line in data.items():
            for segment in line:
                if (segment.__contains__('text') == True):
                    buff[segment['fieldname']] = segment['text']
                else:
                    buff[segment['fieldname']] = segment['data']
        return buff

    def make_html_header(self):
        ###Begin Page Header
        cpss.w("""<div class="navbar, propheader">""")
        if (self.unlocked() != True):
            cpss.w("""<ul id="navlist">
            <li><a href="%s">Current Proposal</a></li>
            <li><a href="%s">View Submitted PDF</a></li>""" %
                           ("view/" + str(self.propid),
                            "finalpdf/" + str(self.propid)))
        elif (self.cycleinfo['status'] == 0):
            cpss.w("""<ul id="navlist">
            <li><a href="%s">Current Proposal</a></li>
            <li><a href="%s">View Draft as PDF</a></li>
            <li><a href="%s">Submit Proposal</a></li></ul>""" %
                           ("view/" + str(self.propid),
                            "pdf/" + str(self.propid),
                            "submit_verify/" + str(self.propid)))
        else:
            cpss.w("""<ul id="navlist">
            <li><a href="%s">Current Proposal</a></li>
            <li><a href="%s">View Draft as PDF</a></li>
            <li><a href="%s">View Submitted PDF</a></li>
            <li><a href="%s">Re-Submit Proposal</a></li></ul>""" %
                           ("view/" + str(self.propid),
                            "pdf/" + str(self.propid),
                            "finalpdf/" + str(self.propid),
                            "submit_verify/" + str(self.propid)))

        cpss.w("""</div>""")

        cpss.w("""<div id='redinfo'>Fields highlighted in red must contain valid information 
                  before your proposal can be submitted.</div>""")

        ###End Page Header

    def make_html_proposal(self):
        self.make_html_header()
        unlocked = self.unlocked()

        all_head = (
            """<div id="editlist"><p><a name="%(section)s"></a>%(name)s
               <a href="help_small/%(section)s" 
               onClick="return popup(this, 'help')">
               <img src="static/help.png" alt="Help"></a>""")
        general_edit = (
            """<a href="edit/%(propid)s/%(section)s">
               <img src="static/page_white_edit.png" alt="Edit"></a></p>""")
        repeat_add = (
            """<a href=
               "multi_add/%(propid)s/%(section)s">
               <img src="static/add.png" alt="Add"></a></p>""")
        repeat_eddel = (
            """<a href="edit/%(propid)s/%(section)s/%(id)s">
                 <img src="static/page_white_edit.png" alt="Edit"></a>
               <a href="multi_del/%(propid)s/%(section)s/%(id)s">
                 <img src="static/delete.png" alt="Delete"></a>""")

        post_author = (
            """<div id="editlist">
                 <table><tr>
                   <td style="width:50%%;text-align:center;font-weight:bold;">
                     Advisor must send a supporting letter if Thesis is 
                     checked. See Instructions.</td>
                 </tr></table>
               </div>""")

        post_source = (
            """<div id="editlist">
                 <table>
                   <tr>
                     <th style="width:50%%;text-align:center;
                                font-weight:bold;">
                       Total Hours: %(hours)s
                       <i><a href="help_small/tot_hours" 
                             onClick="return popup(this, 'help')">
                          (Why is this number large?)</a></i>
                     </th>
                   </tr>
                   <tr><td>
                     <sup>1</sup>Requests for A and B-configuration 
                     observations must include a description of the 
                     calibration strategy in the technical justification. 
                     Please see the <a href="http://cedarflat.mmarray.org/observing/doc/instrument_desc.html" 
                     target="_blank"> instrument description</a> for more
                     details.
                   </td></tr>
                 </table>
               </div>""")

        post_fast_source = (
            """<table>
                 <tr><td style="text-align:left;border-top:1px solid black;">
                   <div style="overflow:scroll;width:800px;font-size:small;">
                     <pre>%s</pre>
                   </div>
                 </td></tr>
               </table>""")

        pre_image = (
            """<div id="editlist"><p><a name="image"></a>Image Attachments
                 <a href="help_small/%(section)s" 
                    onClick="return popup(this, 'help')">
                    <img src="static/help.png" alt="Help"></a>""")
        edit_image = (
            """<a href="multi_add/%(propid)s/image">
                 <img src="static/add.png" alt="Add"></a>""") 

        for section in self.sections:
            if (self.justification == True):
                # If true, we have PDF justifications which are
                # handled differently.
                if (section['section'] == 'scientific_justification'):
                    continue
                if (section['section'] == 'technical_justification'):
                    continue

            if (section['type'] == 'general'):
                groups = section['data']
                keys = groups[0].keys()
                keys.sort()

                cpss.w(all_head % {'name'    : section['name'], 
                                   'section' : section['section']})
                if unlocked:
                    cpss.w(general_edit % {'propid' : self.propid, 
                                           'section': section['section']})

                self.html_entry_view(groups, keys)                
            elif (section['type'] == 'repeat'):
                groups = section['data']
                keys = groups[0].keys()
                keys.sort()

                #The IsAuthor lines are part of the crude hack to make
                #Author#1 the PI. Revision 46

                IsAuthor = False
                if (section['section'] == 'author'):
                    IsAuthor = True

                cpss.w(all_head % {'name'    : section['name'], 
                                   'section' : section['section']})

                if unlocked:
                    # Make sure that the add more source lines option isnt
                    # available for fast mode proposals since they can have 
                    # only one source line.
                    if not((self.cycleinfo['type'] == 'fast') and 
                        (section['section'] == 'source')):
                        cpss.w(repeat_add % { 'propid'  : self.propid, 
                                              'section' : section['section']})
                for lines in groups:
                    if unlocked == False:
                        break
                    lines = {keys[0] : lines[keys[0]]}
                    keys = [keys[0]]
                    lines[keys[0]] += [self.element({
                        'name' : '&nbsp;',
                        'data' : repeat_eddel % {
                            'propid'  : self.propid,
                            'section' : section['section'],
                            'id'      : lines[keys[0]][0]['data'],
                            },
                        }, view=True)]

                self.html_entry_view(groups, keys, IsAuthor=IsAuthor)
                if (section['section'] == 'author'):
                    cpss.w(post_author)

                if (section['section'] == 'source'):
                    hours = self.calc_hours()
                    if hours == -1:
                        hours = "N/A"

                    if self.cycleinfo['type'] == 'fast':
                        fast_corr = self.fast_corrconfig()
                        if fast_corr != '':
                            cpss.w(post_fast_source % fast_corr)
                    else:
                        cpss.w(post_source % {'hours' : hours})

            elif (section['type'] == 'image'):
                cpss.w(pre_image % { 'section' : section['section'] })
                if unlocked:
                    cpss.w(edit_image % { 'propid' : self.propid} )

                cpss.w("</p>")
                result = cpss.db.images_list(self.propid)

                if (len(result) == 0):
                    cpss.w("""<table><tr><td>None</td></tr></table>""")
                else:
                    cpss.w("""<span style="font-size:small;">Please use 
                    the sample code provided and insert it in your 
                    justification section where you would like the image to 
                    appear. Only Postscript (ps and eps) image attachments are
                    supported.</span>""")

                    cpss.w("""<table><tr><th>File Name</th><th>
                              Sample Code</th><th>&nbsp;</tr>""")

                    for image in result:
                        self.html_image_view(self.propid, image, unlocked)
                    cpss.w("""</table>""")
            cpss.w("""</div><br>""")

            if (section['section'] == 'prior_obs'):
                if (self.justification == False):
                    web = 'selected'
                    pdf = ''
                else:
                    web = ''
                    pdf = 'selected'

                nodata = ("""<br><form enctype="multipart/form-data" 
                                       method="post" action="save/%s">
                                 <input type="hidden" name="section" 
                                        value="justification">
                                 <input type="file" name="file">
                                 <input type="submit" name="update" 
                                        value="Submit"/>
                                 </form>""" % str(self.propid))
                delete = ("""<a href="del_just/%s">
                             Delete Uploaded LaTeX Justification</a>""" % 
                          str(self.propid))

                if (self.justification == True):
                    data = cpss.db.justification_get_data(self.propid)
                    if data == None:
                        command = nodata
                    else:
                        command = delete
                else:
                    command = ''

                if self.is_key_project and unlocked:
                    cpss.w(cpss.text.html_just_key % command)
                    cpss.w('<br>')
                elif unlocked:
                    cpss.w(cpss.text.html_just_normal % (self.propid, web, 
                                                         pdf, command))
                    cpss.w('<br>')
                elif self.justification == True:
                    # Is locked.
                    cpss.w(all_head % { 'name' : "Latex Justification",
                                        'section' : section['section']})
                    cpss.w("""<div id="editlist">
                              <textarea cols=100 rows=15 readonly>%(prop)s
                              </textarea></div><br>""" % {'prop': data})

        # This if does fix some errors, but not quite sure why its needed.
        # It means there is a bug somewhere else.
        if not unlocked:
            cpss.w("</div>")

    def fast_corrconfig(self, mode=None, freq=None, slbw=None):
        # Pull data from coversheet structure if not explicitely given
        if (mode == None) or (freq == None) or (slbw == None):
            for section in self.sections:
                if section['section'] == 'source':
                    source = section['data'][0][1]

            for element in source:
                if element['fieldname'] == 'f_corrconfig':
                    mode = element
                elif element['fieldname'] == 'f_freq':
                    freq = element
                elif element['fieldname'] == 'f_slbw':
                    slbw = element

            if mode['error'] != '':
                return ''
            if freq['error'] != '':
                return ''
            if slbw['error'] != '':
                return ''

            mode = mode['data']
            freq = freq['data']
            slbw = slbw['data']
        # Otherwise mode, freq, slbw explicitely passed and we assume that
        # it is correct.

        # Pull the config string from the template.
        config = self.tempclass.fast_modes[mode]['config']

        # For the user specified spectral line modes ('_SL'), this gets a 
        # little more complicated. configWideAstroband is used to set up
        # all modes except for the spectral line band. But which one is best
        # to use, and how to we set up the 1st LO? The following is based
        # on an email from Doug Friedel on Dec 3, 2012:
        #
        # configWideAstroband puts bands at the following IF freqs:
        # 1.425, 1.875, 2.325, 2.775, 3.225, 3.675, 4.125, 4.575
        #
        # So would recommend the following:
        #
        # 3mm:
        # above 91 GHz tune to the USB
        # below 91 GHz tune to the LSB
        #
        # between 91 and 109 GHz use band 3 with an IF of 2.325 GHz
        # below 91 and above 109 use band 7 with an IF of 4.125 GHz
        #
        # 1mm:
        # same as for 3mm but substitute 221 for 91 and 259 for 109
        #
        # 1cm:
        # I don;t know what the tuning range or sideband is for these yet.

        if '_SL' in mode:
            # For this we need the frequency to be a float.
            freq = float(freq)

            # This code should be correctly set up to accomidate a 1CM
            # SL mode when the correct ranges are known and the modes
            # are added to the semester_fast.py file.
            frange = { '3MM' : (91.0, 109.0),
                       '1MM' : (221.0, 259.0),
                       '1CM' : (0.0, 0.0), # Update this when modes are avail.
                       }
            
            # Choose correct band:
            if '_3MM_' in mode:
                band = frange['3MM']
            elif '_1MM_' in mode:
                band = frange['1MM']
            elif '_1CM_' in mode:
                band = frange['1CM']

            # Choose to tune to LSB or USB:
            # If the 1cm recievers can ONLY tune to the USB, then setting
            # frange['1CM'][0] = 0.0 above should correctly do this.
            if freq < band[0]:
                tune = 'LSB'
            else:
                tune = 'USB'

            # Choose LO frequency of spectral line band:
            if (freq > band[0]) and (freq < band[1]):
                if_freq = 2.325
                corr_band = 3
            else:
                if_freq = 4.125
                corr_band = 7

            # Calculate 1st LO (not needed, but as a comment in file)
            if tune == 'LSB':
                first_lo = freq + if_freq
            elif tune == 'USB':
                first_lo = freq - if_freq
                
            buf = (config % { 'tune' : tune, 'if_freq' : if_freq, 
                              'corr_band' : corr_band, 'freq' : freq,
                              'first_lo' : first_lo, 'slbw' : slbw } )
        else:
            # This is a 'standard' mode, so only replace slbw and freq.
            # If a mode doesnt need one of these two variables, it wont
            # be used in the template.
            buf = (config % { 'userBW' : slbw, 'freq' : freq })
        return buf

    def make_html(self, section_choose=False, id=False):
        #Validate section
        if (section_choose != False):
            valid = False
            for section in self.sections:
                if (section_choose == section['section']):
                    valid = True
                    do_sections = [section]
            if (valid != True):
                self.req.write("""This section does not exist. Please choose
                                  another. If you believe this is in error,
                                  please contact the administration.""")
                return
        else:
            do_sections = self.sections

        unlocked = self.unlocked()

        self.make_html_header()
        ###Begin Page Body

        for section in do_sections:
            if (section['type'] == 'repeat') and (id == False):
                self.req.write("""Please return to the proposal screen and
                select a valid piece of information to edit.""")
                return
            elif (section['type'] == 'general') and (id != False):
                cpss.w("""Section does not exist. Return to the proposal screen
                          and select a valid section to edit.""")
                return
            
            groups = section['data']
            keys = groups[0].keys()
            keys.sort()
            self.req.write("""<div id="editdata">""")
            self.req.write("""<p>%s&nbsp;</p>""" % (section['name']))
            self.html_entry_edit(groups, keys, self.propid, id=id)
            self.req.write("""</div><br>""")
        ###End Page Body

    def data_verify(self):
        #Validate section
        first_br = True
        main_error = False
        for section in self.sections:
            if (section['section'] == 'image'):
                continue

            groups = section['data']
            keys = groups[0].keys()
            keys.sort()

            if (section['section'] == 'author'):
                type = 'Author'
            elif (section['section'] == 'source'):
                type = 'Source'

            if (section['type'] == 'repeat'):
                for line in keys:
                    error = False
                    first_line = True
                    line_number = 1
                    for lines in groups:
                        line_error = False
                        buf = ''
                        for entry in lines[line]:
                            if (entry['error'] != ''):
                                buf += ("<li>%s : %s - %s </li>" % (
                                    entry['name'], entry['data'],
                                    entry['error']))
                                line_error = True
                                error = True
                                main_error = True
                        if ((line_error == True) and (first_line == True)):
                            first_line = False
                            if (first_br == True):
                                self.req.write("<br>")
                                first_br = False
                            self.req.write("<br>%s<ul>" % (section['name']))
                        if (line_error == True):
                            self.req.write("<li>%s Number %s<ul>" % (type,
                                           line_number))
                            self.req.write(buf)
                            self.req.write("</ul></li>")
                        line_number = line_number + 1
                    if (error == True):
                        self.req.write("</ul>")
            else:
                for line in keys:
                    error = False
                    number = 1
                    for lines in groups:
                        buf = ("<br>%s<ul>" % section['name'])
                        for entry in lines[line]:
                            if (entry['error'] != ''):
                                buf += ("<li>%s : %s - %s</li>" % (
                                    entry['name'], entry['data'],
                                    entry['error']))
                                error = True
                                main_error = True

                if (error == False):
                    pass
                else:
                    if (first_br == True):
                        self.req.write("<br>")
                        first_br = False
                    self.req.write(buf)
                    self.req.write("</ul>")

        return main_error

    def obsblock_verify(self):
        #Validate section

        obsblocks = []

        for section in self.sections:
            if (section['section'] != 'source'):
                continue

            groups = section['data']
            keys = groups[0].keys()
            keys.sort()

            for line in keys:
                for lines in groups:
                    for entry in lines[line]:
                        if (entry['fieldname'] == 'obsblock'):
                            obsblocks.append(entry['data'])


            error = False
            first = True
            obsblock_check = []
            for obsblock in obsblocks:
                if (obsblock_check.count(obsblock) >= 1):
                    continue
                if (obsblocks.count(obsblock) > 1):
                    error = True
                    if (first == True):
                        self.req.write("<ul>")
                        first = False
                    self.req.write("""<li>You have used the obsblock name : "%s"
                    on more than one source line. Each line must have a
                    unique obsblock name.</li>""" % obsblock)
                    obsblock_check.append(obsblock)
            if (error == True):
                self.req.write("</ul>")
        return error
                
    def html_entry_view(self, groups, keys, buffer=False, IsAuthor=False):
        buf = ""
        for line in keys:
            buf += ("""<table>""")

            show_header = True
            for lines in groups:
                header = ""
                data = ""
                for entry in lines[line]:
                    #allows an entry not to appear on the summary line
                    if (entry.__contains__('nosummary') == True):
                        if (entry['nosummary'] == True):
                            continue
                    if (len(lines[line]) == 1):
                        header = ""
                    else:
                        if (entry.__contains__('shortname') == True):
                            header += ("""<th>%s</th>""" % entry['shortname'])
                        else:
                            header += ("""<th>%s</th>""" % entry['name'])

                    #Fairly Crude Hack to make author #1 the PI rev. 46
                    if ((IsAuthor == True) and (entry['fieldname'] == 'numb')
                        and (entry['data'] == 1)):
                        entry['html'] = 'PI'
                
                    data += ("""<td>%s</td>""" % entry['html'])
                    
                if (len(lines[line]) == 1):
                    show_header = False

                if (show_header == False):
                    buf += ("""<tr>%s</tr>""" % (data))
                else:
                    buf += ("""<tr>%s</tr><tr>%s</tr>""" %
                                   (header, data))
                show_header = False
                
            buf += ("""</table>""")

        if (buffer == False):
            self.req.write(buf)
            return
        else:
            return buf
                
    def html_entry_edit(self, groups, keys, propid, id=False):
        cpss.w("""<table><form enctype="multipart/form-data"
                               action='save/%s' method='post' name="form">""" %
               str(propid))

        cpss.w("""<input type="hidden" name="section" value="%s">""" %
               groups[0][keys[0]][0]['section'])
        if (id != False):
            cpss.w("""<input type="hidden" name="id" value="%s">""" %
                   str(id))

        for line in keys:
            for lines in groups:
                if (id != False):
                    if (str(lines[1][0]['data']) != str(id)):
                        continue
                for entry in lines[line]:
                    if (len(lines[line]) == 1):
                        self.req.write("""<tr><td>%s</td></tr>""" %
                                       (entry['html']))
                    else:
                        if (entry.__contains__('info') == True):
                            name = """%s (%s)""" % (entry['name'],
                                                    entry['info'])
                        else:
                            name = """%s""" % entry['name']

                        name = (name +
                               """ [<a href="help_small/%s/%s"
                                onClick="return popup(this, 'help')"
                                >?</a>]""" % (groups[0][keys[0]][0]['section'],
                                 '#' + entry['fieldname']))

                        if (entry['error'] == ''):
                            cpss.w("""<tr><td class="label">%s:</td>
                                      <td class="data">%s</td>
                                      <td class="valid">%s</td></tr>""" %
                                   (name, entry['html'], ''))
                        else:
                            cpss.w("""<tr><td class="label">%s:</td>
                                      <td class="data">%s</td>
                                      <td class="error">%s</td></tr>""" %
                                   (name, entry['html'], entry['error']))
        cpss.w("""</table><center><input id="submit" type='submit' 
                  value='Save Changes'></center></form>""")

    def html_image_view(self, propid, image, unlocked):
        if (image['file'] == '') and unlocked:
            cpss.w("""
                <tr><form enctype="multipart/form-data" action="save/%(prop)s"
                             method="post">
                <td><input type="hidden" name="section" value="image">
                    <input type="hidden" name="id" value="%(id)s">
                    <input type="file" name="file">
                    <input type="submit" name="update" value="Submit"/>
                </td><td></td><td>
                <a href="multi_del/%(prop)s/image/%(id)s">
                <img src="static/delete.png" alt="Delete"></a>
                </td></tr></form>""" % {'prop' : str(propid),
                                        'id'   : image['numb']})
        else:
            fname = image['file']
            fname = fname.split('/')
            editfile = fname[-1]

            sample_code = ("""\\begin{figure}[h!]<br>
            \\begin{center}<br>
            \\includegraphics{%s}<br>
            \\caption{}<br>
            \\end{center}<br>
            \\end{figure}""" % (editfile))
            if unlocked:
                delete = (
                    """<td id="button"><a href="multi_del/%s/image/%s">
                       Delete</a></td>""" % (str(propid), image['numb']))
            else:
                delete = "<td></td>"
            cpss.w("""<tr style="border-bottom:1px solid black;"><td>%s</td>
                      <td style="text-align:left;">%s</td>%s</tr>""" % 
                   (editfile, sample_code, delete))

    def collapse_lines(self, group):
        new_group = []
        keys = group.keys()
        keys.sort()
        for key in keys:
            for entry in group[key]:
                new_group.append(entry)
        return new_group

    def process_fields(self, section_choose, fields, propid, proposal):
        # Pop out any field whose name begins with an underscore and do other
        # cruddy processing
        for field in fields.keys():
            # Due to change in the usage of FieldStorage, this is put in here
            # to filter out "empty" items. This will correctly set their 
            # data fields to NULL below, and activate the missing field
            # tracking.
            if (fields[field] == ""):
                fields.pop(field)
                continue

            if (field[0] == "_"):
                if (fields.keys().__contains__(field[1:]) == True):
                    fields.pop(field)
                else:
                    fields[field[1:]] = fields[field]
                    fields.pop(field)

        if 'numb' not in fields:
            id = False
        else:
            id = fields.pop('numb')
            
        valid = False
        for section in self.sections:
            if (section_choose == section['section']):
                valid = True
                do_section = section
                break
        if (valid != True):
            raise cpss.connector.CpssUserErr("""This section does not exist. 
                  Please choose another. If you believe this is in error, 
                  please contact the site administrator.""")

        # Collapse along line numbers and return value matching id.
        final_group = None # defining this pre loop so it exists post-loop.
        for group in do_section['data']:
            final_group = self.collapse_lines(group)
            if (id == False):
                break
            else:
                for element in final_group:
                    if ((element['fieldname'] == 'numb') and
                        (str(element['data']) == str(id))):
                        break
                else:
                    final_group = None
                    continue
                break

        ##insert data validation and error checking here:

        for data_field in final_group:
            if (data_field['fieldtype'] == 'bool'):
                if (fields.__contains__(data_field['fieldname']) == True):
                    if (fields[data_field['fieldname']] == "on"):
                        data_field['data'] = 1
                    else:
                        data_field['data'] = 0
                else:
                    data_field['data'] = 0
            elif (data_field['fieldtype'] == 'date'):
                data_field['data'] = 'CURDATE()'
            elif (fields.__contains__(data_field['fieldname']) == True):
                data_field['data'] = fields[data_field['fieldname']]
                if (data_field['fieldtype'] == 'fast_corrconfig'):
                    if (data_field['data'] == "No Value Set"):
                        data_field['data'] = None
                if (type(data_field['fieldtype']) == type(list())):
                    if (data_field['data'] == "No Value Set"):
                        data_field['data'] = None
            else:
                data_field['data'] = None

        cpss.db.proposal_tagset(proposal[do_section['table']], propid, 
                                final_group, id=id)

    def element(self, element, edit=False, view=False):
        if (element.__contains__('fieldtype') == False):
            element['fieldtype'] = None
            element['fieldname'] = None
            element['html'] = element['data']
            return element

        ##Begin Error Checking##
        if (element.__contains__('check') == True):
            if (element['check'] == []):
                element['error'] = None
            else:
                a = ErrorCheck(element['data'], element['check'], 
                               self)
                element['error'] = a.GetError()
        else:
            a = ErrorCheck(element['data'], ['NoNull'], self)
            element['error'] = a.GetError()

        #######################################################################
        if (element['fieldtype'] == 'array'):
            element['sqltype'] = """SET('A','B','C','D','E')"""
            set = {'A': 0, 'B': 0, 'C':0, 'D':0, 'E':0}
            if (element['data'] == None):
                data = []
            else:
                data = element['data'].split(',')
                for datum in data:
                    if (datum == 'A'):
                        set['A'] = 1
                    elif (datum == 'B'):
                        set['B'] = 1
                    elif (datum == 'C'):
                        set['C'] = 1
                    elif (datum == 'D'):
                        set['D'] = 1
                    elif (datum == 'E'):
                        set['E'] = 1
                    
            if (edit == True):
                element['html'] = ""
                keys = set.keys()
                keys.sort()
                for key in keys:
                    if set[key] == 1:
                        checked='checked'
                    else:
                        checked=''
                    element['html'] += ("""&nbsp;&nbsp;%s<input id="check" 
                                           type="checkbox" name="%s" 
                                           value="%s" %s>""" % (key,
                                           element['fieldname'], key, checked))
            if (view == True):
                element['html'] = element['data']
        #######################################################################
        elif (type(element['fieldtype']) == type(list())):
            element['sqltype'] = ("enum(" +
                                  str(str(element['fieldtype'])[1:-1]) + ")")
            if (edit == True):
                element['fieldtype'] = ['No Value Set'] + element['fieldtype']
                element['html'] = ("""<select name="%s">""" %
                                   (element['fieldname']))
                for value in element['fieldtype']:
                    if (element['data'] != None):
                        if (element['data'] == value):
                            element['html'] += ("""<option value="%s" selected>
                                                %s""" % (value, value))
                        else:
                            element['html'] += ("""<option value="%s">%s""" %
                                                (value, value))
                    else:
                        element['html'] += ("""<option value="%s">%s""" %
                                            (value, value))
                element['html'] += """</select>"""
            if (view == True):
                element['html'] = element['data']
                if element['error'] != None:
                    element['text'] = ("{\cellcolor{red!45}%s}" % element['data'])
        #######################################################################
        elif (element['fieldtype'] == 'institution'):
            element['sqltype'] = 'text'
            if (edit == True):
                values = ['Caltech', 'UC Berkeley', 'UMD', 'UIUC', 'UChicago']
                element['html'] = ("""<select name="_%s" onChange="
                                   databox = form.%s
                                   selectbox = form._%s
                                   if (selectbox.options[selectbox.selectedIndex].value == 'Other')
                                   {
                                       databox.value='Insert Institution Name Here';
                                       databox.disabled=false;
                                       databox.style.visibility='visible';
                                   }
                                   else
                                   {
                                       databox.style.visibility='hidden';
                                       databox.disabled=true;
                                       databox.value=selectbox.options[selectbox.selectedIndex].value;
                                   }">""" % (element['fieldname'], element['fieldname'], element['fieldname']))

                if (element['data'] == None):
                    element['data'] = values[0]
                
                if (values.__contains__(element['data']) == True):
                    for value in values:
                        if (element['data'] == value):
                            element['html'] += ("""<option value="%s"
                                                    selected>%s"""
                                                % (value, value))
                        else:
                            element['html'] += ("""<option value="%s">%s""" %
                                                (value, value))
                    element['html'] += """<option value="Other">Other"""

                    element['html'] += """</select>"""
                    element['html'] += ("""<input type="text" name="%s"
                    value="%s" disabled style="visibility:hidden;">""" %
                                        (element['fieldname'],element['data']))
                else:
                    for value in values:
                        element['html'] += ("""<option value="%s">%s""" %
                                            (value, value))
                    element['html'] += """<option value="Other" selected>
                                          Other"""

                    element['html'] += """</select>"""
                    element['html'] += ("""<input type="text" name="%s"
                                           value="%s">""" %
                                        (element['fieldname'],element['data']))
            if (view == True):
                element['html'] = element['data']
        #######################################################################
        elif (element['fieldtype'] == 'fast_corrconfig'):
            element['sqltype'] = 'text'
            if (edit == True):
                values = ['No Value Set'] + sorted(element['fielddata'].keys())

                # Populate freqbool and slbwbool:
                freqbool = ['False']
                slbwbool = ['False']
                for i in values:
                    if i == 'No Value Set':
                        continue
                    if element['fielddata'][i]['userFreq'] == True:
                        freqbool.append("True")
                    else:
                        freqbool.append("False")
                    if element['fielddata'][i]['userBW'] == True:
                        slbwbool.append("True")
                    else:
                        slbwbool.append("False")

                element['html'] = ("""<select name="%(fieldname)s" onChange="
                                   freq = form.f_freq;
                                   slbw = form.f_slbw;
                                   selbox = form.%(fieldname)s;
                                   var freqbool=[%(fb)s];
                                   var slbwbool=[%(sb)s];
                                   if (freqbool[selbox.selectedIndex] == 'False')
                                   {
                                       freq.value='';
                                       freq.disabled=true;
                                   }
                                   else
                                   {
                                       freq.disabled=false;
                                   }
                                   if (slbwbool[selbox.selectedIndex] == 'False')
                                   {
                                       slbw.value='No Value Set';
                                       slbw.disabled=true;
                                   }
                                   else
                                   {
                                       slbw.disabled=false;
                                   }">""" % {'fieldname' : element['fieldname'], 
                                             'fb' : ("'" + "','".join(freqbool) + "'"),
                                             'sb' : ("'" + "','".join(slbwbool) + "'"),
                                             })

                for value in values:
                    if (element['data'] != None):
                        if (element['data'] == value):
                            element['html'] += ("""<option value="%s" selected>
                                                %s""" % (value, value))
                        else:
                            element['html'] += ("""<option value="%s">%s""" %
                                                (value, value))
                    else:
                        element['html'] += ("""<option value="%s">%s""" %
                                            (value, value))
                element['html'] += ("</select><script> window.onload=form.%s.onchange;</script>" % (element['fieldname']))
            if (view == True):
                element['html'] = element['data']
                if element['error'] != None:
                    element['text'] = ("{\cellcolor{red!45}%s}" % element['data'])


            if (view == True):
                element['html'] = element['data']
        #######################################################################
        elif (element['fieldtype'] == 'observation_type'):
            element['sqltype'] = 'text'
            values = ['SINGLEPOL', 'DUALPOL', 'FULLPOL', 'CARMA23']
            shortvalues = ['SP', 'DP', 'FP', '23']
            if (edit == True):
                element['html'] = ("""<select name=%s>""" % element['fieldname'])
                if (element['data'] not in values):
                    element['data'] = "Not Specified"
                    element['html'] += "<option value='Not Specified' selected>Not Specified"
                
                for value in values:
                    if ((values.__contains__(element['data']) == True) and
                        (element['data'] == value)):
                        element['html'] += ("""<option value="%s" selected>%s"""
                                            % (value, value))
                    else:
                        element['html'] += ("""<option value="%s">%s""" % (value, value))

                element['html'] += """</select>"""

            if (view == True):
                if element['data'] in values:
                    element['html'] = shortvalues[values.index(element['data'])]
                    element['text'] = shortvalues[values.index(element['data'])]
                else:
                    element['html'] = '#'
                    element['text'] = '{\cellcolor{red!45}$\Box$}'
        #######################################################################
        elif (element['fieldtype'] == 'integer'):
            element['sqltype'] = 'bigint(20)'
            if (edit == True):
                if (element['data'] == None):
                    data = ""
                else:
                    data = element['data']

                if (element['fieldname'] == 'numb'):
                    element['html'] = ("""%s<input type="hidden" name="%s"
                                          value="%s">""" % (
                        data, element['fieldname'], data))
                else:
                    element['html'] = ("""<input type="text" name="%s"
                                          value="%s">""" %
                                       (element['fieldname'], data))
            if (view == True):
                element['html'] = element['data']
                if element['data'] == None:
                    element['text'] = "0"
        #######################################################################
        elif (element['fieldtype'] == 'text'):
            element['sqltype'] = 'text'
            if (edit == True):
                if (element['data'] == None):
                    data = ""
                else:
                    data = element['data']

                element['html'] = ("""<input type="text" name="%s"
                                       value="%s">""" %
                                   (element['fieldname'], str(data.replace('&', '&#38;').replace('"', '&#34;'))))
            if (view == True):
                if (element.__contains__('size') == True):
                    front = '<div style="width:%spx;text-align:center;margin-left:auto;margin-right:auto">' % (element['size'])
                    back = '</div>'
                else:
                    front = ''
                    back = ''
                if (element['data'] == None):
                    element['html'] = element['data']
                    if element['error'] == None:
                        element['text'] = ''
                    else:
                        element['text'] = "{\cellcolor{red!45}$\Box$}"
                else:
                    element['html'] = front + element['data'].replace('&', '&#38;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&#34;') + back
                    if element['error'] != None:
                        element['text'] = ("{\cellcolor{red!45}%s}" % element['data'])
                    if element['fieldname'] == "email":
                        element['text'] = "\\url{" + element['data'] + "}"

        #######################################################################
        elif (element['fieldtype'] == 'date'):
            element['sqltype'] = 'date'
            if (element['data'] != None):
                if (type(element['data']) != type(str(''))):
                    element['data'] = str(element['data'])[0:10]

            if (edit == True):
                if (element['data'] == None):
                    data = ""
                else:
                    data = element['data']
                element['html'] = ("""<input type="hidden" name="%s"
                                     value="%s">%s""" % (element['fieldname'],
                                                         data, data))
            if (view == True):
                if (element['data'] == None):
                    element['html'] = None
                else:
                    element['html'] = element['data']
        #######################################################################
        elif (element['fieldtype'] == 'bool'):
            element['sqltype'] = 'tinyint(1)'
            if (edit == True):
                if (element['data'] == None) or (element['data'] == 0):
                    checked = ""
                else:
                    checked = "checked"
                element['html'] = ("""<input id="check" type="checkbox"
                                       name="%s"%s>""" % (
                    element['fieldname'], checked))
            if (view == True):
                if (element['data'] == None):
                    element['html'] = "None"
                elif (str(element['data']) == "0"):
                    element['html'] = """&mdash;"""
                    element['text'] = """--"""
                else:
                    element['html'] = """X"""
                    element['text'] = """X"""
        #######################################################################
        elif (element['fieldtype'] == 'longtext'):
            element['sqltype'] = 'longtext'

            if (edit == True):
                if (element['data'] == None):
                    data = ""
                else:
                    data = element['data']
                element['html'] = ("""<textarea name="%s">%s</textarea>""" % (
                    element['fieldname'], str(data.replace('&', '&#38;'))))

            if (view == True):
                if (element['data'] != None):
                    data = ("<p class='textview'>" +
                            str(element['data']).replace('&', '&#38;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', "<br>") +
                            "</p>")
                else:
                    data = element['data']
                element['html'] = data
        else:
            element['html'] = element['data']

        if (element['error'] != None):
            if (view == True):
                element['html'] = ("""<font id="error">%s</font>""" %
                                   element['html'])
            self.error = True
        else:
            element['error'] = ''

        if (self.justification == True):
            if (element['fieldname'] == 'technical_justification'):
                element['error'] = ''
            if (element['fieldname'] == 'scientific_justification'):
                element['error'] = ''
                            
        return element

    def escape_underscore(self, data):
        # This function is for conditional escaping of underscores on
        # cover sheet data.
        if type(data) == type(dict()):
            for key in data.keys():
                data[key] = escape_backslash(data[key])
            return data
        elif type(data) != type(""):
            return data

        start_index = 0
        while (1):
            index = data.find("_", start_index)
            if index == -1 :
                break

            if index == 0:
                data = "\\" + data
                # one space for inserted char one for _ itself
                start_index = 2
            elif data[index-1] == "\\":
                # this value is escaped, just skip over
                start_index = index + 1
            else:
                data = data[0:index] + "\\" + data[index:]
                # one space for char, one for the _ itself
                start_index = index + 2

        return data

    def latex_generate(self, propid, file_send=True,
                       carma_propno="Unsubmitted", ignore_pagelength=False):
        base_dir = (cpss.config['base_directory'])
        files_dir = (cpss.config['base_directory'] +
                     cpss.config['files_directory'])
        prop_dir = files_dir + propid + '/'

        if (os.path.isdir(prop_dir) == False):
            os.mkdir(prop_dir)
        if (os.path.isdir(prop_dir + 'justification/') == False):
            os.mkdir(prop_dir + 'justification/')
        if (os.path.isfile(prop_dir + "aastex.cls") == False):
            os.symlink("../aastex.cls", prop_dir+"aastex.cls")
        if (os.path.isfile(prop_dir + "justification/aastex.cls") == False):
            os.symlink("../aastex.cls", prop_dir+"justification/aastex.cls")
        if (os.path.isfile(prop_dir + 'latex.pdf') == True):
            os.unlink(prop_dir + 'latex.pdf')
        if (os.path.isfile(prop_dir + 'latex.dvi') == True):
            os.unlink(prop_dir + 'latex.dvi')
        if (os.path.isfile(prop_dir + 'justification/justification.pdf') == True):
            os.unlink(prop_dir + 'justification/justification.pdf')
        ### Create the cover sheet

        propinfo = None
        authors = None
        sources = None

        for section in self.sections :
            if (section['section'] == 'propinfo'):
                a = section['data']
                propinfo = self.data_strip(section['data'][0])
                # scan propinfo for certain characters
                #charlist = ['&']
                #replace_with = ['\&']
                # iterate over all data lines in propinfo
                #for line in propinfo:
                #    for i in xrange(1):
                #        line.find()
            elif (section['section'] == 'author'):
                authors = []
                for line in section['data']:
                    authors.append(self.data_strip(line))
            elif (section['section'] == 'source'):
                sources = []
                for line in section['data']:
                    sources.append(self.data_strip(line))
            elif (section['section'] == 'prior_obs'):
                temp = self.data_strip(section['data'][0])
                propinfo['prior_obs'] = temp['prior_obs']
            elif (section['section'] == 'special_requirements'):
                temp = self.data_strip(section['data'][0])
                propinfo['special_requirements'] = temp['special_requirements']
            elif (section['section'] == 'abstract'):
                temp = self.data_strip(section['data'][0])
                propinfo['abstract'] = temp['abstract']
            propinfo['total_time'] = self.calc_hours()

        # Set internal flag if the project is a key_project
        if ((propinfo.__contains__('key_project') == True) and 
            (propinfo['key_project'] == "X")):
            is_key_project = True
        else:
            is_key_project = False

        author_lines = ""
        source_data = ""

        for author in authors:
            for i in xrange(1, len(self.tempclass.author_order.keys())+1):
                if ((self.tempclass.author_order[i] == 'numb') and 
                    (author[self.tempclass.author_order[i]] == 1)):
                    data = "PI"
                else:
                    data = str(author[self.tempclass.author_order[i]])

                if self.tempclass.author_order[i] == 'name':
                    data = r"\raggedright\nohyphens{" + data + r"}"

                if self.tempclass.author_order[i] == 'institution':
                    data = r"\raggedright\nohyphens{" + data + r"}"

                if self.tempclass.author_order[i] == 'email':
                    author_lines  = (author_lines + data + " & ")
                else:
                    author_lines  = (author_lines + self.escape_underscore(data) + " & ")
            author_lines = author_lines[:-2] + " \\\\\n"

        for source in sources:
            for i in xrange(1, len(self.tempclass.source_order.keys())+1):
                    source_data += str(source[self.tempclass.source_order[i]]) + " & "
            source_data = source_data[:-2] + " \\\\\n"

        c = open(base_dir + "/Template/" + self.template_name + ".tex", 'r')
        cover_template = c.read()
        c.close()
        
        #propinfo = self.escape_underscore(propinfo)
        #This is done above in author block to remove escaping email addresses.
        #author_lines = self.escape_underscore(author_lines)
        source_data = self.escape_underscore(source_data)
        semester = self.escape_underscore(self.cycleinfo['cyclename'])

        cover = strTemplate(cover_template)
        out = cover.safe_substitute(propinfo, author_lines=author_lines, 
                                    source_data=source_data, 
                                    propno=carma_propno, semester=semester)

        tfile = open(prop_dir + 'latex.tex', 'w')
        tfile.write(out)
        tfile.close()

        # Run latex three times to get any references correct and tables.
        for i in xrange(0, 3):
            latex = os.popen("""cd %s; /usr/bin/pdflatex -interaction=nonstopmode %s""" 
                             % (prop_dir, prop_dir + 'latex.tex'), 'r')
            latex_info = latex.readlines()
            retval = latex.close()

            if (retval != None):
                return ('coversheet', latex_info)

        if self.cycleinfo['type'] in ['fast', 'cs']:
            # If the proposal type doesnt have a justification, dump out file
            # and skip the rest of the routine.
            if ((os.path.isfile(prop_dir + 'latex.pdf') == True) and
                (file_send == True)):
                pdf = open(prop_dir + 'latex.pdf', 'r')
                data = pdf.read()
                pdf.close()
                self.req.headers_out.add('Content-Disposition',
                                         'attachment; filename=%s.pdf' % 
                                         (propid)) 
                self.req.headers_out.add('Content-Length', str(len(data)))
                self.req.content_type='application/pdf'
                self.req.write(data)
                
            return 0

        result = cpss.db.images_list(self.propid)
        if (len(result) != 0):
            for image in result:
                self.image_check(image, prop_dir)

        if self.justification == False:
            for section in self.sections:
                if (section['section'] == 'technical_justification'):
                    tjust = str(self.data_strip(section['data'][0])['technical_justification'])
                elif (section['section'] == 'scientific_justification'):
                    sjust = str(self.data_strip(section['data'][0])['scientific_justification'])

            tfile = open(prop_dir + 'justification/justification.tex', 'w')
            tfile.write(cpss.text.tmpl_just % (sjust, tjust))
            tfile.close()
        
        if (self.justification == True):
            justification = open(prop_dir + 'justification/justification.tex',
                                 'wb')
            data = cpss.db.justification_get_data(self.propid)
            if (data == None):
                justification.write(cpss.text.tmpl_nojust)
                just_skip = 1
            else:
                justification.write(data)
            justification.close()

        # Run latex twice to get any references correct
        for i in xrange(0,2):
            latex = os.popen("""cd %s; /usr/bin/latex -interaction=nonstopmode %s""" % (prop_dir + 'justification/', prop_dir + 'justification/justification.tex'), 'r')
            latex_info = latex.readlines()
            retval = latex.close()

            if (retval != None):
                return ('justification', latex_info)

        at = os.popen("""cd %sjustification/; dvips -t letter -o - %sjustification/justification.dvi | ps2pdf14 - %sjustification/justification.pdf""" % (prop_dir, prop_dir, prop_dir))
        at.close()

        # Merge the two PDF files together

        output_pdf = PdfFileWriter()

        justification_pdf = PdfFileReader(file(prop_dir + "justification/justification.pdf", "rb"))
        latex_pdf = PdfFileReader(file(prop_dir + "latex.pdf", "rb"))

        for i in xrange(latex_pdf.getNumPages()):
            output_pdf.addPage(latex_pdf.getPage(i))

        # If key project is set to true, then set the max number of pages 
        # to 8. Else set to 3
        if is_key_project == True:
            max_pages = 8
        else:
            max_pages = 3

        num_just_pages = justification_pdf.getNumPages()

        if (num_just_pages > max_pages):
            if ignore_pagelength == False:
                # warn info here
                if file_send == False:
                    return 1
                cpss.connector.do_header()
                self.req.write("Your justification has produced %s pages of output. The proposal system will not accept justification sections that are greater than %s pages long. <a href='%s'>Click here</a> to view your PDF with truncated output." % (num_just_pages, max_pages, "pdf/" + str(self.propid) + "/skip"))
                cpss.connector.do_footer()
                return 1
            num_just_pages = max_pages

        for i in xrange(0, num_just_pages):
            output_pdf.addPage(justification_pdf.getPage(i))
        
        output_stream_pdf = open(prop_dir + "latex-final.pdf", "wb")
        output_pdf.write(output_stream_pdf)
        output_stream_pdf.close()

        if ((os.path.isfile(prop_dir + 'latex-final.pdf') == True) and
            (file_send == True)):
            pdf = open(prop_dir + 'latex-final.pdf', 'r')
            data = pdf.read()
            pdf.close()
            self.req.headers_out.add('Content-Disposition',
                                     'attachment; filename=%s.pdf' % (propid)) 
            self.req.headers_out.add('Content-Length', str(len(data)))
            self.req.content_type='application/pdf'
            self.req.write(data)

        return 0

    def image_check(self, image, propdir):
        if (image['file'] == ''):
            return
        if (os.path.isfile(propdir + 'justification/' + image['file']) == True):
            return
        else:
            imdata = cpss.db.images_get(image['proposalid'], image['numb'])[0]
            file = open(propdir + 'justification/' + imdata['file'], 'wb')
            file.write(imdata['ps_data'])
            file.close()

class ErrorCheck:
    def __init__(self, value, error_list, template):
        self.tmpLinescan = template.tmpLinescan # Used in enchanced error checking; can be
                                       # optional.
        self.tempclass = template.tempclass

        self.error = ''
        self.order = ['NoNull',
                      'NoSpaces',
                      'AlphaNumeric',
                      'Alpha',
                      'NoC23',
                      'NoDualPol',
                      'NoFullPol',
                      'Numeric',
                      'num_float',
                      'OBType',
                      'Only3mmInC23', # Placing this here in the chain guarantees
                                      # that the value is already a number.
                      'Only1cm3mmInC23',
                      'CARMAFreq',
                      'CARMAFreqWith1cm',
                      'SZAFreq',
                      'PolFreq',
                      'Integer',
                      'NoZero',
                      'raCheck',
                      'FastraCheck',
                      'decCheck',
                      'FastdecCheck',
                      'obsblockCheck',
                      'timeCheck',
                      'FastArrayConfig',
                      'antCheck',
                      'FastBWCheck',
                      'FastFreqCheck',
                      'FastTrackLength',]
        for error in self.order:
            if (error_list.__contains__(error) == True):
                self.__class__.__dict__[error](self, value)
                if (self.error != ''):
                    break

    def AddError(self, error):
        if (self.error == ''):
            self.error += ' '
        self.error += error

    def GetError(self):
        if (self.error == ''):
            return None
        else:
            return self.error

    def NoNull(self, value):
        if (value == None):
            self.AddError("This field must not be blank.")

    def OBType(self, value):
        values = ['SINGLEPOL', 'DUALPOL', 'FULLPOL', 'CARMA23']
        if value not in values:
            self.AddError("Observation Type must be selected from one of the values in the drop down box.")

    def NoSpaces(self, value):
        for i in value:
            if (i == ' '):
                self.AddError("This field must not contain spaces.")
                break

    def AlphaNumeric(self, value):
        if (value.isalnum() == False):
            self.AddError("This field must only contain alphanumeric characters.")

    def Alpha(self, value):
        if (value.isalpha() == False):
            self.AddError("This field must only contain letters.")

    def Numeric(self, value2):
        if type(value2) == type(long()):
            value = str(value2)
        else:
            value = value2
        error = False
        if (value.count('.') > 1):
            error = True
        else:
            val = value.replace('.', '')
            if (val.isdigit() == False):
                error = True
        if (error == True):
            self.AddError("This field must only contain numbers.")

    def Only3mmInC23(self, value):
        if self.tmpLinescan.__contains__('observation_type') == False:
            return # Simple errorcheck to make sure following lines dont fail.

        if self.tmpLinescan['observation_type'] == 'CARMA23':
            if float(value) > 116.0 or float(value) < 80.0:
                self.AddError("CARMA23 mode is only available at 3mm.")

    def Only1cm3mmInC23(self, value):
        if self.tmpLinescan.__contains__('observation_type') == False:
            return # Simple errorcheck to make sure following lines dont fail.

        if self.tmpLinescan['observation_type'] == 'CARMA23':
            if (float(value) < 116.0) and (float(value) > 80.0):
                return
            elif (float(value) < 36.0) and (float(value) > 26.0):
                return
            else:
                self.AddError("CARMA23 mode is only available at 1cm and 3mm.")
    
    def CARMAFreq(self, value):
        if self.tmpLinescan.__contains__('corr_frequency') == False:
            return
    
        if (value != '0') and (value != None):
            try:
                freq = self.tmpLinescan['corr_frequency']
                if (float(freq) <= 116.0) and (float(freq) >= 80.0):
                    return
                elif (float(freq) <= 270.0) and (float(freq) >= 215.0):
                    return
                else:
                    self.AddError("Frequency must lie in the 3mm or 1mm bands.")
            except TypeError:
                self.AddError("Frequency must lie in the 3mm or 1mm bands.")
            except ValueError:
                self.AddError("Invalid frequency specified in frequency field.")

    def CARMAFreqWith1cm(self, value):
        if self.tmpLinescan.__contains__('corr_frequency') == False:
            return
    
        if (value != '0') and (value != None):
            try:
                freq = self.tmpLinescan['corr_frequency']
                if (float(freq) <= 116.0) and (float(freq) >= 80.0):
                    return
                elif (float(freq) <= 270.0) and (float(freq) >= 215.0):
                    return
                elif (float(freq) <= 36.0) and (float(freq) >= 26.0):
                    return
                else:
                    self.AddError("Frequency must lie in the 3mm or 1mm bands.")
            except TypeError:
                self.AddError("Frequency must lie in the 3mm or 1mm bands.")
            except ValueError:
                self.AddError("Invalid frequency specified in frequency field.")

    def SZAFreq(self, value):
        if self.tmpLinescan.__contains__('corr_frequency') == False:
            return
    
        if (value != '0') and (value != None):
            try:
                freq = self.tmpLinescan['corr_frequency']
                if (float(freq) <= 116.0) and (float(freq) >= 80.0):
                    return
                elif (float(freq) <= 36.0) and (float(freq) >= 26.0):
                    return
                else:
                    self.AddError("Frequency must lie in the 1cm or 3mm bands.")
            except TypeError:
                self.AddError("Frequency must lie in the 1cm or 3mm bands.")
            except ValueError:
                self.AddError("Invalid frequency specified in frequency field.")

    def PolFreq(self, value):
        if self.tmpLinescan.__contains__('observation_type') == False:
            return # Simple errorcheck to make sure following lines dont fail.

        if ((self.tmpLinescan['observation_type'] == 'DUALPOL') or
            (self.tmpLinescan['observation_type'] == 'FULLPOL')):
            if (float(value) > 215.0) and (float(value) < 270.0):
                return
            else:
                self.AddError("DUAL and FULL Polarizations are only available in the 1mm band.")

    def NoC23(self, value):
        if self.tmpLinescan.__contains__('observation_type') == False:
            return # Simple errorcheck to make sure following line doesnt fail.
        if (value != '0') and (self.tmpLinescan['observation_type'] == 'CARMA23'):
            self.AddError("CARMA23 mode is not allowed in this configuration.")

    def NoDualPol(self, value):
        if self.tmpLinescan.__contains__('observation_type') == False:
            return # Simple errorcheck to make sure following line doesnt fail.
        if (value != '0') and (self.tmpLinescan['observation_type'] == 'DUALPOL'):
            self.AddError("DUALPOL mode is not allowed in this array configuration.")        

    def NoFullPol(self, value):
        if self.tmpLinescan.__contains__('observation_type') == False:
            return # Simple errorcheck to make sure following line doesnt fail.
        if (value != '0') and (self.tmpLinescan['observation_type'] == 'FULLPOL'):
            self.AddError("FULLPOL mode is not allowed in this array configuration.")        

    def Integer(self, value):
        if (value.isdigit() == False):
            self.AddError("This field must only contain integers.")

    def NoZero(self, value):
        if (value == '0'):
            self.AddError("This value must be greater than 0.")

    def raCheck(self, RA):
        digit = []
        for i in RA:
            digit.append(i)
        if (len(digit) != 5) or (digit.count(":") > 1):
            self.AddError("Invalid format: must be HH:MM")
        else:
            if (not(digit[0].isdigit() and digit[1].isdigit and
                    (digit[2] == ":") and
                    digit[3].isdigit() and digit[4].isdigit())):
                self.AddError("Invalid format: must be HH:MM")
                return
            hours = 10*int(digit[0]) + int(digit[1])
            if (hours < 0 or hours > 23):
                self.AddError("Invalid hours value.")
                return
            minutes = 10*int(digit[3]) + int(digit[4])
            if(minutes < 0 or minutes > 59):
                self.AddError("Invalid minutes value.")
                return

    def decCheck(self, DEC):
        digit = []
        negative = 0
        for i in DEC:
            digit.append(i)
        if(len(digit) == 0):
            self.AddError("Invalid format: must be (+/-)DD:MM")
            return
        if(digit[0] == '-'):
            negative = 1
        if(digit[0] == '-' or digit[0] == '+'):
            digit = digit[1:]
        if(len(digit) != 5) or (digit.count(":") > 1):
            self.AddError("Invalid format: must be (+/-)DD:MM")
        else:
            if(digit[0].isdigit() and digit[1].isdigit() and
                 (digit[2] == ":") and
                 digit[3].isdigit() and digit[4].isdigit()):
                degrees = 10*int(digit[0]) + int(digit[1])
                if (degrees >= 90 or ((negative == 1) and (degrees > 40))):
                    self.AddError("""Invalid degrees value: must be -40 <
                                   DD <= 90""")
                minutes = 10*int(digit[3]) + int(digit[4])
                if(minutes < 0 or minutes > 59):
                    self.AddError("Invalid minutes value")
            else:
                self.AddError("Invalid format: must be (+/-)DD:MM")

    def obsblockCheck(self, obsblock):
            if(('%' in obsblock) or
               ('#' in obsblock) or
               ('>' in obsblock) or
               ('<' in obsblock) or
               ('.' in obsblock) or
               ('\\' in obsblock) or
               ('/' in obsblock) or
               ('(' in obsblock) or
               (')' in obsblock) or
               ('[' in obsblock) or
               (']' in obsblock) or
               (' ' in obsblock) or
               ('$' in obsblock) or
               ('&' in obsblock) or
               ('!' in obsblock) or
               ('@' in obsblock) or
               ('*' in obsblock) or
               ('?' in obsblock) or
               ('"' in obsblock) or
               ("'" in obsblock)):
                self.AddError("Invalid character in obsblock name.")

    def timeCheck(self, time):
        minTime = ''
        maxTime = ''
        dashFound = 0
        dashes = 0
        for i in time:
            if(i == '-'):
                dashFound = 1
                dashes = dashes+1
            elif(dashFound):
                maxTime = maxTime + i
            else:
                minTime = minTime + i
        if(dashes > 1):
            self.AddError("Invalid format: it must be min-max")
            return

        try:
            lowTime = float(minTime)
            hiTime = float(maxTime)
        except ValueError:
            self.AddError("Invalid Minimum Time")
            return

        if(hiTime < lowTime):
            self.AddError("Max value is less than min value")

    def antCheck(self, numant):
        ant = float(numant)
        if ((ant < 1) or (ant > 15)):
            self.AddError("The range of values must be between 1 and 15.")

    def FastBWCheck(self, bw):
        if 'f_corrconfig' not in self.tmpLinescan:
            self.AddError("Invalid Mode Template")
            return # Check to make sure that the following lines dont fail.
        
        if not hasattr(self.tempclass, 'fast_modes'):
            self.AddError("Invalid Mode Template.")
            return
        
        mode = self.tmpLinescan['f_corrconfig']
        if mode == None:
            self.AddError("A correlator mode must be selected.")
            return

        try:
            userBW = self.tempclass.fast_modes[mode]['userBW']
        except:
            self.AddError("A correlator mode must be selected.")
            return

        if (userBW == False) and (bw != None):
            self.AddError("Selected Mode does not allow for a user selected bandwidth.")
            
        if (userBW == True) and (bw == None):
            self.AddError("Selected Mode requires a user selected bandwidth for spectral line bands.")

    def FastFreqCheck(self, freq):
        if 'f_corrconfig' not in self.tmpLinescan:
            self.AddError("Invalid Mode Template")
            return # Check to make sure that the following lines dont fail.
        
        if not hasattr(self.tempclass, 'fast_modes'):
            self.AddError("Invalid Mode Template.")
            return
        
        mode = self.tmpLinescan['f_corrconfig']
        if mode == None:
            self.AddError("A correlator mode must be selected.")
            return

        try:
            userFreq = self.tempclass.fast_modes[mode]['userFreq']
        except:
            self.AddError("A correlator mode must be selected.")
            return

        if (userFreq == False) and (freq != None):
            self.AddError("Selected Mode does not allow for a user selected frequency.")

        if (userFreq == True) and (freq == None):
            self.AddError("Selected Mode requires a user selected frequency.")
        else:
            if 'freqRange' in self.tempclass.fast_modes[mode]:
                freqRange = self.tempclass.fast_modes[mode]['freqRange']
            else:
                return
            lo = freqRange[0]
            hi = freqRange[1]
            
            try:
                float(freq)
            except:
                self.AddError("Frequency field must be blank or a number.")
                return

            if (float(freq) < lo) or (float(freq) > hi):
                self.AddError("Selected mode has a frequency range of %s GHz to %s GHz." % 
                              (str(lo), str(hi)))
            
    def FastTrackLength(self, value):
        if (float(value) < 1.) or (float(value) > 3.):
            self.AddError("Requested track length must be between 1 and 3 hours.")

    def FastraCheck(self, RA):
        ra = RA.split(':')
        if len(ra) != 3:
            self.AddError("Invalid format: must be HH:MM:SS.SS")
            return

        hours = ra[0]
        minutes = ra[1]
        seconds = ra[2]

        try:
            if "{0:02d}".format(int(hours)) == hours:
                if (int(hours) < 0) or (int(hours) > 23):
                    raise ValueError
            else:
                raise ValueError

            if "{0:02d}".format(int(minutes)) == minutes:
                if (int(minutes) < 0) or (int(minutes) > 59):
                    raise ValueError
            else:
                raise ValueError

            if "{0:05.2f}".format(float(seconds)) == seconds:
                if (float(seconds) < 0) or (float(seconds) > 59.99):
                    raise ValueError
            else:
                raise ValueError
        except:
            self.AddError("Invalid format: must be HH:MM:SS.SS")

    def FastdecCheck(self, DEC):
        dec = DEC.split(':')
        if len(dec) != 3:
            self.AddError("Invalid format: must be (+/-) DD:MM:SS.SS")
            return

        degrees = dec[0]
        minutes = dec[1]
        seconds = dec[2]

        try:
            # Support -00 degrees:
            if (degrees[0] == '-'):
                coef = -1
                degrees = degrees[1:]
            elif (degrees[0] == '+'):
                coef = 1
                degrees = degrees[1:]
            elif (degrees[0].isdigit() == True):
                coef = 1
            else:
                raise ValueError
                            
            if "{0:02d}".format(int(degrees)) == degrees:
                if ((int(degrees)*coef) < -40) or ((int(degrees)*coef) > 90):
                    self.AddError("""Invalid degrees value: must be -40 < DD <= 90""")
                    raise ValueError
            else:
                raise ValueError

            if "{0:02d}".format(int(minutes)) == minutes:
                if (int(minutes) < 0) or (int(minutes) > 59):
                    raise ValueError
            else:
                raise ValueError

            if "{0:05.2f}".format(float(seconds)) == seconds:
                if (float(seconds) < 0) or (float(seconds) > 59.99):
                    raise ValueError
            else:
                raise ValueError
        except:
            self.AddError("Invalid format: must be (+/-) DD:MM:SS.SS")

    def FastArrayConfig(self, array_config):
        if 'f_corrconfig' not in self.tmpLinescan:
            self.AddError("Invalid Mode Template")
            return # Check to make sure that the following lines dont fail.
        
        if not hasattr(self.tempclass, 'fast_modes'):
            self.AddError("Invalid Mode Template.")
            return
        
        mode = self.tmpLinescan['f_corrconfig']
        if mode == None:
            self.AddError("A correlator mode must be selected.")
            return

        sci1_configs = ['A', 'B', 'C', 'D', 'E']
        sci2_configs = ['SH', 'SL']

        # Check if array config exists, error if it doesnt.
        if (array_config in sci1_configs):
            sci1 = True
            sci2 = False
        elif (array_config in sci2_configs):
            sci1 = False
            sci2 = True
        else:
            self.AddError("Configuration does not exist.")
            return
            
        if sci1 and ('SCI1_' not in mode):
            self.AddError("Array Configuration %s unavailable in SCI2 correlator mode." % array_config)
        elif sci2 and ('SCI2_' not in mode):
            self.AddError("Array Configuration %s unavailable in SCI1 correlator mode." % array_config)

    def num_float(self, value):
        try:
            float(value)
        except ValueError:
            self.AddError("This field must only contain numbers.")
        return

