from apiclient import discovery
from httplib2 import Http
from plone import api
from Products.Five import BrowserView
from oauth2client.service_account import ServiceAccountCredentials
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

import datetime,json,urllib,pytz,smtplib


GCAL_KEY = '/opt/plone/plone-5-zeo-0/zeocluster/liboff.google.private.key'
#GCAL_KEY = '/home/vagrant/Plone/zinstance/liboff.google.private.key'



def MailMe(subject, from_email, to_emails, body):
    registry = getUtility(IRegistry)
    smtp_host = registry['plone.smtp_host']
    smtp_port = registry['plone.smtp_port']
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = ','.join(from_email)
    msg['To'] = ','.join(to_emails)

    mail = MIMEText(body, 'html')
    msg.attach(mail)

    s = smtplib.SMTP(smtp_host, smtp_port)
    s.sendmail(','.join(from_email), ','.join(to_emails), msg.as_string())
    s.quit()



def iso_format(dt):
    central = pytz.timezone('US/Central')
    loc_dt = central.localize(dt)
    iso = loc_dt.isoformat()
    return iso

def AddEventToGCAL(name, leave, duration, date, start, end):
    response = {
        'status' : 400,
        'response' : None,
    }
    
    req = {
            'summary': name + ' - ' + leave + ' ' + duration,
            'description': '',
    }
    if float(duration) < 7:
        start_date = iso_format(datetime.datetime.strptime(date + ' ' + start.upper(), '%m/%d/%Y %I:%M %p'))
        end_date = iso_format(datetime.datetime.strptime(date + ' ' + end.upper(), '%m/%d/%Y %I:%M %p'))
        req['start'] = {
            'dateTime': start_date,
        }
        req['end'] = {
            'dateTime': end_date,
        }
    else:
        start_date = datetime.datetime.strftime(datetime.datetime.strptime(date + ' ' + start.upper(), '%m/%d/%Y %I:%M %p'), '%Y-%m-%d')
        end_date = datetime.datetime.strftime(datetime.datetime.strptime(date + ' ' + end.upper(), '%m/%d/%Y %I:%M %p'), '%Y-%m-%d')
        req['start'] = {
            'date': start_date,
        }
        req['end'] = {
            'date': end_date,
        }
        
    try:
        scopes = ['https://www.googleapis.com/auth/calendar']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            GCAL_KEY,
            scopes=scopes
        )
        http = credentials.authorize(Http())
        service = discovery.build('calendar', 'v3', http=http)
        
        result = service.events().insert(
            calendarId = 'libraryoffice@uwosh.edu', 
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
            calendarId = 'libraryoffice@uwosh.edu', 
            eventId = id, 
        ).execute()
        
        response['status'] = 200
        response['response'] = result
        return response
        
    except Exception as e:
        import traceback
        print traceback.format_exc()
        return response  