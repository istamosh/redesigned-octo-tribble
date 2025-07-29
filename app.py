from flask import Flask, request, jsonify
import pymongo
from datetime import datetime

app = Flask(__name__)

client = pymongo.MongoClient("localhost", 27017)
db = client["ticketq-database"]
collection = db["ticketq-collection"]

def is_valid_date(date):
    try:
        if date.endsWith('Z'):
            date = date[:-1] + '+00:00'
        datetime.fromisoformat(date)
        return True
    except ValueError:
        return False

@app.route('/')
def index():
    return "Halo, Welcome to the TicketQ backend!"

@app.route('/tickets', methods=['GET', 'POST'])
def list_or_create_ticket():
    #TODO: ticket model is consists of id, eventName, location, time, isUsed
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({'error': 'Missing JSON in request'}), 400
        
        data = request.get_json()

        required_fields = ["eventName", "location", "time"]
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        if not is_valid_date(data["time"]):
            return jsonify({'error': 'Invalid date, must use this format YYYY-MM-DDTHH:MM:SSZ, example 2025-08-31T20:00:00Z'})

        #TODO: create new ticket
        eventName = data['eventName']
        return f'Created new ticket: {eventName}\n'
    
    return 'Currently viewing all tickets'

@app.route('/tickets/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def manage_ticket(id):
    if request.method == 'PATCH':
        #TODO: mark ticket as used
        return f'Ticket ID: {id} was successfully marked as used'
    elif request.method == 'DELETE':
        #TODO: delete a ticket
        return f'Ticket ID: {id} was successfully deleted'
    
    return f'Viewing a ticket with ID: {id}'


# GET /tickets -list all tickets
# GET /tickets/:id -view specific ticket
# POST /tickets -create new ticket
# PATCH /tickets/:id -mark ticket as used
# DELETE /tickets/:id -remove a ticket