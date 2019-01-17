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
    decorators = [jwt_required]

    def delete(self, recipe_id):
        result = Recipe.delete(recipe_id)
        return result

api.add_resource(APIRecipe, '/api/v1/recipe/<string:recipe_id>')


class APIRecipes(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.parser = reqparse.RequestParser()
        if request.method == 'POST':
            self.parser.add_argument('commands', type=list, required=True, location='json')
            self.parser.add_argument('name', type=str, required=True, location='json')

    def get(self):
        recipes = Recipes.objects()
        result = json.loads(recipes.to_json())
        return result

    def post(self):
        args = self.parser.parse_args()
        result = Recipe.create(args.name, args.commands)
        return result


api.add_resource(APIRecipes, '/api/v1/recipes')
