from django import forms
from django.forms.widgets import Input, Textarea

from Login.models import OBJETSITE
from django.forms import Select, modelformset_factory, ImageField

from bi.models import Messagerie, Autorisation


class AjoutOjetSiteForm(forms.ModelForm):
    class Meta:
        model = OBJETSITE
        fields = ('id', 'type', 'parent', 'slider')
        widgets = {
            'parent': Select(attrs={"class": "form-control"}),
            'type': Select(attrs={'class': 'form-control', "onChange":'RaffraichirChoixtype(this.value)'})
        }
        labels = {
            'parent': '',
            'type': '',
        }

class AutorisationForm(forms.ModelForm):
    class Meta:
        model = Autorisation
        fields = ('id', 'user', 'objetsite')

        widgets = {
            'user': Select(attrs={"class": "form-control"}),
            'objetsite': Select(attrs={'class': 'form-control'})
        }
        labels = {
            'user': '',
            'objetsite': '',
        }

OjetSiteFormset = modelformset_factory(
    OBJETSITE,
    fields=('nom', 'lien'),

    extra=1,
    widgets={
        'nom': Input(attrs={'class': 'form-control nomobjet','placeholder': 'Nom'}),
        'lien': Input(attrs={'class': 'form-control lien','placeholder': 'lien'}),
    },
    labels = {
        'nom': '',
        'lien': '',
    }
)


class MessagerieForm(forms.ModelForm):
    class Meta:
        model = Messagerie
        fields = ('id', 'utilisateur', 'designation', 'sujet', 'probleme', 'lien', 'image')
        widgets = {
            'designation': Input(attrs={"class": "form-control"}),
            'sujet': Input(attrs={'class': 'form-control','placeholder': 'Sujet'}),
            'probleme': Textarea(attrs={'class': 'form-control','placeholder': 'Problématique'}),
        }
        labels = {
            'designation': '',
            'sujet': '',
            'probleme': '',
        }
