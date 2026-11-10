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

        
        result = User.query.filter_by(email=email).first()#filter_by не склеивает строку запроса, а передаёт email отдельно.
                                                        #Поэтому даже если в email ввести SQL-код, база воспримет его как текст, а не как команду(как было до)
        if result and check_password_hash(result.password, password): #check_password_hash здесь потому что теперь мы хэшируем то, что ввел пользователь
            flash('Logged in successfully', category='success')       # и сравниваем с уже сохраненным хэшем, а не пароль с паролем напрямую как было раньше
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
            new_user = User(email=email,first_name=first_name,password=generate_password_hash(password1, method='scrypt') #пароль хранится теперь в захешированном виде: если получить доступ к базе данных,
            db.session.add(new_user)                                                                                      #то нужно ещё расшифровать пароль,чтобы украсть данные с аккаунта (ну и сам аккаунт)
            db.session.commit()
            login_user(new_user,remember=True)
            flash('Account has been created',category="success")
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user = current_user) 
