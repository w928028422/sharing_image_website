import random
from flask_script import Manager
from application import app, db
import unittest
from application.models import User, Image, Comment

manager = Manager(app)


def get_image_url():
    return 'https://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png'


@manager.command
def init_database():
    db.drop_all()
    db.create_all()
    session = db.Session(bind=db.get_engine(app))
    for i in range(100):
        session.add(User('user' + str(i + 1), 'passwd' + str(i + 1)))
        for j in range(3):
            session.add(Image(get_image_url(), i + 1))
            for k in range(3):
                session.add(Comment('Wow' + str(k), i + 1, 3 * i + j + 1))
    session.commit()


@manager.command
def run_test():
    tests = unittest.TestLoader().discover('./')
    unittest.TextTestRunner().run(tests)


if __name__ == "__main__":
    manager.run()
