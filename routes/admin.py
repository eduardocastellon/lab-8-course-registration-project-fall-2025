from flask import Flask, request, redirect, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import JSON
from vars.database import db
from routes.utils.functions import checkUniqueness
from werkzeug.security import generate_password_hash, check_password_hash

admin_blueprint = Blueprint('admin_api', __name__)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True) #INT FOR ID
    username = db.Column(db.String(50), nullable=False) #USERNAME FOR ADMIN
    password = db.Column(db.String(50), nullable=False) #PASSWORD FOR ADMIN
    first_name = db.Column(db.String(50), nullable=False) #STRING FOR FIRST NAME
    last_name = db.Column(db.String(50), nullable=False) #STRING FOR LAST NAME
    status = db.Column(db.String(5), nullable=False, default="ADMIN") #CHECK ACCOUNT STATUS

    def to_dict(self):
        return {"id": self.id, "username": self.username, "first_name": self.first_name, "password": self.password, "last_name": self.last_name, "status": self.status}


#GET
@admin_blueprint.route('/admin', methods=['GET'])
def GetAdmin():
    list = Admin.query.all()
    return jsonify([i.to_dict() for i in list])

#GET BY ID
@admin_blueprint.route('/admin/<int:id>', methods=['GET'])
def GetAdminById(id):
    admin = Admin.query.get_or_404(id)
    return jsonify(admin.to_dict())

#POST
@admin_blueprint.route('/admin', methods=['POST'])
def Create():
    x = request.json
    # Hash the password before storing
    hashed_password = generate_password_hash(x['password'])
    data = Admin(username=x['username'], password=hashed_password, first_name=x['first_name'], last_name=x['last_name'])
    #DEFINE BOOL ARRAY
    repeatedUser = checkUniqueness(data.username)
    if not repeatedUser:
        db.session.add(data)
        db.session.commit()
        return jsonify(data.to_dict())
    else:
        return {'message': "username already exists"}

#PUT
@admin_blueprint.route('/admin/<int:id>', methods=['PUT'])
def Change(id):
    updateData = Admin.query.get_or_404(id)
    x = request.json
    #OVERWRITE DATA
    if 'username' in x:
        updateData.username = x['username']
    if 'password' in x:
        # Hash the password if it's being updated
        updateData.password = generate_password_hash(x['password'])
    repeatedUser = checkUniqueness(updateData.username)
    if not repeatedUser:
        db.session.commit()
        return jsonify(updateData.to_dict())
    else:
        return {'message': "username already exists"}

#DELETE STUDENT
@admin_blueprint.route('/admin/<int:id>', methods=['DELETE'])
def Delete(id):
    remove = Admin.query.get_or_404(id)
    db.session.delete(remove)
    db.session.commit()
    return jsonify({'message': 'deleted'})
