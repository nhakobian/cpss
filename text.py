email_activation=r"""To: "%s" <%s>
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
proposal-help@astro.illinois.edu
"""

email_pwreset=r"""To: %s
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
proposal-help@astro.illinois.edu
"""

error_coversheet=r"""<div class="latex_error_msg">
<img src="./static/exclaimation.png">
A LaTeX error has occurred on the generated coversheet. This usually is caused by a 
LaTeX character in your title, author information, or abstract that is not correctly
escaped. Most commonly, '&' is used instead of '\&', or '%' instead of '\%'. Also
note, that non-ASCII characters are currently not supported. If you are still
receiving this error, please contact the Proposal-help team 
<proposal-help@astro.illinois.edu> for more assistance.
</div>"""

error_justification=r"""<div class="latex_error_msg">
<img src="./static/exclaimation.png">
A LaTeX error has occurred in your justification attachment. The output from LaTeX is
displayed below to assist you in finding your error. If you need additional 
assistance, please contact the 
<a href="mailto:proposal-help@astro.illinois.edu">Proposal-help team</a>.
</div>"""

error_latex_large=r"""The LaTeX file you are trying to upload is greater than the allowed
size of 10MB. Please check to make sure you are uploading the correct
file.
"""

error_ps_large=r"""The postscript image you are trying to upload is greater than the
allowed size of 14MB. If you must upload an image greater than this
size please send a message to proposal-help@astro.illinois.edu for help.
"""

fast_submit_success=r"""
<div class=submitted>
  Congratulations! You have sucessfully submitted your proposal!<br>

  To view your final proposal, click on the Proposals button above to
  return to the screen which lists your proposals, and click on the
  "view final pdf" link available there.<br><br>
</div>
"""

help_abstract=r"""
<div class="helptext">
  Please keep the abstract to 1/4 of a page maximum. You may use LaTeX
  commands, but please keep them to a minimum. The abstract will be
  stored in the project database and any LaTeX commands will be
  stripped out.
</div>
"""

help_author=r"""
<div class="helptext">
  The <b>Authors List</b> section is intended for observers to give
  information regarding who is working on this proposed project, what
  institutions they are from, and whether or not the individuals are
  graduate students.
</div>

<a name="name"></a>
<div class="helptitle">Name</div>
<div class="helptext">
  Please insert your/your co-author(s) name(s) here.
</div>

<a name="email"></a>
<div class="helptitle">E-mail</div>
<div class="helptext">
  Please enter the e-mail addresses of you and your colleagues
  here.
</div>

<a name="phone"></a>
<div class="helptitle">Phone Number</div>
<div class="helptext">
  Please enter the contact phone number here.
</div>

<a name="institution"></a>
<div class="helptitle">Institution</div>
<div class="helptext">
  Please select your institution name here from the drop down box.  If
  you are not at one of the CARMA member institutions, select 'Other'
  and enter your institution name in the box that appears below.
</div>

<a name="grad"></a>
<div class="helptitle">Graduate Student</div>
<div class="helptext">
  Is this person a graduate student?
</div>

<a name="thesis"></a>
<div class="helptitle">Thesis</div>
<div class="helptext">
  Is this proposal part of an approved graduate student thesis
  project? If this box is checked, a supporting e-mail from the
  advisor must be sent to Nikolaus Volgenau
  (volgenau@mmarray.org). The e-mail should describe the role of the
  observations in the thesis.
</div>
"""

help_image=r"""
<div class="helptext">
  Use the images section to attach any images to your proposal. The
  images must be in postscript (PS or EPS) format. If you upload any
  other type of image, you will get an error when you attempt to view
  the PDF of your proposal.  If you need to make any adjustments to
  the attached image (i.e.  rotation, scale, cropping) please refer to
  the documentation for the LaTeX package graphicx. The maximum file
  size for an image is ~14MB.
</div>
"""

