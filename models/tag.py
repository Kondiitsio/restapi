from db import db

stores_tags = db.Table('stores_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('store_id', db.Integer, db.ForeignKey('stores.id'), primary_key=True),
    extend_existing=True
)

items_tags = db.Table('items_tags',
    db.Column('item_id', db.Integer, db.ForeignKey('items.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    extend_existing=True
)

class TagModel(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    
    items = db.relationship("ItemModel", back_populates="tags", secondary="items_tags")
    stores = db.relationship('StoreModel', secondary=stores_tags, backref=db.backref('tags_backref'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }