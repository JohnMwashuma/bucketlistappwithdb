from datetime import datetime

from sqlalchemy import desc

from flask_login import UserMixin, current_user

from werkzeug.security import check_password_hash, generate_password_hash

from bucketlist import db

tags = db.Table('wish_tag',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('wish_id', db.Integer, db.ForeignKey('wishes.id'))
)

class Wishes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(500), nullable=False)
    wish_status = db.Column(db.Boolean, nullable=True, default=False)
    wish_progress = db.Column(db.Boolean, nullable=True, default=False)
    image_filename = db.Column(db.String, default=None, nullable=True)
    image_url = db.Column(db.String, default=None, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    _tags = db.relationship('Tag', secondary=tags, lazy='joined',
                            backref=db.backref('wish_items', lazy='dynamic'))
    @staticmethod
    def all_wishes():
        return Wishes.query.filter(Wishes.tags != None).all()
    
    
    @staticmethod
    def new_wishes(page,POSTS_PER_PAGE):
        return Wishes.query.filter(Wishes.wish_status != True).order_by(desc(Wishes.date)).paginate(page, POSTS_PER_PAGE, False)
    @staticmethod
    def public_wishes(page,POSTS_PER_PAGE):
        return Wishes.query.filter(Wishes.wish_status != True and Wishes.user == current_user).order_by(desc(Wishes.date)).paginate(page, POSTS_PER_PAGE, False)
    
    @staticmethod
    def private_wishes(page,POSTS_PER_PAGE):
        return Wishes.query.filter(Wishes.wish_status == False and Wishes.user == current_user).order_by(desc(Wishes.date)).paginate(page, POSTS_PER_PAGE, False)
    
    @staticmethod
    def wish_detail(wish_title):
        return Wishes.query.filter(Wishes.title==wish_title).first_or_404()
    
    @property
    def tags(self):
        return ",".join([t.name for t in self._tags]) # Takes the names from the comma seperated tags
    
    #Checks if a tag is in the db and if not adds it to the db
    @tags.setter
    def tags(self, string):
        if string:
            self._tags = [Tag.get_or_create(name) for name in string.split(',')]

    def __repr__(self):
        return "<Wishes '{}' : '{}'>".format(self.title, self.description)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    wishes = db.relationship('Wishes', backref = 'user', lazy = 'dynamic')
    password_hash = db.Column(db.String)

    @property
    def password(self):
        raise AttributeError('password: write-only field')
        
    @staticmethod
    def personal_wishes(page,POSTS_PER_PAGE):
        return Wishes.query.filter(Wishes.user == current_user).order_by(desc(Wishes.date)).paginate(page, POSTS_PER_PAGE, False)

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()


    def __repr__(self):
        return "<User %r>" % self.username
    
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False, unique=True, index=True)
    
    
    # Retrieves a tag with a given name and if not creates it
    @staticmethod
    def get_or_create(name):
        try:
            return Tag.query.filter_by(name=name).one()
        except:
            return Tag(name=name)
        
    @staticmethod
    def all():
        return Tag.query.all()
    
    
    def __repr__(self):
        return self.name

