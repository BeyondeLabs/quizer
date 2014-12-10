import logging

from base import BaseHandler,users
from models import QAUser, SLConnect,Inst,UserInst, LectClass, ClassStudent,UserCourse,Course

def create_slconnect(lec_key,stu_key):
    #lecturer = QAUser.get(lec_key) #you can't have two ref to the same object
    #prevent duplicate connections
    q = SLConnect.gql('WHERE lecturer=:1 AND student=:2',lec_key,QAUser.get(stu_key)).fetch(1)
    if(len(q)>0):
        return
    else:
        student = QAUser.get(stu_key)
            
        slconnect = SLConnect()
        slconnect.lecturer = lec_key
        slconnect.student = student
        slconnect.put()
    return

def join_class(class_key,stu_key):
    lect_class = LectClass.get(class_key)
    student = QAUser.get(stu_key)
    #prevent duplicates
    check_duplicate = ClassStudent.gql('WHERE lect_class=:1 AND student=:2',lect_class,student).fetch(1)
    if len(check_duplicate)>0:
        return
    else:
        class_student = ClassStudent()
        class_student.lect_class = lect_class
        class_student.student = student
        class_student.put()
    return

def check_joined(class_key,stu_key):
    lect_class = LectClass.get(class_key)
    student = QAUser.get(stu_key)
    #prevent duplicates
    check_duplicate = ClassStudent.gql('WHERE lect_class=:1 AND student=:2',lect_class,student).fetch(1)
    if len(check_duplicate)>0:
        return True
    return False

class Profile(BaseHandler):
    def get(self):
        #if not signedup
        user = self.get_user()
        if not hasattr(user['user'], "name"):
            self.redirect('/home')

        if not users.get_current_user():
            url = users.create_login_url(self.request.uri)
            self.redirect(url)
        
        # user_info = QAUser.gql('WHERE user = :1',users.get_current_user()).get()
        course_list = UserCourse.gql('WHERE user = :1',user['user'])
        other_info = {
                 'course_list':course_list
                 }
        self.render('profile.html',login = self.login_info(),user=user['user'],other_info=other_info)
        
    def post(self):
        #update profile
        
        #Rita --> code
        
        self.redirect('/profile')

class MyCourses(BaseHandler):
    def get(self):
        course_list = {}
        my_courses = {}
        user = self.get_user()
        my_courses = UserCourse.gql('WHERE user=:1',user['user'])
        course_list = Course.gql('ORDER BY course').fetch(50)

        self.render('signup-2.html',my_courses=my_courses,course_list=course_list)

