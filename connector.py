from mod_python import apache
from mod_python import util
import hashlib
import datetime
import smtplib
import os
import string
from random import choice

cpss = apache.import_module("cpss")

class Connector:
    def __init__(self):
        #Parse the GET/POST fields
        self.fields = util.FieldStorage(cpss.req)
        self.header_sent = False

    def do_header(self, login=False, **keywords):
        if self.header_sent == True:
            return

        if (('authenticated' not in cpss.session) or 
            (cpss.session['authenticated'] == False)):
            cpss.page.header(login=False, **keywords)
        else:
            cpss.page.header(login=True, **keywords)

        self.header_sent = True

    def do_footer(self):
        cpss.page.footer()

    def Dispatch(self, pathstr):
        cpss.session["random"] = self.randomcode()

        # Make sure pathstr is never empty. The root page of the site
        # is ''.
        if (pathstr == []):
            pathstr = ['']

        # Hard code the maintainence mode key override for debugging/testing
        # on the live site.
        if ((cpss.options['maint_mode'] == '2') and
            (pathstr[0] == cpss.options['maint_key'])):
            cpss.session['maint_allow'] = True
            cpss.session.save()
            self.do_header(refresh='')
            return apache.OK

        if (cpss.options['maint_mode'] == '2'):
            if (cpss.session['maint_allow'] == False):
                # If user is logged in, log them out and force a refresh
                # If the user is not logged in, print out the maintenance
                # mode message.
                if (cpss.session['authenticated'] == True):
                    cpss.session.delete()
                    self.do_header(refresh='')
                    self.do_footer()
                    return apahe.OK
                else:
                    self.do_header()
                    cpss.w(cpss.options['maint_message'])
                    self.do_footer()
                    return apache.OK

        # The following are the permission functions.
        # Conditions that these functions must follow:
        #   * Break with 404. (False)
        #   * Break with nothing. (Stop processing more.) (None)
        #   * Continue (True)
        #   * Pass data to processing function. (tuple of key - value)

        def login(params):
            if cpss.session['authenticated'] != True:
                return False
            if cpss.session['activated'] != '0':
                self.Activate()
                return None
            return True

        def logout(params):
            if cpss.session['authenticated'] != False:
                return False
            return True

        def fl_stats(params):
            if cpss.db.test_userflag(cpss.session['username'], 
                                     'STATS') != True:
                return False
            return True

        def owner(params):
            proposal = cpss.db.proposal_fetch(cpss.session['username'],
                                              params[0])
            # If proposal == False, then this means that either the
            # proposal does not exist or does not belong to this user.
            # If its real, return proposal id as a tuple and pass along.
            if proposal == False:
                return False
            else:
                return ('proposal', proposal)

        # The dispatcher works by splitting the path string in pieces by the
        # directory dilemiter '/', testing permissions, then if permissions 
        # pass, pass all the operands to the function to process.
        ddict = { 
            # The root page.
            ''           : { 'perm' : None, 
                             'opt'  : 0,
                             'func' : self.Root,
                             },
            'create'     : { 'perm' : [logout],
                             'opt'  : 0,
                             'func' : self.Create,
                             },
            'login'      : { 'perm' : [logout],
                             'opt'  : 0,
                             'func' : self.Login,
                             },
            'logout'     : { 'perm' : None,
                             'opt'  : 0,
                             'func' : self.Logout,
                             },
            'help'       : { 'perm' : None,
                             'opt'  : lambda x: x <= 1,
                             'func' : self.Help,
                             },
            'help_small' : { 'perm' : None,
                             'opt'  : lambda x: x <= 1,
                             'func' : self.HelpSmall,
                             },
            'user'       : { 'perm' : [login],
                             'opt'  : 0,
                             'func' : self.User,
                             },
            'stats'      : { 'perm' : [login, fl_stats],
                             'opt'  : 0,
                             'func' : self.Stats,
                             },
            'statspdf'   : { 'perm' : [login, fl_stats],
                             'opt'  : 1,
                             'func' : self.StatsPDF,
                             },
            ### Below is old API commands.
            'finalpdf'   : { 'perm' : [login, owner],
                             'opt'  : 1,
                             'func' : self.finalpdf,
                             },
            'list'       : { 'perm' : [login],
                             'opt'  : 0,
                             'func' : self.proposal_list,
                             },
            } 

        # Logged in permission must also check that user is activated. 
        # cpss.session['activated'] != '0'. If true run self.Activate().

        # 'fl_stats' permission means 
        # cpss.db.test_userflag(cpss.session['username'], 'STATS') == True

        # 'owner' permission means that 2nd option MUST be proposal id
        # and the id is a proposal that belongs to the owner.

        #    if (pathstr[0] == 'proposal'):
        #        self.Proposal(pathstr)

        # 404 function executes if there is no match to anything.

        #        self.do_404()
        #The below lines execute when everything else doesnt match anything.


        # pathstr[0] is the function to run, while pathstr[1:] is all of its
        # options.
        if pathstr[0] not in ddict:
            self.do_404()
            return apache.OK

        item = ddict[pathstr[0]]
        params = pathstr[1:]
        kwparams = {}

        # If number of params is incorrect, return 404, else, run function
        # with its params.
        if isinstance(item['opt'], int):
            if item['opt'] != len(params):
                self.do_404()
                return apache.OK
        else:
            if item['opt'](len(params)) == False:
                self.do_404()
                return apache.OK

        # Check permissions. None means that it is always viewable.
        if item['perm'] == None:
            item['perm'] = [None]
        for perm in item['perm']:
            if perm == None:
                break
            elif hasattr(perm, '__call__'):
                result = perm(params)
                if result == True:
                    continue
                elif result == False:
                    self.do_404()
                    return apache.OK
                elif result == None:
                    return apache.OK
                elif isinstance(result, tuple):
                    kwparams[result[0]] = result[1]
                    pass

        item['func'](*params, **kwparams)

        return apache.OK

    def proposal_list(self):
        self.do_header()
        result = cpss.db.proposal_list(cpss.session['username'])
        cpss.page.proposal_list(result, cpss.session['name'])
        self.do_footer()

    def finalpdf(self, propid, proposal=None):
        ### API -- finalpdf -- return the final pdf -- REWRITE to pass file
        ###                    directly to user.
        pdf = cpss.db.pdf_get_data(propid)
        if (len(pdf) == 0):
            self.do_header()
            cpss.w("""This proposal is unsubmitted. Please submit it before
                      attempting to view.""")
            self.do_footer()
        else:
            cpss.req.headers_out.add('Content-Disposition',
                                     'attachment; filename=%s.pdf' % 
                                     (proposal['carmaid']))
            cpss.req.headers_out.add('Content-Length', str(len(pdf)))
            cpss.req.content_type='application/pdf'
            cpss.w(pdf)

                
    def Root(self):
        self.do_header()
        cpss.page.main()
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
                               registered in the system. If you believe this is
                               in error, please contact the website
                               administrator."""
                    self.do_header()
                    cpss.page.user_create(Name=name, Email=email, Error=error)
                    self.do_footer()
                else:
                    code = self.randomcode()
                    self.activation_mail(name, email, code)
                    cpss.db.add_user(name, email, pass1, code)
                    self.do_header()
                    cpss.page.user_create_success(name, email)
                    self.do_footer()
            else:
                self.do_header()
                cpss.page.user_create(Name=name, Email=email, Error=error)
                self.do_footer()
        else:
            self.do_header()
            cpss.page.user_create(random=cpss.session["random"])
            self.do_footer()

    def activation_mail(self, name, email, code):
        if (cpss.config['sendemail'] == False):
            return
        mail = smtplib.SMTP()
        mail.connect()
        msg = (cpss.text.email_activation % (name, email, name, code))
        mail.sendmail("do_not_reply@carma-prop.astro.illinois.edu", email, msg)
        mail.quit()

    def Proposal(self, pathstr):
        # If this access a specific proposal, verify that it can be accessed
        # by the user.
        if len(pathstr) > 2 :
            result = cpss.db.proposal_fetch(cpss.session['username'], 
                                            pathstr[2])
        else:
            result = None
        if (result == False):
            self.do_header(refresh="proposal/")
            cpss.w("""You do not have access to this proposal.""")
            self.do_footer()
            return

        action = self.fields.__contains__('action')
        items = len(pathstr)

        ### ACTION -- edit
        if (action and (self.fields['action'] == 'edit')):
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
        ### ACTION -- add
        elif (action and (self.fields['action'] == 'add')):
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
                self.do_header(refresh='proposal/edit/' + pathstr[2])
            else:
                id = cpss.db.proposal_table_addrow(tablename, pathstr[2],
                                                   numb=True)
                self.do_header(refresh =
                   'proposal/edit/%s/?action=edit&section=%s&id=%s' % 
                               (pathstr[2], section, id))
        ### ACTION -- delete -- delete entry from section (images, author, 
        ###                     sources, justification)
        elif (action and (self.fields['action'] == 'delete')):
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
                
                files_dir = (cpss.config['base_directory'] +
                             cpss.config['files_directory'])
                prop_dir = files_dir + pathstr[2] + '/justification/'
                                
                if (os.path.isfile(prop_dir + image[0]['file']) == True):
                    os.unlink(prop_dir + image[0]['file'])
            elif (section == 'justification'):
                done = True
                cpss.db.justification_delete_data(pathstr[2])

                files_dir = (cpss.config['base_directory'] +
                             cpss.config['files_directory'])
                prop_dir = files_dir + pathstr[2] + '/justification/'

                if (os.path.isfile(prop_dir + 'justification.pdf') == True):
                    os.unlink(prop_dir + 'justification.pdf')
            else:
                done = cpss.db.proposal_table_delrow(tablename, pathstr[2], 
                                                     numb=id)
                
            if (done == True):
                self.do_header(refresh=pathtext)
                self.do_footer()
            if (done == False):
                self.do_header()
                cpss.w("""You must have at least one value in the %s section.
                          You may not delete this last value.""" % 
                       section_name)
        ### ACTION -- submit -- submit data into the db. Replace with API func.
        elif (action and (self.fields['action'] == 'submit')):
            pathtext = ""
            for a in pathstr:
                pathtext += a + '/'
            if (self.fields.__contains__('section') == False):
                self.do_header(refresh=pathtext)
                self.do_footer()
            else:
                template = cpss.Template.Template(result['template'],
                              result['cyclename'], pathstr[2], False)

                fields = dict(self.fields)
                fields.pop('action')
                section = fields.pop('section')

                if (section == 'image'):
                    if (self.fields.__contains__('id') == True):
                        fname = template.process_image(fields)
                        image_data = fields['file'].file.read()
                        if (len(image_data) > (1024*1024*14)):
                            self.do_header()
                            cpss.w(cpss.text.error_ps_large)
                            self.do_footer()
                        else:
                            cpss.db.images_update(pathstr[2], fname, 
                               fields['id'], image_data)
                            self.do_header(refresh=pathtext)
                    else:
                        self.do_header(refresh="proposal/")
                elif (section == 'justification'):
                    pdf_data = fields['file'].file.read()
                    if (len(pdf_data) > (1024*1024*10)):
                        self.do_header()
                        cpss.w(cpss.text.error_latex_large)
                        self.do_footer()
                    else:
                        cpss.db.justification_add_update(pathstr[2], pdf_data)
                        self.do_header(refresh=pathtext)
                else:
                    fields = template.process_fields(section, fields,
                                                     pathstr[2])
                    if (self.fields.__contains__('id') == True):
                        idtext = "&id=%s" % self.fields['id']
                    else:
                        idtext = ''
                    self.do_header(refresh=pathtext)
                    self.do_footer()
        ###########    
        ### API -- typechange -- change the justification type
        elif (items == 3 and pathstr[1] == "typechange"):
            if (self.fields.__contains__('type') == True):
                if (self.fields['type'] == "Website Justification"):
                    cpss.db.justification_type_set(pathstr[2], 0)
                    cpss.db.justification_delete_data(pathstr[2])

                    files_dir = (cpss.config['base_directory'] + 
                                 cpss.config['files_directory'])
                    prop_dir = files_dir + pathstr[2] + '/justification/'

                    if (os.path.isfile(prop_dir+'justification.pdf') == True):
                        os.unlink(prop_dir + 'justification.pdf')
                if (self.fields['type'] == "LaTeX Template"):
                    cpss.db.justification_type_set(pathstr[2], 1)
                self.do_header(refresh=("""proposal/edit/%s""" % pathstr[2]))
                self.do_footer()
            else:
                self.do_header(refresh='proposal/')
                self.do_footer()
        ### API -- edit -- displays editable proposal    
        elif (items == 3 and pathstr[1] == "edit"):
            self.do_header()

            if (result['pdf_justification'] == 1):
                justification = True
            else:
                justification = False
                
            template = cpss.Template.Template(result['template'], 
                          result['cyclename'], pathstr[2], True, 
                          justification=justification)

            template.make_html()
            self.do_footer()
        ### API -- delete -- delete the whole proposal or section data. Replace
        ###                  with individual API calls.
        elif (items == 3 and pathstr[1] == "delete"):
            if (result['carmaid'] != None):
                self.do_header()
                cpss.w("""You may not delete a proposal that has already been
                          submitted.""")
                self.do_footer()
            elif (self.fields.__contains__('delete') == True):
                template = cpss.Template.Template(result['template'], 
                              result['cyclename'], pathstr[2], True)

                cpss.db.proposal_delete(cpss.session['username'],
                   result['proposalid'], template.tables, result['cyclename'])
                self.do_header(refresh="proposal/")
                self.do_footer()
            else:
                pathtext = ""
                for a in pathstr:
                    pathtext += a + '/'
                template = cpss.Template.Template(result['template'],
                              result['cyclename'], pathstr[2], True)

                title = None
                for asection in template.sections:
                    if (asection['section'] == 'propinfo'):
                        section = asection

                for field in section['data'][0][1]:
                    if (field['fieldname'] == 'title'):
                        title = field['data']
                        break
                self.do_header()
                cpss.page.delete_verify(pathtext, str(title))
                self.do_footer()
        ### API -- pdf -- return sample pdf file
        elif (items == 3 and pathstr[1] == "pdf"):
            # Hack to correctly parse for skip pagelength warning
            if pathstr[2][-1] == "i":
                ignore_pagelength = True
                pathstr[2] = pathstr[2][:-1]
            else:
                ignore_pagelength = False

            # Update the date field to the current date:
            cpss.db.proposal_tagset('proposal', pathstr[2], 
                                    [{'fieldname':'date', 'fieldtype':'date'}])
            if (result['pdf_justification'] == 0):
                justification = False
            else:
                justification = True
            template = cpss.Template.Template(result['template'], 
                          result['cyclename'], pathstr[2], True, 
                          justification=justification)
            retval = template.latex_generate(pathstr[2], 
                                          ignore_pagelength=ignore_pagelength)

            if (retval != 0) and (retval != 1):
                self.do_header()
                cpss.w("""<b>A LaTeX error occured. The output is displayed 
                       below:</b><br><br>%s""" % (self.lines2text(retval[7:])))
                self.do_footer()
        ### API -- submit -- submit the proposal and perform checks.
        elif (items == 3 and pathstr[1] == 'submit'):
            if (self.fields.__contains__('sub_prop') == True):
                if (self.fields['sub_prop'] == 'Submit Proposal'):
                    # Update the date field to the current date:
                    cpss.db.proposal_tagset('proposal', pathstr[2],
                                            [{'fieldname':'date', 
                                              'fieldtype':'date'}])
                    idstr = ""
                    if (result['carmaid'] == None):
                        idstr = str(cpss.options['next_propno'])
                        length = len(idstr)
                        if (length < 4):
                            for i in xrange(0, 4 - length):
                                idstr = "0" + idstr
                        idstr = "c" + idstr
                        cpss.db.set_next_propno(cpss.options['next_propno']+1, 
                                                result['cyclename'])
                        cpss.db.pw_generate(pathstr[2])
                        cpss.db.proposal_setcarmaid(pathstr[2], idstr)
                    else:
                        idstr = result['carmaid']

                    if (result['pdf_justification'] == 0):
                        justification = False
                    else:
                        justification = True

                    template = cpss.Template.Template(result['template'], 
                                  result['cyclename'], pathstr[2], True, 
                                  justification=justification)
                    
                    ret = template.latex_generate(template.propid,
                             file_send = False, carma_propno = idstr)

                    self.do_header()

                    if (ret != 0):
                        cpss.w(cpss.text.submit_failed_error %
                                       pathstr[2])
                    else:
                        pdf = open(cpss.config['base_directory']
                                   + cpss.config['files_directory'] + '/' +
                                   pathstr[2] + '/latex-final.pdf', 'r')
                        pdf_data = pdf.read()
                        pdf.close()

                        if (len(pdf_data) > (1024*1024*14)):
                            cpss.w(cpss.text.submit_failed_size % pathstr[2])
                        else:
                            cpss.db.pdf_add_update(pathstr[2], pdf_data)
                            cpss.db.proposal_submit(pathstr[2])
                            cpss.w(cpss.text.submit_success)
                    self.do_footer()
                else:
                    self.do_header(refresh=('proposal/submit/%s' % pathstr[2]))
                    self.do_footer()
            else:
                # Update the date field to the current date:
                cpss.db.proposal_tagset('proposal', pathstr[2],
                                        [{'fieldname':'date',
                                          'fieldtype':'date'}])

                if (result['pdf_justification'] == 0):
                    justification = False
                else:
                    justification = True
                    
                template = cpss.Template.Template(result['template'],
                              result['cyclename'], pathstr[2], True,
                              justification=justification)
                self.do_header()
            
                cpss.w("""<div class="navbar, propheader">
                            <ul id="navlist">
                              <li>
                                <a href="%s">Current Proposal</a>
                              </li>
                            </ul>
                          </div>""" % ("proposal/edit/" +str(template.propid)))
                                        
                cpss.w("""<ul><li>Checking to make sure all required fields 
                          have been completed...""")

                error = template.data_verify()

                #Check to make sure no fields have errors.
                if (error == True):
                    cpss.w("""<br><span style="color:red;font-weight:bold;">
                       You must fix the errors above before you can submit the
                       proposal.</span>""")
                else:
                    cpss.w("""<span style="color:green;font-weight:bold;">
                       All fields have been verified.</span>""")

                cpss.w("</li>")

                #Do additional checks such as obsblock and time alloc.
                if (error == False):
                    cpss.w("<li>Performing other error checks...")
                    ##### IS THIS REQUIRED ANYMORE? ######################
                    #checking to see if all obsblock names are unique.
                    error_obsblock = template.obsblock_verify()
                    #add other checks in here...

                    if (error_obsblock == False):
                        error2 = False
                        cpss.w("""<span style="color:green;font-weight:bold;">
                                  done</span></li>""")
                    else:
                        error2 = True
                        cpss.w("""</li>""")
                else:
                    error2 = False

                if (error2 == True):
                    cpss.w("""<br><span style="color:red;font-weight:bold;">
                       You must fix the errors above before you can submit the
                       proposal.</span>""")
                #display final check
                if ((error == False) and (error2 == False)):
                    cpss.w("""<li>Please click <a href="proposal/pdf/%s">here
                       </a> to proofread your proposal before you perform the 
                       final submit.</li>""" % str(template.propid))
                cpss.w("""</ul>""")

                if ((error == False) and (error2 == False)):
                    cpss.w(cpss.text.submit_verify % str(template.propid))
                self.do_footer()
        ### API -- add -- add proposal        
        elif (items == 2 and pathstr[1] == "add"):
            # Add check to see if proposal creation is enabled
            options = cpss.db.options_get()
            if options['create'] == True:
                template = cpss.Template.Template(options['template'],
                           options['cyclename'], None, True, Fetch=False)
                propno = cpss.db.proposal_add(cpss.session['username'],
                         template.tempclass.tables, options['cyclename'])
                self.do_header(refresh=("proposal/edit/%s" % (propno)))
                self.do_footer()
            else:
                self.do_header(refresh="proposal/")
                self.do_footer()
        ### 404
        else:
            self.do_404()

    def HelpSmall(self, item='index'):
        self.Help(item, small=True)

    def Help(self, item='index', small=False):
        if (small == True):
            cpss.req.content_type="text/html"
            cpss.w("""<html><head>
            <base href="%s" />
            <title>Help</title>
            <link rel="stylesheet" href="static/cpss.css" type="text/css">
            </head><body>""" % cpss.config['html_base'])
        else:
            self.do_header()

        if (item == 'propinfo'):
            cpss.w(cpss.text.help_propinfo)

        elif (item == 'abstract'):
            cpss.w(cpss.text.help_abstract)

        elif (item == 'author'):
            cpss.w(cpss.text.help_author)

        elif (item == 'source'):
            cpss.w(cpss.text.help_source)

        elif (item == 'special_requirements'):
            cpss.w(cpss.text.help_specialreq)

        elif (item == 'prior_obs'):
            cpss.w(cpss.text.help_priorobs)

        elif (item == 'scientific_justification'):
            cpss.w(cpss.text.help_scientificjust)

        elif (item == 'technical_justification'):
            cpss.w(cpss.text.help_technicaljust)

        elif (item == 'image'):
            cpss.w(cpss.text.help_image)

        elif (item == 'tot_hours'):
            cpss.w(cpss.text.help_tothours)
            
        elif (item ==  'index'):
            cpss.w(cpss.text.help_index % (cpss.config['html_base'], 
               cpss.config['html_base'], cpss.config['html_base'], 
               cpss.config['html_base'], cpss.config['html_base'], 
               cpss.config['html_base'], cpss.config['html_base'], 
               cpss.config['html_base']))

        else:
            self.do_404()
            return

        if (small == True):
            cpss.w("""<br><br><br><br><br><br><br></body></html>""")
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
                mail.sendmail("do_not_reply@carma-prop.astro.illinois.edu", 
                              email, msg)
                mail.quit()

        if (self.fields.getfirst('submit') == 'Submit'):
            username = self.fields.getfirst('user')
            password = self.fields.getfirst('pass')

            # Fix for blank field == None issue
            if username == None:
                username = ''
            # Same for password field
            if password == None:
                password = ''

            if (username[0:6] == 'admin:'):
                options = cpss.db.options_get()
                if (hashlib.md5(password).hexdigest() == options['admin_pw']):
                    user = cpss.db.get_user(username[6:])
                    if user == None:
                        Error = """The user does not exist."""
                        self.do_header(logon=True)
                        cpss.page.logon(Error=Error)
                        self.do_footer()
                        return
                    cpss.session['authenticated'] = True
                    cpss.session['username'] = user['email']
                    cpss.session['name'] = user['name']
                    cpss.session['activated'] = '0'
                    cpss.session['admin'] = True
                    cpss.session.save()
                    self.do_header(refresh="proposal/")
                else:
                    Error = """The username and password you have supplied are
                               not valid. Please try again."""
                    self.do_header(logon=True)
                    cpss.page.logon(Error=Error, Username=username)
                    self.do_footer()
                return

            if ((username == None) or (password == None) or
                (username == "") or (password == "")):
                Error = "You must enter both a username and a password."
                authenticate = False
            else:
                (authenticate, user) = cpss.db.verify_user(username, password)
            if (authenticate == False):
                Error = """The username and password you have supplied are not
                         valid. Please try again."""
                self.do_header(logon=True)
                cpss.page.logon(Error=Error, Username=username)
                self.do_footer()
            if (authenticate == True):
                cpss.session['authenticated'] = True
                cpss.session['username'] = user['email']
                cpss.session['name'] = user['name']
                cpss.session['activated'] = user['activated']
                cpss.session.save()
                self.do_header(refresh="proposal/")
        else:
            self.do_header(logon=True)
            cpss.page.logon(Error=Error)
            self.do_footer()

    def Logout(self):
        cpss.session.delete()
        cpss.session['authenticated'] = False
        self.do_header()
        cpss.w('''<center>The session has been closed. You will need
        to login again to view your proposals.</center>''')
        self.do_footer()

    def User(self):
        error=""
        if (self.fields.getfirst('changepw') == "Change Password"):
            username = cpss.session['username']
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

        username = cpss.session['name']
        email = cpss.session['username']
        self.do_header()
        cpss.page.userpage(username, email, error=error)
        self.do_footer()

    def randomcode(self):
        size=8
        password = ''.join([choice(string.letters + string.digits +
                                   "!" + "@" + "_") for i in range(size)])
        return password

    def do_404(self):
        self.do_header()
        cpss.page.do_404()
        self.do_footer()

    def Activate(self):
        if (self.fields.getfirst('sub_activate') == "Activate Account"):
            code = self.fields.getfirst('activate')
            if (code == cpss.session['activated']):
                cpss.db.update_code(cpss.session['username'], "0")
                cpss.session['activated'] = "0"
                cpss.session.save()
                self.do_header(refresh='proposal/')
                cpss.page.activate(Error="""You have successfully activated
                your account. Click on the proposals tab above in order to
                start using the system.""")
                self.do_footer()
            else:
                self.do_header()
                cpss.page.activate(Error="""The code you entered is invalid.
                Either verify that you typed in the correct code or click the
                button at the bottom to send a new one to your e-mail
                account.""")
                self.do_footer()
        elif (self.fields.getfirst('sub_activate') ==
              "Resend Activation Code"):
            code = self.randomcode()
            cpss.session['activated'] = code
            cpss.session.save()
            cpss.db.update_code(cpss.session['username'], code)
            self.activation_mail(cpss.session['name'], 
                                 cpss.session['username'], code)
            self.do_header()
            cpss.page.activate(Error="""A new activation code has been sent
            to the address that you specified when you registered the account.
            If you never recieve it, please inform the webmaster.""")
            self.do_footer()
        else:
            self.do_header()
            cpss.page.activate()
            self.do_footer()

    def lines2text(self, lines):
        buffer = ""
        for line in lines:
            buffer += line + "<br>" 
        return buffer

    def StatsPDF(self, cid):
        pdf = cpss.db.pdf_get_data(cid)
        result = cpss.db.proposal_fetch('admin', cid)
        if (len(pdf) == 0):
            self.do_header()
            cpss.w("""Proposal fetch error. May not exist.""")
            self.do_footer()
        else:
            cpss.req.headers_out.add(
                'Content-Disposition', 'attachment; filename=%s.pdf' % 
                (result['carmaid']))
            cpss.req.headers_out.add('Content-Length', str(len(pdf)))
            cpss.req.content_type='application/pdf'
            cpss.w(pdf)

    def Stats(self):
        # This function returns stats information about the current call.
        _w = cpss.w
        self.do_header()
        for cycle in cpss.db.cycles():
            _w("""
