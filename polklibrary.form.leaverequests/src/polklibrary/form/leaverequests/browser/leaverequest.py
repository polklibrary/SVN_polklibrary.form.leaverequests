from plone import api
from plone.i18n.normalizer import idnormalizer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
import random, time, transaction

def TimeOffFormater(timeoff):
    off = ""
    days = timeoff.replace('\r','').split('\n')
    
    for day in days:
        opts = day.split('|')
        
        leave = 'Other'
        if opts[1] == 'SL':
            leave = 'Sick Leave'
        if opts[1] == 'FH':
            leave = 'Floating/Legal Holiday'
        if opts[1] == 'VA':
            leave = 'Vacation'
        if opts[1] == 'CT':
            leave = 'Comp Time'
        
        off += '(' + opts[2] + ') ' + leave + '&nbsp;&nbsp;&nbsp;&nbsp;'
        off += opts[0]
        off += '&nbsp;&nbsp;&nbsp;&nbsp;'
        off += opts[3] 
        off += ' - '
        off += opts[4] 
        off += '<br />' 
    return off

class LeaveRequestView(BrowserView):

    template = ViewPageTemplateFile("templates/leaverequest_view.pt")
    
    def __call__(self):
        return self.template()
        
    def is_reviewer(self):
        #userid = unicode(api.user.get_current().getProperty("userid"))
        roles = api.user.get_current().getRolesInContext(self.context)
        return ('Manager' in roles or 'Reviewer' in roles) # and userid in self.context.supervisors
      
    def status(self):
        if self.context.workflow_status == 'approved':
            return 'Approved by ' +  self.context.supervisors
        if self.context.workflow_status == 'denied':
            return 'Denied by ' +  self.context.supervisors
        return 'Pending on ' +  self.context.supervisors
        
    def time_off(self):
        return TimeOffFormater(self.context.timeoff)
    
    def created(self):
        return self.context.created().strftime('%B %d, %Y at %I:%M %p')
    
    
    @property
    def portal(self):
        return api.portal.get()
        
        