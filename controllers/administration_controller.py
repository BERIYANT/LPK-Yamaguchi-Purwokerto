from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from mysql.connector import IntegrityError

from utils.authentication import admin_required, login_required
from utils.database import get_db

administration_bp = Blueprint('administration', __name__)


def _year(value):
    try:
        selected = int(value)
    except (TypeError, ValueError):
        selected = date.today().year
    return max(2024, min(selected, date.today().year + 1))


def _years():
    return range(date.today().year + 1, 2023, -1)


@administration_bp.route('/students', methods=['GET', 'POST'])
@login_required
@admin_required
def students():
    db = get_db()
    cur = db.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cur.execute("""
                INSERT INTO student_profiles
                    (nis, full_name, gender, birth_place, birth_date, school_name, nik,
                     phone, address, rt_rw, village, district, city, province,
                     program_name, enrollment_date, graduation_date, departure_date,
                     job_sector, placement, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                request.form['nis'].strip(), request.form['full_name'].strip(),
                request.form.get('gender') or None, request.form.get('birth_place') or None,
                request.form.get('birth_date') or None, request.form.get('school_name') or None,
                request.form.get('nik') or None, request.form.get('phone') or None,
                request.form.get('address') or None, request.form.get('rt_rw') or None,
                request.form.get('village') or None, request.form.get('district') or None,
                request.form.get('city') or None, request.form.get('province') or None,
                request.form.get('program_name') or None, request.form['enrollment_date'],
                request.form.get('graduation_date') or None,
                request.form.get('departure_date') or None,
                request.form.get('job_sector') or None, request.form.get('placement') or None,
                request.form.get('status', 'aktif'), request.form.get('notes') or None
            ))
            db.commit()
            flash('Data siswa berhasil ditambahkan.', 'success')
            return redirect(url_for('administration.student_detail', nis=request.form['nis'].strip()))
        except IntegrityError:
            db.rollback()
            flash('NIS sudah terdaftar. Gunakan NIS lain.', 'danger')

    selected_year = _year(request.args.get('year'))
    nis = request.args.get('nis', '').strip()
    cur.execute("""
        SELECT * FROM student_profiles
        WHERE YEAR(enrollment_date) = %s AND (%s = '' OR nis LIKE %s OR full_name LIKE %s)
        ORDER BY enrollment_date DESC, full_name
    """, (selected_year, nis, f'%{nis}%', f'%{nis}%'))
    rows = cur.fetchall()
    cur.close()
    return render_template('admin/administration/students.html', students=rows,
                           selected_year=selected_year, years=_years(), search_nis=nis)


@administration_bp.route('/students/<nis>')
@login_required
@admin_required
def student_detail(nis):
    cur = get_db().cursor(dictionary=True)
    cur.execute('SELECT * FROM student_profiles WHERE nis = %s', (nis,))
    student = cur.fetchone()
    cur.close()
    if not student:
        flash('Data siswa tidak ditemukan.', 'warning')
        return redirect(url_for('administration.students'))
    return render_template('admin/administration/student_detail.html', student=student)


@administration_bp.route('/student-payments', methods=['GET', 'POST'])
@login_required
@admin_required
def student_payments():
    db = get_db()
    cur = db.cursor(dictionary=True)
    if request.method == 'POST':
        nis = request.form['nis'].strip()
        cur.execute('SELECT id FROM student_profiles WHERE nis = %s', (nis,))
        student = cur.fetchone()
        if not student:
            flash('NIS tidak ditemukan.', 'danger')
        else:
            payment_type = request.form['payment_type']
            installment = request.form.get('installment_no') or None
            if payment_type == 'education' and installment is None:
                flash('Angsuran pendidikan wajib dipilih.', 'danger')
            else:
                try:
                    cur.execute("""
                        SELECT id FROM student_payments
                        WHERE student_id=%s AND payment_type=%s
                          AND ((installment_no IS NULL AND %s IS NULL) OR installment_no=%s)
                    """, (student['id'], payment_type, installment, installment))
                    if cur.fetchone():
                        flash('Jenis pembayaran atau angsuran tersebut sudah tercatat.', 'danger')
                        cur.close()
                        return redirect(url_for('administration.student_payments', nis=nis))
                    cur.execute("""
                        INSERT INTO student_payments
                            (student_id, payment_type, installment_no, payment_date, amount, note)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (student['id'], payment_type, installment,
                          request.form['payment_date'], request.form['amount'],
                          request.form.get('note') or None))
                    db.commit()
                    flash('Pembayaran berhasil dicatat.', 'success')
                    return redirect(url_for('administration.student_payments', nis=nis))
                except IntegrityError:
                    db.rollback()
                    flash('Jenis pembayaran atau angsuran tersebut sudah tercatat.', 'danger')

    nis = request.args.get('nis', '').strip()
    student = None
    payments = []
    totals = {}
    if nis:
        cur.execute('SELECT * FROM student_profiles WHERE nis = %s', (nis,))
        student = cur.fetchone()
        if student:
            cur.execute("""
                SELECT * FROM student_payments WHERE student_id = %s
                ORDER BY payment_date, FIELD(payment_type, 'registration','education','mcu','dormitory'), installment_no
            """, (student['id'],))
            payments = cur.fetchall()
            cur.execute("""
                SELECT payment_type, COALESCE(SUM(amount), 0) total
                FROM student_payments WHERE student_id = %s GROUP BY payment_type
            """, (student['id'],))
            totals = {row['payment_type']: row['total'] for row in cur.fetchall()}
        else:
            flash('NIS tidak ditemukan.', 'warning')
    cur.close()
    return render_template('admin/administration/student_payments.html', student=student,
                           payments=payments, totals=totals, search_nis=nis)


