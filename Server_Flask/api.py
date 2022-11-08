from flask import Flask, request, abort, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug.utils import secure_filename
import os 

import config

configuration = config.LaptopPrototypeConfig()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(configuration.STATUS_PATH, "status.sqlite")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = configuration.MAP_PATH
app.config["ALLOWED_EXTENSIONS"] = configuration.ALLOWED_MAP_EXTENSIONS

#init database & (de)serializer
db = SQLAlchemy(app)
ma = Marshmallow(app)

#database - status model
class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    connected = db.Column(db.Boolean)
    battery = db.Column(db.Integer)
    xpos = db.Column(db.Integer)
    ypos = db.Column(db.Integer)   
    def __init__(self, id, connected, battery, xpos, ypos):
        self.id = id
        self.connected = connected
        self.battery =  battery
        self.xpos = xpos
        self.ypos = ypos

#status schema
class StatusSchema(ma.Schema):
    class Meta:
        fields = ('id', 'connected', 'battery', 'xpos', 'ypos')

#validate file extension
def file_is_valid(filename):
    return filename.rsplit('.', 1)[1].upper() in configuration.ALLOWED_MAP_EXTENSIONS

#init schema
statusSchema   = StatusSchema()
lsStatusSchema = StatusSchema(many=True)   

#create database if it doesn't already exist
db.create_all()

@app.route('/status/all', methods=["GET"])
def get_robot_status_list():
    lsStatus = Status.query.all()
    result = lsStatusSchema.dump(lsStatus)
    return jsonify(result)

@app.route('/status', methods=["POST"])
def add_robot_status():
    if('id' in request.json and 'connected' in request.json and 'battery' in request.json and 'xpos' in request.json and 'ypos' in request.json):
        id = request.json['id']
        if(isinstance(id, int)):
            if not Status.query.filter_by(id = id).first():
                battery = request.json['battery']
                if(not isinstance(battery, int)):
                    abort(404, 'Invalid battery value.')
                connected = request.json['connected']
                if(not isinstance(connected, bool)):
                    abort(404, 'Invalid connected value.')
                xpos = request.json['xpos']
                if(not isinstance(xpos, int)):
                    abort(404, 'Invalid X-position value.')
                ypos = request.json['ypos']
                if(not isinstance(ypos, int)):
                    abort(404, 'Invalid Y-Position value.')

                newRobotStatus = Status(id, connected, battery, xpos, ypos)
                db.session.add(newRobotStatus)
                db.session.commit()

                return statusSchema.jsonify(newRobotStatus)

            else:
                abort(409, 'ID already in use.')
        else:
            abort(404, 'Invalid ID.')

#if('id' in request.json and 'connected' in request.json and 'battery' in request.json and 'xpos' in request.json and 'ypos' in request.json):
#    try:
#        robotID = int(request.json['id'])
#        if not Status.query.filter_by(id = robotID).first():
#            try:
#                battery = int(request.json['battery'])
#                connected = bool(request.json['connected'])
#                xpos = int(request.json['xpos'])
#                ypos = int(request.json['ypos'])
#
#                newRobotStatus = Status(robotID, connected, battery, xpos, ypos)
#                db.session.add(newRobotStatus)
#                db.session.commit()

#            except ValueError:
#                abort(404, 'Invalid parameter data type/s.')
#        else:
#            abort(409, 'ID is already in use.')
#    except ValueError:
#        abort(404, 'Invalid ID.')
#else:
#    abort(400, 'Your request is missing some parameters.') 
#
#    return statusSchema.jsonify(newRobotStatus)

@app.route('/status/<individual_id>', methods=["GET"])
def get_all_data(individual_id):
    status = Status.query.filter_by(id=individual_id).first()
    if status:
         return statusSchema.jsonify(status)
    else:
       abort(404, 'There is not a robot status available with this ID.')  

@app.route('/status/<individual_id>', methods=["PUT"])
def update_individual_data(individual_id):
    status = Status.query.filter_by(id=individual_id).first()
    if status:
        if("battery" in request.json):
            battery = request.json['battery']
            if(isinstance(battery, int)):
                status.battery = battery
        if("connected" in request.json):
            connected = request.json['connected']
            if(isinstance(connected, bool)):
                status.connected = connected
        if("xpos" in request.json):
            xpos = request.json['xpos']
            if (isinstance(xpos, int)):
                status.xpos = xpos
        if("ypos" in request.json):
            ypos = request.json['ypos'] 
            if(isinstance(ypos, int)):
                status.ypos = ypos

        db.session.commit()
        return statusSchema.jsonify(status)
    else:
        abort(404, 'There is not a robot status available with this ID.') 


@app.route('/status/<individual_id>/<request_list>', methods=["GET"])
def get_specific_data(individual_id, request_list):
    status = Status.query.filter_by(id=individual_id).first()
    if status:
            reqs = request_list.split('_') 
            response = {}
            for req in reqs:
                if (req in statusSchema.Meta.fields): 
                    response[req] = status.__dict__[req]
                    
            if len(response):
                return jsonify(response)     
            else:
                abort(404, 'Invalid request')               
    else:
        abort(404, 'There is not a robot status available with this ID.') 


@app.route('/map', methods=["GET"])
def get_map():
    try:
        return send_from_directory(configuration.MAP_PROCESSED_PATH, 'complete.SLAM', as_attachment=False)
    except FileNotFoundError:
        abort(404, 'the requested file was not found')
    

@app.route('/map', methods=["POST"])
def post_map_updates():
    if('file' in request.files):
        file = request.files['file']
        if(file.filename == ''):
            abort(400, 'Invalid filename.')
        if file and file_is_valid(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(configuration.MAP_PATH, filename))
            return "file has been saved"
        else:
            abort(400, 'Issues with file that was uploaded.')       
    else:
        abort(400, 'Request did not contain a file.')

#Start server
if __name__ == '__main__':
    app.run(debug=True)