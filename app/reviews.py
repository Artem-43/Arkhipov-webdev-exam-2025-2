from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, current_user, login_required
from app.models import db, Recipe, User, Image, Review
from flask_login import login_user
from passlib.hash import scrypt
import bleach
import os
from sqlalchemy import select
UPLOAD_FOLDER = 'app/static/uploads'


bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@bp.route('/add/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def add_review(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)
    if not recipe:
        flash("Рецепт не найден.", "danger")
        return redirect(url_for('users.index'))

    if current_user.role.name not in ['user', 'admin']:
        flash("У вас нет прав на добавление отзыва.", "warning")
        return redirect(url_for('admin.show_recipe', recipe_id=recipe_id))

    existing_review = db.session.execute(
        select(Review).where(
            Review.user_id == current_user.id,
            Review.recipe_id == recipe_id
        )
    ).scalar_one_or_none()
    if existing_review:
        flash("Вы уже оставили отзыв на этот рецепт.", "info")
        return redirect(url_for('admin.show_recipe', recipe_id=recipe_id))

    if request.method == 'POST':
        try:
            rating = int(request.form['rating'])
            text = bleach.clean(request.form['text'])
            review = Review(recipe_id=recipe_id, user_id=current_user.id, rating=rating, text=text)
            db.session.add(review)
            db.session.commit()
            flash("Отзыв успешно добавлен!", "success")
            return redirect(url_for('admin.show_recipe', recipe_id=recipe_id))
        except Exception:
            db.session.rollback()
            flash("Ошибка при сохранении отзыва. Проверьте данные.", "danger")

    return render_template('review_form.html', recipe=recipe)
