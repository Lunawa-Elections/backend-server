from django.conf import settings
from django.db import models
from . import processing
import os, shutil, cv2
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
            out_path = os.path.join(settings.PROCESS_ROOT, self.name)
            image = processing.check_valid(file_path)
            if image is not False:
                image, members = processing.draw_bbox(image)
                self.voted_members = members
                cv2.imwrite(out_path, image)
                for mid in members:
                    try:
                        member = Member.objects.get(loc=mid)
                        member.votes += 1
                        member.save()
                    except Exception as e:
                        logger.error(f"Error occurred during update: {e}", exc_info=True)
                self.status = "Processed"
                
        super(Image, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if self.voted_members:
            for mid in self.voted_members:
                member = Member.objects.get(loc=mid)
                member.votes = max(0, member.votes-1)
                member.save()
        try:
            source_path = os.path.join(settings.UPLOAD_ROOT, self.name)
            destination_path = os.path.join(settings.DELETE_ROOT, self.name)
            os.remove(os.path.join(settings.PROCESS_ROOT, self.name))
            shutil.move(source_path, destination_path)
        except Exception as e:
            logger.error(f"Error occurred during deletion: {e}", exc_info=True)

        super(Image, self).delete(*args, **kwargs)
