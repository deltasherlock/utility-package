from django.contrib import admin

# Register your models here.

from .models import ChangesetWrapper, FingerprintWrapper, EventLabel, QueueItem

admin.site.register(EventLabel)
admin.site.register(QueueItem)
admin.site.register(ChangesetWrapper)
admin.site.register(FingerprintWrapper)
