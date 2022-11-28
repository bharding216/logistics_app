#from os import access
from flask import Blueprint, render_template, \
    redirect, url_for, request, flash, session
from flask_mail import Message
from . import db, mail
from .models import users
from flask_login import login_user, logout_user, \
    login_required, current_user
from werkzeug.security import generate_password_hash, \
    check_password_hash
from datetime import timedelta


auth = Blueprint("auth", __name__)

# When you want to have blueprint-specific 
# templates and static files:

#auth = Blueprint(
# "auth", __name__, 
# template_folder='templates',
# static_folder='static'
# )



#--------------------------------------------------------------------
#--------------------------------------------------------------------



@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = users.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Successfully logged in!', category='success')
                login_user(user, remember=False)
                # Documentation on login_user:
                # https://stackoverflow.com/questions/27965897/why-does-setting-remember-false-still-keep-me-logged-in
                session.permanent = True
                return redirect(url_for('views.index'))
            else:
                flash('Password is incorrect. Please try again.', 
                    category='error')
        else:
            flash('That username does not exist. Please try again or contact \
                your system administrator.', 
                category='error')

    return render_template('login.html', user=current_user)


#--------------------------------------------------------------------
#--------------------------------------------------------------------



@auth.route("/signup", methods=['GET', 'POST'])
def signup():

    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username_signup")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        access_ranking = "1"

        email_exists = users.query.filter_by(email=email).first()
        username_exists = users.query.filter_by(username=username).first()

        if email_exists:
            flash('Email is already in use. \
            Choose another email.', category='error')
        elif username_exists:
            flash('Username is already in use. \
            Choose another username.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        else:
            flash("Thanks for signing up! We'll get back to you \
                via email once we create your account.", 
                category='success')
            
            # Signup email code:
            msg = Message('New User Signup', 
                sender = 'hello@carbonfree.dev', 
                recipients = ['bharding@carbonfree.cc'])
            msg.html = render_template('email.html', email=email,
                username=username, password=password1)
            mail.send(msg)  
            
            
            # Redirect the logged in user to 'index.html':
            return redirect(url_for('views.index'))


    return render_template('signup.html', user=current_user)



#--------------------------------------------------------------------
#--------------------------------------------------------------------



@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash('User logged out!', category='success')

    return redirect(url_for('auth.login'))



#--------------------------------------------------------------------
#--------------------------------------------------------------------