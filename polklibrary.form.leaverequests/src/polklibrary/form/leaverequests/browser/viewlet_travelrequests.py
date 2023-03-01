from plone import api
from plone.i18n.normalizer import idnormalizer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase

class TravelRequestViewlet(ViewletBase):
        
    @property
    def get_name(self):
        user = api.user.get_current()
        name = user.getProperty("first_name", '') + ' ' + user.getProperty("last_name", '')
        if len(name) > 5:
            return name
        name = user.getProperty("fullname", '')
        if name:
            return name
        return u"Missing name"
    
    @property
    def get_email(self):
        email = api.user.get_current().getProperty("email")
        if email:
            return email
        return u"Missing email"
    
    @property
    def is_allowed(self):
        return ((self.context.portal_type == 'polklibrary.form.leaverequests.models.travelrequest' and '/edit' in self.request['ACTUAL_URL'])
               or '++add++polklibrary.form.leaverequests.models.travelrequest' in self.request['ACTUAL_URL'])
        
    @property
    def portal(self):
        return api.portal.get()
        
        