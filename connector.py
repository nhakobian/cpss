from mod_python import apache
from mod_python import util
import md5
import datetime
import smtplib
import os
import string
from random import choice

cpss = apache.import_module("cpss")

class Connector:
    def __init__(self, Page):
        self.req = cpss.req
        self.thePage = Page
        self.theSession = cpss.session
        #Parse the GET/POST fields
        self.fields = util.FieldStorage(self.req)
        self.config = cpss.config
        self.options = cpss.options
        
    def do_header(self, login=False, **keywords):
        if (self.theSession['authenticated'] == False):
            self.thePage.header(login=False, **keywords)
        else:
            self.thePage.header(login=True, **keywords)

    def do_footer(self):
        self.thePage.footer()

    def Dispatch(self, pathstr):
        self.theSession["random"] = self.randomcode()

        if (self.options['maint_mode'] == '0'):
            self.theSession['maint_mode'] = 0
        elif (self.options['maint_mode'] == '1'):
            self.theSession['maint_mode'] = 1
        elif (self.options['maint_mode'] == '2'):
            self.theSession['maint_mode'] = 2
            if (self.theSession['maint_allow'] == False):
                if (pathstr == []):
                    pathstr = ['']
                if (pathstr[0] == self.options['maint_key']):
                    self.theSession['maint_allow'] = True
                    self.theSession.save()
                    self.do_header(refresh='')
                else:
                    self.do_header()
                    self.req.write(self.options['maint_message'])
                    self.do_footer()
                    self.theSession.delete()
                    return apache.OK
            else:
                if (pathstr == []):
                    pass
                elif (pathstr[0] == 'invalidate'):
                    self.theSession.delete()
                    self.theSession['authenticated'] = False
                    self.do_header(refresh='')            
        self.theSession.save()
        
        if (pathstr == []):
            self.Root()
        elif (pathstr[0] == 'logout'):
            self.Logout()
        elif (pathstr[0] == 'help'):
            self.Help(pathstr)
        elif (pathstr[0] == 'help_small'):
            self.HelpSmall(pathstr)
        #Anything above this line will be available at any time.
        #Anything below this line will only be available when logged in and
        # user has an activated account.
        elif ((self.theSession['authenticated'] == True) and
            (self.theSession['activated'] != "0")):
            self.Activate()
        elif ((self.theSession['authenticated'] == True) and 
            (self.theSession['activated'] == "0")):
            if (pathstr[0] == 'proposal'):
                self.Proposal(pathstr)
            elif (pathstr[0] == 'user'):
                self.User()
            else:
                self.do_404()
        #Everything below will only be available when people are logged out.
        elif (self.theSession['authenticated'] == False):
            if (pathstr[0] == 'create'):
                self.Create()
            elif (pathstr[0] == 'login'):
                self.Login()
            else:
                self.do_404()
        #The below lines execute when everything else doesnt match anything.
        else:
            self.do_404()
        return apache.OK
        
    def Root(self):
        self.do_header()
        self.thePage.main()
        self.do_footer()

    def Create(self):
        error = ""
        if (self.fields.getfirst('submit') == 'Submit'):
            name = self.fields.getfirst('name')
            email = self.fields.getfirst('email')
            pass1 = self.fields.getfirst('password1')
            pass2 = self.fields.getfirst('password2')
            if (name == ""):
                error = "You must supply your real name."
            if (email == ""):
                error = "You must supply your e-mail address."
            if ((pass1 == "") or (pass1 != pass2)):
                error = "You must supply matching passwords."
            if (error == ""):
                if (cpss.db.user_exists(email) == True):
                    error = """There already is a user with this e-mail address
                               registered in the system. If you believe this
                               is in error, please contact the website
                               administrator."""
                    self.do_header()
                    self.thePage.user_create(Name=name, Email=email,
                                             Error=error)
                    self.do_footer()
                else:
                    code = self.randomcode()
                    self.activation_mail(name, email, code)
                    cpss.db.add_user(name, email, pass1, code)
                    self.do_header()
                    self.thePage.user_create_success(name, email)
                    self.do_footer()
            else:
                self.do_header()
                self.thePage.user_create(Name=name, Email=email, Error=error)
                self.do_footer()
        else:
            self.do_header()
            self.thePage.user_create(random=self.theSession["random"])
            self.do_footer()

    def activation_mail(self, name, email, code):
        if (self.config['sendemail'] == False):
            return
        mail = smtplib.SMTP()
        mail.connect()
        msg = (cpss.text.email_activation % (name, email, name, code))
        mail.sendmail("do_not_reply@carma-prop.astro.illinois.edu", email, msg)
        mail.quit()

    def Proposal(self, pathstr):
        if (self.theSession['authenticated'] == True):
            if (self.fields.__contains__('action') == True):
                if (self.fields['action'] == 'edit'):
                    result = cpss.db.proposal_fetch(
                        self.theSession['username'], pathstr[2])
                    if (result == False):
                        self.do_header(refresh="proposal/")
                        self.req.write("""You do not have access to this
                        proposal, please go back to the proposal list and
                        try again.""")
                        self.do_footer()
                    else:
                        if (self.fields.__contains__('section') == True):
                            section = self.fields['section']
                        else:
                            self.do_header(refresh="proposal/")
                            self.do_footer()
                        if (self.fields.__contains__('id') == True):
                            id = self.fields['id']
                        else:
                            id = False

                        template = cpss.Template.Template(result['template'],
                          result['cyclename'], pathstr[2], False)
                        self.do_header()
                        template.make_html(section_choose=section, id=id)
                        self.do_footer()
                elif (self.fields['action'] == 'add'):
                    result = cpss.db.proposal_fetch(
                        self.theSession['username'], pathstr[2])
                    if (result == False):
                        self.do_header(refresh="proposal/")
                        self.req.write("""You do not have access to this
                        proposal, please go back to the proposal list and
                        try again.""")
                        self.do_footer()
                    else:
                        if (self.fields.__contains__('section') == True):
                            section = self.fields['section']
                        else:
                            self.do_header(refresh="proposal/")
                            self.do_footer()

                        pathtext = ""
                        for a in pathstr:
                            pathtext += a + '/'

                        template = cpss.Template.Template(result['template'],
                          result['cyclename'], pathstr[2], True, Fetch=False)

                        for tempsection in template.sections:
                            if (tempsection['section'] == section):
                                tablename = tempsection['table']
                            else:
                                #put error here
                                pass

                        if (section == 'image'):
                            id = cpss.db.images_add(pathstr[2])
                            self.do_header(refresh='proposal/edit/' +
                                           pathstr[2])
                        else:
                            id = cpss.db.proposal_table_addrow(
                                tablename, pathstr[2], numb=True)
                            self.do_header(refresh='proposal/edit/%s/?action=edit&section=%s&id=%s' % (pathstr[2], section, id))

                elif (self.fields['action'] == 'delete'):
                    result = cpss.db.proposal_fetch(
                        self.theSession['username'], pathstr[2])
                    if (result == False):
                        self.do_header(refresh="proposal/")
                        self.req.write("""You do not have access to this
                        proposal, please go back to the proposal list and
                        try again.""")
                        self.do_footer()
                    else:
                        if (self.fields.__contains__('section') == True):
                            section = self.fields['section']
                        else:
                            self.do_header(refresh="proposal/")
                            self.do_footer()
                        if (self.fields.__contains__('id') == True):
                            id = self.fields['id']
                        else:
                            if (section != 'justification'):
                                self.do_header(refresh="proposal/")
                                self.do_footer()

                        pathtext = ""
                        for a in pathstr:
                            pathtext += a + '/'

                        template = cpss.Template.Template(result['template'],
                          result['cyclename'], pathstr[2], True)

                        for tempsection in template.tempclass.sections:
                            if (tempsection['section'] == section):
                                tablename = tempsection['table']
                                section_name = tempsection['name']
                            else:
                                #put error here
                                pass

                        if (section == 'image'):
                            done = True
                            image = cpss.db.images_get(pathstr[2], id)
                            cpss.db.images_delete(pathstr[2], id)
                            
                            files_dir = (cpss.db.config['base_directory'] +
                                         cpss.db.config['files_directory'])
                            prop_dir = files_dir + pathstr[2] + '/justification/'
                                            
                            if (os.path.isfile(prop_dir + image[0]['file'])
                                == True):
                                os.unlink(prop_dir + image[0]['file'])
                        elif (section == 'justification'):
                            done = True
                            cpss.db.justification_delete_data(
                                pathstr[2])

                            files_dir = (cpss.db.config['base_directory'] +
                                         cpss.db.config['files_directory'])
                            prop_dir = files_dir + pathstr[2] + '/justification/'

                            if (os.path.isfile(prop_dir + 'justification.pdf')
                                == True):
                                os.unlink(prop_dir + 'justification.pdf')
                            if (os.path.isfile(prop_dir + 'justification-up.pdf')
                                == True):
                                os.unlink(prop_dir + 'justification-up.pdf')

                            
                        else:
                            done = cpss.db.proposal_table_delrow(
                                tablename, pathstr[2], numb=id)
                            
                        if (done == True):
                            self.do_header(refresh=pathtext)
                            self.do_footer()
                        if (done == False):
                            self.do_header()
                            self.req.write("""You must have at least one value
                            in the %s section. You may not delete this last
                            value.""" % section_name)
                elif (self.fields['action'] == 'submit'):
                    result = cpss.db.proposal_fetch(
                        self.theSession['username'], pathstr[2])
                    if (result == False):
                        self.do_header(refresh="proposal/")
                        self.req.write("""You do not have access to this
                        proposal, please go back to the proposal list and
                        try again.""")
                        self.do_footer()
                    else:
                        pathtext = ""
                        for a in pathstr:
                            pathtext += a + '/'
                        if (self.fields.__contains__('section') == False):
                            self.do_header(refresh=pathtext)
                            self.do_footer()
                        else:
                            template = cpss.Template.Template(
                              result['template'], result['cyclename'],
                              pathstr[2], False)

                            fields = dict(self.fields)
                            fields.pop('action')
                            section = fields.pop('section')

                            if (section == 'image'):
                                if (self.fields.__contains__('id') == True):
                                    fname = template.process_image(fields)
                                    image_data = fields['file'].file.read()
                                    if (len(image_data) > (1024*1024*14)):
                                        self.do_header()
                                        self.req.write("""The postscript image
                                        you are
                                        trying to upload is greater than the
                                        allowed size of 14MB. If you must
                                        upload an image greater than this size
                                        please send a message to
                                        proposal-help@astro.uiuc.edu for help.
                                        """)
                                        self.do_footer()
                                    else:
                                        cpss.db.images_update(
                                            pathstr[2],
                                            fname, fields['id'],
                                            image_data)
                                        self.do_header(refresh=pathtext)
                                else:
                                    self.do_header(refresh="proposal/")
                            elif (section == 'justification'):
                                pdf_data = fields['file'].file.read()
                                if (len(pdf_data) > (1024*1024*10)):
                                    self.do_header()
                                    self.req.write("""The LaTeX file
                                    you are
                                    trying to upload is greater than the
                                    allowed size of 10MB. Please check to 
                                    make sure you are uploading the correct
                                    file.
                                    """)
                                    self.do_footer()
                                else:
                                    cpss.db.justification_add_update(
                                        pathstr[2], pdf_data)
                                    self.do_header(refresh=pathtext)
                            else:
                                fields = template.process_fields(section,
                                                                 fields,
                                                                 pathstr[2])
                                if (self.fields.__contains__('id') == True):
                                    idtext = "&id=%s" % self.fields['id']
                                else:
                                    idtext = ''
                                self.do_header(refresh=pathtext)
                                self.do_footer()

            else:
                items = len(pathstr)
                if (items == 3):
                    if (pathstr[1] == "typechange"):
                        result = cpss.db.proposal_fetch(
                            self.theSession['username'], pathstr[2])
                        if (result == False):
                            self.do_header(refresh="proposal/")
                            self.req.write("""You do not have access to this
                            proposal, please go back to the proposal list and
                            try again.""")
                            self.do_footer()
                        else:
                            if (self.fields.__contains__('type') == True):
                                if (self.fields['type'] ==
                                    "Website Justification"):
                                    cpss.db.justification_type_set(
                                        pathstr[2], 0)
                                    cpss.db.justification_delete_data(
                                        pathstr[2])

                                    files_dir = (cpss.db.config['base_directory'] + cpss.db.config['files_directory'])
                                    prop_dir = files_dir + pathstr[2] + '/justification/'

                                    if (os.path.isfile(prop_dir +
                                                       'justification.pdf')
                                        == True):
                                        os.unlink(prop_dir +
                                                  'justification.pdf')
                                    if (os.path.isfile(prop_dir +
                                                       'justification-up.pdf')
                                        == True):
                                        os.unlink(prop_dir +
                                                  'justification-up.pdf')
                                if (self.fields['type'] ==
                                    "LaTeX Template"):
                                    cpss.db.justification_type_set(
                                        pathstr[2], 1)
                                self.do_header(refresh=("""proposal/edit/%s"""
                                                        % pathstr[2]))
                            else:
                                self.do_header(refresh='proposal/')
                            

                    elif (pathstr[1] == "edit"):
                        result = cpss.db.proposal_fetch(
                            self.theSession['username'], pathstr[2])
                        if (result == False):
                            self.do_header(refresh="proposal/")
                            self.req.write("""You do not have access to this
                            proposal, please go back to the proposal list and
                            try again.""")
                            self.do_footer()
                        else:
                            self.do_header()

                            if (result['pdf_justification'] == 1):
                                justification = True
                            else:
                                justification = False
                                
                            template = cpss.Template.Template(
                              result['template'], result['cyclename'],
                              pathstr[2], True, justification=justification)

                            template.make_html()
                            self.do_footer()
                    elif (pathstr[1] == "delete"):
                        result = cpss.db.proposal_fetch(
                            self.theSession['username'], pathstr[2])
                        if (result == False):
                            self.do_header(refresh="proposal/")
                            self.req.write("""You do not have access to this
                            proposal, please go back to the proposal list and
                            try again.""")
                            self.do_footer()
                        elif (result['carmaid'] != None):
                            self.do_header()
                            self.req.write("""You may not delete a proposal
                            that has already been submitted.""")
                            self.do_footer()
                        elif (self.fields.__contains__('delete') == True):
                            template = cpss.Template.Template(
                              result['template'], result['cyclename'],
                              pathstr[2], True)

                            cpss.db.proposal_delete(
                                self.theSession['username'],
                                result['proposalid'],
                                template.tables, result['cyclename'])
                            self.do_header(refresh="proposal/")
                            self.do_footer()
                        else:
                            pathtext = ""
                            for a in pathstr:
                                pathtext += a + '/'
                            template = cpss.Template.Template(
                              result['template'], result['cyclename'],
                              pathstr[2], True)

                            title = None
                            for asection in template.sections:
                                if (asection['section'] == 'propinfo'):
                                    section = asection

                            for field in section['data'][0][1]:
                                if (field['fieldname'] == 'title'):
                                    title = field['data']
                                    break
                            self.do_header()
                            self.thePage.delete_verify(pathtext, str(title))
                            self.do_footer()
                    elif (pathstr[1] == "finalpdf"):
                        result = cpss.db.proposal_fetch(
                            self.theSession['username'], pathstr[2])
                        if (result == False):
                            self.do_header(refresh="proposal/")
                            self.req.write("""You do not have access to this
                            proposal, please go back to the proposal list and
                            try again.""")
                            self.do_footer()
                        else:
                            pdf = cpss.db.pdf_get_data(pathstr[2])
                            if (len(pdf) == 0):
                                self.do_header()
                                self.req.write("""You have not submitted this
                                proposal. Please submit a proposal before
                                attempting to view a submitted proposal.""")
                                self.do_footer()
                            else:
                                self.req.headers_out.add('Content-Disposition',
                           'attachment; filename=%s.pdf' % (result['carmaid']))
                                self.req.content_type='application/force-download'
                                self.req.write(pdf)
                            
                    elif (pathstr[1] == "pdf"):
                        result = cpss.db.proposal_fetch(
                            self.theSession['username'], pathstr[2])
                        if (result == False):
                            self.do_header(refresh="proposal/")
                            self.req.write("""You do not have access to this
                            proposal, please go back to the proposal list and
                            try again.""")
                            self.do_footer()
                        else:
                            if (result['pdf_justification'] == 0):
                                justification = False
                            else:
                                justification = True
                            template = cpss.Template.Template(
                              result['template'], result['cyclename'],
                              pathstr[2], True, justification=justification)
                            retval = template.latex_generate(pathstr[2])

                            if (retval != 0):
                                self.do_header()
                                self.req.write("""<b>A LaTeX error occured. The
                                output is displayed below:</b><br><br>%s""" %
                                              (self.lines2text(retval[7:])))
                                self.do_footer()
                    elif (pathstr[1] == 'submit'):
                        result = cpss.db.proposal_fetch(
                            self.theSession['username'], pathstr[2])
                        if (result == False):
                            self.do_header(refresh="proposal/")
                            self.req.write("""You do not have access to this
                            proposal, please go back to the proposal list and
                            try again.""")
                            self.do_footer()
                        elif (self.fields.__contains__('sub_prop') == True):
                            if (self.fields['sub_prop'] == 'Submit Proposal'):
                                idstr = ""
                                if (result['carmaid'] == None):
                                    idstr = str(self.options['next_propno'])
                                    length = len(idstr)
                                    if (length < 4):
                                        for i in xrange(0, 4 - length):
                                            idstr = "0" + idstr
                                    idstr = "c" + idstr
                                    cpss.db.set_next_propno(self.options['next_propno'] + 1, result['cyclename'])
                                    cpss.db.pw_generate(pathstr[2])
                                    cpss.db.proposal_setcarmaid(pathstr[2], idstr)
                                else:
                                    idstr = result['carmaid']


                                if (result['pdf_justification'] == 0):
                                    justification = False
                                else:
                                    justification = True

                                template = cpss.Template.Template(
                                  result['template'], result['cyclename'],
                                  pathstr[2], True,justification=justification)
                                
                                ret = template.latex_generate(template.propid,
                                                          file_send = False,
                                                          carma_propno = idstr)

                                self.do_header()

                                if (ret != 0):
                                    self.req.write(cpss.text.submit_failed_error % pathstr[2])
                                else:
                                    pdf = open(self.config['base_directory']
                                               + self.config['files_directory'] +
                                               '/' + pathstr[2] +
                                               '/latex-final.pdf', 'r')
                                    pdf_data = pdf.read()
                                    pdf.close()

                                    if (len(pdf_data) > (1024*1024*14)):
                                        self.req.write(cpss.text.submit_failed_size % pathstr[2])
                                    else:
                                        cpss.db.pdf_add_update(
                                            pathstr[2], pdf_data)
                                        cpss.db.proposal_submit(
                                            pathstr[2])
                                        self.req.write(cpss.text.submit_success)
                                self.do_footer()
                            else:
                                self.do_header(refresh=('proposal/submit/%s' %
                                                        pathstr[2]))
                                

                        else:
                            if (result['pdf_justification'] == 0):
                                justification = False
                            else:
                                justification = True
                                
                            template = cpss.Template.Template(
                              result['template'], result['cyclename'],
                              pathstr[2], True, justification=justification)
                            self.do_header()
                        
                            self.req.write("""<div class="navbar,
                                                          propheader">""")
                            self.req.write("""<ul id="navlist">
                            <li><a href="%s">Current Proposal</a></li>""" %
                                           ("proposal/edit/" +
                                            str(template.propid)))
                            self.req.write("""</ul></div>""")
                                                    
                            self.req.write("""<ul><li>Checking to make sure
                            all the equired proposal fields have been
                            filled out...""")
                            error = template.data_verify()

                            #Check to make sure no fields have errors.
                            if (error == True):
                                self.req.write("""<br><span style="color:red; font-weight:bold;">You must fix the errors above before you can submit the proposal.</span>""")
                            else:
                                self.req.write("""<span style="color:green; font-weight:bold;">All fields have been verified.</span>""")
                            self.req.write("</li>")
                            #Do additional checks such as obsblock and time
                            #alloc.
                            if (error == False):
                                self.req.write("<li>Performing other error checks...")
                                #checking to see if all obsblock names are
                                #unique.
                                error_obsblock = template.obsblock_verify()
                                #add other checks in here...

                                if (error_obsblock == False):
                                    error2 = False
                                    self.req.write("""<span style="color:green; font-weight:bold;">done</span></li>""")
                                else:
                                    error2 = True
                                    self.req.write("""</li>""")
                            else:
                                error2 = False

                            if (error2 == True):
                                self.req.write("""<br><span style="color:red; font-weight:bold;">You must fix the errors above before you can submit the proposal.</span>""")
                            #display final check
                            if ((error == False) and (error2 == False)):
                                self.req.write("""<li>Please click
                                <a href="proposal/pdf/%s">here</a> to
                                proofread your proposal before you perform the
                                final submit.</li>""" % str(template.propid))
                            self.req.write("""</ul>""")

                            if ((error == False) and (error2 == False)):
                                self.req.write("""<div class="maintenance"
                                style="text-align:left;padding:1em;">
                                Follow these instructions to submit.<br>
                                <br><li>Make sure you have proofread your
                                proposal as directed above.</li>
                                <li>By clicking the submit button below,
                                your proposal will be given a proposal number
                                and you will be given a final PDF with this
                                number embedded in it.</li>
                                <li>Only click the submit button once. It can
                                take a long time to prepare your final
                                PDF.</li>
                                <li>You can access your submitted PDF from your
                                main proposals page ONLY by clicking on "View
                                Submitted Proposal."</li></br>

                                <form action="proposal/submit/%s" method=post>
                                <center><input type=submit name="sub_prop"
                                 value="Submit Proposal"/></center>

                                </form>
                                </div>""" % str(template.propid))

                            self.do_footer()
                        pass
                    else:
                        self.do_404()
                elif (items == 2):
                    if (pathstr[1] == "add"):
                        options = cpss.db.options_get()
                        template = cpss.Template.Template(options['template'],
                          options['cyclename'], None, True, Fetch=False)
                        propno = cpss.db.proposal_add(
                            self.theSession['username'],
                            template.tempclass.tables,
                            options['cyclename'])
                        self.do_header(refresh=("proposal/edit/%s" % (propno)))
                        self.do_footer()
                    else:
                        self.do_404()
                elif (items == 1):
                    self.do_header()
                    result = cpss.db.proposal_list(
                        self.theSession['username'])
                    self.thePage.proposal_list(result, self.theSession['name'])
                    self.do_footer()
                else:
                    self.do_404()
        else:
            self.Login()

    def HelpSmall(self, pathstr):
        self.Help(pathstr, small=True)

    def Help(self, pathstr, small=False):
        if (small == True):
            self.req.content_type="text/html"
            self.req.write("""<html><head>
            <base href="%s" />
            <title>Help</title>
            <link rel="stylesheet" href="cpss.css" type="text/css">
            </head><body>""" % self.config['html_base'])
        else:
            self.do_header()

        if (len(pathstr) == 1):
            pathstr.append('index')
        else:
            pathstr.append('')
            
        if (pathstr[1] == 'propinfo'):
            self.req.write(cpss.text.help_propinfo)

        elif (pathstr[1] == 'abstract'):
            self.req.write(cpss.text.help_abstract)

        elif (pathstr[1] == 'author'):
            self.req.write(cpss.text.help_author)

        elif (pathstr[1] == 'source'):
            self.req.write(cpss.text.help_source)

        elif (pathstr[1] == 'special_requirements'):
            self.req.write(cpss.text.help_specialreq)

        elif (pathstr[1] == 'prior_obs'):
            self.req.write(cpss.text.help_priorobs)

        elif (pathstr[1] == 'scientific_justification'):
            self.req.write(cpss.text.help_scientificjust)

        elif (pathstr[1] == 'technical_justification'):
            self.req.write(cpss.text.help_technicaljust)

        elif (pathstr[1] == 'image'):
            self.req.write(cpss.text.help_image)

        elif (pathstr[1] == 'tot_hours'):
            self.req.write(cpss.text.help_tothours)
            
        elif (pathstr[1] ==  'index'):
            self.req.write(cpss.text.help_index % (
                       self.config['html_base'], self.config['html_base'],
                       self.config['html_base'], self.config['html_base'],
                       self.config['html_base'], self.config['html_base'],
                       self.config['html_base'], self.config['html_base']))

        if (small == True):
            self.req.write("""<br><br><br><br><br><br><br></body></html>""")
        else:
            self.do_footer()

    def Login(self):
        Error = ""
        if (self.fields.getfirst('forgotpw') == 'Password Reset'):
            username = self.fields.getfirst('user')
            if (cpss.db.user_exists(username) == False):
                Error = "That username does not exist."
            else:
                Error = "A new password has been sent to your email address."
                email = username
                newpw = self.randomcode()
                cpss.db.password_change(email, newpw)
                mail = smtplib.SMTP()
                mail.connect()                
                msg = (cpss.text.email_pwreset % (email, email, newpw))
                mail.sendmail("do_not_reply@carma-prop.astro.illinois.edu", email, msg)
                mail.quit()

        if (self.fields.getfirst('submit') == 'Submit'):
            username = self.fields.getfirst('user')
            password = self.fields.getfirst('pass')

            if (username == 'admin'):
                options = cpss.db.options_get()
                if (md5.md5(password).hexdigest() == options['admin_pw']):
                    self.theSession['admin'] = True
                    self.theSession['authenticated'] = True
                    self.theSession['username'] = 'admin'
                    self.theSession['name'] = 'CPSS Administrator'
                    self.theSession['activated'] = "0"
                    self.theSession.save()
                    self.do_header(refresh="proposal/")
                else:
                    Error = """The username and password you have supplied are
                               not valid. Please try again."""
                    self.do_header(logon=True)
                    self.thePage.logon(Error=Error, Username=username)
                    self.do_footer()
                return

            if ((username == None) or (password == None) or
                (username == "") or (password == "")):
                Error = "You must enter both a username and a password."
                authenticate = False
            else:
                (authenticate, user) = cpss.db.verify_user(username,
                                                                   password)
            if (authenticate == False):
                Error = """The username and password you have supplied are not
                         valid. Please try again."""
                self.do_header(logon=True)
                self.thePage.logon(Error=Error, Username=username)
                self.do_footer()
            if (authenticate == True):
                self.theSession['authenticated'] = True
                self.theSession['username'] = user['email']
                self.theSession['name'] = user['name']
                self.theSession['activated'] = user['activated']
                self.theSession.save()
                self.do_header(refresh="proposal/")
        else:
            self.do_header(logon=True)
            self.thePage.logon(Error=Error)
            self.do_footer()

    def Logout(self):
        self.theSession.delete()
        self.theSession['authenticated'] = False
        self.do_header()
        self.req.write('''<center>The session has been closed. You will need
        to login again to view your proposals.</center>''')
        self.do_footer()

    def User(self):
        error=""
        if (self.fields.getfirst('changepw') == "Change Password"):
            username = self.theSession['username']
            oldpw = self.fields.getfirst('oldpw')
            newpw1 = self.fields.getfirst('newpw1')
            newpw2 = self.fields.getfirst('newpw2')

            if (str(type(oldpw)) != "<class 'mod_python.util.StringField'>"):
                oldpw = ""

            (authenticate, user) = cpss.db.verify_user(username, oldpw)
            
            if (authenticate == False):
                error = """Your current password is incorrect. Please verify 
                           your password."""
            elif ((str(type(newpw1)) != "<class 'mod_python.util.StringField'>") or (newpw1 != newpw2)):
                error = """The new passwords do not match. Please make sure 
                           they match."""
            else:
                cpss.db.password_change(username, newpw1)
                error = "Your password has been successfully changed."

        username = self.theSession['name']
        email = self.theSession['username']
        self.do_header()
        self.thePage.userpage(username, email, error=error)
        self.do_footer()

    def randomcode(self):
        size=8
        password = ''.join([choice(string.letters + string.digits + "!" + "@" + "_") for i in range(size)])
        return password

    def do_404(self):
        self.do_header()
        self.thePage.do_404()
        self.do_footer()

    def Activate(self):
        if (self.fields.getfirst('sub_activate') == "Activate Account"):
            code = self.fields.getfirst('activate')
            if (code == self.theSession['activated']):
                cpss.db.update_code(self.theSession['username'], "0")
                self.theSession['activated'] = "0"
                self.theSession.save()
                self.do_header(refresh='proposal/')
                self.thePage.activate(Error="""You have successfully activated
                your account. Click on the proposals tab above in order to
                start using the system.""")
                self.do_footer()
            else:
                self.do_header()
                self.thePage.activate(Error="""The code you entered is invalid.
                Either verify that you typed in the correct code or click the
                button at the bottom to send a new one to your e-mail
                account.""")
                self.do_footer()
        elif (self.fields.getfirst('sub_activate') ==
              "Resend Activation Code"):
            code = self.randomcode()
            self.theSession['activated'] = code
            self.theSession.save()
            cpss.db.update_code(self.theSession['username'], code)
            self.activation_mail(self.theSession['name'],
                                 self.theSession['username'], code)
            self.do_header()
            self.thePage.activate(Error="""A new activation code has been sent
            to the address that you specified when you registered the account.
            If you never recieve it, please inform the webmaster.""")
            self.do_footer()
        else:
            self.do_header()
            self.thePage.activate()
            self.do_footer()

    def lines2text(self, lines):
        buffer = ""
        for line in lines:
            buffer += line + "<br>" 
        return buffer

