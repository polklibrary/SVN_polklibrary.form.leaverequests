from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from plone.i18n.normalizer import idnormalizer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
from plone.app.uuid.utils import uuidToObject
from polklibrary.form.leaverequests.utility import MailMe
from polklibrary.form.leaverequests.browser.leaverequest import TimeOffFormater
import random, time, transaction, json


class WSView(BrowserView):
    
    def __call__(self):
        data = []
        #with api.env.adopt_roles(roles=['Manager']):
        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog.searchResults(
            portal_type='polklibrary.form.leaverequests.models.leaveform'
        )
        
        if brains:
            obj = brains[0].getObject()
            for user in obj.academic_staff.replace('\r','').split('\n'):
                data.append(user)
        return json.dumps(data)
        
    @property
    def portal(self):
        return api.portal.get()
        
        