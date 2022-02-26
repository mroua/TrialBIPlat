import datetime
import json
import re
import threading
import time
from pprint import pprint

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, Sum, Count, Case, When, Value, CharField
import requests



from django.utils import timezone

from Login.models import PROFILE, OBJETSITE, HISTORIQUELOGIN, Pages

from bi.form import AjoutOjetSiteForm, OjetSiteFormset, MessagerieForm, AutorisationForm
from bi.models import EtapeProbleme, Messagerie, Autorisation, Slider, Notification, Requette

page = 'accueil'
lien = ''
idrap = ''

def getdirectionschild(element):
    enfant_act = OBJETSITE.objects.get(id=element)
    if(enfant_act.type == '6'):
        if enfant_act.slider == False:
            return ['RAPPORT', {'nom': enfant_act.nom, 'lien': enfant_act.lien, 'id': enfant_act.id}]

    else:
        if(enfant_act.type == '2'):
            liste_enfant = OBJETSITE.objects.filter(parent__nom=enfant_act.nom, type='4')

        else:
            liste_enfant = OBJETSITE.objects.filter(parent__nom=enfant_act.nom)

        liste=[]
        liste.append(enfant_act.nom+'---'+str(enfant_act.id)+'---')
        for enfant in liste_enfant:
            liste.append(getdirectionschild(enfant.id))
        return liste

def TCAut():
    try:
        consolide = getdirectionschild(OBJETSITE.objects.get(type='1', nom='Consolidé').id)
        liste_pole = OBJETSITE.objects.filter(type='2')
        pole= ['Poles---P---']

        for poleenfant in liste_pole:
            pole.append(getdirectionschild(poleenfant.id))

        liste_societe = OBJETSITE.objects.filter(type='3')
        societe = ['Societe---S---']
        for societeenfant in liste_societe:
            societe.append(getdirectionschild(societeenfant.id))

        return [consolide, pole, societe]
    except Exception:
        return []

def parentinit(elem, liste):
    liste.append(elem)
    if(elem.type in ['1', '2', '3']):
        return(liste[::-1])
    else:
        return(parentinit(elem.parent, liste))

def GetChildbyId(elem):
    if (elem.type == '5'):
        return ['RAPPORT', {'nom': elem.nom, 'lien': elem.lien}]
    else:
        liste_enfant = OBJETSITE.objects.filter(parent=elem)

        liste = []
        liste.append(elem.nom)
        for enfant in liste_enfant:
            liste.append(getdirectionschild(enfant.id))
        return liste

def GetRapport(elem, listerapport):
    if (elem.type == '5'):
        return listerapport.append(elem)
    else:
        liste_enfant = OBJETSITE.objects.filter(parent=elem)

        for enfant in liste_enfant:
            return (GetRapport(enfant, listerapport))

def Verification2(liste, param):
    if isinstance(liste, list):
        if liste[0] == 'RAPPORT':
            objet_verification = OBJETSITE.objects.get(id=liste[1]['id'])
            listeanciens = []
            parentinit(objet_verification, listeanciens)
            elems_in_both_lists = set(listeanciens) & set(param)
            if len(elems_in_both_lists) == 0:
                liste.clear()
        else:
            if isinstance(liste[0], str):
                result = int(liste[0][liste[0].find('---') + len('---'):liste[0].rfind('---')])

                if(result == 2 or result == 3):
                    for i in range(1, len(liste)):
                        Verification2(liste[i], param)
                else:
                    objet_verification = OBJETSITE.objects.get(id=result)

                    ind = 0
                    droit = False

                    while (ind < len(param) and droit == False):
                        listeanciens = []
                        parentinit(param[ind], listeanciens)
                        if(objet_verification in listeanciens):
                            droit = True
                        ind = ind + 1
                    if(droit):
                        for i in range(1, len(liste)):
                            Verification2(liste[i], param)
                    else:
                        liste.clear()

def GetType(param, liste):
    if (param.type in ['1', '2', '3']):
        return (liste)
    else:
        liste.append(param.parent)
        return liste.append(GetType(param.parent, liste))

def Decortic(param):
    consolide = getdirectionschild(OBJETSITE.objects.get(type='1', nom='Consolidé').id)
    liste_pole = OBJETSITE.objects.filter(type='2')
    pole = ['Poles---2---']

    for poleenfant in liste_pole:
        pole.append(getdirectionschild(poleenfant.id))

    liste_societe = OBJETSITE.objects.filter(type='3')
    societe = ['Societe---3---']
    for societeenfant in liste_societe:
        societe.append(getdirectionschild(societeenfant.id))


    Verification2(consolide, param)
    Verification2(pole, param)
    Verification2(societe, list(param))

    listeaenvoyer = []
    consolide = [x for x in consolide if x != []]
    pole = [x for x in pole if x != []]
    societe = [x for x in societe if x != []]
    if(len(consolide) >0):
        listeaenvoyer.append(consolide)
    if (len(pole) > 1):
        listeaenvoyer.append(pole)
    if (len(societe) > 1):
        listeaenvoyer.append(societe)

    return listeaenvoyer

def chargementlisteauto(util):
    profil = PROFILE.objects.get(utilisateur=util)
    type = profil.type_autorisation
    if(type == 'TC'):
        return TCAut()
    else:
        return(Decortic(profil.id_objet.all()))

def getancetrelist(elem, liste):
    if(elem.parent == None):
        liste.append(elem.nom+'/')
        return liste.reverse()
    else:
        liste.append(elem.nom+'/')
        getancetrelist(elem.parent, liste)

def getancetrelistobject(elem, liste):
    if(elem.parent == None):
        liste.append(elem)
        return liste
    else:
        liste.append(elem)
        getancetrelistobject(elem.parent, liste)

def newhysto(userid, type, elementnomid):
        if(type == 'rapport'):
            historique = HISTORIQUELOGIN.objects.create(content_object=User.objects.get(id= int(userid)), type_object = OBJETSITE.objects.get(id= int(elementnomid)))
            historique.save()

        else:
            historique = HISTORIQUELOGIN.objects.create(content_object=User.objects.get(id= int(userid)), type_object = Pages.objects.get(pagenom=elementnomid))
            historique.save()

        return historique.id

