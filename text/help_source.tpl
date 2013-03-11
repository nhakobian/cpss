
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
</div>