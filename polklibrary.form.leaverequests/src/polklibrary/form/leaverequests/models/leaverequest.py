from plone import api
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.supermodel import model
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import directlyProvides
from zope.schema.interfaces import IContextSourceBinder
from datetime import datetime
        
from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm, DefaultEditView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from polklibrary.form.leaverequests.browser.leaverequest import TimeOffFormater
from polklibrary.form.leaverequests.utility import MailMe

def run_mailing_process(context, request, is_update):
    subject = 'Leave Request - New'
    if is_update:
        subject = 'Leave Request - Updated'
    
    body = """
        <div style="border: 1px solid #888; background-color: #eee; padding: 10px; margin-top: 10px; max-width: 500px;">
            <div style="font-weight: bold">${requestor}</div>
            <div style="margin: 10px;">${timeoff}</div>
            <div style="margin: 10px;">Optional Note: ${notes}</div>
            <div style="margin: 10px;">Optional Coverage: ${coverage}</div>
            <div style="margin: 10px;">
                <a style="background-color:#2959af; color:white; display:inline-block; font-weight:bold; margin:10px; padding:5px 10px; text-decoration: none;" href="${link}">View Request</a>
                <a style="background-color:#00ab00; color:white; display:inline-block; font-weight:bold; margin:10px; padding:5px 10px; text-decoration: none;" href="${approve_link}">Approve</a>
                <a style="background-color:#ce0000; color:white; display:inline-block; font-weight:bold; margin:10px; padding:5px 10px; text-decoration: none;" href="${deny_link}">Deny</a>
            </div>
        </div> 
    """
    body = body.replace('${timeoff}', TimeOffFormater(context.timeoff))
    body = body.replace('${link}', context.absolute_url())
    body = body.replace('${approve_link}', context.absolute_url() + '/leaverequest_workflow?no_redirect=1&status=1&token=' + context.UID())
    body = body.replace('${deny_link}', context.absolute_url() + '/leaverequest_workflow?no_redirect=1&status=0&token=' + context.UID())
    body = body.replace('${notes}', context.description)
    body = body.replace('${coverage}', context.coverage)
    body = body.replace('${requestor}', context.title)
    
    MailMe(subject, [context.email], [context.supervisors], body)

    
leave_type_options = SimpleVocabulary([
    SimpleTerm(value=u'VA', title=u'Vacation'),
    SimpleTerm(value=u'SL', title=u'Sick Leave'),
    SimpleTerm(value=u'FH', title=u'Floating/Legal Holiday'),
    SimpleTerm(value=u'CT', title=u'Comp Time (University Staff Only)'),
    SimpleTerm(value=u'O', title=u'Other'),
])

workflow_choices = SimpleVocabulary([
    SimpleTerm(value=u'pending', title=u'Pending'),
    SimpleTerm(value=u'denied', title=u'Denied'),
    SimpleTerm(value=u'approved', title=u'Approved'),
])

workflow_default = SimpleVocabulary([
    SimpleTerm(value=u'pending', title=u'Pending'),
])

def supervisors_choices(context):
    try:
        voc = []
        email = unicode(api.user.get_current().getProperty("email"))
        parent = context
        if context.portal_type == 'polklibrary.form.leaverequests.models.leaverequest':
            parent = context.aq_parent
        supervisor_definition = parent.supervisors.replace('\r','')
        for supervisor in supervisor_definition.split('\n'):
            supervisor_info = supervisor.split('|')
            if email in supervisor_info[2]:
                voc.insert(0, SimpleVocabulary.createTerm(supervisor_info[1], supervisor_info[1], supervisor_info[0]))
            else:
                voc.append(SimpleVocabulary.createTerm(supervisor_info[1], supervisor_info[1], supervisor_info[0]))
        if voc:
            return SimpleVocabulary(voc)
        return []
    except Exception as e:
        print "ERROR VOCA: " + str(e)
        return []
directlyProvides(supervisors_choices, IContextSourceBinder)


class ILeaveRequest(model.Schema):

    title = schema.TextLine(
        title=u"Name",
        required=False,
        missing_value=u"",
        default=u"",
    )
        
    email = schema.TextLine(
        title=u"Email",
        required=False,
        missing_value=u"",
        default=u"",
    )
    
    timeoff = schema.Text(
        title=u"Time Off",
        required=True,
        missing_value=u"",
        default=u"",
    )
    
    coverage = schema.TextLine(
        title=u"Suggested Coverage",
        description=u"(Optional)",
        required=False,
        missing_value=u"",
        default=u"",
    )
    
    description = schema.TextLine(
        title=u"Note",
        description=u"(Optional)",
        required=False,
        missing_value=u"",
        default=u"",
    )
    
    supervisors = schema.Choice(
        title=u"Submit to which supervisor for approval?",
        source=supervisors_choices,
        required=True,
        missing_value=u'',
    )

    directives.write_permission(workflow_status='cmf.ReviewPortalContent')
    workflow_status = schema.Choice(
        title=u"Request Status",
        source=workflow_choices,
        required=False,
        default='pending',
        missing_value='pending',
    )

    gcal_event_id = schema.TextLine(
        title=u"gCal Event ID",
        required=False,
        missing_value=u"",
        default=u"",
    )

        
class AddForm(DefaultAddForm):
    portal_type = 'polklibrary.form.leaverequests.models.leaverequest'

    def update(self):
        DefaultAddForm.update(self)
        timeoff = self.request.form.get('form.widgets.timeoff', u'')
        saved = self.request.form.get('form.buttons.save', u'')
        if timeoff and saved:
            if not self.context.title or not self.context.email:
                raise ValueError('Missing username or email, please contact web administrator.')
            
            self.context.workflow_status = u'pending'
            run_mailing_process(self.context, self.request, False)
        
class AddView(DefaultAddView):
    form = AddForm

    
class EditForm(DefaultEditForm):
    portal_type = 'polklibrary.form.leaverequests.models.leaverequest'

    def update(self):
        DefaultEditForm.update(self)
        timeoff = self.request.form.get('form.widgets.timeoff', u'')
        saved = self.request.form.get('form.buttons.save', u'')
        if timeoff and saved:
            user = api.user.get_current()
            if not self.context.title or not self.context.email:
                raise ValueError('Missing username or email, please contact web administrator.')
            if user.getProperty('id') in self.context.listCreators():
                self.context.workflow_status = u'pending'
                self.context.reindexObject()
            run_mailing_process(self.context, self.request, True)
            
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        