<table class='stats'>
  <tr>
    <th colspan='5'>""" + cycle['cyclename'] + """
  <tr>
    <th class='carma-id'>ID</th>
    <th class='name'>Name</th>
    <th class='email'>Email</th>
    <th class='title'>Title</th>
    <th class='date'>Date</th>
  </tr>""")
            proposals = cpss.db.proposal_list_by_cycle(cycle['cyclename'])
            for proposal in proposals:
                _w("<tr>")
                if proposal['status'] == 1:
                    _w("<td class='carma-id'><a href='" + 
                       cpss.config['html_base'] + "statspdf/" + 
                       str(proposal['proposalid']) + "'>" + 
                       str(proposal['carmaid'])+"</a></td>")
                else:
                    _w("<td class='carma-id'>" + 
                       str(proposal['carmaid'])+"</td>")
                _w("<td class='name'>"+str(proposal['name'])+"</td>")
                _w("<td class='email'>"+str(proposal['email'])+"</td>")
                res = cpss.db.proposal_get_propinfo(
                    proposal['proposalid'], cycle['proposal'])
                _w("<td class='title'>"+ str(res['title']) + "</td>")
                if proposal['status'] == 1:
                    _w("<td class='date'>" + str(res['date']) + "</td>")
                else:
                    _w("<td class='date'>Unsubmitted</td>")
                _w("</tr>")
            _w("""</table><br/>""")
        self.do_footer()
        return
