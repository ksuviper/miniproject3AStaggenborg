from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('homeo', __name__)


@bp.route('/')
def index():
    db = get_db()
    remedies = db.execute(
        'SELECT r.id, r.name, potency, created, updated, user_id, username'
        ' FROM remedy r '
        ' JOIN user u ON r.user_id = u.id'
        ' JOIN remedy_potency p ON r.potency_id = p.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('homeo/index.html', remedies=remedies)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        potency_id = request.form['potency']
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO remedy (name, potency_id, user_id)'
                ' VALUES (?, ?, ?)',
                (name, potency_id, g.user['id'])
            )
            db.commit()
            return redirect(url_for('homeo.index'))

    return render_template('homeo/create.html')


def get_remedy(id, check_user=True):
    remedy = get_db().execute(
        'SELECT r.id, r.name, potency, created, updated, user_id, username'
        ' FROM remedy r '
        ' JOIN user u ON r.user_id = u.id'
        ' JOIN remedy_potency p ON r.potency_id = p.id'
        ' WHERE r.id = ?',
        (id,)
    ).fetchone()

    if remedy is None:
        abort(404, f"Remedy id {id} doesn't exist.")

    if check_user and remedy['user_id'] != g.user['id']:
        abort(403)

    return remedy


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    remedy = get_remedy(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE rememdy SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('homeo.index'))

    return render_template('homeo/update.html', remedy=remedy)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_remedy(id)
    db = get_db()
    db.execute('DELETE FROM remedy WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('homeo.index'))