class SignUp(BaseHandler):
    def get(self,user_type,lec_key=''):
        #if already signed up user
        user = self.get_user()
        if hasattr(user['user'], "name"):
            self.redirect('/')  
        if user_type not in ['student','lecturer']:
            user_type = 'student'
        user_type = user_type.capitalize()
        form_cont = {}
        inst_list = Inst.all().fetch(100)
        self.render('signup.html',user_type=user_type,form_cont=form_cont,inst_list=inst_list)
    
    def post(self,user_type,lec_key=''):
        #need form validation
        tac = self.request.get('tac')
        name = self.request.get('name')
        title = self.request.get('title')
        user_type = self.request.get('type')
        url = self.request.get('url')
        inst_key = self.request.get('inst_key')
        institution = self.request.get('institution')
        courses = self.request.get('courses')
        
        form_cont = {
                    'name':name,
                    'title':title,
                    'inst_list':Inst.all().fetch(100),
                    'url':url,
                    'courses':courses,
                    'institution':institution
                    }
        
        user_object = users.get_current_user()
        
        if tac and name: #need better validation / can be done with JS too
            qa_user = QAUser()
            qa_user.user = user_object
            qa_user.name = name
            qa_user.title = title
            qa_user.url = url
            qa_user.type = user_type
            qa_user.institution = institution
            qa_user.email = users.get_current_user().email()
            user_key = qa_user.put()
            
            #update institution details
            inst_user = UserInst()
            inst_user.user = QAUser.get(user_key)
            inst_user.inst = Inst.get(inst_key)
            inst_user.type = user_type
            inst_user.put()
            
            #link student with lecturer
            if lec_key != '':
                #meaning, was invited by a lecturer
                #we create the connection
                stu_key = user_key
                create_slconnect(lec_key, stu_key) #old
            
            #now send confirmation email
            if user_key:
                email = user_object.email()
                self.send_welcome_email(name, email)
                
                self.redirect('/home/signup/step2')
            else:
                #most unlikely error
                self.render('signup.html',user_type=user_type,form_cont=form_cont)
        else:
            self.render('signup.html',user_type=user_type,form_cont=form_cont,inst_list=form_cont['inst_list'])
    
    def send_welcome_email(self,name,email):
        #send welcoming email
        #later use HTML email
        to = email
        subject = "Welcome to QuizerApp"
        body = """
Hello %s,
<p>You just activated your <strong>QuizerApp account</strong>. Please fill free to
recommend the app to your colleagues and friends.</p> 
            
Regards,
            
QuizerApp Team
            """%name
            
        body_content = """
            <p>Hello %s,</p>
<p>You just activated your <strong>QuizerApp account</strong>. Please feel free to
recommend the app to your colleagues and friends.</p> 
            
<p>Regards,<br/><br/>
            
<strong>QuizerApp Team</strong></p>
            """%name

        html = """
<html>
<body>
<table width="590" align="center" border="0" style="font-family: Helvetica, Arial, sans-serif;">
<tr>
    <td style="background:#cecece;color:#336699;font-size:30px;padding:5px;font-weight:bold;border-bottom:solid 5px #777;">
        Quizer<span style="color:#555;">App</span><span style="font-size:12px;">&reg;</span>
    </td>
</tr>
<tr>
    <td style="padding:10px 3px;color:#555;font-size:14px;line-height:18px;">
        %s
    </td>
</tr>
<tr>
    <td>
<table width="590" cellspacing="0" cellpadding="0" border="0">
                            <tbody>
                                <tr>
                                    <td width="590" valign="middle" height="5" style="background-color: #dbdbd9"></td>
                                </tr>
                                
                                <tr>
                                    <td style="padding:5px 2px;">
                                    <p style="font-size: 11px; line-height: 15px; font-family: Helvetica, Arial, sans-serif; color: #999999; margin: 0px 0px 10px 0">
                                    QuizerApp Inc &bull; <a style="color: #588631; text-decoration: none" href="http://www.quizer.info" target="_blank">University of Quizer</a>* (actual name withheld)<br>
                                    See our <a style="color: #588631; text-decoration: none" href="#" target="_blank">Privacy Policy</a> and <a style="color: #588631; text-decoration: none" href="#" target="_blank">Terms &amp; Conditions</a>.</p>

                                    </td>
                                </tr>
                            </tbody>
                        </table>
    </td>
</tr>

</table>

</body>
</html>
"""%body_content
        
        self.send_mail(to, subject, body, html)
        #for logging purposes
        self.send_mail("profnandaa@gmail.com", subject, body, html)
        
        return

class JoinLecturer(BaseHandler):
    #replaced by JoinClass
    def get(self,lec_key):
        #check first if the user is signed up
        #if not signed up, redirect to signup, else link to lecturer
        user = self.get_user()
        if hasattr(user['user'], "name"):
            #already signed up user
            logging.info(user['user'])
            stu_key = user['user'].key()
            create_slconnect(lec_key, stu_key)
            self.redirect('/explore/lecturer/%s'%lec_key)
        else:
            self.redirect('/home/signup/student/%s'%lec_key)

class JoinClass(BaseHandler):
    def post(self,class_key):
        user = self.get_user()
        if hasattr(user['user'], "name"):
            #already signed up user
            stu_key = user['user'].key()
            join_class(class_key, stu_key)
            
            #ajax response
            self.write(user['user'].name)
            
            #send notification to lecturer / write to list of activities
#        self.redirect('/class/page/%s'%class_key)