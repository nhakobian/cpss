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
                maintain = """<div class="maintainence">""" + self.options['maint_warn'] + "</div>"
            elif ((self.theSession['maint_mode'] == 2) and
                  (self.theSession['maint_allow'] == True)):
                maintain = """<div class="maintainence">A maintainence or debugging cycle is currently in effect. Beware that some features currently are not working as indended. To see the maintence page that is shown to people who do not have access during a maintainence cycle, please click <a href='invalidate/'>here</a>. This will log out out if you are currently logged in.</div>"""

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
        <center><h2>Semester 2011a: Deadline 31 Aug 2010 12PM CDT (1800 UT)</h2></center>

        <div style="width:75%;border:1px solid black;margin:0 auto;padding:5px;font-size:small;">
        <h3>Bug with WebKit Browsers (Safari, Google Chrome) 2010-Aug-26</h3>

        A bug was discovered today which prevented some users from creating a
        new proposal or adding additional authors and sources to their
        proposals. If you still encounter this issue, please fully exit your
        browser and restart to force your web browser to use the fix. If this
        does not correct the problem, please send an e-mail to the help
        address below.<br/><br/>

        This issue did not affect users of Mozilla Firefox or Internet 
        Explorer.
        </div>
        <br/>

        <div style="width:75%;border:1px solid black;margin:0 auto;padding:5px;font-size:small;">

        <h3>Figure issue workaround:</h3>

        If you have a problem where figures with LaTeX are causing 
        large amounts of whitespace to be added to the bottom of your
        page forcing figures to appear on a fourth justification page
        please try this workaround:<br><br>

        Change all your figure lines from:<br><br>
        \\begin{figure}<br>
        \\includegraphics{myfigure.ps}<br>
        \\caption{}<br>
        \\end{figure}<br><br>

        To:<br><br>

        \\begin{figure}<b>[h!]</b><br>
        \\includegraphics{myfigure.ps}<br>
        \\caption{}<br>
        \\end{figure}<br><br>

        If you still are having issues, please contact the proposal-help
        email address below.<br>
        </div><br>

        Welcome to the CARMA Proposal System. We hope that you will
        find this system will make it straightforward for you to apply
        for observing time on CARMA. If you have comments, or if you
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
        to use our template, located <a href="images/justification.tar.gz">
        here</a>. Please follow the guidelines listed below for the 
        justification sections. Non-compliant proposals will not be forwarded
        to the TAC.
        <ul>
        <li>2 Pages of text, no embedded figures.</li>
        <li>1 Page for figures, tables, and references.</li>
        <li>Do Not change the style sheet, or amend margins, type face, line spacing, etc.</li>
        </ul>

        <br/>
        If your proposal is accepted and observations are successful,
        we ask that you acknowledge CARMA in relevant publications and
        lectures. The form for acknowledgement in papers is on the
        CARMA website. Please also advise Mary Daniel (mary @
        mmarray.org) of any publications that use CARMA data.

        """)

    def bugs(self):
        self.req.write("""
        Below is a list of the known and resolved issues and bugs with the
        proposal system. Before you send in a bug report please take a look
        at the list below and make sure the bug you have seen has not already
        been reported. In reporting a bug, make sure that if there is a
        "Python Traceback," that you include the text of that error with
        your bug report, in addition to what you were doing at the time of the
        error and if it is reproducable. This will help in debugging the
        proposal system. You can always return to this page by clicking the
        CARMA logo at the top of the page.<br>
        <table style="width:100%;"><tr><th>Known Issues</th><th>Resolved Issues</th></tr>
        <tr>
        <td style="border:1px solid black;width:50%;vertical-align:top;">
        <b>Need to do (4 items)</b>
        <ul>
        <li>Data Validation - Proposal submit section. R07c</li>
        <li>PDF - Add proposal number and year to cover sheet. R07e</li>
        <li>PDF - Remove "Submission System" text at top and decrease
            in size. R03a</li>
        <li>PDF - Warn after 4 pages total that sci and tech
            justification must be less than 3 pages including
            refrences and figures. R03bii</li>
        </ul>
        <b>If time (11 issues)</b>
        <ul>
        <li>PDF - Lock out "View PDF" after one click and/or make a
            PDF generation queue in order to prevent spawning of
            unnecessary processes and overloading of the server.</li>
        <li>General - Cookies and Javascript enabled check.</li>
        <li>Authors - Be able to change the order of the authors
            without deleting and re-typing in all the information
            again.</li>
        <li>Authors - Hour percentages breakdown for
            author/institution billing. Will need check in final
            submission process that the total of these is 100(%).</li>
        <li>Observing Constraints - Collect the 7 observing
            constraints that the system needs. Low priority, but nice
            to have. R01</li>
        <li>Source - Possibly rename obsblock to something more
            intuitive. R03j</li>
        <li>PDF/General - PDF based technical and scientific
            justifications. Low priority. R03i</li>
        <li>Propinfo - Change name "Extensive" under Level of Help to
            something more clear. Possibly "Request Collaborator" ?
            R03k</li>
        <li>PDF - PDF Header/Footer on subsequent pages.</li>
        <li>Proposal Page - Copy proposal as new option.</li>
        <li>General - Create a facility to reset a user(s)
            password. Due to the way that the system stores passwords,
            there is *no* way for anyone (including the system
            admistrator) to view or tell the user what the pasword is
            used to (however it can be reset). This is for added
            security.</li>  
        </ul>
        </td>
        <td style="border:1px solid black;width:50%;vertical-align:top;"><ul>
        <li>9/19/06 - Help System - Make sure it is made clear that
            all text box inputs are under stood to accept
            LaTeX. R07d</li>
        <li>9/19/06 - Help System - State that inline references to papers,
            etc. are used.</li>
        <li>9/18/06 - Help System - Use the text that Doug wrote to explain
            what the various fields do. R02 & R04 (Web page info)</li>
        <li>9/16/06 - Data Validation - All fields validations complete.</li>
        <li>9/14/06 - Source - Obsblock verification added.</li>
        <li>9/14/06 - Data Validation - Ra/Dec checking is now enabled.</li>
        <li>9/14/06 - Help System/General - Make sure that it is very well
            noticed that Cookies and Javascript are required for this
            site to work as indended. Auto notices in window if these are
            not enabled.</li>
        <li>9/14/06 - PDF - Increased font size in "General" and
            "Propinfo." R03f</li>
        <li>9/14/06 - Source - Changed short name of Channnel Width to
            Width.</li>
        <li>9/14/06 - PDF - First paragraph of each written section is now
            indented as it is supposed to be.</li>
        <li>9/14/06 - PDF - Page break added after special requirements.
            R03bi</li>
        <li>9/14/06 - Source - Disabled point, flux columns from current call.
            R03c & R06a</li>
        <li>9/14/06 - Propinfo - Can now choose both for continuum or
            spectral line. R03d</li>
        <li>9/14/06 - Propinfo - Added comet to scientific category selection.
            R05</li>
        <li>9/14/06 - Source - Obsblock short name is now obsblk.</li>
        <li>9/14/06 - Source - "Is self calibratable" is not shown on the
            summary line now.</li>
        <li>9/14/06 - Source - Reordered source table to read : Min-Max and
            Flex.Ha at end of line.  Put Freq. after array. R03h</li>
        <li>9/14/06 - Source - Renamed "Filler" to "Flex.HA" for the displayed
            text. R03g</li>
        <li>9/13/06 - Added maintainence mode to enable/disable the system</li>
        <li>9/13/06 - Added some security checks</li>
        <li>9/13/06 - Changed login timer to 6 hours</li>
        <li>9/13/06 - Data Entry - Fixed several instances where entering
            some special characters in any type of text box would trigger html
            commands on view/edit instead of the correct symbol.</li>
        <li>9/13/06 - Data Validation - Most numeric entries are now contrained
            to numeric values that are appropriate to that type of data. RA,
            DEC do not have their constraints yet.</li>
        <li>9/13/06 - Data Validation - Valid/invalid prompt for spaces
            which do not need it has been removed.</li>
        <li>9/13/06 - Data Validation - Mosaic Fields minimum is 1.</li>
        <li>9/12/06 - Data Validation - Level of Help = None no longer appears
            as red on the PDF form.</li>
        <li>9/12/06 - Under "General Proposal Information", clicking "save
            changes" generates a python traceback error. Only happens
            if any drop down boxes is set to the value "No Value Set."
            This also happens under Source Information. R07a This was
            caused my a mysql version change on the server which
            behaves differently than any other mysql version before it
            or since. Also had to correct the below point as well to
            fix this.</li>
        <li>9/12/06 - Data Validation - Default on date field is current
            submission date.</li>
        <li>9/10/06 - Circular activation - On some sun machines (and others?),
            attempting to enter the activation code would return you to the
            main page, without actually sending the activation code to the
            server. This is believed to be fixed with the clarification of
            activation page patch below. If you use Netscape 7 on a Sun
            machine, please test this. If activation works fine, then it is
            working properly.</li>
        <li>9/10/06 - Clarified and simplified the mechanics of the
            activate account page. After activation, it now automatically
            goes to the proposal page.</li>
        <li>9/10/06 - Changed Username to E-mail address on login screen to
            make it clearer that the username is the e-mail address that the
            user signed up with.</li>
        <li>9/10/06 - Only 3mm band is allowed currently.</li>
        <li>9/10/06 - Only C and D arrays are selectable currently.</li>
        <li>9/9/06 - Image attachments glitches have been solved. The
            interface for uploading images has been cleaned up. Please
            continue testing this feature. Due to changes on this feature,
            any currently uploaded images may be deleted. Sorry for the
            inconvienience.</li>
        <li>Creation of a PDF file no longer crashes the Proposal System.
            Please continue testing this feature.</li>
        </ul></td>
        </table>
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
#        self.req.write("""<h3>%s's Proposals
#                          (<a href="proposal/add">Add New Proposal</a>)</h3>""" % name)
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
        
