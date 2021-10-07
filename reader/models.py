from django.db import models

STATUS = [
    ('preparing', 'preparing'),
    ('started', 'started'),
    ('processing', 'processing'),
    ('completed', 'completed'),
    ('failed', 'failed')
]

# Create your models here.
class Log(models.Model):
    start_at = models.DateTimeField()
    filename = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS)
