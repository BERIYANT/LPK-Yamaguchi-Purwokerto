from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from utils.authentication import login_required
from utils.database import get_db
from datetime import datetime

forum_bp = Blueprint('forum', __name__)

@forum_bp.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        title = request.form['title'].strip()
        body = request.form['body'].strip()
        
        if not title or not body:
            flash("Judul dan isi diskusi tidak boleh kosong.")
            return redirect(url_for('forum.forum'))
        
        cur.execute("""
            INSERT INTO forum_posts (title, body, user_id, created_at) 
            VALUES (%s, %s, %s, %s)
        """, (title, body, g.user['id'], datetime.now()))
        db.commit()
        flash("Topik diskusi berhasil dibuat.")
        return redirect(url_for('forum.forum'))
    
    # Filter and sorting
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'latest')
    
    # Base query
    query = """
        SELECT p.*, u.username, u.full_name, u.role, u.avatar,
               (SELECT COUNT(*) FROM forum_replies WHERE post_id = p.id) as reply_count
        FROM forum_posts p
        LEFT JOIN users u ON u.id = p.user_id
    """
    
    params = []
    
    # Search filter
    if search:
        query += " WHERE p.title LIKE %s OR p.body LIKE %s"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    # Sorting
    if sort == 'oldest':
        query += " ORDER BY p.created_at ASC"
    elif sort == 'popular':
        query += " ORDER BY reply_count DESC, p.created_at DESC"
    else:  # latest (default)
        query += " ORDER BY p.created_at DESC"
    
    if params:
        cur.execute(query, tuple(params))
    else:
        cur.execute(query)
    
    posts = cur.fetchall()
    cur.close()
    
    return render_template('forum/index.html', posts=posts)

