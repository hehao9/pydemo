import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from werkzeug.security import check_password_hash

from flaskr.User import User, get_user_by_id, get_user_by_name


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    csrf = CSRFProtect(app)
    bootstrap = Bootstrap(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'Access denied.'

    @login_manager.user_loader
    def user_loader(user_id):
        user = get_user_by_id(user_id)
        if not user:
            return

        fl_user = User()
        fl_user.id = user['id']
        fl_user.username = user['username']
        return fl_user

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from flaskr import db
    db.init_app(app)

    from flaskr import auth
    app.register_blueprint(auth.bp)

    from flaskr import three
    app.register_blueprint(three.bp)

    app.add_url_rule('/', endpoint='index')

    return app
