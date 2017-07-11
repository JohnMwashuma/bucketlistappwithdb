from flask_wtf import Form
from wtforms.fields import StringField, PasswordField, BooleanField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired,Regexp
from flask_wtf.file import FileField, FileAllowed, FileRequired





class WishForm(Form):
    title = StringField('title' , validators=[DataRequired()])
    description = StringField('description', widget=TextArea(), validators=[DataRequired()])
    wish_status = BooleanField('wish_status')
    wish_progress = BooleanField('wish_progress')
    wish_image = FileField('wish_image')
    tags = StringField('tags', validators=[Regexp(r'^[a-zA-Z0-9, ]*$',
                    message="Tags can only contain letters and numbers")])
    
    
    def validate(self):
        if not Form.validate(self):
            return False       

        # filter out empty and duplicate tag names
        stripped = [t.strip() for t in self.tags.data.split(',')] # Split the data and remove white space
        not_empty = [tag for tag in stripped if tag] # Temoves all empty strings from the list
        tagset = set(not_empty) # Removes all duplicate strings
        self.tags.data = ",".join(tagset) # Joins the unique strings to a comma separated string again

        return True


class LoginForm(Form):
    username = StringField('username' , validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])



