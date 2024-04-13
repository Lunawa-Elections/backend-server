from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import AppConfig
from django.conf import settings
import pandas as pd
import json, os

class LunawaElectionsConfig(AppConfig):
    name = 'lunawaelections'

    def ready(self, *args, **kwargs):
        super(LunawaElectionsConfig, self).ready(*args, **kwargs)
        post_migrate.connect(init_members, sender=self)

@receiver(post_migrate)
def init_members(sender, **kwargs):
    from . import models

    names_data = json.load(open(os.path.join(settings.REFERENCE_ROOT, 'names.json')))
    votes_data = pd.read_csv(os.path.join(settings.REFERENCE_ROOT, 'votes.csv'), index_col="Member")

    for k, data in names_data.items():
        vaas = data["name"]
        for loc, name in data.items():
            if loc != "name":
                candidate, created = models.Member.objects.get_or_create(loc=loc,name=name,vaas=vaas)
                if created:
                    candidate.votes = votes_data.loc[int(loc), "Votes"]
                    candidate.save()