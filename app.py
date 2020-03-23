from flask import Flask  # importing Flask class.
from flask import render_template, url_for, flash, redirect

from forms import RegistrationForm, LoginForm  # Classes from forms.py

app = Flask(__name__)

# Secret Key: Protect against modifying cookies and other attacks.
app.config['SECRET_KEY'] = '3c36493447a6e32d68167947ddac18ec'

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
    form = RegistrationForm()  # Create an instance of form.
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))

    return render_template('register.html', title='Register', form=form)
    # We have access to form (in red) inside our HTML files.


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Create an instance of form.
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':  # dummy data.
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')

    return render_template('login.html', title='Login', form=form)
    # We have access to form(in read) inside our HTML files.


if __name__ == '__main__':
    app.run(debug=True)
