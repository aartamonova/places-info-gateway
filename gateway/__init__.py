from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

jwt = JWTManager(app)
bootstrap = Bootstrap(app)
api = Api(app)

from gateway.gateway_resource import GatewayTagListResource, GatewayOauthTokenResource

api.add_resource(GatewayTagListResource, '/tags/all')
api.add_resource(GatewayOauthTokenResource, '/oauth/token')

from gateway.routes import index_routes, errors_routes

# Migration
from gateway import gateway_model
