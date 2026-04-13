from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from utils.authentication import login_required, admin_required
from models.job_model import JobModel

job_bp = Blueprint('jobs', __name__)


# Student-facing routes (view only)
@job_bp.route('/jobs')
@login_required
def list_jobs():
    jobs = JobModel.get_all(include_inactive=False)
    return render_template('student/jobs.html', jobs=jobs)


@job_bp.route('/jobs/<int:job_id>')
@login_required
def job_detail(job_id):
    job = JobModel.get_by_id(job_id)
    if not job or job.get('status') != 'active':
        flash('Lowongan tidak ditemukan atau sudah tidak aktif.')
        return redirect(url_for('jobs.list_jobs'))
    return render_template('student/job_detail.html', job=job)


# Admin routes (CRUD)
@job_bp.route('/admin/jobs')
@login_required
@admin_required
def admin_jobs():
    jobs = JobModel.get_all(include_inactive=True)
    return render_template('admin/jobs.html', jobs=jobs)


@job_bp.route('/admin/job/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_create_job():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company = request.form.get('company', '').strip() or None
        location = request.form.get('location', '').strip() or None
        description = request.form.get('description', '').strip() or None
        requirements = request.form.get('requirements', '').strip() or None
        salary = request.form.get('salary', '').strip() or None
        employment_type = request.form.get('employment_type', '').strip() or None
        application_link = request.form.get('application_link', '').strip() or None
        contact_email = request.form.get('contact_email', '').strip() or None
        deadline = request.form.get('deadline') or None
        status = request.form.get('status', 'active')

        if not title:
            flash('Judul lowongan wajib diisi.')
            return render_template('admin/create_job.html')

        try:
            JobModel.create(
                title=title,
                company=company,
                location=location,
                description=description,
                requirements=requirements,
                salary=salary,
                employment_type=employment_type,
                application_link=application_link,
                contact_email=contact_email,
                deadline=deadline,
                status=status,
                created_by=g.user['id'] if g.user else None
            )
            flash('Lowongan berhasil dibuat.')
            return redirect(url_for('jobs.admin_jobs'))
        except Exception as e:
            flash(f'Gagal membuat lowongan: {str(e)}')
            return render_template('admin/create_job.html')

    return render_template('admin/create_job.html')


@job_bp.route('/admin/job/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_job(job_id):
    job = JobModel.get_by_id(job_id)
    if not job:
        flash('Lowongan tidak ditemukan.')
        return redirect(url_for('jobs.admin_jobs'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company = request.form.get('company', '').strip() or None
        location = request.form.get('location', '').strip() or None
        description = request.form.get('description', '').strip() or None
        requirements = request.form.get('requirements', '').strip() or None
        salary = request.form.get('salary', '').strip() or None
        employment_type = request.form.get('employment_type', '').strip() or None
        application_link = request.form.get('application_link', '').strip() or None
        contact_email = request.form.get('contact_email', '').strip() or None
        deadline = request.form.get('deadline') or None
        status = request.form.get('status', 'active')

        if not title:
            flash('Judul lowongan wajib diisi.')
            return render_template('admin/edit_job.html', job=job)

        try:
            JobModel.update(
                job_id=job_id,
                title=title,
                company=company,
                location=location,
                description=description,
                requirements=requirements,
                salary=salary,
                employment_type=employment_type,
                application_link=application_link,
                contact_email=contact_email,
                deadline=deadline,
                status=status
            )
            flash('Lowongan berhasil diperbarui.')
            return redirect(url_for('jobs.admin_jobs'))
        except Exception as e:
            flash(f'Gagal memperbarui lowongan: {str(e)}')
            return render_template('admin/edit_job.html', job=job)

    return render_template('admin/edit_job.html', job=job)


@job_bp.route('/admin/job/<int:job_id>/delete')
@login_required
@admin_required
def admin_delete_job(job_id):
    job = JobModel.get_by_id(job_id)
    if not job:
        flash('Lowongan tidak ditemukan.')
        return redirect(url_for('jobs.admin_jobs'))

    try:
        JobModel.delete(job_id)
        flash('Lowongan berhasil dihapus.')
    except Exception as e:
        flash(f'Gagal menghapus lowongan: {str(e)}')
    return redirect(url_for('jobs.admin_jobs'))
