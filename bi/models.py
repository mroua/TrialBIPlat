from django.contrib.auth.models import User
from django.db import models

from Login.models import PROFILE, OBJETSITE


class Messagerie(models.Model):
    id = models.AutoField(primary_key=True)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    designation = models.CharField(max_length=80, default='', null=True, blank=True)
    sujet = models.CharField(max_length=80, default='')
    probleme = models.TextField(default='')
    image = models.FileField(upload_to="images/", blank=True, null=True)
    lien = models.CharField(max_length=600, default='', blank=True, null=True)
    date= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.designation

TypeEtape = [
    ('1', 'Recue'),
    ('2', 'En-cours'),
    ('3', 'Validation'),
    ('4', 'Confirmation'),
]

class EtapeProbleme(models.Model):
    id = models.AutoField(primary_key=True)
    messagerie = models.ForeignKey(Messagerie, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=TypeEtape, default='1')
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

typeact = [
    ('1', 'Ajouter'),
    ('2', 'Supprimer'),

]

class Autorisation(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE, blank=True, null=True)
    action = models.CharField(max_length=7, choices=typeact, default='1')
    useract = models.CharField(max_length=60)
    dateact= models.DateTimeField(auto_now_add=True)
    objetsite = models.ForeignKey(OBJETSITE, on_delete=models.CASCADE, blank=True, null=True)
    validite = models.BooleanField(default=False)
    refuser = models.BooleanField(default=False)
    userchoix = models.CharField(max_length=60) #la personne qui valide ou refuse la demande

notifcouleur = [
    ('#2E538B', 'login/newint/Notification Circle Bleu.svg'), #blue
    ('#a5cf4b', 'login/newint/Notification Circle Green.svg'), #green
    ('#ffc34a', 'login/newint/Notification Circle Yellow.svg'), #yellow
    ('#B21122', 'login/newint/RED.svg'),  #red
]

class Notification(models.Model):
    id = models.AutoField(primary_key=True, unique =True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    titre = models.CharField(max_length=120)
    texte = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    couleur = models.CharField(max_length=7, choices=TypeEtape, default='#2E538B')
    recu = models.BooleanField(default=False)
    lien = models.CharField(max_length=200, null=True, blank=True)

class Slider(models.Model):
    id = models.AutoField(primary_key=True, unique =True)
    users = models.ForeignKey(User, related_name='userslider', on_delete=models.CASCADE, blank=True, null=True)
    nom = models.CharField(max_length=200)
    listerapport = models.ManyToManyField(OBJETSITE, blank=True,related_name='listerapport')
    active = models.BooleanField(default=True)

    def __str__(self):
        corporal_segment_associated = ", ".join(str(seg) for seg in self.listerapport.all())
        return "{}".format(corporal_segment_associated)

class Requette(models.Model):
    id = models.AutoField(primary_key=True, unique =True)
    texteliens = models.TextField()
    texteutilisateur = models.TextField()
    texteact = models.TextField()