from django.contrib import admin
from .models import Log
# Register your models here.


class LogAdmin(admin.ModelAdmin):
    list_filter = ('start_at', 'filename', 'status')


admin.site.register(Log, LogAdmin)