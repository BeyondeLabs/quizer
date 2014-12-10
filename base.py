#base
import os
import webapp2
import jinja2
import logging

from google.appengine.api import mail
from google.appengine.api import users
from models import QAUser

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class BaseHandler(webapp2.RequestHandler):
    def auth(self):
        if not users.get_current_user():
            url = users.create_login_url(self.request.uri)
            self.redirect(url)
            
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self,template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.auth() #authenticated user
        sess_user = self.get_user()
        self.write(self.render_str(template,sess_user=sess_user, **kw))
    
    def render_public(self, template, **kw):
        self.write(self.render_str(template, **kw))
    
    def login_info(self):
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            name = users.get_current_user()
            temp_data = {
                     'name': name,
                     'url':url,
                     'url_linktext':url_linktext
                     }
            return temp_data
        else:
            return {} #poor!
    
    def send_mail(self,to,subject,body,html):
        sender = "QuizerApp<no_reply@quizer-test.appspotmail.com>"
        message = mail.EmailMessage(sender=sender,
                            subject=subject)
        message.to = to
        message.body = body
        message.html = html
        
        message.send()
            
    def get_user(self):
        #to be memcached later
        user_info = QAUser.gql('WHERE user = :1',users.get_current_user()).get()
        logout_url = users.create_logout_url("/")
        return {'user':user_info,
                'logout_url':logout_url,
                'username': users.get_current_user()
                }
    
    def handle_exception(self, exception, debug):
        if debug:
            webapp2.RequestHandler.handle_exception(self, exception, debug)
        else:
            logging.error(500)
            #display error msg
            self.redirect('/')