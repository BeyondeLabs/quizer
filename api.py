import logging
import md5

#from base import BaseHandler
from models import SLConnect,UserContactLogs,Revision
from explore import get_rev_set_raw

from google.appengine.api import users
from google.appengine.ext import db


def getstudents(for_,email,token,added):
    '''for_ e.g. lec, or all or res (response)
    email, the one requesting access
    token, md5(email + salt)'''
    
    if for_=='lec':
        #find out if request is valid, later use raise exceptions
        m = email+"nrw";
        logging.info("TOKEN-M: "+m)
        token2 = md5.md5(m).hexdigest()
        #test = md5.md5("admin@test.quizer.info"+"nrw")
        #logging.info("TEST TOKEN: "+test.__str__())
        logging.info("TOKEN: "+token2.__str__())
        if token2.__str__() != '': # == token, will come to it later (unicode issues)
            #presumed valid request
            if for_=='lec':
                user = users.User(email)
                q = db.GqlQuery('SELECT * FROM QAUser WHERE user = :1',user).fetch(1)
                logging.info(q)
                if q:
                    logging.info(q[0].key().__str__())
                    students = SLConnect.gql('where lecturer=:1',q[0].key().__str__()).fetch(50) #first 50 students
                    logging.info(students)
                    
                    results = []
                    if students:
                        for student in students:
                            stu = {
                                    'name': student.student.name,
                                    'email': student.student.email,
                                    'courses': student.student.courses,
                                    'key':student.student.key().__str__()
                                    }
                            results.append(stu)
                    return results
                else:
                    #user not available
                    return ['nothing']
        else:
            #invalid request
            logging.info("False")
            return False

    if for_ == 'res':
        #response sent back by GAS
        user = users.User(email)
        q = db.GqlQuery('SELECT * FROM QAUser WHERE user = :1',user).fetch(1)
        if q:
            contacts_log = UserContactLogs()
            contacts_log.user = q[0].key()
            contacts_log.num_added = added
            contacts_log.put()
            
        return
    
    if for_ == 'stu':
        #email == lecturer's key (instead of email)
        #token user email + salt
        lec_key = email
        students = SLConnect.gql('where lecturer=:1',lec_key).fetch(50) #first 50 students
        results = []
        if students:
            for student in students:
                stu = {
                        'name': student.student.name,
                        'email': student.student.email,
                        'courses': student.student.courses,
                        'key':student.student.key().__str__()
                        }
                results.append(stu)
            return results
        return ["nothing"]

def getrevisionset(rev_key='',email=''):
    #test revision
    logging.info("Function getrev... called")
    rev = Revision.get(rev_key)
    if rev:
        rev_set = get_rev_set_raw(rev)
        logging.info(rev_set)
        return rev_set
    else:
        return ["nothing"]
    