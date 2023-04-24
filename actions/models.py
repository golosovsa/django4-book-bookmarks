from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Action(models.Model):
    user = models.ForeignKey(get_user_model(), related_name='actions', on_delete=models.CASCADE)
    verb = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    target_ct = models.ForeignKey(ContentType, blank=True, null=True, related_name='target_obj',
                                  on_delete=models.CASCADE)
    target_pk = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_ct', 'target_pk')

    class Meta:
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['target_ct', 'target_pk'])
        ]
        ordering = ['-created', ]
