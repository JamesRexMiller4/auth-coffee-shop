import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def drinks():
    drinks = Drink.query.order_by(Drink.id).all()
    results = []

    if len(drinks) == 0:
        abort(404)

    for drink in drinks:
        results.append(drink.short())

    response = {
        "success": True,
        "drinks": results
    }

    return jsonify(response)

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    drinks = Drink.query.order_by(Drink.id).all()
    results = []

    if len(drinks) == 0:
        abort(404)

    for drink in drinks:
        results.append(drink.long())


    response = {
        "success": True,
        "drinks": results
    }
    return jsonify(response)

@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def post_drinks(jwt):
    try:
        body = request.get_json()
        new_drink_title = body.get("title", None)
        new_drink_recipe = body.get("recipe", None)
        
        new_drink_recipe = json.dumps(new_drink_recipe)

        drink = Drink(title=new_drink_title, recipe=new_drink_recipe)
        drink.insert()

        new_drink = Drink.query.filter_by(title=new_drink_title).one_or_none()

        response = {
            "success": True,
            "drinks": [new_drink.long()]
        }
        return jsonify(response)
    except:
        abort(422)

@app.route('/drinks/<int:drink_id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def patch_drinks(jwt, drink_id):
    try:
        body = request.get_json()
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)

        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        print(drink)
        if drink is None:
            abort(404)
        
        if new_title and new_recipe:
            drink.title = new_title
            drink.recipe = new_recipe
        elif new_title:
            drink.title = new_title
        elif new_recipe:
            drink.recipe = new_recipe
        else: 
            abort(422)

        new_drink = Drink.query.filter_by(id=drink_id).one_or_none()

        response = {
            "success": True,
            "drinks": [new_drink.long()]
        }
        return jsonify(response)
    except:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()

        if drink is None:
            abort(404)
            
        drink.delete()

        return jsonify({
            "success": True,
            "delete": drink_id
        })

    except:
        abort(422)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
