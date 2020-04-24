from django.db.models import Model, CharField, IntegerField, TextField


class Variable(Model):
    owner_id = IntegerField()

    CORE = 'core'
    GLOBAL = 'global'
    SERVER = 'server'
    PRIVATE = 'private'
    VARIABLE_TYPES = [
        (CORE, 'core'),
        (GLOBAL, 'global'),
        (SERVER, 'server'),
        (PRIVATE, 'private'),
    ]
    var_type = CharField(max_length=7, choices=VARIABLE_TYPES, default=SERVER)

    value_string = TextField()
    name = CharField(max_length=2000)

    class Meta:
        unique_together = [['name', 'owner_id']]