help_index=r"""<span style="font-weight:bold;font-size:14pt">
  Choose a help topic below:
</span>

<ul style="help">
  <li>
    <a href="%shelp/propinfo">
      General Proposal Information
    </a>
  </li>
  <li>
    <a href="%shelp/author">
      Authors List
    </a>
  </li>
  <li>
    <a href="%shelp/abstract">Abstract</a>
  </li>
  <li>
    <a href="%shelp/source">Source Information</a>
  </li>
  <li>
    <a href="%shelp/special_requirements">
      Special Requirements
    </a>
  </li>
  <li>
    <a href="%shelp/scientific_justification">
      Scientific Justification
    </a>
  </li>
  <li>
    <a href="%shelp/technical_justification">
      Technical Justification
    </a>
  </li>
  <li>
    <a href="%shelp/image">Image Attachments</a>
  </li>
</ul>
<br>
If you have an issue or question (whether it is a technical problem
with the proposal site or a clarification on what type of information
is expected) please send an e-mail to proposal-help@astro.illinois.edu
. If it is a technical issue, please make sure to give exact
information as to what you were trying to do, and what the error
message (if any) said.
"""

help_priorobs=r"""
<div class="helptext">
  The Status of Prior CARMA Observations section allows the proposer
  to report on the status of the PI's prior CARMA observations. For
  example, whether they are reduced, in press, published, etc. Include
  previous project codes.
</div>
"""

help_propinfo=r"""<div class="helptext"> 
  The <b>General Proposal Information</b> section is intended for the
  proposer to give some general information about their proposed
  project. Below is a description of what information is requested in
  this section.
</div>

<a name="title"></a>
<div class="helptitle">Title</div>
<div class="helptext">
  The title of your proposal (no LaTeX characters are allowed).<br>
</div>

<a name="date"></a>
<div class="helptitle">Date</div>
<div class="helptext">
  This date is set automatically to when you last edited the
  information on your proposal.
</div>

<a name="toe"></a>
<div class="helptitle">Time Critical</div>
<div class="helptext">
  Check this box if the object(s) you wish to observe need to be
  scheduled only at specific times (whether known in advance or not)
  (e.g. cometary observations, solar flares, transient source
  follow-up, coordinated observations).
</div>

<a name="priority"></a>
<div class="helptitle">Priority</div>
<div class="helptext">
  If you are submitting several proposals, you may assign a priority
  number to each proposal if you wish to designate one project as
  being more important than another. No error checking is performed on
  this field.
</div>

<a name="scientific_category"></a>
<div class="helptitle">Scientific Category</div>
<div class="helptext">
  What general category best describes your project?
</div>

<a name="type_of_observation"></a>
<div class="helptitle">Type of Observation</div>
<div class="helptext">
  Is this a spectral line observation, continuum observation, or
  both?
</div>

<a name="frequency_band"></a>
<div class="helptitle">Frequency / Receiver Band</div>
<div class="helptext">
  What receiver band are you requesting for your obervations?
</div>

<a name="help_required"></a>
<div class="helptitle">Level of Help Required</div>
<div class="helptext">
  Choose "Consultation" for help preparing for your observations. A
  collaborator is currently recommended if you are not already
  familiar with millimeter interferometer data reduction
  techniques.
</div>
"""

help_scientificjust=r"""
<div class="helptext">
  In the <b>Scientific Justification</b> section describe the
  scientific motivation for the project. The Scientific and Technical
  Justification sections combined may be no longer than three pages: 2
  pages of text, and 1 for tables, figures, and references. LaTeX text
  may be used in this section. If you need to make a reference to an
  article or paper, please use inline references.
</div>
"""

