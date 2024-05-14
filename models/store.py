from db import db

stores_tags = db.Table('stores_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('store_id', db.Integer, db.ForeignKey('stores.id'), primary_key=True),
    extend_existing=True
)

class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic")
    tags = db.relationship('TagModel', secondary=stores_tags, backref=db.backref('stores_backref'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }