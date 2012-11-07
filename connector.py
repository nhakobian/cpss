from mod_python import apache
from mod_python import util
import hashlib
import datetime
import smtplib
import os
import string
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from random import choice

cpss = apache.import_module("cpss")

max_image_size = 1024*1024*14 # 14 MiB
max_latex_size = 1024*1024*10 # This used to be uploaded pdf, now latex.
max_pdf_size = 1024*1024*14

class CpssUserErr(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

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

    def forward(self, url, local=True):
        cpss.page.forward(url, local)

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
            self.forward('')
            return apache.OK

        if (cpss.options['maint_mode'] == '2'):
            if (cpss.session['maint_allow'] == False):
                # If user is logged in, log them out and force a refresh
                # If the user is not logged in, print out the maintenance
                # mode message.
                if (cpss.session['authenticated'] == True):
                    cpss.session.delete()
                    self.forward('')
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

        def login(params, kwparams):
            if cpss.session['authenticated'] != True:
                self.forward('login?redir=' + cpss.req.path_info[1:])
                return None
            if cpss.session['activated'] != '0':
                self.Activate()
                return None
            return True

        def logout(params, kwparams):
            if cpss.session['authenticated'] != False:
                return False
            return True

        def fl_stats(params, kwparams):
            if cpss.db.test_userflag(cpss.session['username'], 
                                     'STATS') != True:
                return False
            return True

        def owner(params, kwparams):
            proposal = cpss.db.proposal_fetch(cpss.session['username'],
                                              params[0])
            # If proposal == False, then this means that either the
            # proposal does not exist or does not belong to this user.
            # If its real, add proposalinfo to kwparams and return True.
            if proposal == False:
                return False
            else:
                kwparams['proposal'] = proposal
                return True
        owner.error_string = """You are not the owner of this proposal."""

        def unlocked(params, kwparams):
            if 'proposal' not in kwparams:
                # Err on the safe side. If owner didnt return anything
                # it means its not our proposal, so treat it as if it was
                # locked. Realistically, owner = False should break the
                # permissions tree and this should not get run unless
                # someone forgot to put owner in the chain. This catches
                # that possibility.
                return False
            
            if kwparams['proposal']['lock'] == 1:
                # If lock is true, this is definitely locked.
                return False
            elif kwparams['proposal']['lock'] == 0:
                # If lock is 0, then allow editing even if the cycle 
                # permissions say no. Useful to set this if there is a
                # late proposal, or someone needs to make a correction after
                # a cycle has ended.
                return True
            elif kwparams['proposal']['lock'] == None:
                # None is the same as SQL Null. If this is present, respect
                # the cycle editable setting (`create`). This is what most
                # will be at until they are extracted. The extraction script
                # should set lock to 1.
                if kwparams['proposal']['create'] == 1:
                    # Remember create is the opposite of lock. If create is
                    # true, its also editable. If its '0', editing is also
                    # disabled.
                    return True
                else:
                    # Anything else but '1' and the proposal is uneditable,
                    # i.e. locked.
                    return False
        unlocked.error_string = """The proposal you are editing has been set
          as uneditable. This usually occurs when your proposal has been 
          submitted, or after a proposal call has ended."""

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
            'add'        : { 'perm' : [login],
                             'opt'  : 1,
                             'func' : self.proposal_add,
                             },
            'delete'     : { 'perm' : [login, owner, unlocked],
                             'opt'  : 1,
                             'func' : self.proposal_delete,
                             },
            'view'       : { 'perm' : [login, owner],
                             'opt'  : 1,
                             'func' : self.proposal_view,
                             },
            'typechange' : { 'perm' : [login, owner, unlocked],
                             'opt'  : 1,
                             'func' : self.proposal_typechange,
                             },
            'edit'       : { 'perm' : [login, owner, unlocked],
                             'opt'  : lambda x: x in [2, 3],
                             'func' : self.proposal_edit,
                             },
            'multi_add'  : { 'perm' : [login, owner, unlocked],
                             'opt'  : 2,
                             'func' : self.proposal_multi_add,
                             },
            'multi_del'  : { 'perm' : [login, owner, unlocked],
                             'opt'  : 3,
                             'func' : self.proposal_multi_delete,
                             },
            'del_just'   : { 'perm' : [login, owner, unlocked],
                             'opt'  : 1,
                             'func' : self.proposal_justification_delete,
                             },
            'save'       : { 'perm' : [login, owner, unlocked],
                             'opt'  : 1,
                             'func' : self.proposal_data_save,
                             },
            'pdf'        : { 'perm' : [login, owner, unlocked],
                             'opt'  : lambda x: x in [1, 2],
                             'func' : self.proposal_draft_pdf,
                             },
            'submit_verify' : { 'perm' : [login, owner, unlocked],
                                'opt'  : 1,
                                'func' : self.submit_verify,
                                },
            'submit'     : { 'perm' : [login, owner, unlocked],
                             'opt'  : 1,
                             'func' : self.submit,
                             },
            'ddt'        : { 'perm' : None,
                             'opt'  : 0,
                             'func' : self.ddt,
                             },
            'fast-track' : { 'perm' : None,
                             'opt'  : 0,
                             'func' : self.fasttrack,
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
                result = perm(params, kwparams)
                if result == True:
                    continue
                elif result == False:
                    if hasattr(perm, 'error_string'):
                        self.do_header()
                        cpss.w(perm.error_string)
                        self.do_footer()
                    else:
                        self.do_404()
                    return apache.OK
                elif result == None:
                    return apache.OK

        try:
            item['func'](*params, **kwparams)
        except CpssUserErr as error:
            self.do_header()
            cpss.w(error.value)
            self.do_footer()

        return apache.OK

    def proposal_list(self):
        self.do_header()
        result = cpss.db.proposal_list(cpss.session['username'])
        cpss.page.proposal_list(result, cpss.session['name'])
        self.do_footer()

    def proposal_add(self, prop_type):
        ### API -- add -- add proposal        
        # Verify data.
        if prop_type not in ['main', 'ddt', 'cs', 'fast']:
            self.do_404()
            return
        
        # Add check to see if proposal creation is enabled
        # Get the cyclename they are requesting a new proposal for.
        # Never allow adding a proposal if there isnt a cycle defined
        # for the chosen proposal type.
        if cpss.options['cycle_' + prop_type] != '':
            cycle = cpss.db.cycle_info(cpss.options['cycle_' + prop_type])
            if cycle['create'] != 1:
                raise CpssUserErr("""No %s proposals are being accepted at
                                     this time.""" % prop_type)
                return

            template = cpss.Template.Template(cycle, None, True, Fetch=False)
            propno = cpss.db.proposal_add(
                cycle, cpss.session['username'], template.tempclass.tables)
            self.forward('list')
        else:
            raise CpssUserErr("""No %s proposals are being accepted at this 
                                 time.""" % prop_type)

    def proposal_delete(self, proposalid, proposal=None):
        ### API -- delete -- delete the whole proposal 
        if proposal['status'] == 1:
            raise CpssUserErr("You cannot delete a submitted proposal.")

        if 'delete' in self.fields:
            template = cpss.Template.Template(proposal, proposalid, True,
                                              Fetch=False)
            cpss.db.proposal_delete(
                cpss.session['username'], proposalid, template.tables, 
                proposal)
            self.forward('list')
            return

        # In this case proposal['proposal'] is the name of the 
        # database table that has the title info.
        propinfo = cpss.db.proposal_get_propinfo(
            proposalid, proposal['proposal'])

        self.do_header()
        cpss.page.delete_verify('delete/' + str(proposalid), propinfo['title'])
        self.do_footer()

    def proposal_view(self, proposalid, proposal=None):
        ### API -- view -- displays proposal, editable if unlocked
        self.do_header()

        if (proposal['pdf_justification'] == 1):
            justification = True
        else:
            justification = False
                
        template = cpss.Template.Template(proposal, proposalid, True, 
                                          justification=justification)

        template.make_html_proposal()
        self.do_footer()

    def proposal_typechange(self, proposalid, proposal=None):
        ### API -- typechange -- change the justification type
        if 'type' in self.fields:
            if (self.fields['type'] == "Website Justification"):
                cpss.db.justification_type_set(proposalid, 0)
                cpss.db.justification_delete_data(proposalid)
            elif (self.fields['type'] == "LaTeX Template"):
                cpss.db.justification_type_set(proposalid, 1)
        self.forward("view/%s#type" % proposalid)

    def proposal_edit(self, proposalid, section, id=False, proposal=None):
        ### ACTION -- edit
        ## command formatted like /edit/propid/section/id
        template = cpss.Template.Template(proposal, proposalid, False)
        self.do_header()
        template.make_html(section_choose=section, id=id)
        self.do_footer()

    def proposal_multi_add(self, proposalid, section, proposal=None):
        ### ACTION -- add
        template = cpss.Template.Template(proposal, proposalid, True, 
                                          Fetch=False)

        # Verify that section exists and can have additional values.
        verify = False
        for tempsection in template.sections:
            if (tempsection['section'] == section):
                tablename = tempsection['table']
                if section == 'image':
                    verify = True
                elif template.tables[tablename]['type'] == 'repeat':
                    verify = True
                else:
                    verify = False

        if verify == False:
            raise CpssUserErr("""This section does not exist or cannot carry 
                                 any more rows of data.""")

        if ((proposal['type'] == 'fast') and (section == 'source')):
            # Fast mode proposals can't have more than one source line. Make
            # sure that its impossible to add an additional one.
            raise CpssUserErr("""Fast mode proposals have a limit of one 
                                 source per proposal.""")

        if (section == 'image'):
            id = cpss.db.images_add(proposalid)
            self.forward('view/' + proposalid + '#image')
        else:
            id = cpss.db.proposal_table_addrow(proposal[tablename], proposalid,
                                               numb=True)
            self.forward('edit/%s/%s/%s' % (proposalid, section, id))

    def proposal_multi_delete(self, proposalid, section, id, proposal=None):
        ### ACTION -- delete -- delete entry from section (images, author, 
        ###                     sources, justification)
        template = cpss.Template.Template(proposal, proposalid, True)

        # Verify that the section and id exist before you try to delete it.
        verify = False
        for tempsection in template.sections:
            if (tempsection['section'] == section):
                tablename = tempsection['table']
                section_name = tempsection['name']
                if section == 'image':
                    verify = True
                elif template.tables[tablename]['type'] == 'repeat':
                    verify = True
                else:
                    verify = False

        if verify == False:
            raise CpssUserErr("This section does not exist.")

        if (section == 'image'):
            image = cpss.db.images_list(proposalid, id)
            if len(image) == 0:
                status = None
            else:
                cpss.db.images_delete(proposalid, id)
            
                files_dir = (cpss.config['base_directory'] +
                             cpss.config['files_directory'])
                prop_dir = files_dir + proposalid + '/justification/'
                
                if (os.path.isfile(prop_dir + image[0]['file']) == True):
                    os.unlink(prop_dir + image[0]['file'])
                status = True
        else:
            status = cpss.db.proposal_table_delrow(proposal[tablename], 
                                                   proposalid, numb=id)
            
        if (status == True):
            self.forward('view/' + str(proposalid) + '#' + section)
        elif (status == False):
            raise CpssUserErr(
                "You must have at least one value in the %s section." % 
                section_name)
        elif (status == None):
            raise CpssUserErr("Cannot delete non-existant item.")

    def proposal_justification_delete(self, proposalid, proposal=None):
        cpss.db.justification_delete_data(proposalid)
        self.forward('view/' + str(proposalid) + '#type')

    def proposal_data_save(self, proposalid, proposal=None):
        ### ACTION -- submit -- submit data into the db.
        template = cpss.Template.Template(proposal, proposalid, False)

        fields = dict(self.fields)
        section = fields.pop('section')

        if (section == 'image'):
            if ('id' in fields):
                fname = fields['file'].filename
                image_data = fields['file'].file.read()
                if (len(image_data) > max_image_size):
                    raise CpssUserErr(cpss.text.error_ps_large)
                else:
                    cpss.db.images_update(proposalid, fname, 
                       fields['id'], image_data)
                    self.forward('view/' + str(proposalid) + '#image')
            else:
                raise CpssUserErr("Improperly formatted data for saving.")
        elif (section == 'justification'):
            latex_data = fields['file'].file.read()
            if (len(latex_data) > (max_latex_size)):
                raise CpssUserErr(cpss.text.error_latex_large)
            else:
                cpss.db.justification_add_update(proposalid, latex_data)
                self.forward('view/' + str(proposalid) + '#type')
        else:
            fields = template.process_fields(section, fields, proposalid, 
                                             proposal)
            self.forward('view/' + str(proposalid) + '#' + section)

    def proposal_draft_pdf(self, proposalid, skipwarn=False, proposal=None):
        ### API -- pdf -- return sample pdf file
        # Hack to correctly parse for skip pagelength warning
        if skipwarn == False:
            ignore_pagelength = False
        elif skipwarn == 'skip':
            ignore_pagelength = True

        # Update the date field to the current date:
        cpss.db.proposal_tagset(proposal['proposal'], proposalid, 
                                [{'fieldname':'date', 
                                  'fieldtype':'date'}])

        if (proposal['pdf_justification'] == 0):
            justification = False
        else:
            justification = True

        template = cpss.Template.Template(proposal, proposalid, True, 
                                          justification=justification)
        retval = template.latex_generate(proposalid, 
                                         ignore_pagelength=ignore_pagelength)

        if (retval != 0) and (retval != 1):
            self.do_header()
            cpss.w("""<b>A LaTeX error occured. The output is displayed 
                   below:</b><br><br>%s""" % (self.lines2text(retval[7:])))
            self.do_footer()

    def finalpdf(self, propid, proposal=None):
        ### API -- finalpdf -- return the final pdf -- REWRITE to pass file
        ###                    directly to user.
        pdf = cpss.db.pdf_get_data(propid)
        if (len(pdf) == 0):
            raise CpssUserErr("""This proposal is unsubmitted. Please submit 
                                 it before attempting to view.""")
        else:
            cpss.req.headers_out.add('Content-Disposition',
                                     'attachment; filename=%s.pdf' % 
                                     (proposal['carmaid']))
            cpss.req.headers_out.add('Content-Length', str(len(pdf)))
            cpss.req.content_type='application/pdf'
            cpss.w(pdf)

    def submit_verify(self, proposalid, proposal=None):
        # Update the date field to the current date:
        cpss.db.proposal_tagset(proposal['proposal'], proposalid,
                                [{'fieldname':'date',
                                  'fieldtype':'date'}])

        if (proposal['pdf_justification'] == 0):
            justification = False
        else:
            justification = True
            
        template = cpss.Template.Template(proposal, proposalid, True,
                                          justification=justification)
        self.do_header()
        cpss.w("""<div class="navbar, propheader">
                    <ul id="navlist">
                      <li>
                        <a href="%s">Current Proposal</a>
                      </li>
                    </ul>
                  </div>
                  <ul><li>Checking to make sure all required fields 
                  have been completed...""" % 
               ('view/' + str(template.propid)))
                                
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
            cpss.w("""<li>Please click <a href="pdf/%s">here
               </a> to proofread your proposal before you perform the 
               final submit.</li>""" % str(template.propid))
        cpss.w("""</ul>""")

        if ((error == False) and (error2 == False)):
            cpss.w(cpss.text.submit_verify % str(template.propid))
        self.do_footer()

    def submit(self, proposalid, proposal=None):
        ### API -- submit -- submit the proposal and perform checks.
        if (('sub_prop' not in self.fields) or
            (self.fields['sub_prop'] != 'Submit Proposal')):
            self.forward('submit_verify/' + str(proposalid))
            return

        # Update the date field to the current date:
        cpss.db.proposal_tagset(proposal['proposal'], proposalid,
                                [{'fieldname':'date', 
                                  'fieldtype':'date'}])

        if (proposal['carmaid'] == None):
            # Generate carmaid.
            type_prefix = { 'main' : 'c',
                            'ddt'  : 'cx',
                            'cs'   : 'cs',
                            'fast' : 'cf',
                            }
            min_digits = { 'main' : 4,
                           'ddt'  : 3,
                           'cs'   : 3,
                           'fast' : 4,
                           }

            next_propno = cpss.options['propid_' + proposal['type']]

            if len(str(next_propno)) < min_digits[proposal['type']]:
                padding = min_digits[proposal['type']] - len(str(next_propno))
            else:
                padding = 0

            carmaid = (type_prefix[proposal['type']] + ('0' * padding) +
                       str(next_propno))

            cpss.db.set_next_propno(int(next_propno) + 1, proposal['type'])
            cpss.db.pw_generate(proposalid)
            cpss.db.proposal_setcarmaid(proposalid, carmaid)
            # Since we've changed fundamental data in the db, re-read that
            # db entry so things below do not fail.
            proposal = cpss.db.proposal_fetch(cpss.session['username'],
                                              proposalid)
        else:
            carmaid = proposal['carmaid']

        if (proposal['pdf_justification'] == 0):
            justification = False
        else:
            justification = True

        template = cpss.Template.Template(proposal, proposalid, True, 
                      justification=justification)
        
        ret = template.latex_generate(template.propid, file_send=False,
                                      carma_propno=carmaid)

        self.do_header()

        if (ret != 0):
            cpss.w(cpss.text.submit_failed_error % proposalid)
        else:
            if proposal['type'] in ['fast', 'cs']:
                pdfname = '/latex.pdf'
            else:
                pdfname = '/latex-final.pdf'

            pdf = open(cpss.config['base_directory'] + 
                       cpss.config['files_directory'] + '/' + proposalid + 
                       pdfname, 'r')
            pdf_data = pdf.read()
            pdf.close()

            if (len(pdf_data) > max_pdf_size):
                cpss.w(cpss.text.submit_failed_size % proposalid)
            else:
                cpss.db.pdf_add_update(proposalid, pdf_data)
                cpss.db.proposal_submit(proposalid)
                cpss.w(cpss.text.submit_success)
                # Fast proposal system integration. This is a three part procedure.
                # It locks the proposal for further editing, this is done since the
                # output is sent directly to the CARMA RTS. If the proposer were to
                # make a change and resubmit, the RTS would receive an updated proposal.
                # Therefore this is disallowed. Next is creating the two XML files
                # (stored locally in case of email failure). Then is sending the
                # email itself.
                if proposal['type'] == 'fast':
                    cpss.db.proposal_lock(proposalid)
                    template.tempclass.export.export_xml(proposal, template)
                    template.tempclass.export.fast_email(carmaid)

                # Email notification of DDT and Fast-track proposal submissions.
                if proposal['type'] in ['fast', 'ddt']:
                    self.email_notify(proposal)

        self.do_footer()

    def email_notify(self, proposal):
        # Email notification of proposal submission
        carmaid = proposal['carmaid']

        message_text = ("""This is notification that the %(type)s proposal:

%(carmaid)s - %(title)s

has been submitted to the CARMA Proposal System. The proposal is located in a
file attachment to this email. For Fast-track proposals, this email additionally
serves as notification that the proposal has been sent to the high site for
submission into the CARMA Project Database.

** This email was sent by an automated system. Do not reply to this email.
** For any questions contact proposal-help <proposal-help@astro.illinois.edu>
""")

        propinfo = cpss.db.proposal_get_propinfo(proposal['proposalid'], 
                                                 proposal['proposal'])
        title = propinfo['title']

        if proposal['type'] == 'ddt':
            type_string = 'DDT'
        elif proposal['type'] == 'fast':
            type_string = 'Fast-track'
        else:
            return

        CS = ', '
        mail = MIMEMultipart()
        mail['Subject'] = '[Prop-Notify] %s - %s Proposal Submitted' % (carmaid, type_string)
        mail['From'] = "CARMA Proposal System <no-reply@carma-prop.astro.illinois.edu>"
        mail['To'] = CS.join(cpss.config['submit_notify'])
        
        pdf = open(cpss.config['data_directory'] + 'pdf/' + str(proposal['proposalid'])
                   + '.pdf')
        attach = MIMEBase('application', 'pdf')
        attach.set_payload(pdf.read())
        pdf.close()
        encoders.encode_base64(attach)
        attach.add_header('Content-Disposition', 'attachment', filename=(carmaid + '.pdf'))

        message = MIMEText(message_text % { 'type' : type_string, 'carmaid' : carmaid,
                                            'title' : title})
        
        mail.attach(message)
        mail.attach(attach)

        mailer = smtplib.SMTP()
        mailer.connect()
        mailer.sendmail(mail['From'], cpss.config['submit_notify'], mail.as_string())
        mailer.quit()

    def ddt(self):
        self.do_header()
        cpss.w(cpss.text.page_ddt)

        if cpss.session['authenticated'] == False:
            cpss.page.logon(redir='ddt')
        elif cpss.session['authenticated'] == True:
            cpss.w(cpss.text.page_ddt_disclaimer)

        self.do_footer()
           
    def fasttrack(self):
        self.do_header()
        cpss.w(cpss.text.page_fasttrack)

        if cpss.session['authenticated'] == False:
            cpss.page.logon(redir='fast-track')
        elif cpss.session['authenticated'] == True:
            cpss.w(cpss.text.page_fasttrack_disclaimer)

        self.do_footer()
     
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

    def Login(self, redir='list'):
        if 'redir' in self.fields:
            redir = self.fields['redir']

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
            redir = self.fields.getfirst('redir')
            # Fix for blank field == None issue
            if username == None:
                username = ''
            # Same for password field
            if password == None:
                password = ''

            if (username[0:6] == 'admin:'):
                options = cpss.db.options_get()
                if (hashlib.md5(password).hexdigest() == 
                    options['admin_pw']):
                    user = cpss.db.get_user(username[6:])
                    if user == None:
                        Error = """The user does not exist."""
                        cpss.page.logon(Error=Error)
                        return
                    cpss.session['authenticated'] = True
                    cpss.session['username'] = user['email']
                    cpss.session['name'] = user['name']
                    cpss.session['activated'] = '0'
                    cpss.session['admin'] = True
                    cpss.session.save()
                    self.forward(redir)
                else:
                    Error = """The username and password you have supplied 
                               are not valid. Please try again."""
                    self.do_header()
                    cpss.page.logon(Error=Error, Username=username, 
                                    redir=redir)
                    self.do_footer()
                return

            if ((username == None) or (password == None) or
                (username == "") or (password == "")):
                Error = "You must enter both a username and a password."
                authenticate = False
            else:
                (authenticate, user) = cpss.db.verify_user(username, password)
            if (authenticate == False):
                Error = """The username and password you have supplied are 
                           not valid. Please try again."""
                self.do_header()
                cpss.page.logon(Error=Error, Username=username, redir=redir)
                self.do_footer()
            if (authenticate == True):
                cpss.session['authenticated'] = True
                cpss.session['username'] = user['email']
                cpss.session['name'] = user['name']
                cpss.session['activated'] = user['activated']
                cpss.session.save()
                self.forward(redir)
        else:
            self.do_header()
            cpss.page.logon(Error=Error, redir=redir)
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
                self.forward('list')
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
