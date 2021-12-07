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

class LeaveReportView(BrowserView):

    template = ViewPageTemplateFile("templates/leavereport_view.pt")
    
    def __call__(self):
        self.submission_limit = int(self.request.form.get('form.report.submission.limit', '20'))
        self.all_reports = self.get_reports()
        return self.template()

    def get_reports(self):
        userid = api.user.get_current().getProperty("id")
        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog.searchResults(
            portal_type='polklibrary.form.leaverequests.models.leaverequest',
            sort_on='created, Creator',
            sort_order='descending, ascending'
        )
        
        data = {}
        for brain in brains:
            if userid in brain.supervisors or 'hietpasd' in userid or 'admin' in userid:
            
                if brain.Creator not in data: 
                    data[brain.Creator] = []
                    
                if len(data[brain.Creator]) < self.submission_limit:
                    data[brain.Creator].append({
                        'creator' : brain.Creator,
                        'info' : TimeOffFormater(brain.timeoff),
                        'workflow_status' : brain.workflow_status.capitalize(),
                        'url' : brain.getURL(),
                    })
                    
        return data

        
    @property
    def portal(self):
        return api.portal.get()
        
        