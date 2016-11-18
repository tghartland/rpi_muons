from flask import render_template, jsonify, request

from flask_bootstrap import Bootstrap
from flask_admin import Admin

import os
import os.path as op

import app
from app import db, app, APP_ROOT

from analysis import scheduler
import navbar

# Import blueprints
from detector.views import detector as detector_views
from result.views import result as result_views

# Import models
from result.models import Result


app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

app.config.update(
    SECRET_KEY="verysecretkey",
    SQLALCHEMY_DATABASE_URI='sqlite:////tmp/rsmdg.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

db.init_app(app)

Bootstrap(app)
admin = Admin(app, name="rsmdg", template_mode="bootstrap3")

# register blueprints
app.register_blueprint(detector_views)
app.register_blueprint(result_views)


@app.before_first_request
def before_first_request():
    db.create_all()

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/log")
def log():
    with open(op.join(APP_ROOT, "rsmdg.log")) as logfile:
        return render_template("generic.html", title="Log", body="<h3>Log file</h3><pre>{}</pre>".format(logfile.read()))



if __name__ == '__main__':
    app.run()
