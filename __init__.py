import requests
import urllib.parse

from flask import Blueprint, jsonify, abort
from pathlib import Path

from CTFd.models import db
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.plugins.dynamic_challenges import DynamicChallenge, DynamicValueChallenge
from CTFd.plugins.flags import BaseFlag, FLAG_CLASSES
from CTFd.plugins.migrations import upgrade
from CTFd.utils.decorators import authed_only,get_current_user

plugin_name = __name__.split('.')[-1]

class CTFdInstanceDynamicFlag(BaseFlag):
    name = "instance_dynamic"
    templates = {  # Nunjucks templates used for key editing & viewing
        "create": f"/plugins/{plugin_name}/assets/flagcreate.html",
        "update": f"/plugins/{plugin_name}/assets/flagedit.html",
    }

    @staticmethod
    def compare(chal_key_obj, provided):
        user = get_current_user()
        challenge = InstanceChallenge.query.filter_by(id=chal_key_obj.challenge_id).first()
        if challenge is None:
            return False
        try:
            r = requests.get(urllib.parse.urljoin(challenge.api, 'flag'), headers={"Authorization": f"Token {challenge.apikey}"}, params={'userid': user.id})
            if r.status_code != 200:
                return False
        except:
            return False
        
        saved = r.text
        data = chal_key_obj.data

        if len(saved) != len(provided):
            return False
        result = 0

        if data == "case_insensitive":
            for x, y in zip(saved.lower(), provided.lower()):
                result |= ord(x) ^ ord(y)
        else:
            for x, y in zip(saved, provided):
                result |= ord(x) ^ ord(y)
        return result == 0

class InstanceChallenge(DynamicChallenge):
    __mapper_args__ = {"polymorphic_identity": "instance"}
    id = db.Column(
        db.Integer, db.ForeignKey("dynamic_challenge.id", ondelete="CASCADE"), primary_key=True
    )
    api = db.Column(db.Text, default='http://localhost:80')
    apikey = db.Column(db.Text, default='')
    plugin_name = plugin_name

    def __init__(self, *args, **kwargs):
        super(InstanceChallenge, self).__init__(**kwargs)


class InstanceChallengeControler(DynamicValueChallenge):
    id = "instance"  # Unique identifier used to register challenges
    name = "instance"  # Name of a challenge type
    templates = (
        {  # Handlebars templates used for each aspect of challenge editing & viewing
            "create": f"/plugins/{plugin_name}/assets/create.html",
            "update": f"/plugins/{plugin_name}/assets/update.html",
            "view": f"/plugins/{plugin_name}/assets/view.html",
        }
    )
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": f"/plugins/{plugin_name}/assets/create.js",
        "update": f"/plugins/{plugin_name}/assets/update.js",
        "view": f"/plugins/{plugin_name}/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = f"/plugins/{plugin_name}/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        plugin_name,
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = InstanceChallenge

    @classmethod
    def read(cls, challenge):
        data = super().read(challenge)
        data.update(
            {
                'plugin_name': plugin_name,
            }
        )
        return data

def load(app):
    upgrade(plugin_name=plugin_name)
    CHALLENGE_CLASSES["instance"] = InstanceChallengeControler
    FLAG_CLASSES["instance_dynamic"] = CTFdInstanceDynamicFlag
    register_plugin_assets_directory(
        app, base_path=f"/plugins/{plugin_name}/assets/"
    )

    @authed_only
    @app.route(f'/plugins/{plugin_name}/status/<int:id>',methods=['GET'])
    def status(id):
        user = get_current_user()
        challenge = InstanceChallenge.query.filter_by(id=id).first_or_404()
        try:
            r = requests.get(urllib.parse.urljoin(challenge.api, ''), headers={"Authorization": f"Token {challenge.apikey}"}, params={'userid': user.id})
            if r.status_code == 200:
                return jsonify(r.json())
        except:
            abort(500)
        abort(404)
    
    @authed_only
    @app.route(f'/plugins/{plugin_name}/create/<int:id>',methods=['POST'])
    def create(id):
        user = get_current_user()
        challenge = InstanceChallenge.query.filter_by(id=id).first_or_404()
        try:
            r = requests.post(urllib.parse.urljoin(challenge.api, 'create'), headers={"Authorization": f"Token {challenge.apikey}"}, json={'userid': user.id})
            if r.status_code == 200:
                return jsonify(r.json())
        except:
            abort(500)
        abort(404)
    
    @authed_only
    @app.route(f'/plugins/{plugin_name}/destroy/<int:id>',methods=['POST'])
    def destroy(id):
        user = get_current_user()
        challenge = InstanceChallenge.query.filter_by(id=id).first_or_404()
        try:
            r = requests.post(urllib.parse.urljoin(challenge.api, 'destroy'), headers={"Authorization": f"Token {challenge.apikey}"}, json={'userid': user.id})
            if r.status_code == 200:
                return jsonify(r.json())
        except:
            abort(500)
        abort(404)
