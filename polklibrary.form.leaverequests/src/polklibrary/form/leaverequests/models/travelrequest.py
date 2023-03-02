from Acquisition import aq_inner
from plone import api
from plone.autoform import directives
from plone.supermodel import model
from plone.uuid.interfaces import IUUID
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import directlyProvides
from zope.schema.interfaces import IContextSourceBinder
        
from plone.dexterity.browser.add import  DefaultAddForm, DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm

from polklibrary.form.leaverequests.browser.leaverequest import TimeOffFormater
from polklibrary.form.leaverequests.utility import MailMe


def email_supervisor(context, parent, url):
    subject = 'Travel Request - Approval Required'
    body = parent.email_supervisor
    body = body.replace('${link}', url)
    body = body.replace('${requestor}', context.title)
    
    #MailMe(subject, context.email, ['hietpasd@uwosh.edu'], body)
    MailMe(subject, context.email, [context.supervisors], body)

yes_no_options = SimpleVocabulary([
    SimpleTerm(value=u'Yes', title=u'Yes'),
    SimpleTerm(value=u'No', title=u'No'),
])

workflow_choices = SimpleVocabulary([
    SimpleTerm(value=u'pending', title=u'Pending'),
    SimpleTerm(value=u'denied', title=u'Denied'),
    SimpleTerm(value=u'supervisor_approved', title=u'Supervisor Approved'),
    SimpleTerm(value=u'director_approved', title=u'Library Director Approved'),
])

def supervisors_choices(context):
    try:
        voc = []
        email = api.user.get_current().getProperty("email")
        parent = context
        if context.portal_type == 'polklibrary.form.leaverequests.models.travelrequest':
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
        print("ERROR VOCA: " + str(e))
        return []
directlyProvides(supervisors_choices, IContextSourceBinder)


class ITravelRequest(model.Schema):

    
    directives.write_permission(workflow_status='cmf.ReviewPortalContent')
    workflow_status = schema.Choice(
        title=u"Current Approval Status",
        description=u"(Making changes to this request, will reset approval status to 'Pending')",
        source=workflow_choices,
        required=False,
        default=u"pending",
        missing_value=u"pending"
    )
    
    directives.write_permission(workflow_status='cmf.ReviewPortalContent')
    workflow_status_comments = schema.Text(
        title=u"Status Comments",
        required=False,
        default=u"",
        missing_value=u""
    )

    title = schema.TextLine(
        title=u"Your name",
        required=True,
        missing_value=u"",
        default=u"",
    )
    
    email = schema.TextLine(
        title=u"Your email",
        required=True,
        missing_value=u"",
        default=u"",
    )
        
    activity = schema.TextLine(
        title=u"Name of conference or activity?",
        required=True,
        missing_value=u"",
        default=u"",
    )
    
    location = schema.TextLine(
        title=u"Where is the location of your conference/activity?",
        required=True,
        missing_value=u"",
        default=u"",
    )
    
    # activity_datetime = schema.TextLine(
        # title=u"Date and time you will be traveling from work?",
        # required=True,
        # missing_value=u"",
        # default=u"",
    # )
    
    
    activity_description = schema.Text(
        title=u"Describe the nature of the professional development/activity and how it relates to your job:",
        required=True,
        missing_value=u"",
        default=u"",
    )
    
    
    development_type = schema.TextLine(
        title=u"Type of professional development",
        description=u"(Conference, workshop, etc.)",
        required=True,
        missing_value=u"",
        default=u"",
    )
    
    funding = schema.Choice(
        title=u"Did you apply or will you apply for university professional development funding?",
        source=yes_no_options,
        required=True,
        default=u'No',
    )
    
    others_attending = schema.Text(
        title=u"Names of other staff attending:",
        required=True,
        missing_value=u"",
        default=u"",
    )
    
    provisions = schema.Text(
        title=u"Provisions for assigned responsibilities:",
        required=True,
        missing_value=u"",
        default=u"",
    )
    
    estimated_cost = schema.TextLine(
        title=u"Estimated total cost of trip for UWO Libraries?",
        #description=u"(Registration costs, mileage, parking, meals, lodging, etc.)",
        required=True,
        missing_value=u"",
        default=u"",
    )
    
    departure_datetime = schema.TextLine(
        title=u"Departure date and time?",
        required=True,
        missing_value=u"",
        default=u"",
    )
    
    return_datetime = schema.TextLine(
        title=u"Return date and time?",
        required=True,
        missing_value=u"",
        default=u"",
    )
    
    supervisors = schema.Choice(
        title=u"Submit to which supervisor for approval?",
        source=supervisors_choices,
        required=True,
        missing_value=u'',
    )
    
class AddForm(DefaultAddForm):
    portal_type = 'polklibrary.form.leaverequests.models.travelrequest'

    def add(self, obj):
        DefaultAddForm.add(self, obj)
        obj.workflow_status = u'pending'
        obj.reindexObject()
        
        url = "/".join([aq_inner(self.context).absolute_url(), obj.id])
        
        email_supervisor(obj, aq_inner(self.context), url)
        return obj
    
class AddView(DefaultAddView):
    form = AddForm

    
class EditForm(DefaultEditForm):
    portal_type = 'polklibrary.form.leaverequests.models.travelrequest'

    def update(self):
        DefaultEditForm.update(self)
        saved = self.request.form.get('form.buttons.save', u'')
        if saved:
            user = api.user.get_current()
            if user.getProperty('id') in self.context.listCreators():
                self.context.workflow_status = u'pending'
                self.context.reindexObject()
            email_supervisor(self.context, self.context.aq_parent, self.context.absolute_url())
            
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        