from django.db.models import CharField, IntegerField, TextField
from django.db import models


class Variable(models.Model):
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
