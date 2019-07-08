from apiclient import discovery
from httplib2 import Http
from plone import api
from Products.Five import BrowserView
from oauth2client.service_account import ServiceAccountCredentials
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

import datetime,json,urllib,pytz,smtplib,time


GCAL_KEY = '/opt/plone/plone-5-zeo-0/zeocluster/polkservices.google.private.key'
#GCAL_KEY = '/home/vagrant/Plone/zinstance/liboff.google.private.key'


def TimeOffFormater(timeoff):
    off = ""
    days = timeoff.replace('\r','').split('\n')
    
    for day in days:
        opts = day.split('|')
        
        leave = 'Other'
        if opts[1] == 'SL':
            leave = 'Sick Leave'
        if opts[1] == 'PH':
            leave = 'Personal Holiday'
        if opts[1] == 'FH':
            leave = 'Floating/Legal Holiday'
        if opts[1] == 'VA':
            leave = 'Vacation'
        if opts[1] == 'CT':
            leave = 'Comp Time'
        if opts[1] == 'TRAVEL':
            leave = 'Travel'
        
        off += '(' + opts[2] + ') ' + leave + '&nbsp;&nbsp;&nbsp;&nbsp;'
        off += opts[0]
        off += '&nbsp;&nbsp;&nbsp;&nbsp;'
        off += opts[3] 
        off += ' - '
        off += opts[4] 
        off += '<br />' 
    return off



def MailMe(subject, from_email, to_emails, body):
    registry = getUtility(IRegistry)
    smtp_host = registry['plone.smtp_host']
    smtp_port = registry['plone.smtp_port']
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(to_emails)

    mail = MIMEText(body, 'html')
    msg.attach(mail)

    s = smtplib.SMTP(smtp_host, smtp_port)
    s.sendmail(from_email, to_emails, msg.as_string())
    s.quit()



def iso_format(dt):
    central = pytz.timezone('US/Central')
    loc_dt = central.localize(dt)
    iso = loc_dt.isoformat()
    return iso

def AddEventMailed(UID, RequestedBy, ApprovedBy, TimeOff):
    subject = "Leave Request Approved - ID:" + str(UID)
    body = """
        <div style="border: 1px solid #888; background-color: #eee; padding: 10px; margin-top: 10px; max-width: 800px;">
            <div style="font-weight: bold; margin-left: 10px;">Leave for ${requestor} was approved by ${approver}.  Please <u>add</u> the following to the calendar.</div>
            <div style="margin: 10px;">${timeoff}</div>
        </div> 
    """
    body = body.replace('${approver}', ApprovedBy)
    body = body.replace('${timeoff}', TimeOffFormater(TimeOff))
    body = body.replace('${requestor}', RequestedBy)
    
    MailMe(subject, 'librarytechnology@uwosh.edu', ['libraryoffice@uwosh.edu','schneidm@uwosh.edu'], body)

def DeleteEventMailed(UID, RequestedBy, ApprovedBy, TimeOff):
    subject = "Leave Request Removal - ID:" + str(UID)
    body = """
        <div style="border: 1px solid #888; background-color: #eee; padding: 10px; margin-top: 10px; max-width: 500px;">
            <div style="font-weight: bold; margin-left: 10px;">Please <u>remove</u> the following leave for ${requestor}.</div>
            <div style="margin: 10px;">${timeoff}</div>
        </div> 
    """
    body = body.replace('${approver}', ApprovedBy)
    body = body.replace('${timeoff}', TimeOffFormater(TimeOff))
    body = body.replace('${requestor}', RequestedBy)
    
    MailMe(subject, 'librarytechnology@uwosh.edu', ['libraryoffice@uwosh.edu','schneidm@uwosh.edu'], body)

    
    
def AddEventToGCAL(name, leave, duration, date, start, end):
    response = {
        'status' : 400,
        'response' : None,
    }
    
    req = {
            'summary': name + ' - ' + leave + ' ' + duration,
            'description': '',
    }
    # if float(duration) < 7:
    start_date = iso_format(datetime.datetime.strptime(date + ' ' + start.upper(), '%m/%d/%Y %I:%M %p'))
    end_date = iso_format(datetime.datetime.strptime(date + ' ' + end.upper(), '%m/%d/%Y %I:%M %p'))
    req['start'] = {
        'dateTime': start_date,
    }
    req['end'] = {
        'dateTime': end_date,
    }
    # else:
        # start_date = datetime.datetime.strftime(datetime.datetime.strptime(date + ' ' + start.upper(), '%m/%d/%Y %I:%M %p'), '%Y-%m-%d')
        # end_date = datetime.datetime.strftime(datetime.datetime.strptime(date + ' ' + end.upper(), '%m/%d/%Y %I:%M %p'), '%Y-%m-%d')
        # req['start'] = {
            # 'date': start_date,
        # }
        # req['end'] = {
            # 'date': end_date,
        # }
        
    try:
        scopes = ['https://www.googleapis.com/auth/calendar']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            GCAL_KEY,
            scopes=scopes
        )
        http = credentials.authorize(Http())
        service = discovery.build('calendar', 'v3', http=http)
        
        result = service.events().insert(
            calendarId = 'qkkjn49i0bksj786kk1mgiu0vs@group.calendar.google.com',
            body = req, 
            sendNotifications=None, 
            supportsAttachments=None, 
            maxAttendees=None
        ).execute()
        
        response['status'] = 200
        response['response'] = result
        return response
        
    except Exception as e:
        import traceback
        print traceback.format_exc()
        return response

   
def DeleteEventToGCAL(id):
    response = {
        'status' : 400,
        'response' : None,
    }
    
    try:
        scopes = ['https://www.googleapis.com/auth/calendar']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            GCAL_KEY,
            scopes=scopes
        )
        http = credentials.authorize(Http())
        service = discovery.build('calendar', 'v3', http=http)
        
        result = service.events().delete(
            calendarId = 'qkkjn49i0bksj786kk1mgiu0vs@group.calendar.google.com', 
            eventId = id, 
        ).execute()
        
        response['status'] = 200
        response['response'] = result
        return response
        
    except Exception as e:
        import traceback
        print traceback.format_exc()
        return response  