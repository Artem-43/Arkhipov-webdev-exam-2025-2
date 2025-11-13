from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, current_user, login_required
from app.models import db, Recipe, User, Image
from flask_login import login_user
from passlib.hash import scrypt
import bleach
import os
UPLOAD_FOLDER = 'app/static/uploads'


bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/recipe/add', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        print("request.form:", request.form)
        print("request.files:", request.files)
        try:
            title = bleach.clean(request.form['title'])
            description = bleach.clean(request.form['description'])
            cook_time = int(request.form['cook_time'])
            servings = int(request.form['servings'])
            ingredients = bleach.clean(request.form['ingredients'])
            steps = bleach.clean(request.form['steps'])

            recipe = Recipe(
                title=title,
                description=description,
                cook_time=cook_time,
                servings=servings,
                ingredients=ingredients,
                steps=steps,
                author_id=current_user.id
            )
            db.session.add(recipe)
            db.session.flush()

            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    filename = file.filename
                    mime_type = file.mimetype
                    path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(path)

                    img = Image(file_name=filename, mime_type=mime_type, recipe_id=recipe.id)
                    db.session.add(img)

            db.session.commit()
            flash('Рецепт успешно добавлен!', 'success')
            return redirect(url_for('users.index'))

        except Exception as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            print(e)

    return render_template('recipe_form.html', recipe=None)


@bp.route('/recipe/edit/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe.author_id != current_user.id and current_user.role.name != 'admin':
        flash('У вас недостаточно прав для выполнения данного действия.', 'warning')
        return redirect(url_for('users.index'))

    if request.method == 'POST':
        try:
            recipe.title = bleach.clean(request.form['title'])
            recipe.description = bleach.clean(request.form['description'])
            recipe.cook_time = int(request.form['cook_time'])
            recipe.servings = int(request.form['servings'])
            recipe.ingredients = bleach.clean(request.form['ingredients'])
            recipe.steps = bleach.clean(request.form['steps'])

            db.session.commit()
            flash('Изменения сохранены!', 'success')
            return redirect(url_for('users.index'))

        except Exception:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')

    return render_template('recipe_form.html', recipe=recipe)


@bp.route('/recipe/delete/<int:recipe_id>', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)
    if not recipe:
        flash("Рецепт не найден", "warning")
        return redirect(url_for('users.index'))

    if recipe.author_id != current_user.id and current_user.role.name != 'Администратор':
        flash("У вас недостаточно прав для удаления рецепта", "danger")
        return redirect(url_for('users.index'))

    try:
        for image in recipe.images:
            try:
                os.remove(os.path.join('app/static/uploads', image.file_name))
            except FileNotFoundError:
                pass

        db.session.delete(recipe)
        db.session.commit()
        flash("Рецепт успешно удалён", "success")
    except Exception as e:
        db.session.rollback()
        flash("Ошибка при удалении рецепта", "danger")
        print("Ошибка удаления рецепта:", e)

    return redirect(url_for('users.index'))


@bp.route('/recipe/<int:recipe_id>')
def show_recipe(recipe_id):
    recipe = db.session.query(Recipe).filter_by(id=recipe_id).first()

    if not recipe:
        abort(404)

    return render_template('recipe_show.html', recipe=recipe, current_user=current_user)