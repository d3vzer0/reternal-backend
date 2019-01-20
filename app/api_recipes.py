from app import app, api, jwt
from app.models import Recipes
from app.operations import Recipe
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from bson.json_util import dumps
import json


class APIRecipe(Resource):
    decorators = []

    def get(self, recipe):
        pipeline = [{ '$unwind': '$commands' },{'$lookup': {'from':'command_mapping',
            'localField':'commands.reference', 'foreignField':'_id', 'as':'metadata'},},
            {'$unwind': {'path':'$metadata', 'preserveNullAndEmptyArrays':True}}]
        recipes = Recipes.objects(name=recipe).aggregate(*pipeline)
        result = json.loads(dumps(recipes))
        return result

    def delete(self, recipe):
        result = Recipe(recipe).delete()
        return result

api.add_resource(APIRecipe, '/api/v1/recipe/<string:recipe>')


class APIRecipes(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == 'POST':
            self.args.add_argument('commands', type=list, required=True, location='json')
            self.args.add_argument('name', type=str, required=True, location='json')

    def get(self):
        recipes = Recipes.objects()
        result = json.loads(recipes.to_json())
        return result

    def post(self):
        args = self.args.parse_args()
        result = Recipe(args.name).create(args.commands)
        return result


api.add_resource(APIRecipes, '/api/v1/recipes')
