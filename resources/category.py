from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import IntegrityError

from db import db

from models import CategoryModel
from schemas import CategorySchema

blp = Blueprint("Categories", __name__, description="Operations on categories")

@blp.route("/category")
class CreateCategory(MethodView):
    @blp.arguments(CategorySchema)
    @blp.response(201, CategorySchema)
    def post(self, category_data):
        category = CategoryModel(**category_data)
        try:
            category.save_to_db()
        except IntegrityError:
            db.session.rollback()
            return {"message": "A category with this name already exists"}, 400

        return {"message": "Category created successfully", "category": CategorySchema().dump(category)}
    
@blp.route("/category")
class CategoryList(MethodView):
    @blp.response(200, CategorySchema(many=True))
    def get(self):
        return CategoryModel.query.all()
    
@blp.route("/category/<int:category_id>")
class Category(MethodView):
    @blp.response(200)
    def delete(self, category_id):
        category = CategoryModel.query.get(category_id)
        if category is None:
            return {"message": "Category not found"}, 404

        db.session.delete(category)
        db.session.commit()

        return {"message": "Category deleted successfully"}
    
    @blp.response(200, CategorySchema)
    def get(self, category_id):
        category = CategoryModel.query.get(category_id)
        if category is None:
            return {"message": "Category not found"}, 404

        return category
    

    