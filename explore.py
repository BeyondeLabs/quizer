import logging

from base import BaseHandler
from models import Revision,Question,Answer,QAUser, UserContactLogs,\
    QuestionComment, LectClass, UserCourse, RevisionAttempt

#general functions
def get_all_classes():
    #there should be another version that gets only relevant classes to the user
    class_list = LectClass.all().fetch(50) #should be paginated
    return class_list

#get 'related' classes / based on users course
def get_rel_classes(user):
    user_course = UserCourse.gql('WHERE user=:1',user)
    class_list = []
    for course in user_course:
        class_list += LectClass.gql('WHERE course=:1',course.course)
    return class_list
    
def get_lect_revs(user):
    revs = Revision.gql('WHERE user=:1',user).fetch(50)
    return revs

def get_all_revs():
    #top 50 revisions, to be fine-tuned according to users course, university, etc
    #also gives some stats, etc e.g. 23 qs, 500 attempts,etc
    revs = Revision.all().fetch(50)
    return revs

def get_rev_set(rev):
    questions = Question.gql('WHERE revision = :1',rev).fetch(100) #how do we fetch all the Qs?
    qs = []
    for q in questions:
        answers = Answer.gql('WHERE question=:1',q)
        comments = QuestionComment.gql('WHERE question=:1',q)
        comments_ = []
        for c in comments:
            c_ = {
                  'comment':c.comment,
                  'ckey':c.key().__str__(),
                  'user':QAUser.get(c.ukey)
                  }
            comments_.append(c_)

        question = {
                    'question':q,
                    'qkey':q.key().__str__(),
                    'answers':answers,
                    'comments':comments_,
                    'comment_count':comments.count()
                    }
        qs.append(question)
    return qs

def get_rev_set_raw(rev):
    qs = []
    #first object to be the description of the revision
    lect_class = LectClass.get(rev.lect_class)
    rev_desc = {
                'lecturer':rev.user.name,
                'institution':rev.user.institution,
                'title':rev.title,
                'class':lect_class.name,
                'description':rev.description,
                'created':rev.created.strftime("%B %d, %Y")
                }
    qs.append(rev_desc)
    questions = Question.gql('WHERE revision = :1',rev).fetch(100) #how do we fetch all the Qs?
    for q in questions:
        answers = Answer.gql('WHERE question=:1',q)
        ans = []
        for a in answers:
            ans.append(a.answer)
        question = {
                    'question':q.question.replace("\n","").replace("\r",""),
                    'answers':ans
                    }
        qs.append(question)
    return qs

def getcontactslog(user_key):
    user = QAUser.get(user_key)
    clog = UserContactLogs.gql('WHERE user = :1 ORDER BY date_added DESC',user).fetch(1)
    logging.info(clog)
    if len(clog)>0:
        return clog[0]
    return
    
class ExploreHome(BaseHandler):
    def get(self):
        user = self.get_user()
        class_list = get_rel_classes(user['user'])
#        class_list  = get_all_classes()
        self.render("explore-home.html",class_list=class_list)

class ExploreRevision(BaseHandler):
    def get(self,rev_key):
        rev = Revision.get(rev_key)
        class_key = rev.lect_class
        lect_class = LectClass.get(class_key)
        qs = get_rev_set(rev)
        q_count = len(qs)
        #see if student had attempted test before
        user = self.get_user()
        student = user['user']
        attempt = RevisionAttempt.gql('WHERE student=:1 AND revision=:2 ORDER BY created DESC',student,rev).fetch(1)
        class_hidden1 = ""
        class_hidden2=""
        score = ""
        started = ""
        akey = ""
        if len(attempt)>0:
            class_hidden1 = "js-hidden"
            score = attempt[0].score
            started = attempt[0].created
            akey = attempt[0].key()
        else:
            class_hidden2 = "js-hidden"
        extra = {
                 'class_hidden1':class_hidden1,
                 'class_hidden2':class_hidden2,
                 'score':score,
                 'started':started,
                 'akey':akey
                 }
        self.render("explore-revision.html",rev=rev,qs=qs,lect_class=lect_class,extra = extra,q_count=q_count)

class ExploreLecturer(BaseHandler):
    '''Display lecturer's profile'''
    def get(self,user_key):
        user = QAUser.get(user_key)
        if user.type != "Lecturer":
            self.redirect('/explore/student/%s'%user_key)
        
        course_list = UserCourse.gql('WHERE user=:1',user)
        #get revision sets by the lecturer
        # revs = get_lect_revs(user)
#        students = SLConnect.gql('where lecturer=:1',user_key).fetch(100) #first 100 students
        #user_key now is for the person logged in
#        sess_user = self.get_user()
#        logging.info(sess_user)
#        user_key = sess_user['user'].key()
#        contacts_log = getcontactslog(user_key)
        class_list = LectClass.gql('WHERE lecturer=:1',user)
        self.render("explore-lecturer.html",lect=user,class_list=class_list,course_list=course_list)

class ExploreStudent(BaseHandler):
    '''Display student's profile'''
    def get(self,user_key):
        #try/catch non-available key first!
        user = QAUser.get(user_key)
        if user.type != "Student":
            self.redirect('/explore/lecturer/%s'%user_key)
        
        self.render("explore-student.html",stu=user)

class ExploreQuestionComment(BaseHandler):
    def post(self):
        qkey = self.request.get('qkey')
        ukey = self.request.get('ukey')
        comment = self.request.get('comment')
        rev_key = self.request.get('rev_key')
        
        if comment != '':
            question = Question.get(qkey)
            q_comment = QuestionComment()
            q_comment.comment = comment
            q_comment.question = question
            q_comment.ukey = ukey
            q_comment.put()
        
        self.redirect("/explore/revision/%s"%rev_key)
