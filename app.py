from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timezone
from bson.objectid import ObjectId
from flask_swagger_ui import get_swaggerui_blueprint

# set up basic logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# swagger
SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'TicketQ API Documentation'
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

client = MongoClient("mongodb://mongoadmin:passw0rd@mongo:27017/?authSource=admin")

# test connection
try:
    client.admin.command('ping')
    logger.info("Successfully connected to Mongo")
except Exception as e:
    logger.error(f"Could not connect to Mongo: {e}")

db = client["ticketqdb"]
collection = db["ticketqcollection"]

def is_valid_date(date):
    try:
        if date.endswith('Z'):
            date = date[:-1] + '+00:00'
        datetime.fromisoformat(date)
        return True
    except ValueError:
        return False
    
def is_past_date(date):
    try:
        if date.endswith('Z'):
            date = date[:-1] + '+00:00'
        ticket_time = datetime.fromisoformat(date)
        now = datetime.now(timezone.utc)
        
        # get the date only
        ticket_date = ticket_time.date()
        today = now.date()
        
        return ticket_date <= today
    except ValueError:
        return False

@app.route('/')
def index():
    return "Halo, Welcome to the TicketQ backend!"

@app.route('/tickets', methods=['GET', 'POST'])
def list_or_create_ticket():
    if request.method == 'POST':
        try:
            if not request.is_json:
                return jsonify({'error': 'Missing JSON in request'}), 400
            
            data = request.get_json()

            # log request
            logger.debug(f"Received POST request: {data}")

            required_fields = ["eventName", "location", "time"]
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
                
            if not is_valid_date(data["time"]):
                return jsonify({'error': 'Invalid date, must use this format YYYY-MM-DDTHH:MM:SSZ, example 2025-08-31T20:00:00Z'}), 400
            if is_past_date(data["time"]):
                return jsonify({'error': 'Date must be in the future'}), 400

            post = {
                "eventName": data["eventName"],
                "location": data["location"],
                "time": data["time"],
                "isUsed": False
            }

            result = collection.insert_one(post)

            return jsonify({
                "message": f"Created new ticket: {data['eventName']}",
                "id": str(result.inserted_id)
            }), 201
        
        except Exception as e:
            logger.error(f'Error creating ticket: {str(e)}', exc_info=True)
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    
    try:
        # sort by all unused then used, and earliest to later in the future
        tickets = list(collection.find().sort([
            ('isUsed', 1),
            ('time', 1)
            ]))
        for ticket in tickets:
            ticket['_id'] = str(ticket['_id'])

        return jsonify({
            "message": "Success retrieving all tickets",
            "tickets": tickets
        }), 200
    
    except Exception as e:
        logger.error(f'Error viewing tickets: {str(e)}', exc_info=True)
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    

@app.route('/tickets/<string:id>', methods=['GET', 'PATCH', 'DELETE'])
def manage_ticket(id):
    try:
        oid = ObjectId(id)
    except:
        return jsonify({'error': 'Invalid ticket ID format'}), 400

    if request.method == 'PATCH':
        try:
            ticket = collection.update_one(
                {"_id": oid},
                {"$set":
                    {"isUsed": True}
                }
            )

            # check if nothing was affected
            if ticket.modified_count == 0:
                return jsonify({'error': 'Ticket not found or already used'}), 404

            return jsonify({
                "message": "Successfully marked a ticket",
                "id": str(oid)
            }), 200

        except Exception as e:
            logger.error(f'Error marking ticket: {str(e)}', exc_info=True)
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500

    elif request.method == 'DELETE':
        try:
            ticket = collection.delete_one({"_id": oid})

            # check if nothing was affected
            if ticket.deleted_count == 0:
                return jsonify({'error': 'Ticket not found or already deleted'}), 404

            return jsonify({
                "message": "Successfully deleted a ticket",
                "id": str(oid)
            }), 200

        except Exception as e:
            logger.error(f'Error deleting ticket: {str(e)}', exc_info=True)
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    
    try:
        ticket = collection.find_one({"_id": oid})
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        ticket['_id'] = str(ticket['_id'])

        return jsonify({
            "message": "Success retrieving ticket",
            "ticket": ticket
        }), 200
    
    except Exception as e:
        logger.error(f'Error viewing ticket: {str(e)}', exc_info=True)
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500