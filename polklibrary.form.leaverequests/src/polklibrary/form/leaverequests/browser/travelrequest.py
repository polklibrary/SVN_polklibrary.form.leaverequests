from plone import api
from plone.i18n.normalizer import idnormalizer
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
from zope.interface import alsoProvides
from polklibrary.form.leaverequests.utility import MailMe, DeleteEventMailed
import random, time, transaction


class TravelRequestPrint(BrowserView):

    template = ViewPageTemplateFile("templates/travelrequest_print.pt")
    
    def __call__(self):
        if self.context.UID() != self.request.form.get('hash',''):
            self.request.response.redirect(self.portal.absolute_url())
    
        return self.template()
        
    def comment_as_html(self):
        return self.context.workflow_status_comments.replace('\n','<br />')
      
    def created(self):
        return self.context.created().strftime('%B %d, %Y at %I:%M %p')
        
    @property
    def portal(self):
        return api.portal.get()
        
        
class TravelRequestView(BrowserView):

    template = ViewPageTemplateFile("templates/travelrequest_view.pt")
    
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        
        # security: limit to owner and reviewers
        if not self.is_reviewer():
            user = api.user.get_current()
            if not str(user.getProperty("id")) in self.context.email:
                self.request.response.redirect(self.context.aq_parent.absolute_url())
                
        
        self.skip_reviewer_worflow_step()
            
        if self.request.form.get('form.test.pending', ''):
            self.context.workflow_status = u'pending'
            self.context.reindexObject()      
                    
        if self.request.form.get('form.workflow.forward', ''):
            print('forward')
            self.workflow_forward()
            self.workflow_comments()
            self.context.reindexObject()            
            
        if self.request.form.get('form.workflow.back', ''):
            print('back')
            self.workflow_back()
            self.workflow_comments()
            self.context.reindexObject()
            
        return self.template()
        
    def is_reviewer(self):
        user = api.user.get_current()
            
        roles = user.getRolesInContext(self.context)
        userid = user.getProperty("id")
        parent = self.context.aq_parent
        
        is_supervisor = False
        supervisor_list = parent.supervisors.split('\n')
        for s in supervisor_list:
            supervisors = s.split('|')
            if userid in supervisors[1]:
                is_supervisor = True
                
        return userid == 'admin' or (('Manager' in roles or 'Reviewer' in roles) and is_supervisor) # and userid in self.context.supervisors
      
      
    def is_director(self):
        user = api.user.get_current()
        userid = user.getProperty("id")
        parent = self.context.aq_parent
        
        return (userid in parent.librarydirector_email or userid == parent.librarydirector_email)
      
              
              
              
              
    def is_in_workflow(self):
        return self.context.workflow_status == 'pending' or self.context.workflow_status == 'supervisor_approved'
      
    def comment_as_html(self):
        return self.context.workflow_status_comments.replace('\n','<br />')
      
      
      
    def skip_reviewer_worflow_step(self):
        if self.context.workflow_status == u'pending' and self.is_reviewer():
            self.context.workflow_status = u'supervisor_approved'
            self.context.reindexObject()
            
      
    def workflow_forward(self):
    
        if self.context.workflow_status == u'supervisor_approved':
            print('supervisor_approved to director_approved')
            self.context.workflow_status = u'director_approved'
            self.email_status_change()
            self.email_library_office()
            
        elif self.context.workflow_status == u'pending':
            print('pending to supervisor_approved')
            self.context.workflow_status = u'supervisor_approved'
            self.email_status_change()
            self.email_library_director()
        
      
      
    def workflow_back(self):
    
        if self.context.workflow_status == u'director_approved':
            self.context.workflow_status = u'pending'
            self.email_status_change()
            
        elif self.context.workflow_status == u'supervisor_approved':
            self.context.workflow_status = u'pending'
            self.email_status_change()
        
        elif self.context.workflow_status == u'pending':
            self.context.workflow_status = u'denied'
            self.email_status_change()
        
        
    def workflow_comments(self):
        user = api.user.get_current()
        userid = user.getProperty("id")
        comment = self.request.form.get('form.workflow.comment', '')
        
        if comment:
            print('adding comment')
            if self.context.workflow_status_comments:
                self.context.workflow_status_comments = 'Comment by ' + userid + '\n' + comment + '\n\n' + self.context.workflow_status_comments
            else:
                self.context.workflow_status_comments = 'Comment by ' + userid + '\n' + comment
        
        
        
    def email_status_change(self):
        parent = self.context.aq_parent
        subject = 'Travel Request - Updated'
        body = parent.email_status_change
        body = body.replace('${link}', self.context.absolute_url())
        body = body.replace('${requestor}', self.context.title)
        
        MailMe(subject, parent.mail_from_email, [self.context.email], body)
      
    # not used here?
    def email_supervisor(self):
        parent = self.context.aq_parent
        subject = 'Travel Request - Approval Required'
        body = parent.email_supervisor
        body = body.replace('${link}', self.context.absolute_url())
        body = body.replace('${requestor}', self.context.title)
        
        MailMe(subject, self.context.email, ['hietpasd@uwosh.edu'], body)
        #MailMe(subject, self.context.email, [self.context.supervisors], body)
      
      
    def email_library_director(self):
        parent = self.context.aq_parent
        subject = 'Travel Request - Approval Required'
        body = parent.email_library_director
        body = body.replace('${link}', self.context.absolute_url())
        body = body.replace('${requestor}', self.context.title)
        
        MailMe(subject, self.context.email, parent.librarydirector_email.split(','), body)
        
    def email_library_office(self):
        parent = self.context.aq_parent
        
        subject = 'Travel Request - Approved'
        body = parent.email_library_office
        body = body.replace('${requestor}', self.context.title)
        body = body.replace('${hashlink}', self.context.absolute_url() + '/travelrequest_print?hash=' + self.context.UID())
        
        MailMe(subject, self.context.email, parent.libraryoffice_email.split(','), body)
        
    
        
    def created(self):
        return self.context.created().strftime('%B %d, %Y at %I:%M %p')
    
    
    @property
    def portal(self):
        return api.portal.get()
        
        