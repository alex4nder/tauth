from django.db import models

class Role(models.Model):
    # XXX - this max_length is totally arbitrary.
    uri = models.CharField(max_length=255)

    def __unicode__(self):
        return self.uri

class Resource(models.Model):
    uri = models.CharField(max_length=255)

    def __unicode__(self):
        return self.uri

class Permission(models.Model):
    ALLOW = 'allow'
    DENY = 'deny'

    effect = models.CharField(choices=((ALLOW, "Allow"),
                                       (DENY, "Deny")),
                              default=DENY,
                              max_length=255)

    role = models.ForeignKey('Role')
    resource = models.ForeignKey('Resource')

    action_uri = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return "%s - %s - %s" % (self.role.uri, self.resource.uri, self.action_uri)
