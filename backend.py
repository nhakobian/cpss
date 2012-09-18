import MySQLdb
import hashlib
import string
import operator
import os.path
import os
import gzip
from random import choice
from mod_python import apache
cpss = apache.import_module("cpss")

class Backend:
    def __init__(self):
        self.Database = MySQLdb.connect(
            host        = cpss.config['db']['host'], 
            user        = cpss.config['db']['user'],
            passwd      = cpss.config['db']['passwd'],
            db          = cpss.config['db']['db'],
            unix_socket = cpss.config['db']['unix_socket'])
        self.literal = self.Database.literal
        self.options = self.options_get()
        self.path_justification = (cpss.config['data_directory'] + 
                                   'justifications/')
        self.path_pdf = cpss.config['data_directory'] + 'pdf/'
        self.path_images = cpss.config['data_directory'] + 'images/'


    def verify_user(self, username, password):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        response = cursor.execute("""SELECT * 
                                     FROM `users`
                                     WHERE `email`=%(username)s 
                                     LIMIT 1"""
                                  % {'username': self.literal(username)})
        result = cursor.fetchall()
        if (len(result) == 0):
            return (False, 0)
        user = result[0]
        md5_pass = hashlib.md5(password).hexdigest()
        cursor.close()
        if((user['email'] == username) and (user['password'] == md5_pass)):
            return (True, user)
        return (False, 0)


    def get_user(self, username):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        response = cursor.execute("""SELECT * 
                                     FROM `users`
                                     WHERE `email`=%(username)s 
                                     LIMIT 1"""
                                  % {'username': self.literal(username)})
        result = cursor.fetchone()
        return result

    def test_userflag(self, username, flag):
        result = self.get_user(username)

        # list of userflags:
        # 1 : STATS - Can see stats page of calls.
        flags = {
            'STATS' : 1,
            }
        if flag in flags.keys():
            if (result['flags'] & flags[flag]) == flags[flag]:
                return True
            else:
                return False
        else:
            return False


    def user_exists(self, username):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        response = cursor.execute("""SELECT * 
                                     FROM `users`
                                     WHERE `email`=%(username)s 
                                     LIMIT 1""" %
                                  {'username' : self.literal(username)})
        result = cursor.fetchall()
        cursor.close()
        if (len(result) == 1):
            return True
        return False

    def add_user(self, name, email, password, code):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        response = cursor.execute("""INSERT INTO `users` 
                                     SET `name`=%(name)s, `email`=%(email)s,
                                         `password`=MD5(%(password)s),
                                         `activated`=%(code)s""" %
                                  {'name'     : self.literal(name),
                                   'email'    : self.literal(email),
                                   'password' : self.literal(password),
                                   'code'     : self.literal(code)})
        cursor.close()

    def password_change(self, email, newpassword):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        response = cursor.execute("""UPDATE `users` 
                                     SET `password`=MD5(%(code)s) 
                                     WHERE `email`=%(email)s""" %
                                  {'code'   : self.literal(newpassword),
                                   'email'  : self.literal(email)})
        cursor.close()
        
    def update_code(self, user, code):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        response = cursor.execute("""UPDATE `users` 
                                     SET `activated`=%(code)s 
                                     WHERE `email`=%(email)s""" %
                                  {'code'   : self.literal(code),
                                   'email'  : self.literal(user)})
        cursor.close()

    def cycles(self):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        ret = cursor.execute("""SELECT `cyclename`, `final_date`, `proposal`
                                FROM `cycles`
                                ORDER BY `final_date` DESC""")
        result = cursor.fetchall()
        cursor.close()
        return result

    def proposal_list_by_cycle(self, cyclename):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        ret = cursor.execute("""SELECT *
                                FROM `proposals`, `users`
                                WHERE `proposals`.`cyclename`=%(cyclename)s 
                                      AND `proposals`.`user`=`users`.`email`
                                ORDER BY `proposals`.`status` DESC,
                                      `proposals`.`carmaid` DESC""" %
                             {'cyclename' : self.literal(cyclename)})
        result = cursor.fetchall()
        cursor.close()
        return result

    def proposal_get_propinfo(self, proposalid, tablename):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        # Table name isnt passed through the literal function since it isn't
        # data that is ingested (possible security risk). The risk is low
        # since all other data is 'literalized', and the source for the 
        # information passed to the tablename variable is in the database
        # itself and cannot be changed except for direct editing of the
        # table.
        response = cursor.execute("""SELECT *
                                     FROM `%(tablename)s` as `propinfo`
                                     WHERE `propinfo`.`proposalid`=%(propid)s
                                     LIMIT 1""" % 
                                  {'tablename' : tablename,
                                   'propid' : self.literal(proposalid)})
        result = cursor.fetchone()
        cursor.close()
        return result

    def proposal_list(self, user):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        response = cursor.execute(
            """SELECT * FROM `proposals`, `cycles`
               WHERE `proposals`.`user`=%(user)s 
                     AND `cycles`.`cyclename`=`proposals`.`cyclename`
               ORDER BY `final_date` DESC, 
                        `proposals`.`carmaid` DESC, 
                        `proposals`.`proposalid`""" %
            {'user'   : self.literal(user)})
        result = cursor.fetchall()
        list=[]
        for proposal in result:
            cursor.execute("""SELECT * 
                              FROM `%(table)s` 
                              WHERE proposalid=%(propid)s""" %
                          {'table'  : proposal['proposal'],
                           'propid' : self.literal(proposal['proposalid'])})
            res = cursor.fetchone()
            proposal['title'] = res['title']
            proposal['date'] = res['date']
            list.append(proposal)

        cursor.close()
        list.sort(key=operator.itemgetter('date'), reverse=True)
        return list

    def proposal_fetch(self, user, proposalid):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("""SELECT * 
                          FROM `proposals`, `cycles`
                          WHERE `proposalid`=%(propid)s 
                                AND `proposals`.`cyclename`=
                                    `cycles`.`cyclename`""" %
                       {'propid' : self.literal(proposalid)})
        res = cursor.fetchone()
        cursor.close()
        if user == 'admin':
            return res
        if (res == None):
            return False
        if (res['user'] != user):
            return False
        return res

    def proposal_status(self, propid):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("""SELECT `status` 
                          FROM `proposals`
                          WHERE `proposalid`=%(propid)s 
                          LIMIT 1""" %
                       {'propid' : self.literal(propid)})
        ret = cursor.fetchone()
        cursor.close()
        return ret

    def proposal_get(self, tables, cyclename, proposalid, subid=False):
        result = {}
        table_list = tables.keys()
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        for key in table_list:
            if (tables[key]['type'] == 'single'):
                cursor.execute("""SELECT * 
                                  FROM `%(cyclename)s`
                                  WHERE `proposalid`=%(propid)s 
`                                 LIMIT 1""" %
                               {'cyclename' : self.options[key],
                                'propid'    : self.literal(proposalid)})
                temp = cursor.fetchall()

                result[key] = temp
            if (tables[key]['type'] == 'repeat'):
                cursor.execute("""SELECT * 
                                  FROM `%(cyclename)s`
                                  WHERE `proposalid`=%(propid)s
                                  ORDER BY `numb`""" %
                               {'cyclename' : self.options[key],
                                'propid'    : self.literal(proposalid)})
                temp = cursor.fetchall()

                result[key] = temp
        cursor.close()
        return result

    def proposal_tagset(self, table, propid, tags, id=False):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        tagtext = ""
        wheretext = ""
        for tag in tags:
            if (tag['fieldname'] == 'numb'):
                continue
            elif (tag['fieldname'] == 'date'):
                tagtext += """`%s`=CURDATE(), """ % (tag['fieldname'])
            elif (tag['data'] == None):
                tagtext += """`%s`=NULL, """ % (tag['fieldname'])
            elif (tag['fieldtype'] == 'array'):
                tagtext = "`%s`='" % (tag['fieldname'])
                for array in tag['data']:
                    tagtext += array + ","
                tagtext = tagtext[:-1]
                tagtext += "',"

            else:
                tagtext += """`%s`=%s, """ % (tag['fieldname'],
                                              self.literal(tag['data']))
        tagtext = tagtext[:-2]

        if (id == False):
            wheretext = """`proposalid`=%s""" % self.literal(propid)
        else:
            wheretext = ("""`proposalid`=%s AND `numb`=%s""" %
                         (self.literal(propid), self.literal(id)))
        text = ("""UPDATE `%(table)s` 
                   SET %(tag)s 
                   WHERE %(where)s""" %
                {'table'  : self.options[table],
                 'tag'    : tagtext,
                 'where'  : wheretext}) 
        
        cursor.execute(text)
        cursor.close()
    
    def proposal_table_addrow(self, table, propid, numb=False):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        if (numb != False):
            cursor.execute("""SELECT * 
                              FROM `%(table)s`
                              WHERE `proposalid`=%(propid)s
                              ORDER BY `numb` DESC""" %
                           {'table'  : self.options[table],
                            'propid' : self.literal(propid)})
            res = cursor.fetchone()
            numbtext = ", `numb`=%s" % self.literal((res['numb'] + 1))
        else:
            numbtext = ""
            res = {'numb' : -1}
            
        cursor.execute("""INSERT INTO `%(table)s`
                          SET `proposalid`=%(propid)s %(numbtext)s""" %
                       {'table'    : self.options[table],
                        'propid'   : self.literal(propid),
                        'numbtext' : numbtext})
        cursor.close()
        return str(res['numb'] + 1)

    def proposal_table_delrow(self, table, propid, numb=False):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        if (numb != False):
            numbtext = "AND `numb`=%s" % (self.literal(numb))
            cursor.execute("""SELECT `numb` 
                              FROM `%(table)s`
                              WHERE `proposalid`=%(propid)s
                              ORDER BY `numb`""" %
                           {'table'  : self.options[table],
                            'propid' : self.literal(propid)})
            res = cursor.fetchall()
            if (len(res) == 1):
                cursor.close()
                return False
        else:
            numbtext = ""
            
        cursor.execute("""DELETE FROM `%(table)s`
                          WHERE `proposalid`=%(prop)s %(numbtext)s
                          LIMIT 1""" %
                       {'table'    : self.options[table],
                        'prop'     : self.literal(propid),
                        'numbtext' : numbtext})

        if (numb != False):
            new_numb = 1
            for line in res:
                if (str(line['numb']) == str(numb)):
                    continue
                elif (line['numb'] == new_numb):
                    new_numb += 1
                    continue
                else:
                    cursor.execute("""UPDATE `%(table)s`
                                      SET `numb`=%(new_numb)s 
                                      WHERE `proposalid`=%(propid)s 
                                            AND `numb`=%(linenumb)s 
                                      LIMIT 1""" %
                                   {'table'    : self.options[table],
                                    'new_numb' : self.literal(new_numb),
                                    'propid'   : self.literal(propid),
                                    'linenumb' : self.literal(line['numb'])})
                    new_numb += 1
        cursor.close()
        return True

    def options_get(self):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("""SELECT * FROM `options`""")
        res = cursor.fetchall()
        cursor.close()

        options = {}
        for option in res:
            options[option['key']] = option['value']

        return options

    def set_next_propno(self, nextpropno, cyclename):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("""UPDATE `options` 
                          SET `next_propno`=%(propno)s
                          WHERE `cyclename`=%(cyclename)s""" %
                       {'propno'    : self.literal(nextpropno),
                        'cyclename' : self.literal(cyclename)})
        cursor.close()

    def proposal_setcarmaid(self, proposalid, carmaid):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("""UPDATE `proposals` 
                          SET `carmaid`=%(carmaid)s
                          WHERE `proposalid`=%(propid)s """ %
                       {'carmaid' : self.literal(carmaid),
                        'propid'  : self.literal(proposalid)})
        cursor.close()

    def proposal_submit(self, proposalid):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("""UPDATE `proposals` 
                          SET `status`=%(status)s
                          WHERE `proposalid`=%(propid)s""" %
                       {'status' : self.literal(str(1)),
                        'propid' : self.literal(proposalid)})
        cursor.close()

    def pw_generate(self, proposalid):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        #Generate the random password
        size=8
        password = ''.join([choice(string.letters + string.digits + "!" + 
                                   "@" + "_") for i in range(size)])
        cursor.execute("""UPDATE `proposals` 
                          SET `carmapw`=%(pw)s
                          WHERE `proposalid`=%(propid)s""" %
                       {'pw'     : self.literal(password),
                        'propid' : self.literal(proposalid)})        
        cursor.close()

    def proposal_add(self, user, tables, cyclename):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("""INSERT INTO `proposals` 
                          SET `user`=%(user)s, `cyclename`=%(cyclename)s, 
                              `status`='none'""" %
                       {'user'      : self.literal(user),
                        'cyclename' : self.literal(cyclename)})
        cursor.execute("""SELECT `proposalid` 
                          FROM `proposals` 
                          WHERE `user`=%(user)s 
                          ORDER BY `proposalid` DESC""" %
                       {'user'   : self.literal(user)})
        proposalid = cursor.fetchone()['proposalid']

        for table in tables.keys():
            self.proposal_table_addrow(table, proposalid)

        cursor.close()
        return proposalid

    def proposal_delete(self, user, proposalid, tables, cyclename):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        the_tables = tables.keys()
        # Delete each row in the proposal tables corresponding to this
        # proposal.
        for table_name in tables.keys():
            cursor.execute("""DELETE FROM `%(table)s`
                              WHERE `proposalid`=%(propid)s""" %
                           {'table'  : self.options[table_name],
                            'propid' : self.literal(proposalid)})
        # Delete the proposal entry itself.
        cursor.execute("""DELETE FROM `proposals`
                          WHERE `proposalid`=%(propid)s""" %
                       {'propid' : self.literal(proposalid)})
        # Delete images
        result = self.images_list(proposalid)
        for res in result:
            self.images_delete(proposalid, res['numb'])
        cursor.close()
        # Justification delete
        self.justification_delete_data(proposalid)

    def close(self):
        self.Database.close()

    def images_list(self, proposalid, numb=False):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        if (numb == False):
            numb_text = ""
        else:
            numb_text = " AND `numb`=%s" % self.literal(numb)

        cursor.execute("""SELECT * 
                          FROM `images`
                          WHERE `proposalid`=%(propid)s%(numb)s
                          ORDER BY `numb`""" %
                       {'prefix' : self.prefix,
                        'propid' : self.literal(proposalid),
                        'numb'   : numb_text})
        result = cursor.fetchall()
        cursor.close()
        return result

    def images_get(self, proposalid, numb=False):
        result = self.images_list(proposalid, numb)
        # Pull out the raw data from files and merge into the result structure.
        # Using number offsets since we are adjusting the original structure 
        # instead of returning modified data.
        for i in xrange(0, len(result)):
            if os.path.isfile(self.path_images + str(result[i]['proposalid']) +
                              '.' + str(result[i]['numb']) + '.gz') == True:
                im = gzip.open(self.path_images + str(result[i]['proposalid'])
                               + '.' + str(result[i]['numb']) + '.gz', 'rb')
                result[i]['ps_data'] = im.read()
                im.close()
        return result

    def images_add(self, proposalid):
        result = self.images_list(proposalid)
        if (len(result) == 0):
            numb = 1
        else:
            numb = result[-1]['numb'] + 1
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("""INSERT INTO `images`
                          SET `proposalid`=%(propid)s, `numb`=%(numb)s""" %
                       {'propid' : self.literal(proposalid),
                        'numb'   : self.literal(str(numb))})
        cursor.close()
        return numb

    def images_update(self, proposalid, filename, numb, bin_data):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("""UPDATE `images` 
                          SET `file`=%(filename)s
                          WHERE `proposalid`=%(propid)s 
                                AND `numb`=%(numb)s""" %
                       {'filename' : self.literal(filename),
                        'propid'   : self.literal(proposalid),
                        'numb'     : self.literal(numb)})
        cursor.close()
        # File is now written after the tag is written to the database.
        im = gzip.open(self.path_images + str(proposalid) + '.' + str(numb) + 
                       '.gz', 'wb')
        im.write(bin_data)
        im.close()

    def images_delete(self, proposalid, numb):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("""DELETE FROM `images`
                          WHERE `proposalid`=%(propid)s 
                                AND `numb`=%(numb)s""" %
                       {'propid' : self.literal(proposalid),
                        'numb'   : self.literal(numb)})
        cursor.close()
        # File is deleted now that the tag is not in database anymore.
        if os.path.isfile(self.path_images + str(proposalid) + '.' + str(numb)
                          + '.gz') == True:
            os.unlink(self.path_images + str(proposalid) + '.' + str(numb) +
                      '.gz')

    def pdf_add_update(self, proposalid, pdfdata):
        pdf_file = open(self.path_pdf + str(proposalid) + '.pdf', 'wb')
        pdf_file.write(pdfdata)
        pdf_file.close()

    def pdf_get_data(self, proposalid):
        try:
            pdf_file = open(self.path_pdf + str(proposalid) + '.pdf', 'rb')
            pdf = pdf_file.read()
            pdf_file.close()
            return pdf
        except IOError:
            return ''

    def justification_add_update(self, proposalid, pdfdata):
        just_file = open(self.path_justification + str(proposalid) + ".pdf", 
                         'wb')
        just_file.write(pdfdata)
        just_file.close()

    def justification_get_data(self, proposalid):
        # Even though all justifications are now LaTeX files (.tex) they were 
        # originally uploaded pdf files.
        if (os.path.isfile(self.path_justification + str(proposalid) + ".pdf") 
            == True):
            just_file = open(self.path_justification + str(proposalid) + 
                             ".pdf", 'r')
            just = just_file.read()
            just_file.close()
            return just
        else:
            return None

    def justification_delete_data(self, proposalid):
        if (os.path.isfile(self.path_justification + str(proposalid) + ".pdf")
            == True):
            return os.unlink(self.path_justification + str(proposalid) + 
                             ".pdf")
        else:
            return None        

    def justification_type_set(self, proposalid, type):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("""UPDATE `proposals`
                          SET `pdf_justification`=%(type)s
                          WHERE `proposalid`=%(propid)s""" %
                       {'type'   : self.literal(type),
                        'propid' : self.literal(proposalid)})
        cursor.close()

    def justification_type_latex(self, proposalid):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("""SELECT `pdf_justification` 
                          FROM `proposals`
                          WHERE `proposalid`=%(propid)s""" %
                       {'propid' : self.literal(proposalid)})
        result = cursor.fetchone()
        cursor.close()

        if result['pdf_justification'] == 1 :
            return True
        else:
            return False

    def is_key_project(self, proposalid):
        cursor = self.Database.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("""SELECT * 
                          FROM `proposals`, `cycles`
                          WHERE `proposals`.`cyclename`=`cycles`.`cyclename`
                                AND `proposals`.`proposalid`=%(propid)s 
                          LIMIT 1""" %
                       {'propid' : self.literal(proposalid)})
        result = cursor.fetchone()
        proptable = result['proposal']

        cursor.execute("""SELECT * 
                          FROM `%(proptable)s` 
                          WHERE `proposalid`=%(propid)s 
                          LIMIT 1""" %
                       {'proptable' : proptable,
                        'propid' : self.literal(proposalid)})

        result = cursor.fetchone()
        cursor.close()
        if result.__contains__('key_project') == True:
            if result['key_project'] == 1 :
                return True
            else:
                return False
        else:
            return False
