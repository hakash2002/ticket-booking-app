import os
from flask import Flask
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_security import Security
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from application.models import User
from flask_cors import CORS
app = None

def create_app():
    app = Flask(__name__, template_folder="templates")
    CORS(app)
    if os.getenv('ENV', "development") == "production":
      raise Exception("Currently no production config is setup.")
    else:
      print("Staring Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    
    db.init_app(app)
    app.app_context().push()

    return app



app = create_app()


login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def user_loader(id):
    user = User.query.filter_by(id=id).first()
    return user

# Import all the controllers so they are loaded
from application.controllers import *

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(401)
def unauthorised(e):
    return render_template("401.html"), 401

if __name__ == '__main__':
  # Run the Flask app
  db.create_all()
  app.run(host='0.0.0.0')
  