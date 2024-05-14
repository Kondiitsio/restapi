from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

from db import db
from models import TagModel, StoreModel, ItemModel
from models.store import stores_tags
from schemas import TagSchema, TagAndItemSchema

blp = Blueprint("Tags", "tags", description="Operations on tags")

@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)

        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(
                500,
                message=str(e)
            )
        return tag
    
@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting the tag.")

        return tag
    
    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while deleting the tag.")
        
        return {"message": "Tag deleted from item.", "item": item, "tag": tag}
    
@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    @blp.response(
        202,
        description="Deletes tag if no items are tagged to it.",
        example={"message": "Tag deleted."}
    )
    @blp.alt_response(404, description="Tag not found.")
    @blp.alt_response(
        400,
        description="Returned if the tag is assigned one or more items. In this case, the tag is not deleted.",
    )
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        # Delete the rows in the stores_tags table that are associated with the tag
        db.session.execute(
            stores_tags.delete().where(
                and_(stores_tags.c.tag_id == tag.id)
            )
        )

        db.session.delete(tag)
        db.session.commit()
        return {"message": "Tag deleted."}


@blp.route("/tag")
class CreateTag(MethodView):
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data):
        tag_name = tag_data.get('name')
        existing_tag = TagModel.query.filter_by(name=tag_name).first()

        if existing_tag:
            abort(400, message="A tag with this name already exists.")

        tag = TagModel(**tag_data)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(
                500,
                message=str(e)
            )
        return tag
    

@blp.route("/tag/<int:tag_id>/store/<int:store_id>")
class LinkTagToStore(MethodView):
    @blp.response(200, TagSchema)
    def put(self, tag_id, store_id):
        tag = TagModel.query.get_or_404(tag_id)
        store = StoreModel.query.get_or_404(store_id)

        # Add the tag to the store's tags
        store.tags.append(tag)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            abort(
                500,
                message=str(e)
            )
        return tag
    
@blp.route("/tags")
class GetAllTags(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self):
        tags = TagModel.query.all()
        return tags