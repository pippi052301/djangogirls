from django.db import models

# Create your models here.
# create a note page
class Note(models.Model):
    title = models.CharField(max_length=500)
    content = models.TextField()
    
    def _str_(self):
        return self.title