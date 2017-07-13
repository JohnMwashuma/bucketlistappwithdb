import os
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_moment import Moment
from forms import WishForm, LoginForm
from sqlalchemy import desc
from flask_heroku import Heroku


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Secret key for the flash messages
app.config['SECRET_KEY'] = '\x0c\x07\xbb\xf6\x9c\xbb\xb6NFN\x84fIq\xb3}\xb0\xb00\x01\xc0\x9cih'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'bucketlist.db')
#app.config['DEBUG'] = True
#heroku = Heroku(app)
db = SQLAlchemy(app)

# Configuring Authentication
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'  # Redirects a user to login page if not logged in already
login_manager.init_app(app)

# Configure the image uploading via Flask-Uploads
app.config['UPLOADED_IMAGES_DEST'] = "TOP_LEVEL_DIR + '/static/images/"


# pagination
POSTS_PER_PAGE = 2


images = UploadSet('images', IMAGES)
configure_uploads(app, images)

# for displaying timestamps
moment = Moment(app)


import models

# Tells flask_login to retrieve a user based on the id stored in the http session
@login_manager.user_loader
def load_user(userid):
    return models.User.query.get(int(userid))

# Method for Adding a new wish
@app.route('/newwish', methods=['GET','POST'])
@login_required
def newwish():

    # Create an instance of wishform class which checks for data in the request
    form = WishForm()
    if form.validate_on_submit():  # Checks the http request and validates the form
        title = form.title.data
        description = form.description.data
        tags = form.tags.data
        wish_status = form.wish_status.data
        wish_progress = form.wish_progress.data
        filename = images.save(request.files['wish_image'])
        url = images.url(filename)
        wishitem = models.Wishes(user=current_user,title=title,description=description,tags=tags,wish_status=wish_status, wish_progress=wish_progress, image_filename=filename, image_url=url)
        db.session.add(wishitem)
        db.session.commit()
        flash("stored wish '{}'" .format(title))
        return redirect(url_for('index'))
    return render_template('wishform.html', form = form, heading = "Create a New Wish")


# Method for Adding a new wish
@app.route('/edit_wish/<int:wish_id>', methods=['GET','POST'])
@login_required
def edit_wish(wish_id):
    # Retrieve wish items of the id provided
    wish_item = models.Wishes.query.get_or_404(wish_id)

    # Check if the retrieved wish is owned by the logged in user
    if current_user != wish_item.user:
        abort(403)

    # Fills the form with data received from the database
    form = WishForm(obj=wish_item)
    if form.validate_on_submit():  # Checks the http request and validates the form
        form.populate_obj(wish_item) # Copies the form data to the wish_item object
        db.session.commit()
        flash("Updated wish '{}'" .format(wish_item.title))
        return redirect(url_for('index'))
    return render_template('wishform.html', form = form, heading = "Edit a wish item")


@app.route('/delete_wish/<int:wish_id>', methods=['GET', 'POST'])
@login_required
def delete_wish(wish_id):
    wish = models.Wishes.query.get_or_404(wish_id)
    if current_user != wish.user:
        abort(403)
    else:
        db.session.delete(wish)
        db.session.commit()
        flash("Deleted '{}'".format(wish.title))        
    return redirect(url_for('index'))
    




# Method for logging in the system
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # validate and login the user..
        user = models.User.get_by_username(form.username.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in successfully as {}.".format(user.username))
            return redirect(request.args.get('next') or url_for('index'))

        flash('Incorrect Username or Password')
    return render_template('login.html', form = form)



# Method for logging out
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Signup
@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = models.User(email=form.email.data,
                    username=form.username.data,
                    password = form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome, {}! Please login.'.format(user.username))
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/index')
@app.route('/')
@app.route('/index/<int:page>', methods=['GET','POST'])
def index(page=1):     
    return render_template('index.html', wish_per_page = models.Wishes.new_wishes(page,POSTS_PER_PAGE), WishTags = models.Tag.all())


@app.route('/user/<username>')
@app.route('/user/<username>/<int:page>', methods=['GET','POST'])
@login_required
def mywishes(username,page=1):
    #user = models.User.query.filter_by(username=username).first_or_404()
    return render_template('mywishlist.html', personal_wishes=models.User.personal_wishes(page,POSTS_PER_PAGE), WishTags = models.Tag.all())


@app.route('/wishdetails/<wish_title>')
def wishdetails(wish_title):    
    return render_template('wishdetails.html', wish_detail = models.Wishes.wish_detail(wish_title))


@app.route('/manageaccnt/<int:user_id>', methods=["GET", "POST"])
@login_required
def manageaccnt(user_id):
    # Retrieve user with user_id provided
    user = models.User.query.get_or_404(user_id)
    
    # Fills the form with data received from the database
    form = ManageForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user) # Copies the form data to the wish_item object
        db.session.commit()
        flash("Updated user '{}'" .format(user.username))
        return redirect(url_for('index'))    
    return render_template('manageaccount.html', form = form)

@app.route('/publicwishes/<username>')
@app.route('/publicwishes/<username>/<int:page>', methods=['GET','POST'])
def publicwishes(username,page=1):
    user = models.User.query.filter_by(username=username).first_or_404()
    return render_template('publicwishes.html', user_wish=user,  public_wishes = models.Wishes.public_wishes(page,POSTS_PER_PAGE), WishTags = models.Tag.all())


@app.route('/privatewishes/<username>')
@app.route('/privatewishes/<username>/<int:page>', methods=['GET','POST'])
@login_required
def privatewishes(username,page=1):
    user = models.User.query.filter_by(username=username).first_or_404()
    return render_template('privatewishes.html', user_wish=user,  private_wishes = models.Wishes.private_wishes(page,POSTS_PER_PAGE), WishTags = models.Tag.all())    


@app.errorhandler(404)
def page_not_found(e):
    return render_template('page_404.html'), 404


@app.errorhandler(403)
def page_not_found(e):
    return render_template('page_403.html'), 403


@app.errorhandler(500)
def page_not_found(e):
    return render_template('page_500.html'), 500




from flask_wtf import Form
from wtforms.fields import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo,ValidationError

class SignupForm(Form):
    username = StringField('username', validators=[DataRequired(), Length(3, 80), Regexp('^[A-Za-z0-9_]{3,}$',
                                                                                         message='Usernames consist of numbers, letters,'
                                                                                                 'and underscores.')])
    password = PasswordField('password',
                             validators=[
                                 DataRequired(),
                                 EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('password2', validators=[DataRequired()])
    email = StringField('email',
                        validators=[DataRequired(), Length(1, 120), Email()])

    def validate_email(self, email_field):
        if models.User.query.filter_by(email=email_field.data).first():
            raise ValidationError('There is already a user with this email address.')

    def validate_username(self, username_field):
        if models.User.query.filter_by(username=username_field.data).first():
            raise ValidationError('This username is already taken.')
            

class ManageForm(Form):
    username = StringField('username', validators=[Length(3, 80), Regexp('^[A-Za-z0-9_]{3,}$',
                                                                                         message='Usernames consist of numbers, letters,'
                                                                                                 'and underscores.')])
    password = PasswordField('password',
                             validators=[
                                 
                                 EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('password2')
    email = StringField('email',
                        validators=[Length(1, 120), Email()])

    
        

    

if __name__ == '__main__':
    app.run(debug=True)