help_source=r"""
<div class="helptext">
  The <b>Source Information</b> section allows the proposer to enter
  information about what sources he/she wants to observe using
  CARMA. If you have any questions as to what types of data are
  expected in the fields, please read the descriptions below. Please
  enter sources in the list in priority order.
</div>

<a name="array_config"></a>
<div class="helptitle">Array Configuration</div>
<div class="helptext">
  Which array configuration(s) are you requesting? See <a
  href="http://cedarflat.mmarray.org/observing/doc/instrument_desc.html"
  target="_blank">this page</a> for a description of the different
  array configurations. Please also see the definition of hours
  requested.
</div>

<a name="corr_frequency"></a>
<div class="helptitle">Frequency of Observation</div>
<div class="helptext">
  Please give the frequency of your observations in GHz.
</div>

<a name="name"></a>
<div class="helptitle">Source Name</div>
<div class="helptext">
  A short, simple, descriptive name for the object that you are
  observing.
</div>

<a name="ra"></a>
<div class="helptitle">Right Ascension</div>
<div class="helptext">
  Please give coordinates to the object or region that you are
  observing in J2000 format. If your proposal is accepted, you will be
  able to give more accurate coordinates at that time. Make sure that
  your Right Ascension is in the format HH MM or HH:MM.
</div>

<a name="dec"></a>
<div class="helptitle">Declination</div>
<div class="helptext">
  Please give the Declination of the object you are observing. See the
  restrictions and notes for Right Ascension above.
</div>

<a name="numb_fields"></a>
<div class="helptitle">Number of Mosaic Fields</div>
<div class="helptext">
  How many different pointings are involved in the observations of
  this source?
</div>

<a name="species"></a>
<div class="helptitle">Species / Transition Name</div>
<div class="helptext">
  If these are molecular line observations what species and transition
  are being observed. For continuum projects just enter
  "continuum".
</div>

<a name="self_cal"></a>
<div class="helptitle">Can Self-Calibrate</div>
<div class="helptext">
  Can your source be self-calibrated?
</div>

<a name="min_max"></a>          
<div class="helptitle">Time Requested</div>
<div class="helptext">
  How long are you requesting to observe this obsblock in hours (this
  time includes your source(s) and any calibrators observed), per
  array configuration?  If the time requested is longer than can be
  accomodated in a single track, the observation will be on multiple
  days. Track lengths will depend on declination and whether the
  project is primarily an imaging project, or requires the best
  SNR. See <a
  href="http://cedarflat.mmarray.org/observing/doc/instrument_desc.html"
  target="_blank">this page</a> for more details.
</div>

<a name="imaging"></a>
<div class="helptitle">Imaging/SNR</div>
<div class="helptext">
  If the aim of this obsblock is to get the most complete UV coverage
  (and thus the best image possible) then select IMAGE. For detection
  projects, or other projects where signal to noise is critical,
  select SNR. Such projects can often be observed in smaller pieces or
  off transit to increase the scheduling efficiency of the
  telescope. To allow this, and receive compensation in the form of
  increased observation time will be made if you elect this option.
</div>

<a name="f_sourcename"></a>
<div class="helptitle">Fast-Track Proposals</div>

<div class="helptitle">Source Name</div>
<div class="helptext">
  A short, simple, descriptive name for the object that you are
  observing.
</div>

<a name="f_ra"></a>
<div class="helptitle">Right Ascension</div>
<div class="helptext">
  Specify your Right Ascension in the format HH:MM:SS.SS.
</div>

<a name="f_dec"></a>
<div class="helptitle">Declination</div>
<div class="helptext">
  Specify your Declination in the format HH:MM:SS.SS.
</div>

<a name="f_vlsr"></a>
<div class="helptitle">LSR Velocity</div>
<div class="helptext">
  Specify your source's LSR Velocity in km/s.
</div>

<a name="f_time"></a>
<div class="helptitle">Track Length</div>
<div class="helptext">
  Specify the requested time for the observing track. You can
  request 1 to 3 hour long tracks with this tool.
</div>

<a name="f_array"></a>
<div class="helptitle">Array Configuration</div>
<div class="helptext">
  Choose the array configuration that your track should be
  observed in. Some correlator modes are only available in
  specific array configurations. See the help on correlator
  modes for more information.  
</div>

<a name="f_corrconfig"></a>
<div class="helptitle">Correlator Mode</div>
<div class="helptext">
<b>SCI1_1MM_DP_CO</b> : Dual polarization (1mm) observations
of CO, 13CO and C18O, a bandwidth must also be selected, one
band is set to continuum.<br>

<b>SCI1_1MM_DP_SL</b> : Dual polarization (1mm) observations
of a user specified spectral line, a bandwidth and line rest
frequency must also be specified, 3 bands are set to 
continuum.<br>

<b>SCI1_1MM_DP_WB</b> : Dual polarization (1mm) continuum, a
rest frequency must also be given.<br>

<b>SCI1_1MM_FP_CO</b> : Full stokes (1mm) observations of CO,
13CO and C18O, a bandwidth must also be selected, one band is
set to continuum.<br>

<b>SCI1_1MM_FP_SL</b> : Full stokes (1mm) observations of a
user specified spectral line, a bandwidth and line rest 
frequency must also be specified, 3 bands are set to 
continuum.<br>

<b>SCI1_1MM_FP_WB</b> : Full stokes (1mm) continuum, a rest 
frequency must also be given.<br>

<b>SCI1_1MM_SP_CO</b> : 1mm observations of CO, 13CO and C18O, 
a bandwidth must also be selected, five bands are set to 
continuum.<br>

<b>SCI1_1MM_SP_SL</b> : 1mm observations of a user specified 
spectral line, a bandwidth and line rest frequency must also 
be specified, 7 bands are set to continuum.<br>

<b>SCI1_1MM_SP_WB</b> : 1mm continuum, a rest frequency must 
also be given.<br>

<b>SCI1_3MM_C23_CO</b> : CARMA 23 3mm observations of CO, 
13CO and C18O, a bandwidth must also be selected, one band 
is set to continuum.<br>

<b>SCI1_3MM_C23_HCO+</b> : CARMA 23 3mm observations of HCN, 
HCO+, and N2H+, a bandwidth must also be selected, one band 
is set to continuum.<br>

<b>SCI1_3MM_C23_SL</b> : CARMA 23 3mm observations of a user
specified spectral line, a bandwidth and line rest frequency 
must also be specified, 3 bands are set to continuum.<br>

<b>SCI1_3MM_C23_WB</b> : CARMA 23 3mm continuum, a rest 
frequency must also be given.<br>

<b>SCI1_3MM_SP_CO</b> : 3mm observations of CO, 13CO and C18O, 
a bandwidth must also be selected, 5 bands are set to 
continuum.<br>

<b>SCI1_3MM_SP_HCO+</b> : 3mm observations of N2H+, HCN, HCO+, 
NH2D, H13CO+, H13CN, and CS, a bandwidth must also be 
selected, one band is set to continuum.<br>

<b>SCI1_3MM_SP_SL</b> : 3mm observations of a user specified 
spectral line, a bandwidth and line rest frequency must also 
be specified, 7 bands are set to continuum.<br>

<b>SCI1_3MM_SP_WB</b> : 3mm continuum, a rest frequency must 
also be given.<br>

<b>SCI2_1CM_SP_WB</b> : 1cm continuum, 3.5m antennas only.<br>

<b>SCI2_3MM_SP_WB</b> : 3mm continuum, 3.5m antennas only, a 
rest frequency must also be given.<br>
</div>

<a name="f_freq"></a>
<div class="helptitle">Frequency</div>
<div class="helptext">
  Specify your observing frequency in (GHz) for correlator
  modes that require a user specified frequency. Leave this
  field blank for modes that do not require a frequency.
</div>

<a name="f_slbw"></a>
<div class="helptitle">Spectral Line Bandwidth</div>
<div class="helptext">
  For correlator modes that require a user specified bandwidth,
  select one of the options in the drop down box. Select 'No Value
  Set' for modes that do not require a specified bandwidth.
</div>

<a name="f_mosaic"></a>
<div class="helptitle">Mosaic</div>
<div class="helptext">
  Currently the fast-track system only supports standard 7 Point 
  mosaics. If you do not wish to perform mosaic observations,
  select 'No Value Set'.
</div>"""

