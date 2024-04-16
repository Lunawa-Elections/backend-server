from django.conf import settings
from django.db.models import F
from django.db import models
from . import processing
import os, shutil, cv2
import threading
import logging

logger = logging.getLogger('lunawaelections')

class AndroidID(models.Model):
    name = models.CharField(max_length=255)
    counter = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}: {self.counter}"

class Member(models.Model):
    loc = models.CharField(max_length=50)
    name = models.CharField(max_length=255, default="")
    vaas = models.CharField(max_length=255, default="")
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.loc},{self.name},{self.vaas},{self.votes}"

class Image(models.Model):
    name = models.CharField(max_length=255)
    android_id = models.ForeignKey(AndroidID, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default="Uploaded")
    voted_members = models.JSONField(default=list)

    def __str__(self):
        return f"{self.name}: {self.voted_members}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.status = "Invalid"
            file_path = os.path.join(settings.UPLOAD_ROOT, self.name)
            image = processing.check_valid(file_path)

            if image is not False:
                self.status = "Processed"
                threading.Thread(target=self.post_process, args=(image,)).start()
                
        super(Image, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        Member.objects.filter(loc__in=self.voted_members).update(votes=F('votes') - 1)
        shutil.rmtree(os.path.join(settings.PROCESS_ROOT, self.name), ignore_errors=True)
        shutil.rmtree(os.path.join(settings.UPLOAD_ROOT, self.name), ignore_errors=True)

        super(Image, self).delete(*args, **kwargs)

    def post_process(self, image):
        out_path = os.path.join(settings.PROCESS_ROOT, self.name)
        self.android_id.counter += 1
        self.android_id.save()

        image, members = processing.draw_bbox(image)
        self.voted_members = members
        Member.objects.filter(loc__in=members).update(votes=F('votes') + 1)

        cv2.imwrite(out_path, image)
        self.status = "Parsed"
        self.save(update_fields=['status', 'voted_members'])