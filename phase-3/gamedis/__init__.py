# Root file of the system
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask import Flask, Blueprint, render_template, abort, flash, session, redirect, url_for
from decouple import config as en_var  # import the environment var
from datetime import timedelta
db = SQLAlchemy()
DB_NAME = en_var(
    'DATABASE_URL', "sqlite:///gamedis_database.sqlite")
TIMEOUT = timedelta(hours=1)
try:
    PORT = en_var("port", 5500)
except:
    PORT = 5500

try:
    DOMAIN = en_var('server')
except:
    DOMAIN = f"127.0.0.1:{PORT}"


def createApp():
    app = Flask(__name__)
    f_bcrypt = Bcrypt()
    app.config['FLASK_ADMIN-SWATCH'] = 'cerulean'
    # Encrepted with Environment Variable
    app.config['SECRET_KEY'] = en_var('gamedis_secret', 'gamedis_secret')
    app.config['DATABASE_NAME'] = DB_NAME
    app.config['SQLALCHEMY_DATABASE_URI'] = f'{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['REMEMBER_COOKIE_SECURE'] = True
    # set session timeout (need to use with before_request() below)
    app.config['PERMANENT_SESSION_LIFETIME'] = TIMEOUT
    app.config['TIMEZONE'] = 'Asia/Bangkok'

    f_bcrypt.init_app(app)
    db.init_app(app)

    from .account import acc
    from .search import s
    from .iden import iden
    app.register_blueprint(rootView, url_prefix='/')
    app.register_blueprint(s, url_prefix='/search')
    app.register_blueprint(iden, url_prefix='/iden-operation')
    app.register_blueprint(acc, url_prefix='/account')
    app.register_error_handler(404, notFound)

    # with app.app_context(): # Drop all of the tables
    #     db.drop_all()

    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        db.session.rollback()
        flash(f'{e}', category='error')

    from .models import User

    # @app.before_request
    # def acc():

    #     try:
    #         d1 = User(fname="ADMIN", alias="admin",
    #                   password=generate_password_hash("admin").decode('utf-8'))
    #         db.session.add(d1)
    #         db.session.commit()
    #         try:
    #             from .accounts import create_accounts
    #             a = create_accounts()
    #             db.session.add_all(a)
    #             db.session.commit()

    #         except Exception as e:
    #             db.session.rollback()
    #             flash(f'{e}', category='error')

    #     except OperationalError:
    #         with app.app_context():
    #             db.create_all()

    #     except Exception as e:
    #         db.session.rollback()
    #         flash(f'{e}', category='error')

    # config the user session
    @app.before_request
    def before_request():
        session.permanent = True
        # session.modified = True # default set to true. Consult the lib to confirm

    login_manager = LoginManager()
    login_manager.login_view = 'iden.login'
    login_manager.refresh_view = 'iden.login'
    login_manager.login_message_category = 'info'
    login_manager.needs_refresh_message_category = "info"
    login_manager.needs_refresh_message = "You have to login again to confirm your identity!"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


rootView = Blueprint('rootView', __name__)


@rootView.route("/dev/root-template/")
# config app theme
def root_view():
    return render_template("root.html", user=current_user)


@rootView.route("/home")
@rootView.route("/", methods=['GET'])
# redirector to home page (search page)
def redirectToHome():
    return redirect(url_for("search.searchHome"))


@rootView.route("/login", methods=['GET'])
# redirector to login page
def redirectToLogin():
    return redirect(url_for("iden.login"))


@rootView.route("/signup")
# redirector to signup page
def redirectToSignup():
    return redirect(url_for("iden.signup"))


@rootView.route("/about/")
# return about page
def about():
    return render_template("about.html", user=current_user)


# handle not found
def notFound(e):
    """ not found 404 """
    return "NOT FOUND<br>Please proceed to the path <u>/home</u> instead!"
