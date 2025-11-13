from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.models import db, Recipe, User, Image
from flask_login import login_user
from passlib.hash import scrypt
import bleach
import os
UPLOAD_FOLDER = 'app/static/uploads'


bp = Blueprint('users', __name__, url_prefix='')


@bp.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    recipes = (
        db.session.query(Recipe)
        .order_by(Recipe.id.desc())
        .paginate(page=page, per_page=9)
    )
    print(scrypt.hash("user"))
    return render_template('index.html', recipes=recipes, current_user=current_user)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['login']
        password_input = request.form['password']
        remember = 'remember' in request.form

        user = db.session.query(User).filter_by(login=login_input).first()

        print("пароль", scrypt.hash("admin"))

        if user and user.check_password(password_input):
            login_user(user, remember=remember)
            return redirect(url_for('users.index'))
        else:
            flash("Невозможно аутентифицироваться с указанными логином и паролем", "danger")
            return render_template('login.html')

    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.index'))
