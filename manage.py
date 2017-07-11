from bucketlist import app, db
from models import User, Wishes, Tag
from flask.ext.script import Manager, prompt_bool
from flask.ext.migrate import Migrate, MigrateCommand

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def insert_data():
    jmwashuma = User(username="jmwashuma", email="jmwashuma@example.com", password="test")
    db.session.add(jmwashuma)
    
    def add_wish(title, description, tags):
        db.session.add(Wishes(title=title, description=description, user=jmwashuma,
                                tags=tags,wish_status=wish_status,wish_progress=wish_progress))

    for name in ["Travelling", "Career", "Education", "Relationship", "Family", "Health", "Business"]:
        db.session.add(Tag(name=name))
    db.session.commit()

    add_wish("Joining Andela Fellowship", "Joining andela will be a dream come true because of the passion that i have for programming and the will to make africa a better place through developing featuristic solutions that will solve africa problems", "Business,Career,Education","True","True")
    add_wish("Learning Python", "Film festivals used to be do or die moments for movie makers They were where you met the producers that could fund your project and if the buyers liked your flick they pay to Fast forward", "Education,Family")
    add_wish("Who Needs Sundance When You ve Got Crowdfunding", "Joining andela will be a dream come true because of the passion that i have for programming and the will to make africa a better place through developing featuristic solutions that will solve africa problems", "Health,Business,Relationship","False","False")   

    gillian = User(username="gillian", email="gillian@robben.nl", password="test")
    db.session.add(gillian)
    db.session.commit()
    print 'Initialized the database'  

@manager.command
def dropdb():
    if prompt_bool(
        "Are you sure you want to lose all your data"):
        db.drop_all()
        print 'Dropped the database'

if __name__ == '__main__':
    manager.run()
