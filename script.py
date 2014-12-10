import logging
import json

from google.appengine.api.urlfetch import fetch

from base import webapp2
from revision import RevisionHandler,QuestionHandler,AnswerHandler,DeleteAnswer,DeleteQuestion,\
    LectClassHandler, LectClassPublicHandler, AddCourse, DeleteCourse,\
    RevisionAttemptHandler, RevisionAttemptAnswerHandler
from profile import Profile,SignUp, JoinLecturer, JoinClass, MyCourses
from base import BaseHandler
from explore import ExploreHome, ExploreRevision, ExploreLecturer,\
    ExploreStudent, ExploreQuestionComment
from models import QAUser, ClassStudent, LectClass, Inst, Course, UserCourse
import api

class StartHandler(BaseHandler):
    def get(self):
        #add initial universities
        inst = Inst.all().fetch(50)
        if len(inst)==0:
            new_inst = Inst()
            new_inst.name = 'Other'
            new_inst.put()
            
            #add also introductory course
            courses = ['Electrical Engineering','Mechanical Engineering','Civil Engineering','Software Engineering','Geospatial Engineering','Business Courses','Accounts','Commerce',
'Economics','Pure Mathematics','Statistics','Info Tech Courses','Computer Science','Computer Technology','Informatics','Computer Security & Forensics','Nursing',
'Medical Laboratory','Biochemestry','Biotechnology','Microbiology','Applied Physics','Industrial Chemistry','Analytical Chemistry','Astronomy & Astrophysics',
'Applied Chemistry','Sociology','Journalism','Counselling Psychology','Forestry','Physical Education']
            for c in courses:
                course = Course()
                course.course = c
                course.put()
        self.redirect('/home')

class Error404(BaseHandler):
    def get(self):
        self.render("error-404.html")

class MainPage(BaseHandler):
    def get(self):
        class_list = {}
        course_list = {}
        my_courses = {}
        user = self.get_user()
        if not hasattr(user['user'], "name"):
            self.redirect('/home')
        else:
            if user['user'].type=='Student':
                class_list = ClassStudent.gql('WHERE student=:1',user['user'])
            else:
                class_list = LectClass.gql('WHERE lecturer=:1',user['user'])
            my_courses = UserCourse.gql('WHERE user=:1',user['user'])
            course_list = Course.gql('ORDER BY course').fetch(50)
        self.render('base.html',class_list=class_list,course_list=course_list,my_courses=my_courses)

class PublicHome(BaseHandler):
    def get(self):
        user = self.get_user()
        
        if hasattr(user['user'], "name"):
            self.redirect('/')
        self.render_public("public-home.html")

class TestJSON(BaseHandler):
    def get(self):
        result = []
        #get all user emails and their names
        qa_users = QAUser.all().fetch(100)
        for i in qa_users:
            user = {
                 'name':i.name,
                 'email':i.email
                 }
            result.append(user)
        
        self.write(json.dumps(result))

#class ApiServe(BaseHandler):
#    def get(self,method_,**kw):
#        if method_=='getstudents':
#            results = Api.getstudents(**kw) #an array of dictionary objs
#            self.write(json.dumps(results))

class ApiJson(BaseHandler):
    def get(self):
        method_ = self.request.get('m')
            
        if method_ == 'getstudents':
            for_ = str(self.request.get('f'))
            email = str(self.request.get('e'))
            token = str(self.request.get('t'))
            if self.request.get('a'):
                added = int(self.request.get('a'))
            else:
                added = 0
            results = api.getstudents(for_,email,token,added)
            if results:
                self.write(json.dumps(results))
            else:
                self.write(json.dumps(['nothing']))
                
        if method_ == 'getrevisionset':
            rev_key = str(self.request.get('rk'));
            results = api.getrevisionset(rev_key)
            if results:
                self.write(json.dumps(results))
            else:
                self.write(json.dumps(['No results']))
            
                    
class TestUrlFetch(BaseHandler):
    def get(self):
        response = fetch("https://script.googleusercontent.com/echo?user_content_key=oxxNqGlEHC_uBQPK-hOnfATtHbKPKUZXs4XWIWWd6mD93wIoddwrsX9FP25COsho255qSLnCjciVUSMZcbSBeZgVkPBmfgQfm5_BxDlH2jW0nuo2oDemN9CCS2h10ox_nRPgeZU6HP_KzBwqHZ0m1fr9OIFZypRch8JJZFsljkgjNJocW3bI78NYIKFds8DrcdeJ3L4C5p1ADa7ZhhZrnRC2VhQt20LoL_JVeqVV92apsX33uK41mQ&lib=My6vURSm-W5nS6tEi3XSgNwTNlasQMO7u",deadline=60)
        #still needs a better fix to avoid the timeout errors
        if(response.status_code==200):
            logging.info(response.status_code)
            logging.info(response.content)
            self.write(response.content)
        else:
            self.write("Nothing")

class HelpHandler(BaseHandler):
    def get(self,topic):
        self.redirect("/help#%s"%topic)

class HelpMain(BaseHandler):
    def get(self):
        self.render("help-main.html")

#improve the patterns later-->regex!
        
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/home',PublicHome),
                               ('/home/signup/step2',MyCourses),
                               ('/home/signup/([^/]+)',SignUp),
                               ('/profile',Profile),
                               ('/revision/',RevisionHandler),
                               ('/revision/questions/([^/]+)',QuestionHandler),
                               ('/revision/questions/ans/([^/]+)',AnswerHandler),
                               ('/revision/questions/del/([^/]+)',DeleteQuestion),
                               ('/revision/questions/ans/del/([^/]+)',DeleteAnswer),
                               ('/explore',ExploreHome),
                               ('/explore/revision/([^/]+)',ExploreRevision),
                               ('/explore/revision/question/comment',ExploreQuestionComment),
                               ('/explore/revision/attempt/first',RevisionAttemptHandler),
                               ('/explore/revision/attempt/answer',RevisionAttemptAnswerHandler),
                               ('/explore/lecturer/([^/]+)',ExploreLecturer),
                               ('/explore/student/([^/]+)',ExploreStudent),
                               ('/profile/student/([^/]+)',ExploreStudent),
                               ('/profile/join/lecturer/([^/]+)',JoinLecturer),
                               ('/api/json/',ApiJson),
                               ('/json',TestJSON),
                               ('/json/fetch',TestUrlFetch),
                               ('/help/([^/]+)',HelpHandler),
                               ('/help',HelpMain),
                               ('/class',LectClassHandler),
                               ('/class/page/([^/]+)',LectClassPublicHandler),
                               ('/class/join/([^/]+)',JoinClass),
                               ('/course/add/',AddCourse),
                               ('/course/delete/',DeleteCourse),
                               ('/admin/start',StartHandler),
                               ('/.*',Error404)
                               ],
                              debug=True)