help_specialreq=r"""
<div class="helptext">
  The special requirements section is designed for the proposer to
  describe any unusual observing constraints that are not defined
  anywhere else in the proposal.  This includes a summary of special
  equipment, special observing conditions, required dates, or any
  other information even if it is described in another section.
</div>
"""

help_technicaljust=r"""
<div class="helptext">
  In the <b>Technical Justification</b> section justify the proposed
  observations on technical grounds. Include any information that will
  allow the TAC to assess the technical viability of the project. The
  Scientific and Technical Justification sections combined may be no
  longer than three pages: 2 pages of text, and 1 for tables, figures,
  and references. LaTeX text may be used in this section. If you need
  to make a reference to an article or paper, please use inline
  references.
</div>
"""

help_tothours=r"""
<div class="helptext">
  The total number of hours is calculated by adding up how many hours
  per source you have requested, by multiplying Hours Requested by the
  number of array configurations you requested the source to be
  observed in. For example, if you requested a single source to be
  observed in the A, B, C, and D arrays for 8 hours, the Total Hours
  will be 32.
</div>
"""

html_just_key=r"""<div id="editlist">
  <p><a name="type"></a>Justification Type</p>

  <table>
    <tr>
      <td style="width : 50%%; text-align : left;">
        Key Projects are required to upload a <b>LaTeX</b> file for
        their justification. A LaTeX template specifically for Key
        Projects is available <a
        href="static/justification_key.tar.gz">here</a>. This template
        conforms to all the necessary requirements. Use the following
        link for more details about <a href=
        "http://cedarflat.mmarray.org/observing/proposals/KP_call2012b.html"
        target="_blank">Key Projects</a>.
      </td>
      <td>
        %s
      </td>
    </tr>
  </table>
</div>"""

