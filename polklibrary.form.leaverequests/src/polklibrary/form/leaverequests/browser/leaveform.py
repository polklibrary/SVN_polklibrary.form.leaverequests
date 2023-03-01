from plone import api
from plone.i18n.normalizer import idnormalizer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
import random, time, transaction

from polklibrary.form.leaverequests.browser.leaverequest import TimeOffFormater

import logging
logger = logging.getLogger("Plone")

class LeaveFormView(BrowserView):

    template = ViewPageTemplateFile("templates/leaveform_view.pt")
    
    def __call__(self):
    
        return self.template()

    @property
    def is_anonymous(self):
        return api.user.is_anonymous()
        
    def get_your_leaverequests(self):
        limit = int(self.request.form.get('yourleavelimit', 10))
        userid = api.user.get_current().getProperty("id")
        
        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog.searchResults(
            portal_type='polklibrary.form.leaverequests.models.leaverequest',
            sort_on='created',
            sort_order='descending',
            Creator=userid
        )[:limit]
        
        data = []
        for brain in brains:
            data.append({
                'info' : TimeOffFormater(brain.timeoff),
                'workflow_status' : brain.workflow_status.capitalize(),
                'url' : brain.getURL(),
            })
        return data

    def get_your_travelrequests(self):
        limit = int(self.request.form.get('yourtravellimit', 10))
        userid = api.user.get_current().getProperty("id")
        
        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog.searchResults(
            portal_type='polklibrary.form.leaverequests.models.travelrequest',
            sort_on='created',
            sort_order='descending',
            Creator=userid
        )[:limit]
        
        data = []
        for brain in brains:
            obj = brain.getObject()
            
            status = "Pending (Supervisor Approval)"
            if brain.workflow_status == "denied":
                status = "Denied"
            elif brain.workflow_status == "supervisor_approved":
                status = "Pending (Director Approval)"
            elif brain.workflow_status == "director_approved":
                status = "Approved"
            
            
            data.append({
                'info' : obj.activity,
                'workflow_status' : status,
                'url' : brain.getURL(),
            })
        return data

        
    def get_reviewers_content(self):
        limit = int(self.request.form.get('stafflimit', 25))
        userid = api.user.get_current().getProperty("id")
        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog.searchResults(
            portal_type='polklibrary.form.leaverequests.models.leaverequest',
            sort_on='created',
            sort_order='descending'
        ) # grab the last X requests
        data = []
        for brain in brains:
            if userid in brain.supervisors:
                data.append({
                    'creator' : brain.Creator,
                    'info' : TimeOffFormater(brain.timeoff),
                    'workflow_status' : brain.workflow_status.capitalize(),
                    'url' : brain.getURL(),
                })
        return data[:limit]

        
        
    def is_reviewer(self):
        user = api.user.get_current()
        roles = user.getRolesInContext(self.context)
        userid = user.getProperty("id")
        
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
        
        