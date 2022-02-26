from django.contrib import admin


# Register your models here.
from .models import PROFILE, OBJETSITE, HISTORIQUELOGIN, Pages

class PROFILEAdmin(admin.ModelAdmin):
    list_display = ('id', 'getfirstname', 'poste', 'superieur','admin', 'slider')
    #, 'getfirstname'
    def getfirstname(self, obj):
        return obj.utilisateur

class OBJETSITEAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'parent','nom','lien')
    list_filter = ("type", "ancetrenom", "ancetretype")

class HISTORIQUELOGINAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_object', 'type_object','date','temps', 'active')


admin.site.register(PROFILE, PROFILEAdmin)
admin.site.register(OBJETSITE, OBJETSITEAdmin)
#admin.site.register(HISTORIQUELOGIN)
admin.site.register(Pages)
admin.site.register(HISTORIQUELOGIN, HISTORIQUELOGINAdmin)