@administration_bp.route('/payment-recap')
@login_required
@admin_required
def payment_recap():
    selected_year = _year(request.args.get('year'))
    cur = get_db().cursor(dictionary=True)
    cur.execute("""
        SELECT s.nis, s.full_name,
          COALESCE(SUM(CASE WHEN p.payment_type='registration' THEN p.amount ELSE 0 END),0) registration,
          COALESCE(SUM(CASE WHEN p.payment_type='education' THEN p.amount ELSE 0 END),0) education,
          COALESCE(SUM(CASE WHEN p.payment_type='mcu' THEN p.amount ELSE 0 END),0) mcu,
          COALESCE(SUM(CASE WHEN p.payment_type='dormitory' THEN p.amount ELSE 0 END),0) dormitory,
          COALESCE(SUM(p.amount),0) total
        FROM student_profiles s
        LEFT JOIN student_payments p ON p.student_id=s.id AND YEAR(p.payment_date)=%s
        WHERE YEAR(s.enrollment_date)=%s
        GROUP BY s.id, s.nis, s.full_name ORDER BY s.full_name
    """, (selected_year, selected_year))
    rows = cur.fetchall()
    cur.close()
    return render_template('admin/administration/payment_recap.html', rows=rows,
                           selected_year=selected_year, years=_years())


@administration_bp.route('/sensei', methods=['GET', 'POST'])
@login_required
@admin_required
def sensei():
    db = get_db()
    cur = db.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cur.execute("""
                INSERT INTO sensei_profiles
                    (sensei_code, full_name, phone, address, teaching_field, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (request.form['sensei_code'].strip(), request.form['full_name'].strip(),
                  request.form.get('phone') or None, request.form.get('address') or None,
                  request.form.get('teaching_field') or None, request.form.get('status', 'aktif')))
            db.commit()
            flash('Data Sensei berhasil ditambahkan.', 'success')
            return redirect(url_for('administration.sensei_detail', sensei_code=request.form['sensei_code'].strip()))
        except IntegrityError:
            db.rollback()
            flash('ID Sensei sudah terdaftar.', 'danger')
    query = request.args.get('q', '').strip()
    cur.execute("""
        SELECT * FROM sensei_profiles
        WHERE %s='' OR sensei_code LIKE %s OR full_name LIKE %s
        ORDER BY full_name
    """, (query, f'%{query}%', f'%{query}%'))
    rows = cur.fetchall()
    cur.close()
    return render_template('admin/administration/sensei.html', sensei=rows, query=query)


@administration_bp.route('/sensei/<sensei_code>')
@login_required
@admin_required
def sensei_detail(sensei_code):
    cur = get_db().cursor(dictionary=True)
    cur.execute('SELECT * FROM sensei_profiles WHERE sensei_code=%s', (sensei_code,))
    teacher = cur.fetchone()
    cur.close()
    if not teacher:
        flash('Data Sensei tidak ditemukan.', 'warning')
        return redirect(url_for('administration.sensei'))
    return render_template('admin/administration/sensei_detail.html', teacher=teacher)


@administration_bp.route('/teaching-schedules', methods=['GET', 'POST'])
@login_required
@admin_required
def teaching_schedules():
    db = get_db()
    cur = db.cursor(dictionary=True)
    if request.method == 'POST':
        cur.execute("""
            INSERT INTO teaching_schedules
                (sensei_id, teaching_date, start_time, end_time, class_name, subject)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (request.form['sensei_id'], request.form['teaching_date'],
              request.form['start_time'], request.form['end_time'],
              request.form['class_name'].strip(), request.form['subject'].strip()))
        db.commit()
        flash('Jadwal mengajar berhasil ditambahkan.', 'success')
        return redirect(url_for('administration.teaching_schedules'))

    sensei_id = request.args.get('sensei_id', type=int)
    schedule_date = request.args.get('date', '')
    filters, params = [], []
    if sensei_id:
        filters.append('j.sensei_id=%s'); params.append(sensei_id)
    if schedule_date:
        filters.append('j.teaching_date=%s'); params.append(schedule_date)
    where = ' AND '.join(filters) if filters else '1=1'
    cur.execute('SELECT id, sensei_code, full_name FROM sensei_profiles WHERE status="aktif" ORDER BY full_name')
    teachers = cur.fetchall()
    cur.execute(f"""
        SELECT j.*, s.sensei_code, s.full_name,
               CASE DAYOFWEEK(j.teaching_date)
                 WHEN 1 THEN 'Minggu' WHEN 2 THEN 'Senin' WHEN 3 THEN 'Selasa'
                 WHEN 4 THEN 'Rabu' WHEN 5 THEN 'Kamis' WHEN 6 THEN 'Jumat' WHEN 7 THEN 'Sabtu'
               END day_name
        FROM teaching_schedules j JOIN sensei_profiles s ON s.id=j.sensei_id
        WHERE {where} ORDER BY j.teaching_date DESC, j.start_time
    """, tuple(params))
    schedules = cur.fetchall()
    cur.close()
    return render_template('admin/administration/schedules.html', teachers=teachers,
                           schedules=schedules, selected_sensei=sensei_id,
                           selected_date=schedule_date)
