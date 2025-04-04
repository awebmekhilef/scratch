import sys
import json
from rq import get_current_job
from flask import render_template
from app import create_app, db
from app.models import User, Comment, Task
from app.email import send_email

app = create_app()
app.app_context().push()

def _set_task_completed():
    job = get_current_job()
    if job:
        task = db.session.get(Task, job.get_id())
        task.complete = True
        db.session.commit()


def export_data(user_id):
    try:
        user = db.session.get(User, user_id)

        data = {
            'username': user.username,
            'email': user.email,
            'website': user.website,
            'about': user.about,
            '2fa_enabled': user.is_2fa_enabled,
            'games': [],
            'comments': []
        }

        for game in db.session.scalars(user.games.select()):
            data['games'].append({
                'title': game.title,
                'tagline': game.tagline,
                'description': game.description,
                'created_at': game.created_at,
                'updated_at': game.updated_at,
            })
        for comment in db.session.scalars(db.select(Comment).where(Comment.author == user)):
            data['comments'].append({
                'text': comment.text
            })

        send_email(
            '[scratch] Your Data Export',
            app.config['ADMINS'][0],
            [user.email],
            render_template('email/export_data.txt', user=user),
            render_template('email/export_data.html', user=user),
            [('data.json', json.dumps(data, indent=4, default=str), 'application/json')],
            True
        )
    except Exception:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        _set_task_completed()
