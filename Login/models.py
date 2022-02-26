from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import int_list_validator
from django.db import models

# Create your models here.

autorisationType = [
    ('TC', 'Consolidé (tous)'),
    ('AU', 'Autre'),
]

TypeObjet = [
    ('1', 'Consolidé'),
    ('2', 'Pole'),
    ('3', 'Région'),
    ('4', 'Direction'),
    ('5', 'Sous-direction'),
    ('6', 'Rapport'),
]


class OBJETSITE(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=1, choices=TypeObjet, default='1')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    nom = models.CharField(max_length=80, default='')
    lien = models.CharField(max_length=500, null=True, blank=True)
    slider = models.BooleanField(default=False)
    ancetrenom = models.CharField(max_length=100, null=True, blank=True)
    ancetretype = models.CharField(max_length=1, null=True, blank=True)

    def __str__(self):
        return str(self.nom)+'/'+str(self.ancetrenom)

class PROFILE(models.Model):
    id = models.AutoField(primary_key=True, unique =True)
    utilisateur = models.ForeignKey(User, null=True, related_name='utilisateur', on_delete=models.CASCADE)
    superieur = models.ForeignKey(User, null=True, related_name='superieur', on_delete=models.CASCADE, blank=True)
    poste = models.CharField(max_length=160, null=True, blank=True)
    slider = models.BooleanField(default=False)
    type_autorisation = models.CharField(max_length=2, choices=autorisationType, default='AU')
    id_objet = models.ManyToManyField(OBJETSITE, blank=True,related_name='id_objet')
    admin = models.BooleanField(default=False)
    photo = models.FileField()

    def __str__(self):
        return self.utilisateur.username





class HISTORIQUELOGIN(models.Model):
    id = models.AutoField(primary_key=True)
    utilisateur = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='utilisateur') #User ou Userinconnue
    utilisateurid = models.PositiveIntegerField()#id objet
    content_object = GenericForeignKey('utilisateur', 'utilisateurid')
    typepage = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='page')  # Page ou OBJETSITE
    typepageid = models.PositiveIntegerField()  # id objet
    type_object = GenericForeignKey('typepage', 'typepageid')
    date = models.DateTimeField(auto_now_add=True)
    temps = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.content_object)

class Userinconnu(models.Model):
    id = models.AutoField(primary_key=True)
    utilisateur = models.CharField(max_length=160, default='', blank=True, null=True)

class Pages(models.Model):
    id = models.AutoField(primary_key=True)
    pagenom = models.CharField(max_length=160, default='', blank=True, null=True)

    def __str__(self):
        return self.pagenom
