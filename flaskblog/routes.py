import secrets, os
from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm  # Classes from forms.py
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image  # Resize Picture to take less Space.

posts = [
    {
        'author': 'Corey',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 23, 2018'
    }
]


# Multiple routes for the same page.
@app.route('/home')
@app.route('/')
def home():
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:  # Check if User is already Log In
        return redirect(url_for('home'))
    form = RegistrationForm()  # Create an instance of form.
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)  # Create User
        db.session.add(user)
        db.session.commit()  # Add User to the Database
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)
    # We have access to form (in red) inside our HTML files.


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # Check if User is already Log In
        return redirect(url_for('home'))
    form = LoginForm()  # Create an instance of form.
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  # None if no User already with same email.
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Use Login Manager
            login_user(user, remember=form.remember.data)

            # If we are trying to access a page, we'll be able to access it after entering our login information
            # instead of re-directing us to the home page again. (we have to import 'request' from flask)
            next_page = request.args.get('next')  # Return None if we don't have a query...

            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)
    # We have access to form(in read) inside our HTML files.


@app.route('/logout')
def logout():
    logout_user()  # We use a function already built by Flask to Log Out the Current User (with login manager)
    return redirect(url_for('home'))


def save_picture(form_picture):
    # Take Care to Store Picture from User inside our Files System
    random_hex = secrets.token_hex(8)  # Store a Random Hex Numbers by importing secrets
    # OS (import) take care of files-extension
    _, f_ext = os.path.splitext(form_picture.filename)  # _ is the file name (that we don't actually need)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics',
                                picture_fn)  # Take Care of the Entire Path of File

    # Resize Picture to take less space and run faster.
    output_size = (125, 125)  # Size of Picture
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


# Add a security layer: Make sure user can't access pages if he don't have access to it... (use login_required )
@app.route('/account', methods=['GET', 'POST'])
@login_required  # Decorator
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account had been updated!', 'success')  # Success is the bootstrap class to make it prettier.
        return redirect(url_for('account'))
        # We want to do a redirect instead of render template because: (not calling post a 2nd time)
        # Post/Get/Redirect Pattern: we don't want to re-submit the data a second time.
        # Browser will send a get request instead

    elif request.method == 'GET':  # We want to show the info of the user, when he arrive on the page.
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route('/post/new')
@login_required  # Decorator
def new_post():
    return render_template('create_post.html', title='New Post')