html_just_normal=r"""<div id="editlist">
  <p><a name="type"></a>Justification Type</p>

  <table>
    <tr>
      <td style="width : 50%%; text-align : left;">
        Using this proposal submission tool, you have a choice of
        using the web-based tool to submit your Scientific and
        Technical Justification sections or to upload a LaTeX file
        containing this information using the template located <a
        href='static/justification.tar.gz'>here</a>.
      </td>
      <td>
        <form action='typechange/%s' method='post' name="form">
          I want to use: 
          <select name="type">
            <option value="Website Justification" %s>Website Justification
            <option value="LaTeX Template" %s>LaTeX Template
          </select>
          <input type="submit" value="Select Choice" name="submit">
        </form>
	%s
      </td>
    </tr>
  </table>

</div>"""

page_ddt=r"""<h2 class="center">DDT Proposals</h2>

Welcome to the CARMA Proposal System. This system is used to propose
for Director's Discretionary Time (DDT) on the CARMA array. If you
have comments, encounter difficulties, or need help, please send an
email to: <a href="mailto:proposal-help@astro.illinois.edu">
proposal-help@astro.illinois.edu</a>

<ul>
  <li>Please login if directed to below.</li>
  <li>Read the disclaimer.</li>
  <li>Click on the button to create a new DDT proposal.</li>
</ul>

This will add a new DDT to your list of proposals which you can then
edit and submit as you would a standard CARMA proposal.

<br/><br/>"""

page_ddt_disclaimer=r"""<div class="warn">
     <img src="static/exclaimation.png">
     By clicking the button below, you certify that you have been instructed to
     fill out and submit a DDT proposal. After clicking the button, a new
     DDT proposal will be created and you will be returned to the list of your
     proposals. You may edit and delete DDT proposals as you would a standard
     proposal. 

     <form action="add/ddt" method="get">
       <input type=submit value="Create DDT Proposal">
     </form>
</div>"""

page_error=r"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html>
<head>
   <title>CARMA Proposal Submission System</title>
   <base href="" />
</head>
<body style="background:#CCCC77;font-family:sans-serif;font-size:10pt;">

<div class="container" style="width:100%%;height:100%%;">

<div style="width:750px;background:#FF5555;border:1px solid black;margin:0 auto;padding:0.5ex">
<b>The CARMA proposal system has encountered an error.</b><br><br>
This page is here to help you help us to solve this error. An error
report has been sent to the site administers. If you would like to
help expidite this error being fixed, please send an email to 
<a href="mailto:proposal-help@astro.illinois.edu">
proposal-help@astro.illinois.edu</a> with the following information:
<ul>
  <li>Your Name</li>
  <li>Your username</li>
  <li>What you were doing when the error occured (as many details as 
    possible).</li>
  <li>The following error code:<br>
      Error ID: %s -- Time: %s</li>
</ul>
Thank you for your assistance in this matter.
</div>

</div>

</body>
</html>
"""

page_fasttrack=r"""<h2 class="center">Fast-track Proposals</h2>

Welcome to the CARMA Proposal System. Use this system to propose for 
Fast-track Time on the CARMA array. This will add a new Fast-track 
proposal to your proposals list. A fast-track proposal cannot be
edited once submitted.

If you have comments, encounter difficulties, or need help, please 
send an email to: <a href="mailto:proposal-help@astro.illinois.edu">
proposal-help@astro.illinois.edu</a>

