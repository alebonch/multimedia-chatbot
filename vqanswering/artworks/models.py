from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .signals import delete_artwork_images


class Artwork(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150)
    year = models.CharField(max_length=7, default="Unknown")
    century = models.CharField(max_length=7, default="Unknown")
    time_period = models.CharField(max_length=200, null=True, blank=True, default="Unknown")
    image = models.CharField(max_length=200)
    thumb_image = models.CharField(max_length=200)
    subject = models.CharField(max_length=200, default="Unknown")
    type_of_object = models.CharField(max_length=200, default="Unknown")
    measurement = models.CharField(max_length=200, default="Unknown")
    maker = models.CharField(max_length=200, default="Unknown")
    materials_and_techniques = models.CharField(max_length=200, default="Unknown")
    location = models.CharField(max_length=200, default="Unknown")
    description = models.TextField()
    description_validated_by = models.CharField(max_length=200, blank=True, null=True)
    web_link = models.CharField(max_length=250, default="-", blank=True)
    link = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.title


class Chat(models.Model):
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    question_language = models.CharField(max_length=50, default='English')
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.question

class Metadata(models.Model):

    TYPE_CHOICES = [
        ('audio', 'Audio'),
        ('link', 'Link'),
        ('video', 'Video'),
    ]

    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=100,choices=TYPE_CHOICES)
    link = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField()
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, null=True, blank=True)
    weblink = models.CharField(max_length=255, default="-",null=True, blank=True)
    museumgroup = models.CharField(max_length=200, default="Is not shared")

    def __artwork__(self):
        return self.artwork

# Connect the signal receiver to the pre_delete signal of Artwork
pre_delete.connect(delete_artwork_images, sender=Artwork)
