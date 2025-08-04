from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timezone
from bson.objectid import ObjectId

# set up basic logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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
        return ticket_time < now
    except ValueError:
        return False

@app.route('/')
def index():
    return "Halo, Welcome to the TicketQ backend!"

@app.route('/tickets', methods=['GET', 'POST'])
def list_or_create_ticket():
    #TODO: ticket model is consists of id (auto-gen), eventName, location, time, isUsed
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
                return jsonify({'error': 'Date cannot be in the past'}), 400

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
    
    #TODO: (optional) return only non-used and sorted
    try:
        tickets = list(collection.find())
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
            logger.error(f'Error creating ticket: {str(e)}', exc_info=True)
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500

    elif request.method == 'DELETE':
        #TODO: delete a ticket
        return f'Ticket ID: {id} was successfully deleted'
    
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


# GET /tickets -list all tickets
# GET /tickets/:id -view specific ticket
# POST /tickets -create new ticket
# PATCH /tickets/:id -mark ticket as used
# DELETE /tickets/:id -remove a ticket