<br/><br/>"""

page_fasttrack_disclaimer=r"""<div class="warn">
     <img src="static/exclaimation.png">
     By clicking the button below, a new Fast-track proposal will be
     created and you will be returned to the list of your proposals. 
     You may then edit a Fast-track proposal as you would a standard
     proposal. 

     <form action="add/fast" method="get">
       <input type=submit value="Create Fast-track Proposal">
     </form>
</div>"""

page_footer=r"""  </div>
</div>

<div id="copyright" class="nojs">
  All site content &copy;2005-2013 CARMA, all rights reserved.<br>
  Site maintained by the Proposal-Help Team 
  &lt;<a href="mailto:proposal-help@astro.illinois.edu">proposal-help@astro.illinois.edu</a>&gt;.
</div>

</body>
</html>
"""

page_header=r"""<!DOCTYPE html>

<html>
<head>
   <title>CARMA Proposal Submission System</title>
   <base href="%s" />
   <script type="text/javascript" src="static/cpss.js"></script>
   <link rel="stylesheet" href="static/cpss.css" type="text/css">
   <link rel="icon" href="/favicon.ico" type="image/x-icon" />
   <link rel="shortcut icon" href="/favicon.ico" />
</head>

<body>
%s

<noscript>
   <div id="nojs">
   </div>
   <div id="nojs_message">
     <img src="static/exclaimation.png">
     <span>Your browser currently has javascript disabled. The CARMA Proposal
     System requires javascript.</span>
   </div>
</noscript>
                       
<div id="container" class="nojs">
   <p id="logo">
            <a href="%s"><img src="static/carmasmall.jpg"/></a>
            CARMA Proposal Submission System
   </p>
   <div class="navbar">
      <ul id="navlist">

"""

page_logon=r"""<div class="login" id="login" style="width:500px;margin:0 auto 0 auto">
<center>
  Please enter your information to login. If you do not have a
  username or password, <a href="create">create one</a>. Your
  username is the e-mail address that you registered with.
  <br><br>
 
  If you have forgotten your password, type in your e-mail address
  and click password reset. A new password will then be sent to you.

  <br>
  <font color="red">%s</font>

  <form action="login" method="post">
     <table>
       <tr>
         <td>
           E-mail:
         </td>
         <td>
           <input type="text" name="user" value="%s">
         </td>
       </tr>
       <tr>
         <td>
           Password:
         </td>
         <td>
           <input type="password" name="pass">
	   <input type="hidden" name="redir" value="%s">
         </td>
       </tr>
       <tr>
         <td colspan=2>
           <center>
             <input type="submit" name="submit" value="Submit">
             <input type="submit" name="forgotpw" value="Password Reset">
           </center>
         </td>
       </tr>
     </table>
  </form>
</center>
</div>

"""

page_main=r"""  <h2 class="center">
    Semester 2013b: Deadline 21 May 2013 5PM CDT (UTC-5)
  </h2>

<p>Welcome to the CARMA Proposal System. This system is used to propose
for time on the CARMA array during TAC-approved proposal calls. If you
have comments, or encounter difficulties and need help, please send
email to: <a href="mailto:proposal-help@astro.illinois.edu">
proposal-help@astro.illinois.edu</a></p>

<p>Information for proposers, including a link to information on the
CARMA Array status, is available at: <a href="http://www.mmarray.org/">
www.mmarray.org</a></p>

<p>The CARMA Proposal System will ask you to establish an account for
your proposals. You can work on proposals and save partial and draft
results, and come back later to edit and finish your proposals. Old
proposals will be kept on the system as reference.</p>

<p>Most people try to write proposals the last day or last hour before
the deadline. Be aware that things may be very busy near the deadline,
with the proposal computer response slower than normal and our ability
to help you with problems in time for you to meet the deadline
reduced. It would be to your advantage to get proposals into the
system as early as possible. Even after you submit a proposal, you can
come back and revise it anytime before the deadline, so getting a
complete proposal in early insures that you will meet the deadline
without compromising your ability to make last minute changes.</p>

<h3>Scientific and Technical Justification</h3>

<p>This part of the proposal is strictly limited to 3 pages, 2 pages of
text and 1 page of figures and tables. One way to enter this
information is to type or paste LaTex into the Scientific
Justification and Technical Justification sections. The 
<a href="http://www.journals.uchicago.edu/AAS/AASTeX/">AASTeX</a> system
is fully supported. Postscript figures may be uploaded for inclusion
using standard LaTex figure conventions. When you submit, the proposal
system will compile your LaTex and display a PDF file on your screen
for you to check (make sure the total justification is no more than 3
pages).</p>

