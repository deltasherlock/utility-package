from django.contrib import admin

# Register your models here.

from .models import ChangesetWrapper, FingerprintWrapper

admin.site.register(ChangesetWrapper)
admin.site.register(FingerprintWrapper)
