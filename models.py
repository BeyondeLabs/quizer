#models
from google.appengine.ext import db

class QAUser(db.Model):
    user = db.UserProperty()
    name = db.StringProperty()
    title = db.StringProperty()
    joined = db.DateTimeProperty(auto_now_add=True)
    url = db.StringProperty()
    type = db.StringProperty() #duplicated for now
    institution = db.StringProperty()
#    courses = db.TextProperty()
    email = db.TextProperty()

class Inst(db.Model):
    name = db.StringProperty()
    description = db.TextProperty()
    lon = db.FloatProperty()
    lat = db.FloatProperty()
    url = db.StringProperty()

class UserInst(db.Model):
    user = db.ReferenceProperty(QAUser) #qauser
    inst = db.ReferenceProperty(Inst)
    type = db.StringProperty()
    
class Course(db.Model):
    course = db.StringProperty()
    description = db.TextProperty()

class UserCourse(db.Model):
    course = db.ReferenceProperty(Course)
    user = db.ReferenceProperty(QAUser)

class LectClass(db.Model):
    name = db.StringProperty()
    description = db.TextProperty()
    lecturer = db.ReferenceProperty(QAUser) #qauser
    course = db.ReferenceProperty(Course)
    date_from = db.DateProperty()
    date_to = db.DateProperty()
    created = db.DateTimeProperty(auto_now_add=True)

class ClassStudent(db.Model):
    lect_class = db.ReferenceProperty(LectClass)
    student = db.ReferenceProperty(QAUser) #qauser
    joined = db.DateTimeProperty(auto_now_add=True)
      
class Revision(db.Model):
    user = db.ReferenceProperty(QAUser)
    title = db.StringProperty()
    lect_class = db.StringProperty()
    description = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    published = db.BooleanProperty()

class Question(db.Model):
    revision = db.ReferenceProperty(Revision)
    question = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    
class Answer(db.Model):
    question = db.ReferenceProperty(Question)
    answer = db.TextProperty()
    correct = db.BooleanProperty()
    created = db.DateTimeProperty(auto_now_add=True)

class RevisionAttempt(db.Model):
    student = db.ReferenceProperty(QAUser)
    revision = db.ReferenceProperty(Revision)
    score = db.FloatProperty()
    created = db.DateTimeProperty(auto_now_add=True)

class RevisionAttemptAnswer(db.Model):
    attempt = db.ReferenceProperty(RevisionAttempt)
    question = db.ReferenceProperty(Question)
    answer = db.ReferenceProperty(Answer)
    created = db.DateTimeProperty(auto_now_add=True)

class SLConnect(db.Model):
    lecturer = db.StringProperty()
    student = db.ReferenceProperty(QAUser)
    lect_class = db.ReferenceProperty(LectClass)
    joined = db.DateTimeProperty(auto_now_add=True)

class UserContactLogs(db.Model):
    user = db.ReferenceProperty(QAUser)
    num_added = db.IntegerProperty()
    date_added = db.DateTimeProperty(auto_now_add=True)

class QuestionComment(db.Model):
    question = db.ReferenceProperty(Question)
    ukey = db.StringProperty()
    comment = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)