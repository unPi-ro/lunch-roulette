from flask import render_template
from app import app
from app.models import User, Company
from threading import Thread
import sendgrid
import urllib
import os
from sendgrid.helpers.mail import *

INTRO="[Lunch Roulette{co}]"

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

def send_async_email(app, subject, sender, recipient, text_body, html_body,
        extras=None, attachments=None):
    with app.app_context():
        mail = Mail()
        mail.subject = subject
        mail.from_email = Email(sender)
        if not extras: extras = Personalization()
        extras.add_to(Email(recipient))
        mail.add_personalization(extras)
        if text_body: mail.add_content(Content("text/plain", text_body))
        if html_body: mail.add_content(Content("text/html", html_body))
        if attachments:
            for item in attachments: mail.add_attachment(item)
        # print(mail.get())
        response = sg.client.mail.send.post(request_body=mail.get())
        # TODO: log the response
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)

def send_email(subject, sender, recipient, text_body, html_body=None,
        extras=None, attachments=None):
    Thread(target=send_async_email, args=(app, subject,
                sender, recipient, text_body, html_body,
                extras, attachments)).start()

def send_all_email(user, subject, text):
    custom = Personalization()
    corporate = ""
    if user.is_admin:
        filter = { 'company_id': user.company_id, 'confirmed': True }
        corporate = " for " + Company.query.get(user.company_id).name
    if user.is_super: filter = { 'confirmed': True }
    # send announcement to confirmed users, # TODO: paginate for 1K+ users
    users = User.query.filter_by(**filter).all()
    # remove user from BCC: as it cannot be set together with recipient/To:
    users.remove(user)
    for u in users: custom.add_bcc(Email(u.email))
    send_email(INTRO.format(co=corporate) + ' Announcement :: ' + subject,
        sender=app.config['SENDGRID_DEFAULT_FROM'],
        recipient=user.email,
        text_body=render_template('email/announcement_email.txt',
                 user=user, firstname="Colleague", message=text),
        html_body=render_template('email/announcement_email.html',
                 user=user, firstname="Colleague", message=text),
        extras=custom)

def send_lunch_invite_email(pair):
    custom = Personalization()
    userList = []
    for uid in pair: userList.append(User.query.get(int(uid)))
    user = userList.pop()
    corporate = " for " + Company.query.get(user.company_id).name
    for u in userList: custom.add_cc(Email(u.email))
    usertoo = userList.pop()
    send_email(INTRO.format(co=corporate) + ' You are Invited for Lunch Today',
        sender=app.config['SENDGRID_DEFAULT_FROM'],
        recipient=user.email,
        text_body=render_template('email/lunch_invite_email.txt',
                 username=user.username, usernametoo=usertoo.username,
                 lunchtime=user.lunch_time, canteen=user.canteen),
        html_body=render_template('email/lunch_invite_email.html',
                 username=user.username, usernametoo=usertoo.username,
                 lunchtime=user.lunch_time, canteen=user.canteen),
        extras=custom)

def send_invite_email(user, to_name, to_email, text):
    corporate = " for " + Company.query.get(user.company_id).name
    send_email(INTRO.format(co=corporate) + ' Invitation',
               sender=app.config['SENDGRID_DEFAULT_FROM'], recipient=to_email,
               text_body=render_template('email/invite_email.txt',
                        user=user, firstname=to_name, message=text),
               html_body=render_template('email/invite_email.html',
                        user=user, firstname=to_name, message=text))

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    if user.confirmed:
        corporate = " for " + Company.query.get(user.company_id).name
    else:
        corporate = ""
    send_email(INTRO.format(co=corporate) + ' Reset Your Password',
               sender=app.config['SENDGRID_DEFAULT_FROM'],
               recipient=user.email,
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_confirm_email(user):
    token = user.get_confirm_email_token()
    # we don't know yet // we're not sure who the user really is
    corporate = ""
    send_email(INTRO.format(co=corporate) + ' Confirm Your Email',
               sender=app.config['SENDGRID_DEFAULT_FROM'],
               recipient=user.email,
               text_body=render_template('email/confirm_email.txt',
                                         user=user, token=token),
               html_body=render_template('email/confirm_email.html',
                                         user=user, token=token))

# from https://stackoverflow.com/questions/45076896/send-email-as-calendar-invite-appointment-in-sendgrid-c-sharp
# def build_meeting_invite(subject, from, to, desc): #, startTime, endTime, location):
