from flask import Blueprint

config_bp = Blueprint('config', __name__)

from . import config 