#celery CSV export of student applications.
#used llms here to generate codes which i didnt know how to 
import os
import csv
import uuid
import logging
from datetime import datetime

from app import celery
from extensions import db

logger = logging.getLogger(__name__)


@celery.task(name='tasks.exports.export_applications_csv', bind=True, max_retries=3)
def export_applications_csv(self, student_id):#particular student data export
    from flask import current_app
    try:
        from models.application import Application
        from models.drive import PlacementDrive
        from models.company import CompanyProfile

        results = (
            db.session.query(Application, PlacementDrive, CompanyProfile)
            .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
            .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)
            .filter(Application.student_id == student_id)
            .order_by(Application.application_date.desc())
            .all()
        )

        export_dir = os.path.join(current_app.root_path, 'exports')
        os.makedirs(export_dir, exist_ok=True)

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"applications_{student_id}_{timestamp}_{uuid.uuid4().hex[:6]}.csv"
        filepath = os.path.join(export_dir, filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Application_ID', 'Company_Name', 'Drive_Title',
                'Job_Description', 'Application_Date', 'Status', 'Feedback',
            ])

            for app, drive, company in results:
                writer.writerow([
                    app.id,
                    company.company_name,
                    drive.job_title,
                    drive.job_description,
                    str(app.application_date) if app.application_date else '',
                    app.status,
                    app.feedback or '',
                ])

        logger.info(
            "CSV export completed for student %s: %s (%d records)",
            student_id, filename, len(results),
        )

        return filename

    except Exception as exc:
        logger.error(
            "Error exporting applications for student %s: %s",
            student_id, exc, exc_info=True,
        )
        raise self.retry(exc=exc, countdown=30)


@celery.task(name='tasks.exports.export_company_applications_csv', bind=True, max_retries=3)
def export_company_applications_csv(self, company_id, status=None):#company drive csv
    from flask import current_app
    try:
        from models.application import Application
        from models.drive import PlacementDrive
        from models.student import StudentProfile

        query = (
            db.session.query(Application, PlacementDrive, StudentProfile)
            .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
            .join(StudentProfile, Application.student_id == StudentProfile.id)
            .filter(PlacementDrive.company_id == company_id)
        )
        
        if status:
            query = query.filter(Application.status == status)
            
        results = query.order_by(Application.application_date.desc()).all()

        export_dir = os.path.join(current_app.root_path, 'exports')
        os.makedirs(export_dir, exist_ok=True)

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"company_apps_{company_id}_{timestamp}_{uuid.uuid4().hex[:6]}.csv"
        filepath = os.path.join(export_dir, filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Application_ID', 'Drive_Title', 'Student_Name',
                'Branch', 'CGPA', 'Application_Date', 'Status'
            ])

            for app, drive, student in results:
                writer.writerow([
                    app.id,
                    drive.job_title,
                    student.full_name,
                    student.branch,
                    str(student.cgpa) if student.cgpa else '',
                    str(app.application_date) if app.application_date else '',
                    app.status
                ])

        logger.info("CSV export completed for company %s", company_id)
        return filename

    except Exception as exc:
        logger.error("Error exporting applications for company %s: %s", company_id, exc)
        raise self.retry(exc=exc, countdown=30)


@celery.task(name='tasks.exports.export_admin_applications_csv', bind=True, max_retries=3)
def export_admin_applications_csv(self, status=None):#all applications csv
    from flask import current_app

    try:
        from models.application import Application
        from models.drive import PlacementDrive
        from models.company import CompanyProfile
        from models.student import StudentProfile
        from models.placement import Placement

        query = (
            db.session.query(Application, PlacementDrive, CompanyProfile, StudentProfile, Placement)
            .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
            .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)
            .join(StudentProfile, Application.student_id == StudentProfile.id)
            .outerjoin(Placement, Application.id == Placement.application_id)
        )

        if status:
            query = query.filter(Application.status == status)

        results = query.order_by(Application.application_date.desc()).all()

        export_dir = os.path.join(current_app.root_path, 'exports')
        os.makedirs(export_dir, exist_ok=True)

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"master_apps_{timestamp}_{uuid.uuid4().hex[:6]}.csv"
        filepath = os.path.join(export_dir, filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Application_ID', 'Application_Date', 'Application_Status', 'Feedback',
                'Student_Name', 'Student_RollNo', 'Student_Branch', 'Student_CGPA', 'Student_Phone',
                'Company_Name', 'Company_Industry', 'Company_Website',
                'Drive_Title', 'Drive_Location', 'Drive_Salary', 'Drive_Deadline',
                'Placement_Package', 'Placement_Status', 'Offer_Date'
            ])

            for app, drive, company, student, placement in results:
                writer.writerow([
                    app.id,
                    str(app.application_date) if app.application_date else '',
                    app.status,
                    app.feedback or '',
                    student.full_name,
                    student.roll_number or '',
                    student.branch or '',
                    student.cgpa or '',
                    student.phone or '',
                    company.company_name,
                    company.industry or '',
                    company.website or '',
                    drive.job_title,
                    drive.location or '',
                    drive.salary or '',
                    str(drive.application_deadline) if drive.application_deadline else '',
                    placement.salary if placement else '',
                    'Accepted' if placement and placement.is_accepted else ('Pending' if placement else ''),
                    str(placement.created_at) if placement and placement.created_at else ''
                ])

        logger.info("Master CSV export completed")
        return filename

    except Exception as exc:
        logger.error("Error exporting master applications: %s", exc)
        raise self.retry(exc=exc, countdown=30)
