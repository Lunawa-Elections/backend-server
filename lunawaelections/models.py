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
    loc = models.CharField(max_length=255)
    name = models.CharField(max_length=50)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}: {self.votes}"

class Image(models.Model):
    name = models.CharField(max_length=255)
    android_id = models.ForeignKey(AndroidID, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, default="Uploaded")
    voted_members = models.ManyToManyField(Member, related_name='voted_images')

    def __str__(self):
        return f"{self.name}: {self.voted_members}"
    
    def save(self, *args, **kwargs):
        if not self.pk: 
            file_path = os.path.join(settings.UPLOAD_ROOT, self.name)
            out_path = os.path.join(settings.PROCESS_ROOT, self.name)
            image = processing.check_valid(file_path)
            if image is not False:
                image = processing.draw_bbox(image)
                cv2.imwrite(out_path, image)
                self.status = "Processed"
                # for member_id in member_ids:
                #     try:
                #         member = Member.objects.get(id=member_id)
                #         new_image.voted_members.add(member)
                #     except Member.DoesNotExist:
                #         pass
            else:
                self.status = "Invalid"
            
        super(Image, self).save(*args, **kwargs)

    
    def delete(self, *args, **kwargs):
        if self.voted_members.exists():
            for member in self.voting_members.all():
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
