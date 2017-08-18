from unittest import TestCase
from application import app


class ApplicationTest(TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        pass

    def tearDown(self):
        print('teardown')
        pass

    def test_reg_logout_login(self):
        assert self.register('hllpp', 'word').status_code == 200
        assert 'hllpp'.encode('utf-8') in self.app.open('/').data
        self.logout()
        assert 'hllpp'.encode('utf-8') not in self.app.open('/').data
        self.login('hello', 'word')
        assert 'hllpp'.encode('utf-8') in self.app.open('/').data

    def register(self ,username, password):
        return self.app.post('/reg/', data={'username':username, 'password':password}, follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/login/', data={'username': username, 'password': password}, follow_redirects=True)

    def logout(self):
        return self.app.get('/logout/')