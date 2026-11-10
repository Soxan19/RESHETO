from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from sqlalchemy import text
from flask_login import login_user, login_required, logout_user, current_user



auth = Blueprint('auth',__name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        query = f"SELECT * FROM user WHERE email = '{email}' AND password = '{password}'" #сами склеиваем строчку(пользователь может ввести текст, а sql рассмотрит его как команду)
        result = db.session.execute(text(query)).fetchone()

        if result:
            flash('Logged in successfully', category='success')
            user = User.query.get(result.id)
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
        else:
            flash('Incorrect password', category='error')
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))  

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        elif len(email) < 4:
            flash('Email must be at least 4 characters long.',category='error')
        elif len(first_name)<2:
            flash('First name must be at least 2 characters long.',category='error')
        elif password1 != password2:
            flash('Passwords fo not match.',category='error')
        elif len(password1) < 5:
            flash('Passwords must be at least 5 characters long.',category='error')
        else:
            new_user = User(email=email,first_name=first_name,password=password1) #пароль хранится просто как есть, не хэшируется ничё кароче с ним не делается 
            db.session.add(new_user)                                              #тепер если заполучить базу данных можно спокойненько зайти на акк и украсть всю инфу оттуда
            db.session.commit()
            login_user(new_user,remember=True)
            flash('Account has been created',category="success")
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user = current_user) 
