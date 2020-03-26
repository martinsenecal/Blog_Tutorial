import os
import secrets

from PIL import Image  # Resize Picture to take less Space.
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required

from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, \
    ResetPasswordForm  # Classes from forms.py
from flaskblog.models import User, Post
from flask_mail import Message


# Pagination is Useful since we won't have to load everything at once.

# Multiple routes for the same page.
@app.route('/home')
@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)  # Pagination
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


@app.route('/post/new', methods=['GET', 'POST'])
@login_required  # Decorator
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post had been created!', 'success')  # Success is the bootstrap class to make it prettier.
        return redirect(url_for('home'))

    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route('/post/<int:post_id>')  # Useful for Custom Routes
def post(post_id):
    post = Post.query.get_or_404(post_id)  # If we are trying to look for a post that doesn't exist: return error.
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])  # Useful for Custom Routes
@login_required  # Decorator
def update_post(post_id):
    post = Post.query.get_or_404(post_id)  # If we are trying to look for a post that doesn't exist: return error.
    if post.author != current_user:
        abort(403)  # HTTP response for when user doesn't have the permission.

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()  # no add to db, since they are already inside the database.
        flash('Your post had been updated!', 'success')  # Success is the bootstrap class to make it prettier.
        return redirect(url_for('post', post_id=post.id))

    elif request.method == 'GET':
        # Add Current Information from the Post.
        form.title.data = post.title
        form.content.data = post.content

    # legend is useful so we don't have to create 2 different html files just for 1 small difference.
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])  # Useful for Custom Routes
@login_required  # Decorator
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)  # If we are trying to look for a post that doesn't exist: return error.
    if post.author != current_user:
        abort(403)  # HTTP response for when user doesn't have the permission.
    db.session.delete(post)
    db.session.commit()
    flash('Your post had been deleted!', 'success')  # Success is the bootstrap class to make it prettier.
    return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=5)  # Pagination

    return render_template('user_posts.html', posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
