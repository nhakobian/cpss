from mod_python import apache
from mod_python import Session
from mod_python import util
import os

def handler(req):
    Debug = False #comment out the next line for normal processing
    #Debug = True

    os.umask(2)

    config = { 'html_base' : "http://carma-prop.astro.illinois.edu/proposals/",
               'base_directory' : '/srv/www/htdocs/proposals/',
               'files_directory' : 'files/',
               'data_directory' : '/home/nick/cpss/cpss-data/',
               'sendemail' : True}
    
    Page = apache.import_module("page")
    Connector = apache.import_module("connector")
    Backend = apache.import_module("backend")
    Template = apache.import_module("Template/__init__")

    #Figure out which page is requested.
    pathstr = req.path_info.split('/')
    temp = []
    for a in pathstr:
        if a != '':
            temp.append(a)
    pathstr = temp

    #begin session and read information 6 hour timeout
    session = Session.Session(req, timeout=21600)
    if session.is_new():
        session['authenticated'] = False
        session['activated'] = 0
        session['admin'] = False
        session['maint_mode'] = 0
        session['maint_allow'] = False
    session.save()
        
    theBackend = Backend.Backend(req, Template, config)
    options = theBackend.options_get()
    thePage = Page.Page(req, config, session, options)
    theConnector = Connector.Connector(req, Template, theBackend, thePage,
                                       session, config, options)

    if (Debug == False):
        try:
            result = theConnector.Dispatch(pathstr)
        except:
            theConnector.do_header()
            req.write("""<center>An internal error has occured. If it persists
            please contact the person in charge of this site.
            </center>""")
            result = apache.OK
            theBackend.close()
    else:
        try:
#            fields = util.FieldStorage(req)
#            file = open('/srv/www/htdocs/proposals/files/url.txt', 'a')
#            file.write(str(pathstr) + str(fields) + '\n\n\n')
#            file.close()
            result = theConnector.Dispatch(pathstr)
        finally:
            theBackend.close()
    return result
