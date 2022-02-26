from django.contrib import admin

# Register your models here.
from .models import EtapeProbleme, Messagerie, Autorisation, Notification, Requette


class EtapeProblemeAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_utilisateur', 'get_sujet')

    def get_utilisateur(self, obj):
        return obj.messagerie.designation
    def get_sujet(self, obj):
        return obj.messagerie.sujet

class MessagerieAdmin(admin.ModelAdmin):
    list_display = ('id', 'designation', 'sujet', 'lien', 'date')

class AutorisationAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'user', 'useract', 'userchoix')


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'texte', 'recu')

admin.site.register(EtapeProbleme, EtapeProblemeAdmin)
admin.site.register(Messagerie, MessagerieAdmin)
admin.site.register(Autorisation, AutorisationAdmin)
admin.site.register(Notification,NotificationAdmin)
admin.site.register(Requette)