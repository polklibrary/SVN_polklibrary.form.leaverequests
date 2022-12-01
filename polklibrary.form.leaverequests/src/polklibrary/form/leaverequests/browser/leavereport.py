from plone import api
from plone.i18n.normalizer import idnormalizer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
import random, time, transaction

from polklibrary.form.leaverequests.browser.leaverequest import TimeOffFormater

import re
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
            sort_on='created',
            sort_order='descending'
        )
        
        supervisor_data = {}
        for supervisor in self.context.supervisors.split('\n'):
            supervisor_data_parts = supervisor.split('|')
            supervisor_data[supervisor_data_parts[1].strip()] = supervisor_data_parts[2].strip()
        
        data = {}
        for brain in brains:
        
            if userid + '@uwosh.edu' in supervisor_data:
                staff_emails = supervisor_data[userid + '@uwosh.edu']
                
                if brain.email.strip() in staff_emails:
                    if userid in brain.supervisors or 'hietpasd' in userid or 'admin' in userid:
                    
                        fullname = self.to_title(brain.Title)
                    
                        if fullname not in data: 
                            data[fullname] = []
                            
                        if len(data[fullname]) < self.submission_limit:
                            data[fullname].append({
                                'fullname' : self.to_title(brain.Title),
                                'creator' : brain.Creator,
                                'info' : TimeOffFormater(brain.timeoff),
                                'workflow_status' : brain.workflow_status.capitalize(),
                                'url' : brain.getURL(),
                            })
                        
        return dict(sorted(data.items()))

        
    def to_title(self, title):
        title = title.replace('-',' ')
        return re.sub(r'[0-9]+', '', title).title()
        
        
    @property
    def portal(self):
        return api.portal.get()
        
        