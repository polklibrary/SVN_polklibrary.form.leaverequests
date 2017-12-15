from plone import api
from plone.i18n.normalizer import idnormalizer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase

class LeaveRequestViewlet(ViewletBase):
    
    @property
    def is_allowed(self):
        return ((self.context.portal_type == 'polklibrary.form.leaverequests.models.leaverequest' and '/edit' in self.request['ACTUAL_URL'])
               or '++add++polklibrary.form.leaverequests.models.leaverequest' in self.request['ACTUAL_URL'])
        
    @property
    def portal(self):
        return api.portal.get()
        
        