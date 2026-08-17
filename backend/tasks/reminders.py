# daily reminder  8 am..time set at ext.py
import logging
from datetime import datetime, timedelta
from app import celery
from extensions import db

logger = logging.getLogger(__name__)

@celery.task(name='tasks.reminders.send_daily_reminders', bind=True, max_retries=3)
def send_daily_reminders(self):#interview,deadline
    from flask import current_app 
    try:
        from models.application import Application
        from models.drive import PlacementDrive
        from models.student import StudentProfile
        from models.company import CompanyProfile
        from models.user import User

        now = datetime.utcnow()
        tomorrow = now + timedelta(hours=24)

        #deadlines
        upcoming_deadlines = (
            db.session.query(PlacementDrive, CompanyProfile)
            .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)
            .filter(
                PlacementDrive.status == 'approved',
                PlacementDrive.application_deadline >= now,
                PlacementDrive.application_deadline <= tomorrow,
            )
            .all()
        )

        #active applications
        active_applications = (
            db.session.query(Application, StudentProfile, PlacementDrive, CompanyProfile)
            .join(StudentProfile, Application.student_id == StudentProfile.id)
            .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
            .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)
            .filter(
                Application.status.in_(['shortlisted', 'interview', 'selected'])
            )
            .all()
        )

        user_messages = {}

        # fill  active applications
        for app, student, drive, company in active_applications:
            user = User.query.get(student.user_id)
            if not user:
                continue

            if user.email not in user_messages:
                user_messages[user.email] = {
                    'name': student.full_name,
                    'student_id': student.id,
                    'shortlisted': [],
                    'interview': [],
                    'selected': []
                }

            if app.status == 'shortlisted':
                user_messages[user.email]['shortlisted'].append(f"'{drive.job_title}' at {company.company_name}")
            elif app.status == 'interview':
                user_messages[user.email]['interview'].append(f"'{drive.job_title}' at {company.company_name}")
            elif app.status == 'selected':
                from models.placement import Placement
                placement = Placement.query.filter_by(application_id=app.id).first()
                if placement and placement.is_accepted:
                    continue  # Do not remind if already accepted
                user_messages[user.email]['selected'].append(f"'{drive.job_title}' at {company.company_name}")

        #  all student deadlines
        all_students = StudentProfile.query.all()
        for student in all_students:
            user = User.query.get(student.user_id)
            if not user:
                continue

            if user.email not in user_messages:
                user_messages[user.email] = {
                    'name': student.full_name,
                    'student_id': student.id,
                    'shortlisted': [],
                    'interview': [],
                    'selected': []
                }

        emails_sent = 0
        for email, data in user_messages.items():
            lines = []
            lines.append(f"Dear {data['name']},\n")
            lines.append("Here is your daily Placement Portal update:\n")
            
            has_updates = False
            
            if data['shortlisted']:
                has_updates = True
                lines.append("=== SHORTLISTED ===")
                for item in data['shortlisted']:
                    lines.append(f"- You have been shortlisted for {item}.")
                lines.append("")
                
            if data['interview']:
                has_updates = True
                lines.append("=== INTERVIEW ===")
                for item in data['interview']:
                    lines.append(f"- You have been selected for an interview for {item}. You will be contacted shortly.")
                lines.append("")

            if data['selected']:
                has_updates = True
                lines.append("=== JOB OFFERS ===")
                for item in data['selected']:
                    lines.append(f"- Congratulations! You have been selected for {item}. Please log in to accept the offer.")
                lines.append("")

            # Add deadlines
            student_id = data['student_id']
            unapplied_deadlines = []
            for drive, company in upcoming_deadlines:
                # Check if this student applied to this drive
                app = Application.query.filter_by(student_id=student_id, drive_id=drive.id).first()
                if not app:
                    deadline_str = drive.application_deadline.strftime('%Y-%m-%d') if drive.application_deadline else 'N/A'
                    unapplied_deadlines.append(f"- '{drive.job_title}' at {company.company_name} (Deadline: {deadline_str})")
            
            if unapplied_deadlines:
                has_updates = True
                lines.append("=== UPCOMING DEADLINES ===")
                lines.append("The following drives are closing soon. Please apply if you are eligible:")
                for item in unapplied_deadlines:
                    lines.append(item)
                lines.append("")

            if has_updates:
                lines.append("Best regards,\nPlacement Portal Team")
                body = "\n".join(lines)
                subject = "Daily Placement Portal Update"
                _send_email(subject, [email], body)
                emails_sent += 1

        summary = f"Daily reminders sent: {emails_sent} email(s) containing updates and deadlines."
        logger.info(summary)
        return summary

    except Exception as exc:
        logger.error("error sending daily reminders: %s", exc, exc_info=True)
        raise self.retry(exc=exc, countdown=60)


def _send_email(subject, recipients, body):#send mail via flsk mail
    
    try:
        from flask_mail import Message
        from extensions import mail

        msg = Message(
            subject=subject,
            recipients=recipients,
            body=body,
        )
        mail.send(msg)
        logger.info("Email sent to %s: %s", recipients, subject)
#these error handling by llm
    except ImportError:
        logger.warning(
            "Flask-Mail not installed. Logging email instead.\n"
            "Subject: %s\nTo: %s\nBody:\n%s", subject, recipients, body,
        )
    except Exception as e:
        logger.warning(
            "mail  not  configured): %s\n"
            "Subject: %s\nTo: %s\nBody:\n%s", e, subject, recipients, body,
        )
