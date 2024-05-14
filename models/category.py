from db import db

class CategoryModel(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    # Relationship to items
    items = db.relationship('ItemModel', backref='category', lazy='dynamic')

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()