<p>If you wish to have more control over your justification section, you
may upload a completed LaTeX file. You are required to use our <a
href="static/justification.tar.gz"> template</a>. Please follow the
guidelines listed below for the justification sections. Non-compliant
proposals will not be forwarded to the TAC.  </p>

<ul>
  <li>
    2 Pages of text, no embedded figures.
  </li>
  <li>
    1 Page for figures, tables, and references.
  </li>
  <li>
    Do Not change the style sheet, or amend margins, type face, line spacing,
    etc.
  </li>
</ul>

<h3>Key Projects</h3>

<p>If you are submitting a proposal for a Key Project, the justification
requirements are different. <b>Make sure you select the 'Key Project'
option listed in the 'General Proposal Information' section. Adjustments
to the length of key projects are listed below.</b> For more information
about these projects, visit the <a 
href="http://cedarflat.mmarray.org/observing/proposals/KP_call2013a.html">Key
Project</a> page. For the Key Project justification, you must upload a
LaTeX file containing the content. We provide a <a
href="static/justification_key.tar.gz">template</a> that you must
adhere to in order for your proposal to be considered (this template
is slightly different that the one for standard proposals).</p>

<ul>
  <li>
    Proposal text (5 pages maximum):<br> 

    The proposal text must contain the following information:<br>

    a) Scientific Justification and anticipated scientific impact of
        the proposed observations.<br>

    b) Technical justification, including the timeline for the
        proposed observations. <br> 

    c) Management. This section should provide a plan for the overall
       management of the project. This should include (i) a
       description of the data products and data release plans, (ii)
       key benchmarks covering the duration of the project against
       which progress may be gauged, and (iii) how the project team
       will contribute to CARMA operations and provide regular
       feedback on data quality.
  </li><br>

  <li>
      Figures, Table, and References (3 pages maximum):<br>

      If the proposer needs help inputing a large number of sources into the
      source configuration section, please contact the Proposal Help email
      address. The total time for the project per configuration
      per semester must be clearly indicated.
  </li>
</ul>

<p>If your proposal is accepted and observations are successful, we ask
that you acknowledge CARMA in relevant publications and lectures. The
form for acknowledgement in papers is on the CARMA website. Please
also advise Mary Daniel (mary @ mmarray.org) of any publications that
use CARMA data.</p>
"""

page_user=r"""<div class=browser_error style="%(errorsty)s">%(error)s</div>

<center>
   <h1>User Information</h1>

   <table>
      <tr>
        <td>
          Name:
        </td>
        <td>
          %(name)s
        </td>
      </tr>

      <tr>
        <td>
          Email:
        </td>
        <td>
          %(email)s
        </td>
      </tr>
   </table>
</center>

<br>

<center>
   <form action="user" method="post">
   <table>
      <tr>
        <td colspan=2>
          <h3>Change Password</h3>
        </td>
      </tr>
      
      <tr>
        <td>
          Old Password:
        </td>
        <td>
          <input type=password name="oldpw">
        </td>
      </tr>

      <tr>
        <td>
          New Password:
        </td>
        <td>
          <input type=password name="newpw1">
        </td>
      </tr>

      <tr>
        <td>
          Repeat New Password:
        </td>
        <td>
          <input type=password name="newpw2">
        </td>
      </tr>

      <tr>
        <td colspan=2>
          <center>
            <input type=submit name="changepw" value="Change Password">
          </center>
        </td>
      </tr>
   </table>
   </form>
   <br/>
   <h3>Change Username</h3>
   <p style="width:50%%">
   To change your username/email, please send a message to
   <a href="mailto:proposal-help@astro.illinois.edu">proposal-help@astro.illinois.edu</a>.
   Make sure to include both your old and your new username in this message.
   </p>
</center>
"""

submit_failed_error=r"""
<div class="browser_error">
  Submission failed!<br>
  Please go back and check your document for LaTeX errors. Your
  proposal has NOT been submitted. You may use the "View as PDF"
  option to view your proposal and any errors that were generated. You
  must complete the submit process again.<br>Click
  <a href="view/%s">here</a> to continue.
