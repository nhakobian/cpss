from mod_python import apache
from mod_python import util
import md5
import datetime
import smtplib
import os
import string
from random import choice

class Connector:
    def __init__(self, req, Template, Backend, Page, session, config, options):
        self.req = req
        self.theBackend = Backend
        self.thePage = Page
        self.theSession = session
        self.Template = Template
        #Parse the GET/POST fields
        self.fields = util.FieldStorage(self.req)
        self.config = config
        self.options = options
        
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
        elif (pathstr[0] == 'bugs'):
            self.do_header()
            self.thePage.bugs()
            self.do_footer()
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
                if (self.theBackend.user_exists(email) == True):
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
                    self.theBackend.add_user(name, email, pass1, code)
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
        msg = ("""To: "%s" <%s>
From: "CARMA Proposal System" <no_not_reply@carma-prop.astro.illinois.edu>
Subject: CARMA Proposal System Activation Code
Content-Type: text/plain;

Dear %s,

This automatically generated message is to inform you that you have
successfully registered for the CARMA Proposal system website. If
you believe you have recieved this message in error, please disregard
or forward it to the e-mail address below.

To activate your account:

1. Point your browser to http://carma-prop.astro.illinois.edu/proposals
2. Log into your account with the username (email address) and
   password that you created when signing up for the account. For
   security purposes, the password will not be displayed here. If
   you have forgotten your password, please contact the person below
   and request that it be reset. The password can never be seen or
   retrieved by the Proposal system staff, only reset.
3. Since this is your first time logging in, it will display a page
   requesting an activation code. Your activation code is:
   %s
   This is a one time procedure and you will never see or need this
   code again. It is used to verify that the e-mail address you
   have provided is accurate in case we need to contact you.
4. Press the activate button and you are ready to use the system!

If you have any questions or comments, please direct them to the
e-mail address below. This address is not checked and any message
directed to it will be returned with an error.

Thank You,
CARMA Proposal Staff
proposal-help@astro.uiuc.edu
""" % (name, email, name, code))
        mail.sendmail("do_not_reply@carma-prop.astro.illinois.edu", email, msg)
        mail.quit()

    def Proposal(self, pathstr):
        if (self.theSession['authenticated'] == True):
            if (self.fields.__contains__('action') == True):
                if (self.fields['action'] == 'edit'):
                    result = self.theBackend.proposal_fetch(
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

                        template = self.Template.Template(self.req,
                                                          result['template'],
                                                          result['cyclename'],
                                                          self.theBackend,
                                                          pathstr[2], False)
                        self.do_header()
                        template.make_html(section_choose=section, id=id)
                        self.do_footer()
                elif (self.fields['action'] == 'add'):
                    result = self.theBackend.proposal_fetch(
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

                        template = self.Template.Template(self.req,
                                                          result['template'],
                                                          result['cyclename'],
                                                          self.theBackend,
                                                          pathstr[2],
                                                          True, Fetch=False)

                        for tempsection in template.sections:
                            if (tempsection['section'] == section):
                                tablename = tempsection['table']
                            else:
                                #put error here
                                pass

                        self.theBackend.cache_invalidate(pathstr[2], section)

                        if (section == 'image'):
                            id = self.theBackend.images_add(pathstr[2])
                            self.do_header(refresh='proposal/edit/' +
                                           pathstr[2])
                        else:
                            id = self.theBackend.proposal_table_addrow(
                                tablename, pathstr[2], numb=True)
                            self.do_header(refresh='proposal/edit/%s/?action=edit&section=%s&id=%s' % (pathstr[2], section, id))

                elif (self.fields['action'] == 'delete'):
                    result = self.theBackend.proposal_fetch(
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

                        template = self.Template.Template(self.req,
                                                          result['template'],
                                                          result['cyclename'],
                                                          self.theBackend,
                                                          pathstr[2],
                                                          True)
                        for tempsection in template.tempclass.sections:
                            if (tempsection['section'] == section):
                                tablename = tempsection['table']
                                section_name = tempsection['name']
                            else:
                                #put error here
                                pass

                        if (section == 'image'):
                            done = True
                            image = self.theBackend.images_get(pathstr[2], id)
                            self.theBackend.images_delete(pathstr[2], id)
                            
                            files_dir = (self.theBackend.config['base_directory'] +
                                         self.theBackend.config['files_directory'])
                            prop_dir = files_dir + pathstr[2] + '/justification/'
                                            
                            if (os.path.isfile(prop_dir + image[0]['file'])
                                == True):
                                os.unlink(prop_dir + image[0]['file'])
                        elif (section == 'justification'):
                            done = True
                            self.theBackend.justification_delete_data(
                                pathstr[2])

                            files_dir = (self.theBackend.config['base_directory'] +
                                         self.theBackend.config['files_directory'])
                            prop_dir = files_dir + pathstr[2] + '/justification/'

                            if (os.path.isfile(prop_dir + 'justification.pdf')
                                == True):
                                os.unlink(prop_dir + 'justification.pdf')
                            if (os.path.isfile(prop_dir + 'justification-up.pdf')
                                == True):
                                os.unlink(prop_dir + 'justification-up.pdf')

                            
                        else:
                            self.theBackend.cache_invalidate(pathstr[2],
                                                             section)
                            done = self.theBackend.proposal_table_delrow(
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
#                    file = open('/srv/www/htdocs/proposals/files/dump4.txt', 'a')
#                    file.write(str(self.fields) + '\n\n\n')
#                    file.close()

                    result = self.theBackend.proposal_fetch(
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
                            template = self.Template.Template(self.req,
                                       result['template'], result['cyclename'],
                                       self.theBackend, pathstr[2], False)
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
                                        self.theBackend.images_update(
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
                                    self.theBackend.justification_add_update(
                                        pathstr[2], pdf_data)
                                    self.do_header(refresh=pathtext)
                            else:
                                self.theBackend.cache_invalidate(pathstr[2],
                                                                 section)
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
                        result = self.theBackend.proposal_fetch(
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
                                    self.theBackend.justification_type_set(
                                        pathstr[2], 0)
                                    self.theBackend.justification_delete_data(
                                        pathstr[2])

                                    files_dir = (self.theBackend.config['base_directory'] + self.theBackend.config['files_directory'])
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
                                    self.theBackend.justification_type_set(
                                        pathstr[2], 1)
                                self.do_header(refresh=("""proposal/edit/%s"""
                                                        % pathstr[2]))
                            else:
                                self.do_header(refresh='proposal/')
                            

                    elif (pathstr[1] == "edit"):
                        result = self.theBackend.proposal_fetch(
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
                                
                            template = self.Template.Template(self.req,
                                                          result['template'],
                                                          result['cyclename'],
                                                          self.theBackend,
                                                          pathstr[2], True,
                                                   justification=justification)

                            template.make_html()
                            self.do_footer()
                    elif (pathstr[1] == "delete"):
                        result = self.theBackend.proposal_fetch(
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
                            template = self.Template.Template(self.req,
                                                          result['template'],
                                                          result['cyclename'],
                                                          self.theBackend,
                                                          pathstr[2], True)
                            self.theBackend.proposal_delete(
                                self.theSession['username'],
                                result['proposalid'],
                                template.tables, result['cyclename'])
                            self.do_header(refresh="proposal/")
                            self.do_footer()
                        else:
                            pathtext = ""
                            for a in pathstr:
                                pathtext += a + '/'
                            template = self.Template.Template(self.req,
                                                          result['template'],
                                                          result['cyclename'],
                                                          self.theBackend,
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
                        result = self.theBackend.proposal_fetch(
                            self.theSession['username'], pathstr[2])
                        if (result == False):
                            self.do_header(refresh="proposal/")
                            self.req.write("""You do not have access to this
                            proposal, please go back to the proposal list and
                            try again.""")
                            self.do_footer()
                        else:
                            pdf = self.theBackend.pdf_get_data(pathstr[2])
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
                        result = self.theBackend.proposal_fetch(
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
                            template = self.Template.Template(self.req,
                                                          result['template'],
                                                          result['cyclename'],
                                                          self.theBackend,
                                                          pathstr[2], True,
                                                   justification=justification)
                            #open the embedded css
                            css_ps = open(self.config['base_directory'] +
                                          'cpss_ps.css', 'r')
                            data = css_ps.read()
                            css_ps.close()
                            retval = template.latex_generate(pathstr[2], data)

                            if (retval != 0):
                                self.do_header()
                                self.req.write("""<b>A LaTeX error occured. The
                                output is displayed below:</b><br><br>%s""" %
                                              (self.lines2text(retval[23:-2])))
                                self.do_footer()
                    elif (pathstr[1] == 'submit'):
                        result = self.theBackend.proposal_fetch(
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
                                    self.theBackend.set_next_propno(self.options['next_propno'] + 1, result['cyclename'])
                                    self.theBackend.pw_generate(pathstr[2])
                                    self.theBackend.proposal_setcarmaid(pathstr[2], idstr)
                                else:
                                    idstr = result['carmaid']


                                if (result['pdf_justification'] == 0):
                                    justification = False
                                else:
                                    justification = True

                                template = self.Template.Template(self.req,
                                                           result['template'],
                                                           result['cyclename'],
                                                           self.theBackend,
                                                           pathstr[2], True,
                                                   justification=justification)
                                css_ps = open(self.config['base_directory'] +
                                              'cpss_ps.css', 'r')
                                css = css_ps.read()
                                css_ps.close()
                                
                                ret = template.latex_generate(template.propid,
                                                              css,
                                                          file_send = False,
                                                          carma_propno = idstr)

                                self.do_header()

                                if (ret != 0):
                                    self.req.write("""
<div class="browser_error">
Submission failed!<br>
Please go back and check your document for LaTeX errors. Your proposal
has NOT been submitted. You may use the "View as PDF" option to view your
proposal and any errors that were generated. You must complete the submit
process again.<br>Click <a href="proposal/edit/%s">here</a> to continue.</div>
""" % pathstr[2])
                                else:
                                    pdf = open(self.config['base_directory']
                                               + self.config['files_directory'] +
                                               '/' + pathstr[2] +
                                               '/latex-final.pdf', 'r')
                                    pdf_data = pdf.read()
                                    pdf.close()

                                    if (len(pdf_data) > (1024*1024*14)):
                                        self.req.write("""
<div class=browser_error>
Submission Failed!<br><br>
The size of the final PDF file is over the limit that the submission system can
handle. The usual cause of this is using large bitmapped images in your
proposal. One way of reducing this size is to reduce the resolution of your
source image. If you still have a problem, please contact someone at
proposal-help@astro.uiuc.edu.
Click <a href="proposal/edit/%s">here</a> to continue.</div>
""" % pathstr[2])
                                    else:
                                        self.theBackend.pdf_add_update(
                                            pathstr[2], pdf_data)
                                        self.theBackend.proposal_submit(
                                            pathstr[2])
                                        self.req.write("""<div class=submitted>
Congratulations! You have submitted your proposal sucessfully!<br>
To view your final proposal, click on the Proposals button above to return
to the screen which lists your proposals, and click on the "view final pdf" link
available there.<br><br>

If you find a mistake in your proposal after you submit it, you may correct
the errors by editing your proposal and re-submitting it.<br><br>

Reminder: If you make corrections to your proposal and do not re-submit it,
the changes will NOT be reflected in the final PDF. You can always view the
final PDF by opening your proposals page and clicking on the "view final pdf"
link.
</div>""")
                                self.do_footer()
                            else:
                                self.do_header(refresh=('proposal/submit/%s' %
                                                        pathstr[2]))
                                

                        else:
                            if (result['pdf_justification'] == 0):
                                justification = False
                            else:
                                justification = True
                                
                            template = self.Template.Template(self.req,
                                                          result['template'],
                                                          result['cyclename'],
                                                          self.theBackend,
                                                          pathstr[2], True,
                                                   justification=justification)
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
                                self.req.write("""<div class="maintainence"
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
                        options = self.theBackend.options_get()
                        template = self.Template.Template(self.req,
                                                          options['template'],
                                                          options['cyclename'],
                                                          self.theBackend,
                                                          None,
                                                          True, Fetch=False)
                        propno = self.theBackend.proposal_add(
                            self.theSession['username'],
                            template.tempclass.tables,
                            options['cyclename'])
                        self.do_header(refresh=("proposal/edit/%s" % (propno)))
                        self.do_footer()
                    else:
                        self.do_404()
                elif (items == 1):
                    self.do_header()
                    result = self.theBackend.proposal_list(
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
            self.req.write("""

            <div class="helptext"> The <b>General Proposal
            Information</b> section is intended for the proposer to
            give some general information about their proposed
            project. Below is a description of what information is
            requested in this section.  </div>

            <a name="title" />
            <div class="helptitle">Title</div>
            <div class="helptext">The title of your proposal (no LaTeX
            characters are allowed).<br></div>

            <a name="date" />
            <div class="helptitle">Date</div>
            <div class="helptext">This date is set automatically to when
            you last edited the information on your proposal.</div>

            <a name="toe" />
            <div class="helptitle">Time Critical</div>
            <div class="helptext">Check this box if the object(s) you
            wish to observe need to be scheduled only at specific
            times (whether known in advance or not) (e.g. cometary
            observations, solar flares, transient source follow-up,
            coordinated observations).</div>

            <a name="priority" />
            <div class="helptitle">Priority</div>
            <div class="helptext">If you are submitting several
            proposals, you may assign a priority number to each proposal
            if you wish to designate one project as being more
            important than another. No error checking is performed on
            this field.</div>

            <a name="scientific_category" />
            <div class="helptitle">Scientific Category</div>
            <div class="helptext">What general category best describes
            your project?</div>

            <a name="type_of_observation" />
            <div class="helptitle">Type of Observation</div>
            <div class="helptext">Is this a spectral line observation,
            continuum observation, or both?</div>

            <a name="frequency_band" />
            <div class="helptitle">Frequency / Receiver Band</div>
            <div class="helptext">What receiver band are you
            requesting for your obervations?</div>

            <a name="help_required" />
            <div class="helptitle">Level of Help Required</div>
            <div class="helptext">Choose "Consultation" for help preparing
            for your observations. A collaborator is currently recommended
            if you are not already familiar with millimeter
            interferometer data reduction techniques.</div>
            """)
        elif (pathstr[1] == 'abstract'):
            self.req.write("""

            <div class="helptext"> Please keep the abstract
            to 1/4 of a page maximum. You may use LaTeX commands, but
            please keep them to a minimum. The abstract will be
            stored in the project database and any LaTeX commands will
            be stripped out.</div>

            """)
        elif (pathstr[1] == 'author'):
            self.req.write("""

            <div class="helptext">The <b>Authors List</b> section
            is intended for observers to give information regarding
            who is working on this proposed project, what institutions
            they are from, and whether or not the individuals are
            graduate students.</div>

            <a name="name" />
            <div class="helptitle">Name</div>
            <div class="helptext">Please insert your/your co-author(s)
            name(s) here.</div>

            <a name="email" />
            <div class="helptitle">E-mail</div>
            <div class="helptext">Please enter the e-mail addresses of
            you and your colleagues here.</div>

            <a name="phone" />
            <div class="helptitle">Phone Number</div>
            <div class="helptext">Please enter the contact phone
            number here.</div>

            <a name="institution" />
            <div class="helptitle">Institution</div>
            <div class="helptext">Please select your institution name
            here from the drop down box.  If you are not at one of the
            CARMA member institutions, select 'Other' and enter your
            institution name in the box that appears below.</div>

            <a name="grad" />
            <div class="helptitle">Graduate Student</div>
            <div class="helptext">Is this person a graduate student?</div>

            <a name="thesis" /> <div class="helptitle">Thesis</div> <div
            class="helptext">Is this proposal part of an approved graduate
            student thesis project? If this box is checked, a supporting
            e-mail from the advisor must be sent to Nikolaus Volgenau
            (volgenau@mmarray.org). The e-mail should describe the role of the
            observations in the thesis.</div>
            """)
        elif (pathstr[1] == 'source'):
            self.req.write("""

            <div class="helptext">The <b>Source Information</b> section
            allows the proposer to enter information about what sources
            he/she wants to observe using CARMA. If you have any questions
            as to what types of data are expected in the fields, please
            read the descriptions below. Please enter sources in the list in
            priority order.</div>
            
            <a name="array_config" />
            <div class="helptitle">Array Configuration</div>
            <div class="helptext">Which array configuration(s) are you
            requesting? See
            <a href="http://cedarflat.mmarray.org/observing/doc/instrument_desc.html"
            target="_blank">this
            page</a> for a description of the different array
            configurations. Please also see the definition of hours requested.
            </div>

            <a name="corr_frequency" />
            <div class="helptitle">Frequency of Observation</div>
            <div class="helptext">Please give the frequency of your
            observations in GHz.</div>

            <a name="name" />
            <div class="helptitle">Source Name</div>
            <div class="helptext">A short, simple, descriptive name
            for the object that you are observing.</div>

            <a name="ra" />
            <div class="helptitle">Right Ascension</div>
            <div class="helptext">Please give coordinates to the object
            or region that you are observing in J2000 format. If your
            proposal is accepted, you will be able to give more accurate
            coordinates at that time. Make sure that your Right Ascension
            is in the format HH MM or HH:MM.</div>

            <a name="dec" />
            <div class="helptitle">Declination</div>
            <div class="helptext">Please give the Declination of the
            object you are observing. See the restrictions and notes for
            Right Ascension above.</div>

            <a name="numb_fields" />
            <div class="helptitle">Number of Mosaic Fields</div>
            <div class="helptext">How many different pointings are
            involved in the observations of this source?</div>

            <a name="species" />
            <div class="helptitle">Species / Transition Name</div>
            <div class="helptext">If these are molecular line
            observations what species and transition are being
            observed. For continuum projects just enter
            "continuum".</div>

            <a name="self_cal" />
            <div class="helptitle">Can Self-Calibrate</div>
            <div class="helptext">Can your source be self-calibrated?</div>

            <a name="min_max" />          
            <div class="helptitle">Time Requested</div>
            <div class="helptext">How long are you requesting to
            observe this obsblock in hours (this time includes your
            source(s) and any calibrators observed), per array configuration?
            If the time requested
            is longer than can be accomodated in a single track, the
            observation will be on multiple days. Track lengths will
            depend on declination and whether the project is primarily
            an imaging project, or requires the best SNR. See
            <a href="http://cedarflat.mmarray.org/observing/doc/instrument_desc.html"
             target="_blank">this page</a> for more details.</div>

            <a name="imaging" />
            <div class="helptitle">Imaging/SNR</div>
            <div class="helptext">If the aim of this obsblock is to
            get the most complete UV coverage (and thus the best image
            possible) then select IMAGE. For detection projects, or other
            projects where signal to noise is critical, select SNR. Such
            projects can often be observed in smaller pieces or off transit
            to increase the scheduling efficiency of the telescope. To allow
            this, and receive compensation in the form of increased
            observing time, please check the "Flexible HA" box.</div>

            <a name="flexha" />
            <div class="helptitle">Flexible Hour Angle (Flex.HA)</div>
            <div class="helptext">Check this box if the observations for
            this obsblock may be usefully made in small pieces at any time
            the source is up. Checking this box will increase
            the scheduling efficiency of the telescope, and could thus
            increase the TAC disposition to your project and the
            likelihood of observations. Compensation in the form of
            increased observation time will be made if you elect this
            option.</div>

            """)
        elif (pathstr[1] == 'special_requirements'):
            self.req.write("""

            <div class="helptext">The special requirements section is
            designed for the proposer to describe any unusual observing
            constraints that are not defined anywhere else in the proposal.
            This includes a summary of special equipment, special observing
            conditions, required dates, or any other information even if it
            is described in another section.</div>
            
            """)
        elif (pathstr[1] == 'prior_obs'):
            self.req.write("""

            <div class="helptext">The Status of Prior CARMA Observations
            section allows the proposer to report on the status of the
            PI's prior CARMA observations. For example, whether they are
            reduced, in press, published, etc. Include previous project
            codes.
            </div>
            
            """)
        elif (pathstr[1] == 'scientific_justification'):
            self.req.write("""

            <div class="helptext">In the <b>Scientific
            Justification</b> section describe the scientific
            motivation for the project. The Scientific and Technical
            Justification sections combined may be no longer than
            three pages: 2 pages of text, and 1 for tables, figures, and references. LaTeX text may
            be used in this section. If you need to make a reference
            to an article or paper, please use inline references.
            </div>

            """)
        elif (pathstr[1] == 'technical_justification'):
            self.req.write("""

            <div class="helptext">In the <b>Technical
            Justification</b> section justify the proposed
            observations on technical grounds. Include any information
            that will allow the TAC to assess the technical viability
            of the project. The Scientific and Technical Justification
            sections combined may be no longer than three pages: 2 pages of text, and 1 for
            tables, figures, and references. LaTeX text may be used in
            this section. If you need to make a reference to an
            article or paper, please use inline references.</div>
            """)

        elif (pathstr[1] == 'image'):
            self.req.write("""

            <div class="helptext">Use the images section to attach any images
            to your proposal. The images must be in postscript (PS or EPS)
            format. If you upload any other type of image, you will get
            an error when you attempt to view the PDF of your proposal.
            If you
            need to make any adjustments to the attached image (i.e.
            rotation, scale, cropping) please refer to the documentation for
            the LaTeX package graphicx. The maximum file size for an image is
            ~14MB.</div>

            """)

        elif (pathstr[1] == 'tot_hours'):
            self.req.write("""

            <div class="helptext">The total number of hours is calculated by
            adding up how many hours per source you have requested, by
            multiplying Hours Requested by the number of array configurations
            you requested the source to be observed in. For example, if you requested
            a single source to be observed in the A, B, C, and D arrays for 8 hours,
            the Total Hours will be 32.</div>

            """)

            
        elif (pathstr[1] ==  'index'):
            self.req.write("""<span style="font-weight:bold;font-size:14pt">
            Choose a help topic below:</span>
            <ul style="help">
            <li><a href="%shelp/propinfo">General Proposal Information</a></li>
            <li><a href="%shelp/author">Authors List</a></li>
            <li><a href="%shelp/abstract">Abstract</a></li>
            <li><a href="%shelp/source">Source Information</a></li>
            <li><a href="%shelp/special_requirements">
                Special Requirements</a></li>
            <li><a href="%shelp/scientific_justification">
                Scientific Justification</a></li>
            <li><a href="%shelp/technical_justification">
                Technical Justification</a></li>
            <li><a href="%shelp/image">Image Attachments</a></li>
            <ul>
            <br>
            If you have an issue or question (whether it is a technical
            problem with the proposal site or a clarification on what
            type of information is expected) please send an e-mail to
            proposal-help@astro.uiuc.edu . If it is a technical issue,
            please make sure to give exact information as to what you
            were trying to do, and what the error message (if any) said.
            """ % (self.config['html_base'], self.config['html_base'],
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
            if (self.theBackend.user_exists(username) == False):
                Error = "That username does not exist."
            else:
                Error = "A new password has been sent to your email address."
                email = username
                newpw = self.randomcode()
                self.theBackend.password_change(email, newpw)
                mail = smtplib.SMTP()
                mail.connect()                
                msg = ("""To: %s
From: "CARMA Proposal System" <no_not_reply@carma-prop.astro.illinois.edu>
Subject: CARMA Proposal System Password Reset
Content-Type: text/plain;

You have requested a password reset for the account:
%s

Your new password is:
%s

You can change the password if you log in, click on the user option
and enter the information in the "Change Password" section. 

If you have any questions or problems feel free to contact us at the
address listed below.

Thank You,
CARMA Proposal Staff
proposal-help@astro.uiuc.edu
""" % (email, email, newpw))
                mail.sendmail("do_not_reply@carma-prop.astro.illinois.edu", email, msg)
                mail.quit()

        if (self.fields.getfirst('submit') == 'Submit'):
            username = self.fields.getfirst('user')
            password = self.fields.getfirst('pass')

            if (username == 'admin'):
                options = self.theBackend.options_get()
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
                (authenticate, user) = self.theBackend.verify_user(username,
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

            (authenticate, user) = self.theBackend.verify_user(username, oldpw)
            
            if (authenticate == False):
                error = """Your current password is incorrect. Please verify 
                           your password."""
            elif ((str(type(newpw1)) != "<class 'mod_python.util.StringField'>") or (newpw1 != newpw2)):
                error = """The new passwords do not match. Please make sure 
                           they match."""
            else:
                self.theBackend.password_change(username, newpw1)
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
                self.theBackend.update_code(self.theSession['username'], "0")
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
            self.theBackend.update_code(self.theSession['username'], code)
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
