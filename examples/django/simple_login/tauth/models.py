from django.db import models

class Role(models.Model):
    # XXX - this max_length is totally arbitrary.
    uri = models.CharField(max_length=255)

    def __unicode__(self):
        return self.uri
