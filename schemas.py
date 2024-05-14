from marshmallow import Schema, fields

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    message = fields.Str()

class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

class TagUpdateSchema(Schema):
    id = fields.Int()
    name = fields.Str(dump_only=True)

class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    quantity = fields.Int()
    store_id = fields.Int()
    category_id = fields.Int(allow_none=True)
    category = fields.Nested(CategorySchema())
    tags = fields.List(fields.Nested(PlainTagSchema()))

class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class TagSchema(PlainTagSchema):
    id = fields.Int(dump_only=True)
    store_id = fields.Int()
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)

class ItemUpdateSchema(Schema):
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    quantity = fields.Int()
    category_id = fields.Int(allow_none=True)
    store_id = fields.Int(required=True)
    tags = fields.List(fields.Nested(TagUpdateSchema()))

class ItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    price = fields.Float()
    quantity = fields.Int()
    store_id = fields.Int()
    store_name = fields.Method('get_store_name', dump_only=True)
    category_id = fields.Int(allow_none=True)
    category = fields.Nested(CategorySchema())
    tags = fields.List(fields.Nested(TagUpdateSchema()))

    def get_store_name(self, obj):
        return obj.store.name

class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(TagUpdateSchema()))

class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class UserRegisterSchema(UserSchema):
    email = fields.Str(required=True)

