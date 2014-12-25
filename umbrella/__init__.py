# -*- coding: utf-8 -
#

import flask
import os


app = flask.Flask(__name__)
app.config.from_object('config')
ALL_RESOURCE_INDEX = '__ALL_RESOURCE_INDEX__'


from umbrella.views import sync, report, account
app.register_blueprint(sync.mod)
app.register_blueprint(report.mod)
app.register_blueprint(account.mod)


@app.errorhandler(404)
def not_found(error):
    return flask.render_template('404.html'), 404


@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(
        os.path.join(app.root_path, 'static'), 'favicon.ico')


@app.route('/')
def index():
    return flask.render_template('index.html')
