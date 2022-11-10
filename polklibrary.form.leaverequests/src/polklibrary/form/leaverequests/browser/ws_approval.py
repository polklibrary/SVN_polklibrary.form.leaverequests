from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from plone.i18n.normalizer import idnormalizer
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
from zope.container.interfaces import INameChooser
from plone.app.uuid.utils import uuidToObject
from polklibrary.form.leaverequests.utility import MailMe, AddEventMailed
from polklibrary.form.leaverequests.browser.leaverequest import TimeOffFormater
import random, time, transaction


class WSView(BrowserView):
    
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        final_status = "Error"
    
        no_redirect = self.request.form.get('no_redirect', '0')
        token = self.request.form.get('token', '')
        statusid = self.request.form.get('status', '0')
        status = 'pending'
        if statusid == '0':
            status = 'denied'
        if statusid == '1':
            status = 'approved'
            
        with api.env.adopt_roles(roles=['Manager']):
            catalog = api.portal.get_tool(name='portal_catalog')
            brains = catalog.unrestrictedSearchResults(
                portal_type='polklibrary.form.leaverequests.models.leaverequest',
                UID=token
            )
            if brains:
                obj = brains[0].getObject()
                if obj.workflow_status not in ['approved', 'denied']:
                    obj.workflow_status = status
                    obj.reindexObject()
                    body = """
                        <div style="border: 1px solid #888; background-color: #eee; padding: 10px; margin-top: 10px; max-width: 500px;">
                            <div style="font-weight: bold; margin-left: 10px;">Your leave request was <u>${status}</u> by ${approver}</div>
                            <div style="margin: 10px;">${timeoff}</div>
                            <div style="margin: 10px;">
                                <a style="background-color:#2959af; color:white; display:inline-block; font-weight:bold; margin:10px; padding:5px 10px; text-decoration: none;" href="${link}">View Request</a>
                            </div>
                        </div> 
                    """
                    body = body.replace('${approver}', obj.supervisors)
                    body = body.replace('${timeoff}', TimeOffFormater(obj.timeoff))
                    body = body.replace('${link}', obj.absolute_url())
                    body = body.replace('${status}', status.capitalize())
                    body = body.replace('${requestor}', obj.title)
                    
                    MailMe('Leave Request - ' + status.capitalize(), obj.supervisors, [obj.email], body)
                    
                    
                    # for office
                    if obj.workflow_status == 'approved':
                        AddEventMailed(token, obj.title, obj.supervisors, obj.timeoff)
                    
                    
        if no_redirect == '0':        
            return self.request.response.redirect(obj.absolute_url())
        return self.request.response.redirect(self.portal.absolute_url() + '/close_window')
        
    @property
    def portal(self):
        return api.portal.get()
        
        