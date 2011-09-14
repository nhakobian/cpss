from mod_python import apache

class Page:
    def __init__(self, req, config, session, options):
        self.req = req
        self.config = config
        self.base = self.config['html_base']
        self.theSession = session
        self.options = options

    def register(self, Connector, Backend):
        self.theBackend = Backend
        Self.theConnector = Connector
    
    def header(self, login=False, refresh=None, logon=False):
        logout_bar = [["Login", "login/"], ["Help","help/"], 
                      ["Create Account","create/"]]
        login_bar =  [["Proposals", "proposal/"], ["User Info","user/"],
                      ["Help","help/"], ["Logout", "logout/"]]

        if (refresh != None):
            self.req.headers_out['location'] = self.base+refresh
            self.req.status = apache.HTTP_MOVED_TEMPORARILY
            raise apache.SERVER_RETURN, apache.OK

        self.req.headers_out['Expires'] = 'Thu, 19 Nov 1981 09:52:00 GMT'
        self.req.headers_out['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
        self.req.headers_out['Pragma'] = 'no-cache'
        self.req.content_type = "text/html"

        maintain = ""
        if (self.theSession.__contains__('maint_mode') == True):
            if (self.theSession['maint_mode'] == 1):
                maintain = """<div class="maintenance">""" + self.options['maint_warn'] + "</div>"
            elif ((self.theSession['maint_mode'] == 2) and
                  (self.theSession['maint_allow'] == True)):
                maintain = """<div class="maintenance">A maintenance or debugging cycle is currently in effect. Beware that some features currently are not working as intended. To see the maintenance page that is shown to people who do not have access during a maintenance cycle, please click <a href='invalidate/'>here</a>. This will log out out if you are currently logged in.</div>"""

        if (logon==True):
            onLoad = "document.getElementById('login').style.visibility='visible';"
        else:
            onLoad = ""
            
        self.req.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html>
        <head>
        <title>CARMA Proposal Submission System
        </title>
        <script type="text/javascript">
        <!--

        function popup(link, windowname)
        {
           if (! window.focus) return true;
           var href;
           if (typeof(link) == 'string')
              href = link;
           else
              href = link.href;

           newwin = window.open(href, windowname, 'width=400,height=200,scrollbars=yes,toolbar=no,location=no,directories=no,status=no,menubar=no,resizable=yes,dependent=yes');
           if (window.focus) {newwin.focus();}
           return false;
        }

        function getCookie(name)
        {
           var newName = name + "=";
           var nameLength = newName.length;
           var cookieLength = document.cookie.length;
           var i = 0;
           while(i < cookieLength)
           {
              var j = i + nameLength;
              if(document.cookie.substring(i,j) == newName)
              {
                 return true;
              }
              i = document.cookie.indexOf(" ",i) + 1;
              if (i == 0) break;
           }
           return false;
        }
        
        document.cookie = 'test=junk';
        if(getCookie('test'))
        {
           // delete the cookie
           document.cookie = name + '=' + '; expires=Thu, 01-Jan-70 00:00:01 GMT';
        }
        else
        {
           document.write("<div class=browser_error id=test1>If you are seeing this message then cookies are not enabled on this browser. Cookies are required for this system to work properly. Please enable cookies and click <a href='login/'>here</a> to continue.</div>");
        }
        
        // -->
        </script>
        <base href="%s" />
        <link rel="stylesheet" href="cpss.css" type="text/css">
        </head>
        <body onLoad="%s">
        %s

        <noscript>
        <div class="browser_error">If you are seeing this message
        it is because you do not have javascript enabled. Javascript is
        required for this site to work properly. Please enable javascript and
        click <a href="login/">here</a> to continue.</div>
        </noscript>
                       
        <div class="container">
        <div class="top">
        <table><tr><td><a href="%s"><img src="images/carmasmall.jpg"></img>
        </a></td><td>
        CARMA Proposal Submission System</td></tr></table>
        </div>
        <div class="navbar">
        <ul id="navlist">""" % (self.base, onLoad, maintain,
                                self.config['html_base']))

        if (login == False):
            bar = logout_bar
        else:
            bar = login_bar

        for entry in bar:
            self.req.write("""<li><a href="%s">%s</a></li>""" % (entry[1],
                                                                 entry[0]))

        self.req.write("""</ul></div>
        <div class="content">
        """)

    def footer(self):
        #The second set of head tags assure that Internet Explorer will not
        #cache these pages. This would be bad...
        self.req.write("""
        </div>
        </div>
        <div class="copyright">
        All site content &copy;2005-2011 CARMA, all rights reserved.<br>
        Site maintained by the Proposal-Help Team &lt;<a href="mailto:proposal-help@astro.illinois.edu">proposal-help@astro.illinois.edu</a>&gt;.
        </div>
        </body>
        </html>""")
        
    def do_404(self):
        self.req.write("<center>This page cannot be found</center>")
        
    def logon(self, Error='', Username=''):
        self.req.write("""
        <div class="login" id="login" style="visibility:hidden;width:500px;margin:0 auto 0 auto"><center>
        Please enter your information to login. If you do not have a
        username or password, <a href="create">create one</a>. Your
        username is the e-mail address that you registered with.
        <br><br>
        If you have
        forgotten your password, type in your e-mail address and click
        password reset. A new password will then be sent to you.

        <br><font color="red">%s</font>
        
        <form action="login" method="post">
        <table><tr><td>
        E-mail:</td><td><input type="text" name="user" value="%s"></td></tr>
        <tr><td>
        Password:</td><td> <input type="password" name="pass"></td></tr>
        <tr><td colspan=2><center><input type="submit" name="submit" value="Submit">
            <input type="submit" name="forgotpw" value="Password Reset"></center></td></tr>
        </table>
        </form>
        </center>
        </div>""" % (Error, Username))

    def user_create(self, Name="", Email="", Error="", random=""):
        buffer = ("""
        If you wish to create an account, please fill out this form and submit
        it. You will recieve an e-mail shortly after which will contain
        additional instructions on how to login for the first time.""")

        if (Error != ""):
            buffer = buffer + ("""<br><center><font color=red>%s
                                  </font></center>""" % Error)

        buffer = buffer + ("""<form action="create/" method="post">
        <center>
        <table><tr><td>Full Name</td><td><input type="text" name="name"
                       value='%s'></td></tr>
               <tr><td>E-Mail Address</td><td><input type="text" name="email"
                       value='%s'></td></tr>
               <tr><td>Password</td><td><input type="password"
                       name="password1"></td></tr>
               <tr><td>Retype Password</td><td><input type="password"
                       name="password2"></td></tr>
               <tr><td></td><td><input type="hidden" name="random"
                       value='%s'><input type="submit" name="submit"
                       value="Submit"></td></tr>
               <center>""" % (Name, Email, random))
        self.req.write(buffer)       

    def user_create_success(self, name, email):
        self.req.write("""<center>
        Welcome, %s, you have successfully registered yourself in the Carma
        Proposal Submission System. You will shortly recieve an e-mail at
        the address you registered with, %s. You must log-in and enter the
        supplied code in order to gain access. This is done as a security
        measure to make sure that your e-mail address is accurate.</center>
        """ % (name, email))

    def main(self):
        self.req.write("""
        <center><h2>Semester 2012a: Deadline 05 December 2011 5PM CST</h2></center>

        Welcome to the CARMA Proposal System. This system is used to 
        proposose for time on the CARMA array during TAC-approved proposal
        calls. If you have comments, or
        encounter difficulties and need help, please send email to: <a
        href="mailto:proposal-help@astro.uiuc.edu">
        proposal-help@astro.uiuc.edu</a><br><br>
        
        Information for proposers, including a link to information on
        the CARMA Array status, is available at:
        <a href="http://www.mmarray.org/">www.mmarray.org</a><br><br>

        The CARMA Proposal System will ask you to establish an account
        for your proposals. You can work on proposals and save partial
        and draft results, and come back later to edit and finish your
        proposals. Old proposals will be kept on the system as reference.
        <br><br>

        Most people try to write proposals the
        last day or last hour before the deadline. Be aware that
        things may be very busy near the deadline, with the proposal
        computer response slower than normal and our ability to help
        you with problems in time for you to meet the deadline
        reduced. It would be to your advantage to get proposals into
        the system as early as possible. Even after you submit a
        proposal, you can come back and revise it anytime before the
        deadline, so getting a complete proposal in early insures that
        you will meet the deadline without compromising your ability
        to make last minute changes.<br><br>

        <h3>Scientific and Technical Justification</h3>

        This part of the proposal is strictly limited to 3
        pages, 2 pages of text and 1 page of figures and tables. One
        way to enter this information is to type or paste LaTex into
        the Scientific Justification and Technical Justification
        sections. The
        <a href="http://www.journals.uchicago.edu/AAS/AASTeX/">AASTeX<a>
        system is fully supported. Postscript figures may be uploaded
        for inclusion using standard LaTex figure conventions. When
        you submit, the proposal system will compile your LaTex and
        display a PDF file on your screen for you to check (make sure
        the total justification is no more than 3 pages).

        If you wish to have more control over your justification 
        section, you may upload a completed LaTeX file. You are required
        to use our <a href="images/justification.tar.gz">
        template</a>. Please follow the guidelines listed below for the 
        justification sections. Non-compliant proposals will not be forwarded
        to the TAC.
        <ul>
        <li>2 Pages of text, no embedded figures.</li>
        <li>1 Page for figures, tables, and references.</li>
        <li>Do Not change the style sheet, or amend margins, type face, line spacing, etc.</li>
        </ul>

        <h3>Key Projects</h3>

        If you are submitting a proposal for a Key Project, the justification
        requirements are different. <b>Make sure you select the 'Key Project'
        option listed in the 'General Proposal Information' section. Adjustments
        to the length of key projects are listed below.</b> For more information about
        these projects, visit the <a href="http://cedarflat.mmarray.org/observing/proposals/KP_call2011b.html">Key Project</a> page. For the Key Project justification, you must upload a LaTeX file containing the content. We provide a <a href="images/justification_key.tar.gz">template</a> that you must adhere to in order for your proposal to be considered (this template is slightly different that the one for standard proposals).

        <ul> <li>Proposal text (5 pages maximum):<br> The proposal
        text must contain the following information:<br> a) Scientific
        Justification and anticipated scientific impact of the
        proposed observations.<br> b) Technical justification, including the
        timeline for the proposed observations. <br> c) Management. This
        section should provide a plan for the overall management of
        the project. This should include (i) a description of the data
        products and data release plans, (ii) key benchmarks covering
        the duration of the project against which progress may be
        gauged, and (iii) how the project team will contribute to
        CARMA operations and provide regular feedback on data quality.</li><br>

        <li>Figures, Table, and References (3 pages maximum):<br> If
        the complete source list is not entered on the cover sheet,
        then a table must be included that contains the complete
        source list. For each source, the table should indicate the
        coordinates, observed frequencies, velocities, and time per
        configuration. The total time for the project per
        configuration per semester must be clearly indicated.</li>
        </ul>

        If your proposal is accepted and observations are successful,
        we ask that you acknowledge CARMA in relevant publications and
        lectures. The form for acknowledgement in papers is on the
        CARMA website. Please also advise Mary Daniel (mary @
        mmarray.org) of any publications that use CARMA data.

        """)

    def activate(self, Error=""):
        self.req.write("""
        You have not yet confirmed your account. Please enter your activation
        code below, or, if you have lost or not recieved the e-mail, press the
        generate button to generate a new e-mail.

        <br><font color="red">%s</font>

        <center><form action="proposal/" method="post">
        <table><tr><td>Activation Code:</td><td>
        <input type=text name="activate"></td><tr></table>
        <input type=submit name="sub_activate" value="Activate Account">
        </form>
        <br>
        If you need a new activation code sent, please click the button below.
        <form action="" method="post">
        <input type=submit name="sub_activate" value="Resend Activation Code">
        </form>
        </center>""" % Error)

    def userpage(self, name, email, error=""):
        if (error != ""):
            self.req.write("<div class=browser_error>%s</div>" % error )
        self.req.write("""<center><h1>User Information</h1>""")
        self.req.write("""<table><tr><td>Name:</td><td>%s</td></tr>""" % name)
        self.req.write("""<tr><td>Email:</td><td>%s</td></tr></table></center>""" % email)
        self.req.write("""<br><center><form action="user/" method="post">
        <table><tr><td colspan=2><h3>Change Password</h3></td></tr>
        <tr><td>Old Password:</td><td><input type=password name="oldpw"></td></tr>
        <tr><td>New Password:</td><td><input type=password name="newpw1"></td></tr>
        <tr><td>Repeat New Password:</td><td><input type=password name="newpw2"></td></tr>
        <tr><td colspan=2><center><input type=submit name="changepw" value="Change Password"></center></td></tr></table>
        </form></center>
        """)

    def proposal_list(self, list, name):
        if self.options["create"] == True:
            self.req.write("""<h3>%s's Proposals
                 (<a href="proposal/add">Add New Proposal</a>)</h3>""" % name)
        else:
            self.req.write("""<h3>%s's Proposals</h3>""" % name)

        if (len(list) == 0):
            self.req.write("""<div id="proplist"><p><i>You have no saved
            proposals. Click the new button above to add one.</i></p></div>""")
        else:
            buf = """<div id="proplist"><table><tr>
                     <th>ID</th><th>Title</th><th>Status</th>
                     <th>Action</th><th>Data Password</th></tr>"""
            for entry in list:
                if (entry['status'] == 0):
                    carmaid = 'None'
                    status = "Unsubmitted"
                    pdf = ("""<a href="proposal/delete/%s">delete</a>""" %
                           entry['proposalid'])
                    password = ""
                else:
                    carmaid = str(entry['carmaid'])
                    status = 'Submitted'
                    pdf =  ("""<a href="proposal/finalpdf/%s">view final pdf</a>""" %
                            (entry['proposalid']))
                    password = str(entry['carmapw'])
                if ((entry['cyclename'] != self.options['cyclename']) and (entry['status'] == 1)):
                    #placeholder
                    buf += ("""<tr><td>%s</td><td id="title">%s</td><td>%s</td>
                    <td>  %s </td><td>%s</td></tr>"""
                    % (carmaid, entry['title'], status, pdf, password))
                else:
                    buf += ("""<tr><td id="id">%s</td><td id="title">%s</td><td>%s</td>
                    <td><a href="proposal/edit/%s">edit</a> | %s </td><td>%s</td></tr>"""
                    % (carmaid, entry['title'], status, entry['proposalid'],
                       pdf, password))
            buf += """</table></div>""" 
            self.req.write(buf)
        
    def delete_verify(self, pathtext, title):
        self.req.write("""<center>Do you wish to delete the proposal, "%s"?

        <form action="%s" method="post">
        <input type=submit name="delete" value="Delete Proposal"></form>

        <form action="proposal/" method="post">
        <input type=submit name="cancel" value="Cancel"></form> """ %
                       (title, pathtext))
        
