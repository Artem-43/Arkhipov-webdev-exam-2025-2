from flask_migrate import Migrate
from flask import Flask, redirect, url_for, flash, request
from flask_login import LoginManager, current_user
import os
import markdown

from app.models import db
from . import admin
from . import users
from . import reviews
from app.models import User

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    db.init_app(app)
    
    # with app.app_context():
    #     db.create_all()

    migrate = Migrate(app, db)

    login_manager = LoginManager(app)
    login_manager.login_view = 'users.login'
    login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации'
    login_manager.login_message_category = 'warning'

    @login_manager.unauthorized_handler
    def unauthorized():
        flash("Для выполнения данного действия необходимо пройти процедуру аутентификации", "warning")
        return redirect(url_for('users.login'))

    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    app.register_blueprint(users.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(reviews.bp)
    app.route('/', endpoint='index')(users.index)

    @app.template_filter('markdown')
    def markdown_filter(text):
        return markdown.markdown(
            text or "",
            extensions=['nl2br'],
            output_format='html5'
        )

    return app