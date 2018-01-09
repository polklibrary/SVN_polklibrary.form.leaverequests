from plone import api
from plone.i18n.normalizer import idnormalizer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
import random, time, transaction

from polklibrary.form.leaverequests.browser.leaverequest import TimeOffFormater

class LeaveFormView(BrowserView):

    template = ViewPageTemplateFile("templates/leaveform_view.pt")
    
    def __call__(self):
    
        return self.template()

    @property
    def is_anonymous(self):
        return api.user.is_anonymous()
        
    def get_your_content(self):
        limit = int(self.request.form.get('yourlimit', 25))
        userid = unicode(api.user.get_current().getProperty("id"))
        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog.searchResults(
            portal_type='polklibrary.form.leaverequests.models.leaverequest',
            sort_on='created',
            sort_order='descending'
        )[:limit]
        data = []
        for brain in brains:
            if userid == brain.Creator:
                data.append({
                    'info' : TimeOffFormater(brain.timeoff),
                    'workflow_status' : brain.workflow_status.capitalize(),
                    'url' : brain.getURL(),
                })
        return data

        
    def get_reviewers_content(self):
        limit = int(self.request.form.get('stafflimit', 25))
        userid = unicode(api.user.get_current().getProperty("id"))
        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog.searchResults(
            portal_type='polklibrary.form.leaverequests.models.leaverequest',
            sort_on='created',
            sort_order='descending'
        )[:limit]
        data = []
        for brain in brains:
            if userid in brain.supervisors:
                data.append({
                    'creator' : brain.Creator,
                    'info' : TimeOffFormater(brain.timeoff),
                    'workflow_status' : brain.workflow_status.capitalize(),
                    'url' : brain.getURL(),
                })
        return data

        
        
    def is_reviewer(self):
        #userid = unicode(api.user.get_current().getProperty("userid"))
        user = api.user.get_current()
        roles = user.getRolesInContext(self.context)
        userid = unicode(user.getProperty("id"))
        
        is_supervisor = False
        supervisor_list = self.context.supervisors.split('\n')
        for s in supervisor_list:
            supervisors = s.split('|')
            if userid in supervisors[1]:
                is_supervisor = True
        
        return ('Manager' in roles or 'Reviewer' in roles) and is_supervisor # and userid in self.context.supervisors
      
        
    @property
    def portal(self):
        return api.portal.get()
        
        