from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy import and_

from db import db
from models import ItemModel, TagModel, StoreModel, CategoryModel
from models.item import items_tags
from schemas import ItemSchema, ItemUpdateSchema
from flask import jsonify, request

blp = Blueprint("items", __name__, description="Operations on items")


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    def delete(self, item_id):
        
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.name = item_data["name"]
            item.price = item_data["price"]
            item.quantity = item_data["quantity"]
            item.category_id = item_data["category_id"]
            item.store_id = item_data["store_id"]
            item.tags = [TagModel.query.get(tag["id"]) for tag in item_data["tags"]]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item

@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.options(joinedload(ItemModel.store)).all()
    
    
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        tag_ids = [tag['id'] for tag in item_data.pop('tags', [])]
        tags = TagModel.query.filter(TagModel.id.in_(tag_ids)).all()

        # Check if the category exists
        category_id = item_data.get('category_id')
        if category_id is not None and CategoryModel.query.get(category_id) is None:
            abort(400, message=f"Category with id {category_id} does not exist.")

        item_data.pop('tags', None)  # Remove the 'tags' key from item_data

        # Create a new ItemModel instance with the data from the request
        item = ItemModel(**item_data)

        for tag in tags:
            tag.items.append(item)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            error_message = str(e.__dict__['orig'])
            abort(500, message=f"An error occurred while inserting the item: {error_message}")
        
        return item
    
@blp.route('/item/data')
def get_all_data():
    tags = TagModel.query.all()
    items = ItemModel.query.all()
    stores = StoreModel.query.all()
    return jsonify({
        'tags': [tag.to_dict() for tag in tags],
        'items': [item.to_dict() for item in items],
        'stores': [store.to_dict() for store in stores],
    })

@blp.route("/items/move/<int:to_store_id>")
class MoveItems(MethodView):
    def put(self, to_store_id):
        # Get the target store
        to_store = StoreModel.query.get_or_404(to_store_id)

        # Get the item IDs from the request data
        item_ids = request.json.get('item_ids', [])

        # Get the items
        items = ItemModel.query.filter(ItemModel.id.in_(item_ids)).all()

        # Move the items to to_store
        for item in items:
            item.store_id = to_store.id

        # Save the changes to the database
        db.session.commit()

        return {"message": f"Items moved to store {to_store.name}."}
    

@blp.route("/items/delete")
class ItemBulkDelete(MethodView):
    def post(self):
        data = request.get_json()
        item_ids = data.get('item_ids')

        if not item_ids:
            return {"message": "No item_ids provided"}, 400

        # Delete the rows in the items_tags table that refer to the items
        db.session.query(items_tags).filter(items_tags.c.item_id.in_(item_ids)).delete(synchronize_session=False)

        # Delete the items
        ItemModel.query.filter(ItemModel.id.in_(item_ids)).delete(synchronize_session=False)

        db.session.commit()

        return {"message": "Items deleted successfully"}