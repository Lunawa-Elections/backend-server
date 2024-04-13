from django.apps import AppConfig
from django.conf import settings
from . import models
import json, os

class LunawaElectionsConfig(AppConfig):
    name = 'lunawaelections'

    def ready(self, *args, **kwargs):
        super(LunawaElectionsConfig, self).ready(*args, **kwargs)
        self.init_members()

    def initialize_members(self):
        names_data = json.load(open(os.path.join(settings.REFERENCE_ROOT, 'names.json')))
        print(names_data)
        
        # initial_members = [
        #     {'loc': 'Location1', 'name': 'Name1', 'vaas': 'Vaas1', 'votes': 10},
        #     {'loc': 'Location2', 'name': 'Name2', 'vaas': 'Vaas2', 'votes': 20},
        # ]

        # for member in initial_members:
        #     models.Member.objects.get_or_create(
        #         loc=member['loc'],
        #         name=member['name'],
        #         vaas=member['vaas'],
        #         defaults={'votes': member['votes']}
        #     )