</div>
"""

submit_failed_size=r"""
<div class=browser_error>
  Submission Failed!<br><br>
  The size of the final PDF file is over the limit that the submission
  system can handle. The usual cause of this is using large bitmapped
  images in your proposal. One way of reducing this size is to reduce
  the resolution of your source image. If you still have a problem,
  please contact someone at proposal-help@astro.illinois.edu.  Click <a
  href="proposal/edit/%s">here</a> to continue.
</div>
"""

submit_success=r"""
<div class=submitted>
  Congratulations! You have submitted your proposal sucessfully!<br>

  To view your final proposal, click on the Proposals button above to
  return to the screen which lists your proposals, and click on the
  "view final pdf" link available there.<br><br>

  If you find a mistake in your proposal after you submit it, you may
  correct the errors by editing your proposal and re-submitting
  it.<br><br>

  Reminder: If you make corrections to your proposal and do not
  re-submit it, the changes will NOT be reflected in the final
  PDF. You can always view the final PDF by opening your proposals
  page and clicking on the "view final pdf" link.
</div>
"""

submit_verify=r"""<div class="maintenance" style="text-align : left; padding : 1em;">

  Follow these instructions to submit.<br><br>
    <li>
      Make sure you have proofread your proposal as directed above.
    </li>
    <li>
      By clicking the submit button below, your proposal will be
      assigned a proposal number and you will be given a final PDF
      with this number embedded in it.
    </li> 
    <li>
      Click the submit button once. Preparation of your proposal can
      take some time. Clicking it more than once may cause your
      proposal to be incorrectly processed.
    </li>
    <li>
      You can also access your submitted PDF from your main proposals
      page by clicking on "View Submitted Proposal."
    </li>
  </br>
                                                                               
  <form action="submit/%s" method=post>
    <center>
      <input type=submit name="sub_prop" value="Submit Proposal"/>
    </center>
  </form>

</div>
"""

tmpl_just=r"""\documentclass[preprint, letterpaper, 12pt]{aastex}
\usepackage[table,rgb]{xcolor}
\usepackage[letterpaper]{geometry}
\usepackage{helvet}
\usepackage{tabularx}
\pagestyle{empty}
\geometry{left=0.75in, right=0.75in, top=0.75in, bottom=0.75in}
\begin{document}
\newlength{\carmaindent}
\setlength{\carmaindent}{\parindent}
\setlength{\parskip}{0in}
\newlength{\sectitlelength}
\newcommand{\sectitlel}[1]{
  \setlength{\sectitlelength}{\parindent}
  \setlength{\parindent}{0in}
  \vskip 0.15in
  \begin{tabularx}{\textwidth}{@{}l@{}}
    \hiderowcolors
    {\sffamily \Large \textbf{#1} \normalfont} \\
    \hline
    \showrowcolors
  \end{tabularx}
  \setlength{\parindent}{\sectitlelength}
  \vskip -0.3cm
}

\sectitlel{Scientific Justification}

%s

\sectitlel{Techical Justification}

%s

\end{document}
"""

tmpl_nojust=r"""\documentclass[preprint, letterpaper, 12pt]{aastex}
\usepackage[table,rgb]{xcolor}
\usepackage[letterpaper]{geometry}
\usepackage{helvet}
\usepackage{tabularx}
\pagestyle{empty}
\geometry{left=0.75in, right=0.75in, top=0.75in, bottom=0.75in}
\begin{document}
\newlength{\carmaindent}
\setlength{\carmaindent}{\parindent}
\setlength{\parskip}{0in}
\newlength{\sectitlelength}
\newcommand{\sectitlel}[1]{
  \setlength{\sectitlelength}{\parindent}
  \setlength{\parindent}{0in}
  \vskip 0.15in
  \begin{tabularx}{\textwidth}{@{}l@{}}
    \hiderowcolors
    {\sffamily \Large \textbf{#1} \normalfont} \\
    \hline
    \showrowcolors
  \end{tabularx}
  \setlength{\parindent}{\sectitlelength}
  \vskip -0.3cm
}

You have not attached your \LaTeX\ justification. Please upload using the proposal 
website.

\end{document}
"""

