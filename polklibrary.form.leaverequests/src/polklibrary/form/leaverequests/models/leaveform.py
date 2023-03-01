from plone import api
from plone.supermodel import model
from zope import schema



class ILeaveForm(model.Schema):

    title = schema.TextLine(
        title=u"Title",
        required=True,
    )

    description = schema.Text(
        title=u"Description",
        required=False,
    )

    supervisors = schema.Text(
        title=u"Add Supervisors",
        description=u"One per line.  Format as follows:   Ron Hardy|hardyr@uwosh.edu|karelsr@uwosh.edu,harringp@uwosh.edu",
        required=False,
        missing_value=u"",
        default=u"",
    )

    academic_staff = schema.Text(
        title=u"List Academic Staff NetIDs",
        description=u"One per line.  Format as follows:   hardyr,mulveyt,etc...",
        required=False,
        missing_value=u"",
        default=u"",
    )
    
    #-------------------------------------------
    model.fieldset(
        'mailing_settings',
        label=u'Email Settings', 
        fields=['librarydirector_email','libraryoffice_email','mail_from_email',],
    )
    
    librarydirector_email = schema.TextLine(
        title=u"Library Director Email",
        required=True,
        missing_value=u"",
        default=u"",
    )

    libraryoffice_email = schema.TextLine(
        title=u"Library Office Email",
        required=True,
        missing_value=u"",
        default=u"",
    )
    
    mail_from_email = schema.TextLine(
        title=u"From Email",
        required=True,
        missing_value=u"",
        default=u"",
    )
    
    
    
    #-------------------------------------------
    model.fieldset(
        'travel_requests',
        label=u'Travel Request Settings', 
        fields=['email_status_change','email_supervisor','email_library_director','email_library_office'],
    )
    

    email_status_change = schema.Text(
        title=u"Requester Email Notification Message",
        required=False,
        missing_value=u"",
        default="""
<div style="border: 1px solid #888; background-color: #eee; padding: 10px; margin-top: 10px; max-width: 500px;">
    <div style="font-weight: bold">Travel Request</div>
    <div style="margin: 10px;">Please view your request for an update.</div>
    <div style="margin: 10px;">
        <a style="background-color:#2959af; color:white; cursor: pointer; display:inline-block; font-weight:bold; margin:10px; padding:5px 10px; text-decoration: none;" href="${link}">View Request</a>
    </div>
</div> 
        """,
    )

    email_supervisor = schema.Text(
        title=u"Supervisor Email Notification Message",
        required=False,
        missing_value=u"",
        default="""
<div style="border: 1px solid #888; background-color: #eee; padding: 10px; margin-top: 10px; max-width: 500px;">
    <div style="font-weight: bold">Travel Request</div>
    <div style="margin: 10px;">A Travel Request for ${requestor} has been submitted. Please view the request below for your approval options.</div>
    <div style="margin: 10px;">
        <a style="background-color:#2959af; color:white; cursor: pointer; display:inline-block; font-weight:bold; margin:10px; padding:5px 10px; text-decoration: none;" href="${link}">View Request</a>
    </div>
</div> 
        """,
    ) 
    
    email_library_director = schema.Text(
        title=u"Director Email Notification Message",
        required=False,
        missing_value=u"",
        default="""
<div style="border: 1px solid #888; background-color: #eee; padding: 10px; margin-top: 10px; max-width: 500px;">
    <div style="font-weight: bold">Travel Request</div>
    <div style="margin: 10px;">A Travel Request for ${requestor} has been approved by their supervisor. Please view the request below for your approval options.</div>
    <div style="margin: 10px;">
        <a style="background-color:#2959af; color:white; cursor: pointer; display:inline-block; font-weight:bold; margin:10px; padding:5px 10px; text-decoration: none;" href="${link}">View Request</a>
    </div>
</div> 
        """,
    ) 
    
    email_library_office = schema.Text(
        title=u"Office Email Notification Message",
        required=False,
        missing_value=u"",
        default="""
<div style="border: 1px solid #888; background-color: #eee; padding: 10px; margin-top: 10px; max-width: 500px;">
    <div style="font-weight: bold">Travel Request Approved</div>
    <div style="margin: 10px;">A travel request for ${requestor} has been approved by their supervisor and the library director.</div>
    <div style="margin: 10px;">
        <a style="background-color:#2959af; color:white; cursor: pointer; display:inline-block; font-weight:bold; margin:10px; padding:5px 10px; text-decoration: none;" href="${link}">View Request</a>
    </div>
</div> 
        """,
    ) 

        