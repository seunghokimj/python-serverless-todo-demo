from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute


class Todo(Model):
    class Meta:
        table_name = "Todo"
        region = 'ap-northeast-2'

    userId = UnicodeAttribute(hash_key=True)
    createdAt = UnicodeAttribute(range_key=True)
    updatedAt = UnicodeAttribute()
    title = UnicodeAttribute()