@forum_bp.route('/forum/post/<int:post_id>')
@login_required
def view_post(post_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # Get post data
    cur.execute("""
        SELECT p.*, u.username, u.full_name, u.role, u.avatar
        FROM forum_posts p
        LEFT JOIN users u ON u.id = p.user_id
        WHERE p.id = %s
    """, (post_id,))
    post = cur.fetchone()
    
    if not post:
        flash("Topik diskusi tidak ditemukan.")
        return redirect(url_for('forum.forum'))
    
    # Get all replies
    cur.execute("""
        SELECT r.*, u.username, u.full_name, u.role, u.avatar
        FROM forum_replies r
        LEFT JOIN users u ON u.id = r.user_id
        WHERE r.post_id = %s
        ORDER BY r.created_at ASC
    """, (post_id,))
    replies = cur.fetchall()
    
    cur.close()
    
    return render_template('forum/view_post.html', post=post, replies=replies)

@forum_bp.route('/forum/post/<int:post_id>/reply', methods=['POST'])
@login_required
def reply_post(post_id):
    body = request.form.get('body', '').strip()
    
    if not body:
        flash("Balasan tidak boleh kosong.")
        return redirect(url_for('forum.view_post', post_id=post_id))
    
    db = get_db()
    cur = db.cursor()
    
    # Check if post exists
    cur.execute("SELECT id FROM forum_posts WHERE id=%s", (post_id,))
    if not cur.fetchone():
        flash("Topik diskusi tidak ditemukan.")
        return redirect(url_for('forum.forum'))
    
    # Insert reply
    cur.execute("""
        INSERT INTO forum_replies (post_id, user_id, body, created_at)
        VALUES (%s, %s, %s, %s)
    """, (post_id, g.user['id'], body, datetime.now()))
    db.commit()
    cur.close()
    
    flash("Balasan berhasil ditambahkan.")
    return redirect(url_for('forum.view_post', post_id=post_id))

@forum_bp.route('/forum/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    cur.execute("SELECT * FROM forum_posts WHERE id=%s", (post_id,))
    post = cur.fetchone()
    
    if not post:
        flash("Topik diskusi tidak ditemukan.")
        return redirect(url_for('forum.forum'))
    
    # Check access
    if post['user_id'] != g.user['id'] and g.user.get('role') != 'admin':
        flash("Anda tidak memiliki akses untuk mengedit topik ini.")
        return redirect(url_for('forum.view_post', post_id=post_id))
    
    if request.method == 'POST':
        title = request.form['title'].strip()
        body = request.form['body'].strip()
        
        if not title or not body:
            flash("Judul dan isi diskusi tidak boleh kosong.")
            return render_template('forum/edit_post.html', post=post)
        
        cur.execute("""
            UPDATE forum_posts 
            SET title=%s, body=%s, updated_at=%s
            WHERE id=%s
        """, (title, body, datetime.now(), post_id))
        db.commit()
        cur.close()
        
        flash("Topik diskusi berhasil diperbarui.")
        return redirect(url_for('forum.view_post', post_id=post_id))
    
    cur.close()
    return render_template('forum/edit_post.html', post=post)

@forum_bp.route('/forum/post/<int:post_id>/delete')
@login_required
def delete_post(post_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    cur.execute("SELECT * FROM forum_posts WHERE id=%s", (post_id,))
    post = cur.fetchone()
    
    if not post:
        flash("Topik diskusi tidak ditemukan.")
        return redirect(url_for('forum.forum'))
    
    # Check access
    if post['user_id'] != g.user['id'] and g.user.get('role') != 'admin':
        flash("Anda tidak memiliki akses untuk menghapus topik ini.")
        return redirect(url_for('forum.view_post', post_id=post_id))
    
    # Delete all replies first
    cur.execute("DELETE FROM forum_replies WHERE post_id=%s", (post_id,))
    # Delete post
    cur.execute("DELETE FROM forum_posts WHERE id=%s", (post_id,))
    db.commit()
    cur.close()
    
    flash("Topik diskusi berhasil dihapus.")
    return redirect(url_for('forum.forum'))

@forum_bp.route('/forum/reply/<int:reply_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_reply(reply_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    cur.execute("SELECT * FROM forum_replies WHERE id=%s", (reply_id,))
    reply = cur.fetchone()
    
    if not reply:
        flash("Balasan tidak ditemukan.")
        return redirect(url_for('forum.forum'))
    
    # Check access
    if reply['user_id'] != g.user['id'] and g.user.get('role') != 'admin':
        flash("Anda tidak memiliki akses untuk mengedit balasan ini.")
        return redirect(url_for('forum.view_post', post_id=reply['post_id']))
    
    if request.method == 'POST':
        body = request.form['body'].strip()
        
        if not body:
            flash("Isi balasan tidak boleh kosong.")
            return render_template('forum/edit_reply.html', reply=reply)
        
        cur.execute("""
            UPDATE forum_replies 
            SET body=%s, updated_at=%s
            WHERE id=%s
        """, (body, datetime.now(), reply_id))
        db.commit()
        cur.close()
        
        flash("Balasan berhasil diperbarui.")
        return redirect(url_for('forum.view_post', post_id=reply['post_id']))
    
    cur.close()
    return render_template('forum/edit_reply.html', reply=reply)

@forum_bp.route('/forum/reply/<int:reply_id>/delete')
@login_required
def delete_reply(reply_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    cur.execute("SELECT * FROM forum_replies WHERE id=%s", (reply_id,))
    reply = cur.fetchone()
    
    if not reply:
        flash("Balasan tidak ditemukan.")
        return redirect(url_for('forum.forum'))
    
    # Check access
    if reply['user_id'] != g.user['id'] and g.user.get('role') != 'admin':
        flash("Anda tidak memiliki akses untuk menghapus balasan ini.")
        return redirect(url_for('forum.view_post', post_id=reply['post_id']))
    
    post_id = reply['post_id']
    
    cur.execute("DELETE FROM forum_replies WHERE id=%s", (reply_id,))
    db.commit()
    cur.close()
    
    flash("Balasan berhasil dihapus.")
    return redirect(url_for('forum.view_post', post_id=post_id))