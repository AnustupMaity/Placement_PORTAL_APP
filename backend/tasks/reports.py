#celery  monthly placement report

import os
import logging
from datetime import datetime, timedelta
from sqlalchemy import func
from app import celery
from extensions import db

logger = logging.getLogger(__name__)


@celery.task(name='tasks.reports.generate_monthly_report', bind=True, max_retries=3)
def generate_monthly_report(self):#making the report
    from flask import current_app

    try:
        from models.drive import PlacementDrive
        from models.application import Application
        from models.placement import Placement
        from models.company import CompanyProfile
        from models.user import User

        # last 30 days calc
        today = datetime.utcnow()
        start_date = today - timedelta(days=30)
        
        report_period = f"Last 30 Days ({start_date.strftime('%d %b %Y')} - {today.strftime('%d %b %Y')})"

    #stats calc
        drives_conducted = PlacementDrive.query.filter(
            PlacementDrive.created_at >= start_date,
            PlacementDrive.created_at <= today,
        ).count()

        total_applications = Application.query.filter(
            Application.application_date >= start_date,
            Application.application_date <= today,
        ).count()

        students_selected = Application.query.filter(
            Application.status == 'selected',
            Application.application_date >= start_date,
            Application.application_date <= today,
        ).count()

        students_rejected = Application.query.filter(
            Application.status == 'rejected',
            Application.application_date >= start_date,
            Application.application_date <= today,
        ).count()

        total_placements = Placement.query.filter(
            Placement.created_at >= start_date,
            Placement.created_at <= today,
        ).count()

        top_companies_query = (
            db.session.query(
                CompanyProfile.company_name,
                func.count(Placement.id).label('placement_count'),
            )
            .join(Placement, Placement.company_id == CompanyProfile.id)
            .filter(
                Placement.created_at >= start_date,
                Placement.created_at <= today,
            )
            .group_by(CompanyProfile.company_name)
            .order_by(func.count(Placement.id).desc())
            .limit(10)
            .all()
        )

        top_companies = [
            {'name': name, 'placements': count}
            for name, count in top_companies_query
        ]

        stats = {
            'report_period': report_period,
            'drives_conducted': drives_conducted,
            'total_applications': total_applications,
            'students_selected': students_selected,
            'students_rejected': students_rejected,
            'total_placements': total_placements,
            'top_companies': top_companies,
        }

        html_content = current_app.jinja_env.get_template( #from trmplete/report/montly report.html
            'reports/monthly_report.html'
        ).render(**stats)


        reports_dir = os.path.join(current_app.root_path, 'exports', 'reports')#save report local 
        os.makedirs(reports_dir, exist_ok=True)

        base_filename = f"monthly_report_{today.strftime('%Y_%m_%d')}"
        report_path_html = os.path.join(reports_dir, base_filename + '.html')
        report_path_pdf = os.path.join(reports_dir, base_filename + '.pdf')

        with open(report_path_html, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(" report  saved to %s", report_path_html)
        
        
        # xhtml2pdf was suggested by chatgpt and the code below made using llm
        pdf_generated = False
        try:
            from xhtml2pdf import pisa
            with open(report_path_pdf, "w+b") as result_file:
                pisa_status = pisa.CreatePDF(html_content, dest=result_file)
            if not pisa_status.err:
                pdf_generated = True
                logger.info("Monthly report PDF saved to %s", report_path_pdf)
            else:
                logger.error("Error generating PDF: %s", pisa_status.err)
        except ImportError:
            logger.warning("xhtml2pdf not installed. Skipping PDF generation.")
        except Exception as e:
            logger.error("Failed to generate PDF: %s", e)




        users = User.query.filter(User.role.in_(['admin', 'student'])).all()#email monty report to admin+student
        recipient_emails = [u.email for u in users if u.email]

        if recipient_emails:
            _send_report_email(
                subject=f" Monthly Placement Report – {report_period}",
                recipients=recipient_emails,
                html_body=html_content,
                pdf_path=report_path_pdf if pdf_generated else None
            )

        return {
            'status': 'completed',
            'report_period': report_period,
            'report_file_html': report_path_html,
            'report_file_pdf': report_path_pdf if pdf_generated else None,
            'stats': stats,
        }

    except Exception as exc:
        logger.error("error generating  : %s", exc, exc_info=True)
        raise self.retry(exc=exc, countdown=120)


def _send_report_email(subject, recipients, html_body, pdf_path=None):#send mail use flask mail
    try:
        from flask_mail import Message
        from extensions import mail

        msg = Message(
            subject=subject,
            recipients=recipients,
            html=html_body,
        )
        
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as fp:
                msg.attach(os.path.basename(pdf_path), 'application/pdf', fp.read())

        mail.send(msg)
        logger.info("Monthly report emailed to %s", recipients)

#error handling sugegsted by llm...below part code

    except ImportError:
        logger.warning(
            "Flask-Mail not installed. Report saved to file only.\nRecipients: %s", recipients,
        )
    except Exception as e:
        logger.warning(
            "Failed to email report (mail may not be configured): %s\nRecipients: %s",
            e, recipients,
        )


