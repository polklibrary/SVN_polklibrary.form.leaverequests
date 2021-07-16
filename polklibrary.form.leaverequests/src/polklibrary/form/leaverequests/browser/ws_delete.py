from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from datetime import datetime
from DateTime import DateTime

class WSDeleteView(BrowserView):

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        brains = []
        
        end_ymd = self.request.get('ymd','')
        end_ymdhm = self.request.get('ymdhm','')
        execute = self.request.get('execute','0')
        
        start = DateTime(datetime.strptime("2000-01-01", '%Y-%m-%d'))
        end = None
        
        if end_ymd:
            end = DateTime(datetime.strptime(end_ymd, '%Y-%m-%d'))
        if end_ymdhm:
            end = DateTime(datetime.strptime(end_ymdhm, '%Y-%m-%d_%H%M'))
        
        if end:
            date_range_query = { 'query':(start,end), 'range': 'min:max'}
                
            brains = api.content.find(self.context,portal_type="polklibrary.form.leaverequests.models.leaverequest", sort_on='created', created=date_range_query)

            
            if execute == '0':
                output = "TEST ONLY -- Processed: " + str(len(brains)) + '\n\n'
                for brain in brains:
                    output += str(brain.created) + '   ' + brain.getURL() + '\n'
                return output
                
            # if not test, continue
            
            output = "Processed: " + str(len(brains)) + '\n\n'
            for brain in brains:
                output += str(brain.created) + '   ' + brain.getURL() + '\n'
                obj = brain.getObject()
                api.content.delete(obj, check_linkintegrity=False)
            
            return output
        
        return 'Param Example: Year-Month-Day_24HourMinute as ymdhm=2018-01-21_1530 \n' \
               'Param Example: Year-Month-Day as ymd=2018-01-21 \n' \
               'Param Optional to run it: execute=1 \n' \
        
        
    
    @property
    def portal(self):
        return api.portal.get()
        
        