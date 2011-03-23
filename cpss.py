from mod_python import apache
from mod_python import Session
from mod_python import util
import os

_backend = apache.import_module("backend")
db = None
text = apache.import_module("text")

Page = apache.import_module("page")
Connector = apache.import_module("connector")
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

options = None # This will be filled with the SQL options.
session = None
req = None

def w(string):
    if req != None:
        req.write(string)
    return

def handler(request):
    os.umask(2)

    global req
    req = request

    #Figure out which page is requested.
    pathstr = []
    for item in req.path_info.split('/'):
        if item != '':
            pathstr.append(item)

    #begin session and read information 6 hour timeout
    global session
    session = Session.Session(req, timeout=21600)
    if session.is_new():
        session['authenticated'] = False
        session['activated'] = 0
        session['admin'] = False
        session['maint_mode'] = 0
        session['maint_allow'] = False
    session.save()
        
    # Initialize database and connect. ##TODO: Add error checking.
    global db
    db = _backend.Backend()

    global options
    options = db.options_get()
    thePage = Page.Page()
    theConnector = Connector.Connector(thePage)

    if (config['debug'] == False):
        try:
            result = theConnector.Dispatch(pathstr)
        except:
            theConnector.do_header()
            req.write("""<center>An internal error has occured. If it persists
            please contact the person in charge of this site.
            </center>""")
            result = apache.OK
            db.close()
    else:
        try:
            result = theConnector.Dispatch(pathstr)
        finally:
            db.close()
    return result
