from datetime import datetime
from flask import current_app
from extensions import db, mail
from flask_mail import Message
from celery import shared_task
from models.user import User
from models.application import Application
from models.drive import PlacementDrive
from models.notification import Notification

@shared_task
def send_test_link_email(application_id, test_link, custom_message):
    app = Application.query.get(application_id)
    if not app:
        return
    student = app.student
    user = student.user
    
    msg = Message(f"Test Link for {app.drive.job_title} at {app.drive.company.company_name}",
                  recipients=[user.email])
    
    body = f"Hello {student.full_name},\n\n"
    body += f"You have been invited to take a test for the position of {app.drive.job_title} at {app.drive.company.company_name}.\n\n"
    if custom_message:
        body += f"Message from company:\n{custom_message}\n\n"
    body += f"Test Link: {test_link}\n\n"
    body += "Best of luck!\nPlacement Portal Team"
    
    msg.body = body
    mail.send(msg)
    
    # Create notification
    notif = Notification(
        user_id=user.id,
        user_type='student',
        title="Test Link Received",
        message=f"You received a test link for {app.drive.company.company_name} - {app.drive.job_title}.",
        link="/student/applications"
    )
    db.session.add(notif)
    db.session.commit()

@shared_task
def send_interview_invite_email(application_id, interview_link, interview_date, custom_message):
    app = Application.query.get(application_id)
    if not app:
        return
    student = app.student
    user = student.user
    
    msg = Message(f"Interview Scheduled for {app.drive.job_title} at {app.drive.company.company_name}",
                  recipients=[user.email])
    
    body = f"Hello {student.full_name},\n\n"
    body += f"Your interview for the position of {app.drive.job_title} at {app.drive.company.company_name} has been scheduled.\n\n"
    body += f"Date: {interview_date}\n"
    body += f"Interview Link: {interview_link}\n\n"
    if custom_message:
        body += f"Message from company:\n{custom_message}\n\n"
    body += "Best of luck!\nPlacement Portal Team"
    msg.body = body
    
    # Generate ICS attachment
    try:
        from datetime import timedelta
        # Parse the datetime, defaulting to 1 hour duration
        if hasattr(app, 'interview_scheduled') and app.interview_scheduled:
            start_dt = app.interview_scheduled
            end_dt = start_dt + timedelta(hours=1)
            
            dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            dtstart = start_dt.strftime("%Y%m%dT%H%M%SZ")
            dtend = end_dt.strftime("%Y%m%dT%H%M%SZ")
            
            ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Placement Portal//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:Interview: {app.drive.job_title} at {app.drive.company.company_name}
DESCRIPTION:Interview Link: {interview_link}\\n\\nMessage: {custom_message}
LOCATION:{interview_link}
STATUS:CONFIRMED
SEQUENCE:0
ACTION:DISPLAY
END:VEVENT
END:VCALENDAR"""
            msg.attach('interview_invite.ics', 'text/calendar', ics_content.encode('utf-8'))
    except Exception as e:
        current_app.logger.error(f"Error creating ICS: {e}")

    mail.send(msg)
    
    # Create notification
    notif = Notification(
        user_id=user.id,
        user_type='student',
        title="Interview Scheduled",
        message=f"Your interview for {app.drive.company.company_name} is scheduled on {interview_date}.",
        link="/student/applications"
    )
    db.session.add(notif)
    db.session.commit()

@shared_task
def send_shortlist_to_admin_email(drive_id, company_name):
    # Find all admin users
    admins = User.query.filter_by(role='admin', is_active=True).all()
    if not admins:
        return
        
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return
        
    admin_emails = [a.email for a in admins]
    
    msg = Message(f"Shortlist Finalized: {company_name} - {drive.job_title}",
                  recipients=admin_emails)
    
    body = f"Hello Admin,\n\n"
    body += f"{company_name} has updated their shortlist/selections for the drive: {drive.job_title}.\n\n"
    body += "Please log in to the admin dashboard to review the updated applications or export the list.\n\n"
    body += "Placement Portal Team"
    
    msg.body = body
    mail.send(msg)
    
    # Create notification for admins
    for admin in admins:
        notif = Notification(
            user_id=admin.id,
            user_type='admin',
            title="Shortlist Updated",
            message=f"{company_name} updated the shortlist for {drive.job_title}.",
            link=f"/admin/drives/{drive_id}"
        )
        db.session.add(notif)
    db.session.commit()

@shared_task
def notify_status_change(application_id, new_status, feedback):
    app = Application.query.get(application_id)
    if not app:
        return
    student = app.student
    user = student.user
    
    # Create notification
    notif = Notification(
        user_id=user.id,
        user_type='student',
        title=f"Application Status: {new_status.capitalize()}",
        message=f"Your application for {app.drive.company.company_name} has been marked as {new_status}.",
        link="/student/applications"
    )
    db.session.add(notif)
    db.session.commit()
    
    # Only email for major status changes
    if new_status in ['selected', 'rejected']:
        msg = Message(f"Application Update: {app.drive.company.company_name}",
                      recipients=[user.email])
        
        body = f"Hello {student.full_name},\n\n"
        body += f"Your application status for {app.drive.job_title} at {app.drive.company.company_name} has been updated to: {new_status.upper()}.\n\n"
        if feedback:
            body += f"Feedback:\n{feedback}\n\n"
        body += "Log in to the portal for more details.\n\nPlacement Portal Team"
        
        msg.body = body
        mail.send(msg)
