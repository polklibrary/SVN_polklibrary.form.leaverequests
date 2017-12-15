from plone import api
from plone.app.textfield import RichText
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
    
    
        