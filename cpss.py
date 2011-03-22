from mod_python import apache
from mod_python import Session
from mod_python import util
import os

Page = apache.import_module("page")
Connector = apache.import_module("connector")
Backend = apache.import_module("backend")
Template = apache.import_module("Template/__init__")

config = { 'html_base' : "http://localhost/proposals/",
           'base_directory' : '/var/www/proposals/',
           'files_directory' : 'files/',
           'data_directory' : '/home/carmaweb/cpss-data/',
           'sendemail' : True,
           'debug' : True,
           'db' : { 'host' : "",
                    'user' : "",
                    'passwd' : "",
                    'db' : "",
                    'unix_socket' : '/var/run/mysqld/mysqld.sock',
                    },
           }

def handler(req):
    os.umask(2)

    #Figure out which page is requested.
    pathstr = []
    for item in req.path_info.split('/'):
        if item != '':
            pathstr.append(item)

    #begin session and read information 6 hour timeout
    session = Session.Session(req, timeout=21600)
    if session.is_new():
        session['authenticated'] = False
        session['activated'] = 0
        session['admin'] = False
        session['maint_mode'] = 0
        session['maint_allow'] = False
    session.save()
        
    theBackend = Backend.Backend(req, config)
    options = theBackend.options_get()
    thePage = Page.Page(req, config, session, options)
    theConnector = Connector.Connector(req, Template, theBackend, thePage,
                                       session, config, options)

    if (config['debug'] == False):
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
            result = theConnector.Dispatch(pathstr)
        finally:
            theBackend.close()
    return result
