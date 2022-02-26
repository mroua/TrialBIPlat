from django.contrib.auth import authenticate, login as dj_login, logout

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect


from bi.form import MessagerieForm
from bi.models import Notification, EtapeProbleme
from .models import PROFILE, OBJETSITE, HISTORIQUELOGIN, Userinconnu, Pages

lien = ''



def get_all_childs(elem, liste):
    if(elem.type == "6"):
        if(elem.id not in liste):
            liste.append(elem.id)
    else:
        enfant = OBJETSITE.objects.filter(parent=elem)
        for child in enfant:
            if (elem.id not in liste):
                liste.append(child.id)
            get_all_childs(child, liste)

        return liste

def loggin(request):
    if (request.user.id is None):
        msg = MessagerieForm(request.POST)
        if request.method == 'POST':
                identifiant = request.POST['identifiant']
                password = request.POST['password']

                try:
                    login = authenticate(username=identifiant, password=password)
                    dj_login(request, login)

                    if(login is not None):
                        return HttpResponse('Success')
                    else:
                        return HttpResponse('Error')
                except Exception:
                    utilisateur = Userinconnu.objects.create(utilisateur=identifiant)
                    utilisateur.save()
                    historique = HISTORIQUELOGIN.objects.create(content_object=utilisateur,
                                                                type_object=Pages.objects.get(pagenom='login'),
                                                                active=False)
                    historique.save()

                    return HttpResponse('Error')
        else:
            return render(request, 'LoginPage.html', {'msg':msg,
                                                      'lienpage': ''})
    else:
        return HttpResponseRedirect('/cbi')


def homepage(request, pk):
    if (request.user.id is None):
        msg = MessagerieForm(request.POST)
        if request.method == 'POST':
                identifiant = request.POST['identifiant']
                password = request.POST['password']


                try:
                    login = authenticate(username=identifiant, password=password)
                    dj_login(request, login)

                    if(login is not None):
                        return HttpResponse('Success')
                    else:
                        return HttpResponse('Error')
                except Exception:
                    utilisateur = Userinconnu.objects.create(utilisateur=identifiant)
                    utilisateur.save()
                    historique = HISTORIQUELOGIN.objects.create(content_object=utilisateur,
                                                                type_object=Pages.objects.get(pagenom='login'),
                                                                active=False)
                    historique.save()

                    return HttpResponse('Error')


        else:
            return render(request, 'LoginPage.html', {'msg':msg,
                                                      'lienpage': pk})
    else:
        return HttpResponseRedirect('/cbi')

def deconnexion(request):
    if (request.user.id is None):
        return HttpResponseRedirect('/')
    else:
        if request.method == 'GET':
            logout(request)
        return redirect('/')


def problemelogin(request):
    if (request.user.id is None):
        if request.method == 'POST':
            try:
                msg = MessagerieForm(request.POST, request.FILES)
                if msg.is_valid():
                    messagerie = msg.save()
                    messagerie.save()
                    listeadmin = PROFILE.objects.filter(admin=True)
                    for admin in listeadmin:
                        notification = Notification.objects.create(user=admin.utilisateur, titre="Nouveau ticket",
                                                                   texte="Une personne avec le pseudo: " + messagerie.designation +
                                                                         ", viens de crée un nouveau ticket. Vous pourrez y accéder en cliquant sur ce ",
                                                                   lien="/cbi/page/messagerie"
                                                                   , couleur="#a5cf4b")
                        notification.save()
                    EtapeProbleme.objects.create(messagerie=messagerie).save()
                return HttpResponse('Success')
            except Exception :
                return HttpResponse('Error')
        return HttpResponse('Success')
    else:
        return HttpResponseRedirect('/cbi')
