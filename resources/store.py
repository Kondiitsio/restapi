from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import db
from models import StoreModel, TagModel
from models.store import stores_tags
from schemas import StoreSchema
from flask import request

blp = Blueprint("stores", __name__, description="Operations on stores")

@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)

        # Delete the rows in the stores_tags table that are associated with the store
        db.session.execute(
            stores_tags.delete().where(
                stores_tags.c.store_id == store.id
            )
        )
        # Delete the items that belong to the store
        for item in store.items:
            db.session.delete(item)

        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted."}
    

    @blp.arguments(StoreSchema)
    @blp.response(200, StoreSchema)
    def put(self, store_data, store_id):
        # Get the store with the given store_id
        store = StoreModel.query.get_or_404(store_id)

        # Update the store's attributes with the data from the request
        for key, value in store_data.items():
            if key == 'tags':
                # Update the store's tags
                store.tags = [TagModel.query.get(tag['id']) for tag in value]
            else:
                setattr(store, key, value)

        # Save the updated store to the database
        db.session.commit()

        return store

@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()
    
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        # Extract the tags from the request data
        tags_data = store_data.pop('tags', [])

        store = StoreModel(**store_data)

        # For each tag_id in tags_data, get the TagModel and add it to the store's tags
        for tag_id in tags_data:
            tag = TagModel.query.get(tag_id)
            if tag:
                store.tags.append(tag)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message="A store with the same name already exists.",
            )
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting the store.")
        return store