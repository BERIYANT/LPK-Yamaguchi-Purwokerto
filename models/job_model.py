from utils.database import get_db
from datetime import datetime


class JobModel:
    @staticmethod
    def create(title, company=None, location=None, description=None, requirements=None,
               salary=None, employment_type=None, application_link=None, contact_email=None,
               deadline=None, status='active', created_by=None):
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """
            INSERT INTO jobs
            (title, company, location, description, requirements, salary, employment_type,
             application_link, contact_email, deadline, status, created_by, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                title, company, location, description, requirements, salary, employment_type,
                application_link, contact_email, deadline, status, created_by, datetime.now(), datetime.now()
            )
        )
        db.commit()
        job_id = cur.lastrowid
        cur.close()
        return job_id

    @staticmethod
    def get_by_id(job_id):
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM jobs WHERE id=%s", (job_id,))
        job = cur.fetchone()
        cur.close()
        return job

    @staticmethod
    def get_all(include_inactive=True):
        db = get_db()
        cur = db.cursor(dictionary=True)
        if include_inactive:
            cur.execute("SELECT * FROM jobs ORDER BY created_at DESC")
        else:
            cur.execute("SELECT * FROM jobs WHERE status='active' ORDER BY created_at DESC")
        jobs = cur.fetchall()
        cur.close()
        return jobs

    @staticmethod
    def update(job_id, title, company=None, location=None, description=None, requirements=None,
               salary=None, employment_type=None, application_link=None, contact_email=None,
               deadline=None, status='active'):
        db = get_db()
        cur = db.cursor()
        cur.execute(
            """
            UPDATE jobs
            SET title=%s, company=%s, location=%s, description=%s, requirements=%s, salary=%s,
                employment_type=%s, application_link=%s, contact_email=%s, deadline=%s, status=%s,
                updated_at=%s
            WHERE id=%s
            """,
            (
                title, company, location, description, requirements, salary,
                employment_type, application_link, contact_email, deadline, status,
                datetime.now(), job_id
            )
        )
        db.commit()
        cur.close()

    @staticmethod
    def delete(job_id):
        db = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM jobs WHERE id=%s", (job_id,))
        db.commit()
        cur.close()
