#revision module: question, answers, etc.
import logging
from datetime import date

from base import BaseHandler,users
from models import *

class RevisionHandler(BaseHandler):
    def get(self,mode=None):
        user = QAUser.gql('WHERE user = :1',users.get_current_user()).get()
        revs= Revision.gql('WHERE user = :1',user.key())
        class_list = LectClass.gql('WHERE lecturer=:1',user)
        self.render("revision.html",revs = revs,class_list=class_list)
    
    def post(self):
        user = QAUser.gql('WHERE user = :1',users.get_current_user()).get().key()
        title = self.request.get('title')
        lect_class = self.request.get('lect_class')
        description = self.request.get('description')
        
        if title != '': #add better validation later
            rev = Revision()
            rev.user = user
            rev.title = title
            rev.lect_class = lect_class
            rev.description = description
            
            rev_key = rev.put()
            
            self.redirect('/revision/questions/%s'%rev_key)
        else:
            self.redirect(self.request.url)

class LectClassHandler(BaseHandler):
    def get(self,mode=None):
        user = self.get_user()
        if not hasattr(user['user'], "name"):
            self.redirect('/home')
        course_list = Course.all().fetch(100)
        qa_user = QAUser.gql('WHERE user=:1',user['username']).get()
        class_list = LectClass.gql('WHERE lecturer=:1',qa_user)
        self.render("lect_class.html",course_list=course_list,class_list=class_list)
        
    def post(self):
        name = self.request.get('name')
        description = self.request.get('description')
        lecturer = QAUser.gql('WHERE user = :1',users.get_current_user()).get().key()
        course = Course.get(self.request.get('course'))
        date_from = self.request.get('date_from').split('-')
        date_to = self.request.get('date_to').split('-')
        
        #validate
        if name and description and date_from and date_to:
            lect_class = LectClass()
            lect_class.name = name
            lect_class.description = description
            lect_class.lecturer = lecturer
            lect_class.course = course
            lect_class.date_from = date(int(date_from[2]),int(date_from[1]),int(date_from[0])) #yyyy-mm-ddd
            lect_class.date_to = date(int(date_to[2]),int(date_to[1]),int(date_to[0]))
            lect_class_key = lect_class.put()
            #ajax response
            data = "<li><a href='/class/page/"+lect_class_key.__str__()+"'>"+name+" / "+course.course+"</a>"
            self.write(data)

class LectClassPublicHandler(BaseHandler):
    def get(self,class_key):
        lect_class = LectClass.get(class_key)
        student_list = ClassStudent.gql('WHERE lect_class=:1',lect_class).fetch(500)
        student_count = len(student_list)
        rev_list = Revision.gql('WHERE lect_class=:1',lect_class.key().__str__()).fetch(500)
        user = self.get_user()
        student = user['user']
        check_duplicate = ClassStudent.gql('WHERE lect_class=:1 AND student=:2',lect_class,student).fetch(1)
        if len(check_duplicate)>0:
            joined = True
        else:
            joined = False
        self.render("lect_class_public.html",lect_class=lect_class,student_list=student_list,joined=joined,student_count=student_count,rev_list=rev_list)

class AddCourse(BaseHandler):
    def post(self):
        user = self.get_user()
        course_key = self.request.get('course')
        logging.info(course_key)
        if hasattr(user['user'], "name"): #not very necessary
            course = Course.get(course_key)
            user_course = UserCourse()
            q = UserCourse.gql('WHERE course=:1 AND user=:2',course,user['user']).fetch(1)
            if len(q)==0:
                user_course.course = course
                user_course.user = user['user']
                user_course_key = user_course.put()
                self.write(course.course+"|"+user_course_key.__str__())


class DeleteCourse(BaseHandler):
    def post(self):
        user_course_key = self.request.get('user_course_key')
        user_course = UserCourse.get(user_course_key)
        user_course.delete()
        return
        
class QuestionHandler(BaseHandler):
    def get(self,rev_key):
        #rev = Revision.get(rev_key)
        rev = db.get(rev_key)
        qs = Question.gql('WHERE revision = :1',rev)
        class_key = rev.lect_class
        lect_class = LectClass.get(class_key)
        self.render("questions.html",rev=rev,rev_key=rev_key,qs=qs,lect_class=lect_class)
    
    def post(self,rev_key):
        revision = Revision.get(rev_key)
        question = self.request.get('question')
        
        if question != '': #add better validation later
            qs = Question()
            qs.revision = revision
            qs.question = question
            qkey = qs.put()
            
            self.redirect('/revision/questions/ans/%s'%qkey)
        else:
            self.redirect(self.request.url)
        
class AnswerHandler(BaseHandler):
    def get(self,q_key):
        #rev = Revision.get(rev_key)
        question = db.get(q_key)
        revision = question.revision
        answers = Answer.gql('WHERE question = :1',question)
        self.render("answers.html",q=question,rev=revision,ans=answers)
    
    def post(self,q_key):
        question = Question.get(q_key)
        answer = self.request.get('answer')
        if self.request.get('correct'):
            correct = True
        else:
            correct = False
        
        if answer != '': #add more validation later
            ans = Answer()
            ans.question = question
            ans.answer = answer
            ans.correct = correct
            
            ans.put()
        
        self.redirect('/revision/questions/ans/%s'%q_key)

class DeleteAnswer(BaseHandler):
    #ajaxed class
    def post(self,ans_key):
        answer = Answer.get(ans_key)
        answer.delete()

class DeleteQuestion(BaseHandler):
    #ajaxed class
    def post(self,qs_key):
        question = Question.get(qs_key)
        question.delete()

class RevisionAttemptHandler(BaseHandler):
    #ajaxed class
    def post(self):
        rev_key = self.request.get('rev_key')
        if rev_key:
            rev = Revision.get(rev_key)
            user = self.get_user()
            student = user['user']
            attempt = RevisionAttempt()
            attempt.student = student
            attempt.revision = rev
            attempt.score = 0.0
            akey = attempt.put()
        
            self.write(akey.__str__())

class RevisionAttemptAnswerHandler(BaseHandler):
    #ajaxed class
    def post(self):
        q_key = self.request.get('q_key') #question key
        ans_key = self.request.get('ans_key') #answer key
        att_key = self.request.get('att_key') #attempt key
        q_count = int(self.request.get('q_count')) #number of questions
        if ans_key:
            question = Question.get(q_key)
            answer = Answer.get(ans_key)
            attempt = RevisionAttempt.get(att_key)
            #check if already answered Q
            check = RevisionAttemptAnswer.gql('WHERE question=:1 AND attempt=:2',question,attempt).fetch(1)
            if len(check)==0:
                attempt_ans = RevisionAttemptAnswer()
                attempt_ans.question = question
                attempt_ans.answer = answer
                attempt_ans.attempt = attempt
                attempt_ans.put()
                
                #check if answer is correct and update score
                score = 0.0
                if answer.correct == True:
                    score = attempt.score + ((1.0/q_count) * 100)
                    attempt.score = score
                    attempt.put()
                    
                self.write(score)