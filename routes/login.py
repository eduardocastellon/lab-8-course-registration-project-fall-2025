from flask import Flask, request, redirect, jsonify, Blueprint
from sqlalchemy.types import JSON
from vars.database import db
from vars.port import port_number
import requests
from routes.utils.functions import LoginCheck

login_blueprint = Blueprint('login', __name__)

#POST ROUTE FOR LOGGING IN
@login_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    return LoginCheck(username, password)