def tableaudebordenfs(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profil = PROFILE.objects.get(utilisateur=request.user)
        type = profil.type_autorisation
        if request.method == 'POST':
            parent = request.POST['parent']
            if(parent == 'dash'):
                if (type == 'TC'):
                    liste=[
                        {'type': 'dir',
                         'enfants': 'Consolidé---1---',
                         'descendance': 'oui'
                         },{'type': 'dir',
                         'enfants': 'Poles---P---',
                         'descendance': 'oui'
                         },{'type': 'dir',
                         'enfants': 'Societe---S---',
                         'descendance': 'oui'
                         }
                    ]
                    return HttpResponse(json.dumps(liste, cls=DjangoJSONEncoder))
                else:
                    liste = []
                    if(profil.id_objet.filter(ancetretype='1').first()):
                        liste.append({'type': 'dir', 'enfants': 'Consolidé---1---', 'descendance': 'oui'})
                    if (profil.id_objet.filter(ancetretype='2').first()):
                        liste.append({'type': 'dir', 'enfants': 'Poles---P---', 'descendance': 'oui'})
                    if (profil.id_objet.filter(ancetretype='3').first()):
                        liste.append({'type': 'dir', 'enfants': 'Societe---S---', 'descendance': 'oui'})

                    return HttpResponse(json.dumps(liste,cls=DjangoJSONEncoder))
            else:
                if(parent == 'P'):
                    liste_auto = profil.id_objet.filter(type='2')
                elif(parent == 'S'):
                    liste_auto = profil.id_objet.filter(type='2')
                else:
                    liste_auto = profil.id_objet.filter(parent__id=int(parent))
                liste = []
                for elem in liste_auto:
                    if(elem.type == '6'):
                        dir = 'rap'
                        descendance = 'non'
                    else:
                        dir = 'dir'
                        liste2 = profil.id_objet.filter(parent=elem)
                        if(not len(liste2)):
                            descendance = 'non'
                        else:
                            descendance = 'oui'
                    enfants = elem.nom+'---'+str(elem.id)+'----'
                    lien = elem.lien
                    liste.append({'dir': dir, 'descendance': descendance, 'enfants': enfants, 'lien': lien})
                return HttpResponse(json.dumps(liste, cls=DjangoJSONEncoder))
        else:
            return redirect('/')

def verifierelement(liste):
    for element in liste:
        if(element.parent not in liste and element.type != '3'):
            if (element.parent is not None):
                liste.append(element.parent)
                verifierelement(liste)

    return liste

def tableaudebordenfs2(user):
    profil = PROFILE.objects.get(utilisateur=user)
    liste= []
    liste2= []
    if(profil.type_autorisation == 'TC'):
        liste2 = OBJETSITE.objects.filter(slider=False).order_by('nom')
    else:
        liste_auto = profil.id_objet.filter(slider=False).order_by('nom')
        for elem in liste_auto:
            liste2.append(elem)

        verifierelement(liste2)

    for elem in liste2:
        if(elem.parent is None or elem.type == '3'):
            if(elem.type == '1'):
                idparent = 'dash'
            elif(elem.type == '2'):
                idparent = 'P'
            else:
                idparent = 'S'
        else:
            idparent = str(elem.parent.id)
        liste.append({'id': elem.id,'parent_id': idparent, 'nom': elem.nom, 'lien': str(elem.lien),'type': elem.type})
    liste = sorted(liste, key=lambda k: k['type'])
    return liste

def home(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        msg = MessagerieForm(request.POST)
        profile = PROFILE.objects.get(utilisateur=request.user)
        if request.method == 'POST':
            try:
                msg = MessagerieForm(request.POST, request.FILES)
                if msg.is_valid():
                    messagerie = msg.save()
                    messagerie.utilisateur = profile.utilisateur
                    messagerie.designation = profile.utilisateur.username
                    messagerie.save()
                    listeadmin = PROFILE.objects.filter(admin=True)
                    for admin in listeadmin:
                        notification = Notification.objects.create(user= admin.utilisateur, titre= "Nouveau ticket", texte="l'utilisateur :"+messagerie.utilisateur.first_name+
                            " viens de créer un nouveau ticket. Vous pourrez y accéder en cliquant sur ce",
                            lien="/cbi/page/messagerie"
                            , couleur="#ffc34a")
                        notification.save()
                    id_messagerie = messagerie.id
                    EtapeProbleme.objects.create(messagerie=messagerie).save()
                    return HttpResponse(id_messagerie)
            except Exception :
                return HttpResponse('Error')
        else:
            global page, lien, idrap

            anciennepage = page
            ancienlien = lien
            ancienid = idrap
            page = 'accueil'
            lien = ''
            idrap = ''
            auth = tableaudebordenfs2(request.user)
            return render(request, 'conn/index.html', {'profile': profile,
                                                       'auth': auth,
                                                       'idhysto': 0,
                                                       'msg' : msg,
                                                       'idrapport':ancienid,
                                                       'lien': ancienlien,
                                                       'page': anciennepage})

def getlineage(elem, liste):
    if(elem.type == '1' or elem.type == '2'):
        liste.append(elem.nom)
        return (liste[::-1])
    else:
        liste.append(elem.nom)
        return getlineage(elem.parent, liste)

def request_task(url):
    requests.post(url)

def adminpage(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.admin):

            if request.method == 'POST':
                modelform = AjoutOjetSiteForm(request.POST)
                forsmsetobjet = OjetSiteFormset(request.POST, prefix='forsmsetobjet')
                if(modelform.is_valid()):
                    type = int(modelform.cleaned_data['type'])
                    parent = modelform.cleaned_data['parent']
                    slider = modelform.cleaned_data['slider']

                if (forsmsetobjet.is_valid()):
                    for form in forsmsetobjet:
                        element = form.save()
                        element.type = type
                        element.parent = parent
                        element.save()
                        ancetre = gettypeancetre(element)
                        element.ancetrenom = ancetre.nom
                        element.ancetretype = ancetre.type




                        if(type == 6):
                            element.slider = slider

                        element.save()

                        liste = []
                        getancetrelistobject(element, liste)

                        listeprofile = PROFILE.objects.filter(Q(id_objet__in=liste) | Q(type_autorisation='TC') | Q(admin=True)).distinct()
                        for profile in listeprofile:
                            if(type == 6):
                                notif = Notification.objects.create(user=profile.utilisateur,
                                                                       titre="Nouveau Rapport",
                                                                       texte="Un nouveau rapport '"+element.ancetrenom+"/"+element.nom+"' a été ajouté, vous pouvez y accéder en cliquant sur ce"
                                                                       , lien = "/cbi/rapport/"+str(element.id)
                                                                       , couleur="#a5cf4b")
                                notif.save()
                            try:
                                idnum = (profile.id_objet.through.objects.latest('id').id)+1
                            except Exception:
                                idnum = 1
                            try:
                                newauth = profile.id_objet.through.objects.create(id=idnum, profile_id=profile.id,objetsite_id=element.id)
                                newauth.save()


                            except Exception:
                                pass


                    return HttpResponse('Success')
            else:
                FormObjet = AjoutOjetSiteForm(request.POST)
                FormsetObjet = OjetSiteFormset(prefix='forsmsetobjet', queryset=OBJETSITE.objects.none())
                return render(request, 'conn/adminpage.html', {'FormObjet': FormObjet, 'FormsetObjet': FormsetObjet})
        else:
            return redirect('/')

def parent(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.admin):
            if request.method == 'POST':
                type = request.POST['type']
                parent = request.POST['parent']

                try:
                    enfants = []
                    if(type == '1' and parent == '1'):
                        enfants.append(OBJETSITE.objects.get(type='1', nom='Consolidé'))
                    elif(parent == 'Vide' or parent == ''):
                        enfants = []
                    elif(parent == 'all'):
                        if(type == '1'):
                            enfants = OBJETSITE.objects.filter(parent__type='1', parent__nom="Consolidé")
                        else:
                            enfants = OBJETSITE.objects.filter(type=int(type))
                    else:
                        enfants = OBJETSITE.objects.filter(type=int(type), parent= parent)
                except Exception:
                    enfants = []
                return render(request, 'conn/enfant.html', {'enfants': enfants})
        else:
            return redirect('/')

def messagerieAdmin(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.admin):
            if request.method == 'POST':
                pass
            else:
                liste_messagerie = EtapeProbleme.objects.filter(active=True).order_by('-id').exclude(type='4')
                return render(request, 'conn/messagerie.html', {"liste_messagerie": liste_messagerie})
        else:
            liste_messagerie = EtapeProbleme.objects.filter(active=True, messagerie__utilisateur=request.user)
            return render(request, 'conn/messagerieuser.html', {"liste_messagerie": liste_messagerie})

def informationmessage(request, pk):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        historiquemessagerie = EtapeProbleme.objects.filter(messagerie_id=int(pk))
        messagerie = historiquemessagerie.first().messagerie
        try:
            profileuser = PROFILE.objects.get(utilisateur=messagerie.utilisateur)
        except Exception:
            profileuser = None
        if (profile.admin or profile == profileuser):
            if request.method == 'POST':
                choix = request.POST['choix']
                if(choix == '1'):
                    etape = EtapeProbleme.objects.filter(messagerie__id=int(pk))
                    etape.exclude(type="1").delete()
                    etape = etape.get(type='1')
                    etape.active = True
                    etape.save()
                    listeadmin = PROFILE.objects.filter(admin=True)
                    for admin in listeadmin:
                        notification = Notification.objects.create(user=admin.utilisateur, titre="Ré-ouverture d'un ticket",
                                                                   texte="l'utilisateur : " + messagerie.utilisateur.first_name +
                                                                         " a relancé le ticket '"+messagerie.sujet+"'. Vous pourrez y accéder en cliquant sur ce"
                                                                   , lien = "/cbi/page/messagerie"
                                                                   , couleur="#ffc34a")
                        notification.save()
                    return HttpResponse('Success')
                else:
                    try:
                        etape = EtapeProbleme.objects.get(messagerie__id=int(pk), active=True)
                        etape.active = False
                        etape.save()

                    except Exception:
                        return HttpResponse('Error')
                    etape = EtapeProbleme.objects.create(messagerie=Messagerie.objects.get(id=int(pk)), type = choix)
                    etape.save()
                    if(etape.type == '4'):
                        etape.active = False
                        listeadmin = PROFILE.objects.filter(admin=True)
                        for admin in listeadmin:
                            if(profileuser == None):
                                notification = Notification.objects.create(user=admin.utilisateur,
                                                                           titre="Validation d'un ticket",
                                                                           texte="le ticket : '" + messagerie.sujet +
                                                                                 "' a été validé."
                                                                           , couleur="#ffc34a")
                                notification.save()
                            else:
                                notification = Notification.objects.create(user=admin.utilisateur,
                                                                       titre="Validation d'un ticket",
                                                                       texte="l'utilisateur : " + messagerie.utilisateur.first_name +
                                                                             " a validé le ticket '" + messagerie.sujet + "'."
                                                                       , couleur="#ffc34a")
                                notification.save()
                    else:
                        if(etape.type == '2'):
                            message= "Votre ticket : '"+messagerie.sujet+"' est en cours de traitement, merci d'attendre."
                            titre = "Ticket en-cours"
                        else:
                            message = "Votre ticket : "+messagerie.sujet+" a été validé, merci de le confirmé."
                            titre = "Ticket validé"
                        notification = Notification.objects.create(user =messagerie.utilisateur,
                                                                    titre =titre,
                                                                    texte = message
                                                                    , couleur ="#ffc34a")
                        notification.save()
                    return HttpResponse('Success')
            else:
                return render(request, 'conn/information.html', {'historiquemessagerie':historiquemessagerie,
                                                                     'messagerie': messagerie,
                                                                     'profile': profileuser,
                                                                     'profilecon':profile})

        else:
            return redirect('/')

def homerap(request, pk):
    print(pk)
    if (request.user.id is None):
        return redirect('/page/'+str(pk))
    else:
        global lien, idrap
        lien = OBJETSITE.objects.get(id=int(pk)).lien
        idrap = int(pk)
        return redirect('/')

def homepage(request, pk):
    if (request.user.id is None):
        return redirect('/page/'+str(pk))
    else:
        global page
        page = pk
        return redirect('/')

def acceuilpage(request):
    '''print('coucouicicicic')
    listerapport = OBJETSITE.objects.filter(type='6')
    print(listerapport)
    print('passee')
    substr = "&rs:embed=true"
    inserttxt = "&rc:Zoom=Page+Width"
    for elem in listerapport:
        print(elem)
        if('&rc:Zoom=Page+Width' not in elem.lien):
            idx = elem.lien.index(substr)
            elem.lien = elem.lien[:idx] + inserttxt + elem.lien[idx:]
            elem.save()'''
    if (request.user.id is None):
        return redirect('/')
    else:
        histodate = datetime.datetime.now()
        listnotif= Notification.objects.filter(Q(date__day=histodate.day,
                                               date__month=histodate.month,
                                               date__year=histodate.year,
                                               user=request.user)|Q(recu=False, user= request.user)).distinct().order_by('-id')

        for elem in listnotif:
            elem.recu = True
            elem.save()

        return render(request, 'conn/accueil.html',{'listnotif':listnotif})

def ajoutimagemessagerie(request):
    fichier = request.FILES['file']
    id_messagerie = request.POST['id_messagerie']
    try:
        message = Messagerie.objects.get(id= int(id_messagerie))
        message.image = fichier
        message.save()
    except Exception:
        pass
    return HttpResponse('Success')

def recherchemessagerieelem(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        if request.method == 'POST':
            profile = PROFILE.objects.get(utilisateur=request.user)
            if (profile.admin):
                designation = request.POST['designation']
                type = request.POST['type']
                date = request.POST['date']

                newliste = EtapeProbleme.objects.filter(active=True)
                if(date != ''):
                    date = date.split("-")
                    etapes = EtapeProbleme.objects.filter(date__day=int(date[2]),
                                                      date__month=int(date[1]),
                                                      date__year=int(date[0])).values('messagerie').distinct()
                    newliste = newliste.filter(messagerie__in=etapes)

                if(designation != ''):

                    newliste = newliste.filter(Q(messagerie__designation__icontains=designation) | Q(messagerie__sujet__icontains=designation))

                if(type != '0'):
                    newliste = newliste.filter(type=type)
                listeID = []
                listeDesignation = []
                listeSujet = []
                listeEtat = []
                listeDate = []
                listeHeure = []
                listeEtatid = []

                for elem in newliste:
                    listeID.append(elem.messagerie.id)
                    listeDesignation.append(elem.messagerie.designation)
                    listeSujet.append(elem.messagerie.sujet)
                    listeEtatid.append(elem.type)
                    listeEtat.append(elem.get_type_display())
                    listeDate.append(elem.messagerie.date.strftime("%d/%m/%Y"))
                    listeHeure.append(elem.messagerie.date.strftime("%H:%M:%S"))

                print(listeDate)
                dict = {
                    'id':listeID,
                    'designation':listeDesignation,
                    'sujet':listeSujet,
                    'etat':listeEtat,
                    'etatid':listeEtatid,
                    'dates':listeDate,
                    'heure':listeHeure,
                }

                return HttpResponse(json.dumps(dict, cls=DjangoJSONEncoder))
            else:
                return HttpResponse('Success')

def adminauth(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.admin):
            if request.method == 'POST':
                return HttpResponse('Success')
            else:
                authform = AutorisationForm(request.POST)
                profiles = PROFILE.objects.all().order_by('-id')
                dernierutilisateur= PROFILE.objects.all().order_by('-id')
                liste_util = []
                for pro in dernierutilisateur:

                    if(pro.id_objet.order_by('type').first() == None):
                        auto = 'aucun'
                    else:
                        auto = pro.id_objet.order_by('type').first().get_type_display()
                    liste_util.append({'user': pro.utilisateur.first_name,
                                       'auto':auto,
                                       "ad2000": pro.utilisateur.username,
                                       "email": pro.utilisateur.email,
                                       'id': pro.utilisateur.id})
                tovalidate = Autorisation.objects.filter(validite=False, refuser=False)

                listefinal = []
                for elem in tovalidate:
                    if(elem.validite):
                        validate = 'Suppression'
                    else:
                        validate = 'Ajout'
                    listefinal.append({'obj': elem, 'parent': gettypeancetre(elem.objetsite).nom, 'valide': validate})

                return render(request, 'conn/AutorisationAdmin.html', {'listefinal':listefinal,
                                                                       'authform': authform, 'profiles': profiles,
                                                                       'liste_util': liste_util, 'tovalidate':tovalidate})
        elif (profile.droitauth):
            if request.method == 'POST':
                return HttpResponse('Success')
            else:
                authform = AutorisationForm(request.POST)
                profiles = PROFILE.objects.filter(admin=False).order_by('-id')
                listpro = []
                for elem in profiles :
                    listpro.append(elem.utilisateur.id)
                authform.user = User.objects.filter(user__id__in=listpro)
                liste_util = []
                for pro in profiles:

                    if(pro.id_objet.order_by('type').first() == None):
                        auto = 'aucun'
                    else:
                        auto = pro.id_objet.order_by('type').first().get_type_display()
                    liste_util.append({'user': pro.utilisateur.first_name,
                                       'auto':auto,
                                       "ad2000": pro.utilisateur.username,
                                       "email": pro.utilisateur.email,
                                       'id': pro.utilisateur.id})

                return render(request, 'conn/Autorisation.html', {'authform': authform,
                                                                       'profiles': profiles,
                                                                       'liste_util': liste_util})
        else:
            return redirect('/')

def gettypeancetre(elem):
    if(elem.type in ['1', '2', '3']):
        return elem
    else:
        return gettypeancetre(elem.parent)

def loadauthuser(request, pk):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.admin or profile.droitauth):
            if request.method == 'POST':
                return HttpResponse('Success')
            else:
                utilisateur = User.objects.get(id= int(pk))
                profileuser = PROFILE.objects.get(utilisateur=utilisateur)

                #elementlist = profileuser.id_objet.order_by('ancetretype')

                consolide = profileuser.id_objet.filter(ancetretype='1')
                poles = profileuser.id_objet.filter(ancetretype='2')
                societe = profileuser.id_objet.filter(ancetretype='3')

                listeretour = []
                if(len(consolide) > 0):
                    listeretour.append({'id': 'conso','nom':"consolide", 'type': '1'})

                if(len(poles) > 0):
                    listeretour.append({'id': 'poles','nom':"pôles", 'type': '2'})

                if(len(societe) > 0):
                    listeretour.append({'id': 'socie','nom':"société", 'type': '3'})

                return render(request, 'conn/authinfo.html', {'profileuser':profileuser, 'listeretour': listeretour})
        else:
            return redirect('/')


def getelemancetre(elem):
    if(elem.type in ['1', '2', '3']):
        return elem
    else:
        return getelemancetre(elem.parent)


def suppressionauth(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.admin or profile.droitauth):
            if request.method == 'POST':
                idobj = request.POST['idobj']
                profilid = request.POST['profilid']
                profileuser = PROFILE.objects.get(id=int(profilid))
                if(idobj =='conso'):
                    objet = OBJETSITE.objects.filter(type=1)
                elif(idobj == 'poles'):
                    objet = []
                    listequery = profileuser.id_objet.filter(ancetretype='2').exclude(type='3')
                    for elem in listequery:
                        if(elem not in objet):
                            objet.append(getelemancetre(elem))
                elif (idobj == 'socie'):
                    objet = []
                    listequery = profileuser.id_objet.filter(ancetretype='3')
                    for elem in listequery:
                        if (elem not in objet):
                            objet.append(getelemancetre(elem))
                else:
                    objet = []
                    objet.append(OBJETSITE.objects.get(id= int(idobj)))
                for elem in objet:
                    try:
                        autorisation = Autorisation.objects.get(objetsite=elem, action='2', user=profileuser.utilisateur, useract=request.user.username, validite=False, refuser=False)
                    except Exception:
                        autorisation = Autorisation.objects.create(objetsite=elem, action='2', user=profileuser.utilisateur, useract=request.user.username, validite=False, refuser=False)
                        autorisation.save()

                return HttpResponse('Success')
            else:
                return redirect('/')
        else:
            return redirect('/')

def get_all_childs(elem, liste):
    if(elem.type == "6"):
        liste.append(elem)
    else:
        enfant = OBJETSITE.objects.filter(parent=elem)
        for child in enfant:
            liste.append(child)
            get_all_childs(child, liste)

        return liste

def nouveauautuser(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.admin or profile.droitauth):
            if request.method == 'POST':
                idobjet = request.POST['idobjet']
                users = request.POST.getlist('users[]')

                objet = OBJETSITE.objects.get(id=int(idobjet))
                listeadmin = PROFILE.objects.filter(admin=True)
                for use in users:
                    auto = Autorisation.objects.create(user=PROFILE.objects.get(id=int(use)).utilisateur, objetsite=objet, action='1', useract=request.user.username)
                    auto.save()
                    for admin in listeadmin:
                        notification = Notification.objects.create(user=admin.utilisateur,
                                                                   titre="Demande d'autorisation",
                                                                   texte="L'utilisateur : " + request.user.first_name +
                                                                         " a demandé(e) d'octroyer des autorisations à l'utilisateur : '" + auto.user.first_name + "'. Vous pourrez y accéder en cliquant sur  ce "
                                                                   , lien= "/cbi/page/authadmin"
                                                                   , couleur="#B21122")
                        notification.save()

                return HttpResponse('Success')
            else:
                profiles = PROFILE.objects.all()
                authtotal = OBJETSITE.objects.get(type=1, nom='Consolidé')
                return render(request, 'conn/ajoutauth.html', {'profiles': profiles, 'authtotal': authtotal})
        else:
            return redirect('/')

def getchilddir(elem, liste):
    if(elem.type == '6'):
        pass
    else:
        children = OBJETSITE.objects.filter(parent=elem)
        for child in children:
            if(child.type in ['4', '5']):
                liste.append(child)
                getchilddir(child, liste)
        return liste

def newparentchoixe(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.admin or profile.droitauth):
            if request.method == 'POST':
                type = request.POST['type']
                niveau = request.POST['niveau']

                try:
                    enfants = []

                    if(niveau == 'conso' and type == 'all'):
                        enfants = OBJETSITE.objects.filter(type=1, nom="Consolidé")
                    elif(niveau == 'conso' and type == 'dir'):
                        getchilddir(OBJETSITE.objects.get(type=1, nom="Consolidé"), enfants)
                    elif (niveau == 'conso'):
                        enfants = OBJETSITE.objects.filter(type=6, parent__id=int(type))
                    elif (niveau == 'pole' and type == 'all'):
                        enfants = OBJETSITE.objects.filter(type=2)
                    elif (type == 'dir'):
                        getchilddir(OBJETSITE.objects.get(id= int(niveau)), enfants)
                    elif (type == 'all'):
                        enfants = OBJETSITE.objects.filter(type='3', parent__id=int(niveau))
                    else:
                        enfants = OBJETSITE.objects.filter(type=6, parent__id=int(type))

                except Exception:
                    enfants = []
                return render(request, 'conn/enfant.html', {'enfants': enfants})
        else:
            return redirect('/')

def parentfinal(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.admin or profile.droitauth):
            if request.method == 'POST':
                choix = request.POST['choix']
                idparent = request.POST['idparent']
                try:
                    if choix == "1":
                        enfants = OBJETSITE.objects.filter(type= 1, nom="Consolidé")
                    elif choix == "2":
                        enfants = []
                        enfants = getchilddir(OBJETSITE.objects.get(type= 1, nom="Consolidé"), enfants)
                    elif choix in ["3", "6", "9"]:
                        enfants = OBJETSITE.objects.filter(type= 6, parent__id=int(idparent))
                    elif choix == "4":
                        enfants = OBJETSITE.objects.filter(type=2)
                    elif choix == "5":
                        enfants = []
                        enfants = getchilddir(OBJETSITE.objects.get(id=int(idparent)), enfants)
                    elif choix == "7":
                        enfants = OBJETSITE.objects.filter(type=3, parent__id=int(idparent))
                    elif choix == "8":
                        enfants = []
                        enfants = getchilddir(OBJETSITE.objects.get(id=int(idparent)), enfants)
                    else:
                        enfants = []
                except Exception:
                    enfants = []


                return render(request, 'conn/enfant.html', {'enfants': enfants})
        else:
            return redirect('/')

def adminelse(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.droitauth):
            if request.method == 'POST':
                return HttpResponse('Success')
            else:
                authform = AutorisationForm(request.POST)
                profiles = PROFILE.objects.all().order_by('-id')
                return render(request, 'conn/Autorisation.html', {'authform': authform, 'profiles': profiles})
        else:
            return redirect('/')

def actionautorisation(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)


        if(profile.admin):
            idauth = request.POST['idauth']
            action = request.POST['action']

            auth  = Autorisation.objects.get(id=int(idauth))
            profileuser = PROFILE.objects.get(utilisateur=auth.user)
            if(auth.objetsite.type == '1'):
                liste = OBJETSITE.objects.filter(ancetretype='1')
            else:
                liste = [auth.objetsite]
                get_all_childs(auth.objetsite, liste)
            if(action != 'refus'):
                if(auth.action == '1'):
                    idnum = profileuser.id_objet.through.objects.latest('id').id
                    for elem in liste:
                        idnum = idnum + 1
                        try:
                            profileuser.id_objet.through.objects.create(id=idnum, profile_id=profileuser.id,objetsite_id=elem.id).save()
                        except Exception:
                            pass
                    auth.validite = True
                    auth.save()

                    listeadmin = PROFILE.objects.filter(Q(admin=True) | Q(utilisateur__username=auth.useract) | Q(utilisateur=auth.user))
                    for admin in listeadmin:
                        notification = Notification.objects.create(user=admin.utilisateur,
                                                                   titre="Validation d'autorisation",
                                                                   texte="La demande de : " + auth.useract +
                                                                         " concernant l'attribution des autorisations : '" + auth.objetsite.nom +
                                                                         "'  été accordé à l'utilisateur : "+auth.user.first_name+"."
                                                                   , couleur="#B21122")
                        notification.save()
                else:
                    for elem in liste:
                        try:
                            profileuser.id_objet.through.objects.get(profile_id=profileuser.id,objetsite_id=elem.id).delete()
                        except Exception:
                            pass
                    auth.validite = True
                    auth.save()

                    listeadmin = PROFILE.objects.filter(
                        Q(admin=True) | Q(utilisateur__username=auth.useract) | Q(utilisateur=auth.user))
                    for admin in listeadmin:
                        notification = Notification.objects.create(user=admin.utilisateur,
                                                                   titre="Suppression d'autorisation",
                                                                   texte="La demande de : " + auth.useract +
                                                                         " concernant la suppression des autorisations : '" + auth.objetsite.nom + "' a été refusé à l'utilisateur : " + auth.user.first_name + "."
                                                                   , couleur="#B21122")
                        notification.save()
                auth.userchoix = request.user.username
                auth.save()


            else:
                auth.refuser = True
                auth.userchoix = request.user.username
                auth.save()

                listeadmin = PROFILE.objects.filter(
                    Q(admin=True) | Q(utilisateur__username=auth.useract) | Q(utilisateur=auth.user))
                for admin in listeadmin:
                    if (auth.action == '01'):
                        titre = "Demande d'autorisation"
                    else:
                        titre = "Suppression d'autorisation"

                    notification = Notification.objects.create(user=admin.utilisateur,
                                                               titre=titre,
                                                               texte="La demande de : " + auth.useract +
                                                                     " concernant '" + auth.objetsite.nom + "' a été refusé à l'utilisateur : " + auth.user.first_name + "."
                                                               , couleur="#B21122")
                    notification.save()

            return HttpResponse("Success")
        else:
            return redirect('/')

def getdirparent(elem):
    if(elem.type == '4' or elem.parent == None):
        return elem
    else:
        return getdirparent(elem.parent)

def getchildsofobjsite(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.admin or profile.droitauth):
            if request.method == 'POST':
                idobj = request.POST['idobj']
                profileid = request.POST['profileid']

                profileuser = PROFILE.objects.get(id=int(profileid))
                listeauto = []
                if(idobj== 'conso'):
                    res = profileuser.id_objet.filter(ancetretype='1')

                    for elem in res:
                        if (elem.type == '4'):
                            listeauto.append(elem)
                        else:
                            if(elem.type != '1'):
                                parent = getdirparent(elem)
                                if (parent not in listeauto):
                                    listeauto.append(parent)

                elif(idobj== 'poles'):
                    res = profileuser.id_objet.filter(ancetretype='2').values('ancetrenom').distinct()

                    for elem in res:
                        listeauto.append(OBJETSITE.objects.get(type=2, nom = elem['ancetrenom']))

                elif (idobj == 'socie'):
                    res = profileuser.id_objet.filter(ancetretype='3').values('ancetrenom').distinct()

                    for elem in res:
                        listeauto.append(OBJETSITE.objects.get(type=3, nom=elem['ancetrenom']))

                else:
                    idobj = int(idobj)
                    listeauto = profileuser.id_objet.filter(parent__id=idobj).exclude(type='3')

                liste_autorisation = []
                for elem in listeauto:
                    liste_autorisation.append({"id": elem.id, 'nom': elem.nom, 'type': elem.type})


                return HttpResponse(json.dumps(liste_autorisation, cls=DjangoJSONEncoder))

            else:
                return redirect('/')
        else:
            return redirect('/')

def historiqueutil(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        if request.method == 'POST':
            idhisto = request.POST['idhisto']
            action = request.POST['action']

            if(idhisto != ''):
                histo = HISTORIQUELOGIN.objects.get(id=int(idhisto))
                histo.temps = int((timezone.now() - histo.date).total_seconds())
                histo.active = False
                histo.save()

            if(action.isdigit()):
                resultat = newhysto(request.user.id, 'rapport', action)
            else:
                resultat = newhysto(request.user.id, 'page', action)

            return HttpResponse(resultat)
        else:
            return redirect('/')

def StatistiqueAdmin(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        couleurSerie = ['#058DC7', '#24CBE5', '#64E572', "#E69A1C", '#FF9655', '#FFF263', '#6AF9C4',
                        '#ef6c00', '#ffd54f', '#FFD57A', "#aae367", '#64b5f6',
                        '#96a6a6', '#dd2c00', '#00838f', '#00bfa5', '#ffa000',
                        "#ff6e40", "#c7b299", "#64b5f6", "#1976d2", "#ef6c00", '#ED561B',
                        "#ffd54f", '#0072A5', '#3BBA7B', '#FA5446', '#FFCD61'
            , "#008BA3", '#2E8B57', "#FF8119", "#345E80", "#FFDC69", '#50B432',
                        "#1C81E6", '#ed6b4b', '#04B3A8', "#01665F", '#DDDF00'
            , "#455a64", '#6f3448', '#1976d2', '#c26364', "#e2606d", "#ffcaf0", "#DC143C", ]

        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.admin):
            if request.method == 'POST':
                return HttpResponse('Success')
            else:
                dateaujourdui = datetime.datetime.now()
                listeadmin = []
                listeprofile = PROFILE.objects.filter(admin=True)
                #.exclude(utilisateurid__in=listeprofile)
                if (profile.utilisateur.username == 'omarhasnaoui'):
                    for admin in listeprofile:
                        listeadmin.append(admin.utilisateur.id)
                    listhisto = HISTORIQUELOGIN.objects.filter(date__year=dateaujourdui.year,
                                                               date__month=dateaujourdui.month,
                                                               utilisateur_id=4,
                                                               typepage=7
                                                               ).exclude(utilisateurid__in=listeadmin)

                else:
                    for admin in listeprofile:
                        if (admin.utilisateur.username not in ['omarhasnaoui', 'ouldbrahim_h']):
                            listeadmin.append(admin.utilisateur.id)
                    listhisto = HISTORIQUELOGIN.objects.filter(date__year=dateaujourdui.year,
                                                               date__month=dateaujourdui.month,
                                                               utilisateur_id=4,
                                                               typepage=7
                                                               ).exclude(utilisateurid__in=listeadmin)

                #journalier tab
                listhistojournalier = listhisto.filter(date__day= dateaujourdui.day).values('utilisateurid', 'typepageid',).annotate(temps=Sum('temps'))
                listeusers = listhistojournalier.values('utilisateurid').distinct()
                listeusers = listeusers.distinct().order_by()

                listedatatabl = []
                for user in listeusers:
                    profileuser = PROFILE.objects.get(utilisateur_id=user['utilisateurid'])
                    print(profileuser)
                    listerapportid = listhistojournalier.filter(utilisateurid = user['utilisateurid']).values('typepageid',).distinct()

                    rapportdictlist = []
                    for rapportelem in listerapportid:

                        try:
                            rapport = OBJETSITE.objects.get(id=rapportelem['typepageid'])
                            tempscomplet = listhistojournalier.filter(utilisateurid=user['utilisateurid'],
                                                                      typepageid=rapportelem['typepageid']).values('temps').distinct()
                            print('temps: '+str(tempscomplet[0]['temps']))
                            rapportdictlist.append({'nom':rapport.ancetrenom+'/'+rapport.nom, 'temps': datetime.timedelta(seconds = tempscomplet[0]['temps'])})
                        except Exception:
                            pass
                    listedatatabl.append({'user': profileuser.utilisateur.username, 'photo': profileuser.photo, "rapport": rapportdictlist})

                utilisateurjournalier = len(listeusers)
                nombrerapportjournalier = len(listhistojournalier.values('typepageid').distinct())

                #mensuelle line
                listhistoment = listhisto.values('date__date').annotate(nombrevisite=Count('date'))
                newlistemens = []

                for elem in listhistoment:
                    newlistemens.append({
                        'date': datetime.datetime.strptime(str(elem['date__date']),'%Y-%m-%d').strftime('%d'),
                        'nbr':elem['nombrevisite']
                    })
                newlistemens = sorted(newlistemens, key=lambda k: k['date'])

                #mensuelle pie
                consolide={"name": "Consolidé",
                           "y":0,
                           "drilldown": 'Consolidé'
                           }
                consolidedrill={
                    "name": "Consolidé",
                    "id": "Consolidé",
                    "colors": couleurSerie,
                    "data": []
                }
                poles={"name": "poles",
                       "y":0,
                       "drilldown": 'poles',}

                polesdrill={
                    "name": "poles",
                    "id": "poles",
                    "colors": couleurSerie,
                    "data": []
                }
                Societe={"name": "Sociétés",
                         "y":0,
                         "drilldown": 'Sociétés'}
                Societedrill={
                    "name": "Sociétés",
                    "id": "Sociétés",
                    "colors": couleurSerie,
                    "data": []
                }
                listhistomentpie = listhisto.values('typepageid').annotate(tempstotal= Sum('temps')).distinct()

                for elem in listhistomentpie:
                    try:
                        rap = OBJETSITE.objects.get(id=elem['typepageid'])
                        if(rap.ancetretype == '1'):
                            consolide['y'] = consolide['y'] + elem['tempstotal']
                            existe = False
                            for direct in consolidedrill['data']:
                                if direct[0] == rap.parent.nom:
                                    existe = True
                                    direct[1] = direct[1]+ elem['tempstotal']
                            if(existe == False):
                                consolidedrill['data'].append([rap.parent.nom, elem['tempstotal']])
                        elif(rap.ancetretype == '2'):
                            poles['y'] = poles['y'] + elem['tempstotal']
                            existe = False
                            for direct in polesdrill['data']:
                                if direct[0] == rap.ancetrenom:
                                    existe = True
                                    direct[1] = direct[1]+ elem['tempstotal']
                            if(existe == False):
                                polesdrill['data'].append([rap.ancetrenom, elem['tempstotal']])

                        else:
                            Societe['y'] = Societe['y'] + elem['tempstotal']
                            existe = False
                            for direct in Societedrill['data']:
                                if direct[0] == rap.ancetrenom:
                                    existe = True
                                    direct[1] = direct[1] + elem['tempstotal']
                            if (existe == False):
                                Societedrill['data'].append([rap.ancetrenom, elem['tempstotal']])
                    except Exception:
                        pass

                piedrill = {'serie': [consolide, poles, Societe], 'datadrill': [consolidedrill, polesdrill, Societedrill]}


            return render(request, 'conn/statistiqueadmin.html',{'listedatatabl': listedatatabl[::-1],
                                                                 'date': dateaujourdui,
                                                                     'utilisateurjournalier': utilisateurjournalier,
                                                                     'nombrerapportjournalier': nombrerapportjournalier,
                                                                     'listhistoment': newlistemens,
                                                                     'piedrill':piedrill,
                                                                 })

        else:
            return redirect('/')

def loadurlbyid(request, pk):
    if (request.user.id is None):
        return redirect('/')
    else:
        return render(request, 'conn/rapport.html')

def sliderpage(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.slider or profile.admin):
            if(request.method == "POST"):
                pass
            else:
                #listerapport = OBJETSITE.objects.filter(slider=True)
                listeslider = Slider.objects.filter(users=request.user, active=True)
                return render(request, 'conn/slider.html', {"listeslider":listeslider})
        else:
            return redirect('/')

def verifierutilisateurfroit(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        if (request.method == "POST"):
            users = request.POST.getlist('listeid[]')
            objet = OBJETSITE.objects.get(id= int(request.POST['objetid']))
            listprofiles = PROFILE.objects.filter(id__in=users)

            listeverification =[]
            for profile in listprofiles:
                auth = profile.id_objet.all()
                if(objet in auth):
                    listeverification.append(profile.utilisateur.first_name)
            if(len(listeverification) == 0):
                return HttpResponse('Success')
            else:
                return HttpResponse(', '.join(listeverification))
        else:
            return redirect('/')

def historypage (request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.admin):

            if(request.method == "POST"):
                histodesignation = request.POST['histodesignation']
                histodate = request.POST['histodate']

                listeadmin = []
                listeprofile = PROFILE.objects.filter(admin=True)
                if (len(histodate) != 0):
                    histodate = datetime.datetime.strptime(histodate, '%Y-%m-%d')
                else:
                    histodate = datetime.datetime.now()

                if (profile.utilisateur.username == 'omarhasnaoui'):
                    for admin in listeprofile:
                        listeadmin.append(admin.utilisateur.id)
                    listhisto = HISTORIQUELOGIN.objects.filter(date__year=histodate.year,
                                                                date__month=histodate.month,
                                                                date__day=histodate.day,
                                                               utilisateur_id=4,
                                                               typepage__in=[7, 16]
                                                               ).exclude(utilisateurid__in=listeadmin)


                else:
                    for admin in listeprofile:
                        if (admin.utilisateur.username not in ['omarhasnaoui', 'ouldbrahim_h']):
                            listeadmin.append(admin.utilisateur.id)
                    listhisto = HISTORIQUELOGIN.objects.filter(date__year=histodate.year,
                                                               date__month=histodate.month,
                                                                date__day=histodate.day,
                                                               utilisateur_id=4,
                                                               typepage__in=[7, 16]
                                                                ).exclude(utilisateurid__in=listeadmin)
                listefinal = []
                histodatestr = histodate.strftime("%Y-%m-%d %H:%M:%S")
                for elem in listhisto:
                    temps = str(datetime.timedelta(seconds=elem.temps))
                    temps = temps.replace(" days,", "J")
                    temps = temps.replace(" day,", "J")
                    user = User.objects.get(id=elem.utilisateurid).first_name
                    if(elem.typepage.model == "objetsite"):
                        try:
                            objet = OBJETSITE.objects.get(id=elem.typepageid)
                            if (objet.type in ['1', '2', '3']):
                                objet = objet.nom
                            else:
                                objet = objet.ancetrenom + '/' + objet.nom

                            if (len(histodesignation) != 0):
                                if(histodesignation in objet.lower()):
                                    listefinal.append({'user': user, 'rapport': objet, 'temps': temps, 'date': str(elem.date.year)+'-'+ str(elem.date.month) + str(elem.date.day)
                                                   +' '+str(elem.date.hour)+':'+str(elem.date.minute)+':'+str(elem.date.second)})
                            else:
                                listefinal.append({'user': user, 'rapport': objet,
                                                   'temps': temps, 'date': str(elem.date.year)+'-'+ str(elem.date.month) + str(elem.date.day)
                                                   +' '+str(elem.date.hour)+':'+str(elem.date.minute)+':'+str(elem.date.second)})
                        except Exception:
                            pass
                    else:
                        objet = Slider.objects.get(id=elem.typepageid)
                        if (len(histodesignation) != 0):
                            if(histodesignation in objet.lower()):
                                listefinal.append({'user': user, 'rapport': "Slider: "+str(objet), 'temps': temps, 'date': str(elem.date.year)+'-'+ str(elem.date.month) + str(elem.date.day)
                                               +' '+str(elem.date.hour)+':'+str(elem.date.minute)+':'+str(elem.date.second)})
                        else:
                            listefinal.append({'user': user, 'rapport':  "Slider: "+str(objet),
                                               'temps': temps, 'date': str(elem.date.year)+'-'+ str(elem.date.month) + str(elem.date.day)
                                               +' '+str(elem.date.hour)+':'+str(elem.date.minute)+':'+str(elem.date.second)})
                newlist = []


                return HttpResponse(json.dumps({'listefinal': listefinal[::-1], 'newlist': newlist[::-1]}, cls=DjangoJSONEncoder))

            else:
                dateaujourdui = datetime.datetime.now()
                listeadmin = []
                listeprofile = PROFILE.objects.filter(admin=True)
                if (profile.utilisateur.username == 'omarhasnaoui'):
                    for admin in listeprofile:
                        listeadmin.append(admin.utilisateur.id)
                    listhisto = HISTORIQUELOGIN.objects.filter(date__year=dateaujourdui.year,
                                                               date__month=dateaujourdui.month,
                                                               date__day=dateaujourdui.day,
                                                               utilisateur_id=4,
                                                               typepage__in=[7, 16]
                                                               ).exclude(utilisateurid__in=listeadmin)

                else:
                    for admin in listeprofile:
                        if (admin.utilisateur.username not in ['omarhasnaoui', 'ouldbrahim_h']):
                            listeadmin.append(admin.utilisateur.id)
                    listhisto = HISTORIQUELOGIN.objects.filter(date__year=dateaujourdui.year,
                                                               date__month=dateaujourdui.month,
                                                               date__day=dateaujourdui.day,
                                                               utilisateur_id=4,
                                                               typepage__in=[7, 16]
                                                               ).exclude(utilisateurid__in=listeadmin)

                listefinal = []
                for elem in listhisto:
                    temps = str(datetime.timedelta(seconds=elem.temps))
                    temps = temps.replace(" days,", "J")
                    temps = temps.replace(" day,", "J")
                    user = User.objects.get(id=elem.utilisateurid).first_name
                    if (elem.typepage.model == "objetsite"):
                        try:
                            objet = OBJETSITE.objects.get(id=elem.typepageid)

                            if(objet.type in ['1', '2', '3']):
                                objet = objet.nom
                            else:
                                objet = objet.ancetrenom+'/'+objet.nom
                            listefinal.append({'user': user, 'rapport': objet, 'temps': temps, 'date': elem.date})
                        except Exception:
                            pass
                    else:
                        try:
                            objet = Slider.objects.get(id=elem.typepageid)
                            listefinal.append({'user': user, 'rapport':  "Slider: "+str(objet), 'temps': temps, 'date': elem.date})
                        except Exception:
                            pass


                return render(request, 'conn/historique.html', {"listefinal": listefinal[::-1]})
        else:
            return redirect('/')

def informationslider(request, pk):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.slider or profile.admin):
            if(request.method == "POST"):
                pk = int(pk)
                nom = request.POST['nom']
                listerapportid = request.POST.getlist('listefinal[]')
                if(pk == 0):
                    newslider = Slider.objects.create(nom = nom, users=request.user)
                    newslider.save()
                    try:
                        idnum = (newslider.listerapport.through.objects.latest('id').id)+1
                    except Exception:
                        idnum = 1
                    #newauth = profile.id_objet.through.objects.create(id=idnum, profile_id=profile.id,objetsite_id=element.id)
                    if(newslider.nom == ''):
                        newslider.nom = "Slider "+str(newslider.id)
                        newslider.save()
                    for elem in listerapportid:
                        newelem = newslider.listerapport.through.objects.create(id=idnum, slider_id = newslider.id, objetsite_id = int(elem))
                        newelem.save()
                        idnum = idnum + 1
                else:
                    oldslider = Slider.objects.get(id=int(pk))
                    oldslider.active = False
                    oldslider.save()
                    newslider = Slider.objects.create(nom = nom, users=request.user)
                    newslider.save()
                    idnum = (newslider.listerapport.through.objects.latest('id').id) + 1
                    if (newslider.nom == ''):
                        newslider.nom = "Slider " + str(newslider.id)
                        newslider.save()
                    for elem in listerapportid:
                        newelem = newslider.listerapport.through.objects.create(id=idnum, slider_id=newslider.id,
                                                                                objetsite_id=int(elem))
                        newelem.save()
                        idnum = idnum + 1

                return HttpResponse('Success')
            else:
                pk = int(pk)
                if(profile.admin or profile.type_autorisation == 'TC'):
                    listerapport = OBJETSITE.objects.filter(slider=True)
                else:
                    listerapport = profile.id_objet.filter(slider=True)
                if(pk == 0):
                    listfinal = []
                    for elem in listerapport:
                        listfinal.append({'id': elem.id, 'nom': elem.nom, 'selected': False})
                    return render(request, 'conn/sliderinfo.html', {'act': 'new', "listfinal": listfinal})
                else:
                    slider = Slider.objects.get(id=pk)
                    listerapportselect = slider.listerapport.all()

                    listfinal = []
                    for elem in listerapport:
                        if(elem in listerapportselect):
                            listfinal.append({'id': elem.id, 'nom': elem.nom, 'selected': True})
                        else:
                            listfinal.append({'id': elem.id, 'nom': elem.nom, 'selected': False})
                    return render(request, 'conn/sliderinfo.html', {'act': 'change',"listfinal":listfinal, 'slider':slider})
        else:
            return redirect('/')


def playslider(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.slider or profile.admin):
            if(request.method == "POST"):
                listerapportid = request.POST.getlist('listefinal[]')
                for elem in listerapportid:
                    elem = int(elem)
                listerapport = OBJETSITE.objects.filter(id__in=listerapportid)
                sliderliste = Slider.objects.filter(users=request.user, active=True)
                slider = 'aucun'
                for element in sliderliste:
                    if(list(element.listerapport.all()) == list(listerapport)):
                        slider = element
                if(slider == 'aucun'):
                    newslider = Slider.objects.create(nom='', users=request.user, active=False)
                    newslider.save()
                    try:
                        idnum = (newslider.listerapport.through.objects.latest('id').id) + 1
                    except Exception:
                        idnum = 1
                    if (newslider.nom == ''):
                        newslider.nom = "Slider " + str(newslider.id)
                        newslider.save()
                    for elem in listerapportid:
                        newelem = newslider.listerapport.through.objects.create(id=idnum, slider_id=newslider.id, objetsite_id=int(elem))
                        newelem.save()
                        idnum = idnum + 1
                        """historique = HISTORIQUELOGIN.objects.create(content_object=newslider.users,
                                                type_object=newslider)
                        historique.save()"""
                    return HttpResponse(newslider.id)
                else:
                    listerapport = slider.listerapport.all()

                    return HttpResponse(slider.id)
            else:
                return redirect('/')
        else:
            return redirect('/')


def lancementduslider(request, pk):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if(profile.slider or profile.admin):
            if(request.method == "POST"):
                return redirect('/')
            else:
                slider = Slider.objects.get(id= int(pk))
                sliderlisterapport = slider.listerapport.all()
                historique = HISTORIQUELOGIN.objects.create(content_object=slider.users, type_object=slider)
                historique.save()

                return render(request, 'sliderplay.html', {'sliderlisterapport': sliderlisterapport,
                                                           'sliderhisto': historique.id})
        else:
            return redirect('/')


def slidersuppression(request, pk):
    if (request.user.id is None):
        return redirect('/')
    else:
        profile = PROFILE.objects.get(utilisateur=request.user)
        if (profile.slider or profile.admin):
            if (request.method == "POST"):
                slider = Slider.objects.get(id=int(pk))
                if(slider.users == request.user):
                    slider.active = False
                return redirect('/')
            else:
                return redirect('/')
        else:
            return redirect('/')


def pageapropos(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        return render(request, 'conn/apropos.html')


def strlienrap(request, pk):
    if (request.user.id is None):
        return redirect('/')
    else:
        lienap = OBJETSITE.objects.get(id = int(pk))
        return HttpResponse(lienap.lien)


def histochangetimenew(request):
    if (request.user.id is None):
        return redirect('/')
    else:
        #/idhisto
        idhisto = request.POST['idhisto']

        histo = HISTORIQUELOGIN.objects.get(id = idhisto)
        histo.temps = int((timezone.now() - histo.date).total_seconds())
        histo.save()
        return HttpResponse('Success')
