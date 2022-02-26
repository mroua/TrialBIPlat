from Login.models import OBJETSITE


"""def verifierauthaut(utilisateur):
    listedir = []
    liste_final =[]
    listeautorisation = []
    conn = pypyodbc.connect('Driver={SQL Server};'
                            'Server=10.10.10.63;'
                            'Database=ReportServer;'
                            'uid=sa;'
                            'pwd=Azerty@22')

    cursor = conn.cursor()
    cursor.execute(      "SELECT distinct dbo.Catalog.Path as path "
                         " FROM dbo.Catalog INNER JOIN "
                         " dbo.PolicyUserRole ON dbo.Catalog.PolicyID = dbo.PolicyUserRole.PolicyID INNER JOIN "
                         " dbo.Users ON dbo.PolicyUserRole.UserID = dbo.Users.UserID "
                         " WHERE SUBSTRING(dbo.Users.UserName, CHARINDEX('\\', dbo.Users.UserName)+ 1 , LEN(dbo.Users.UserName)) = ? and ((dbo.Catalog.Type = 1) or (dbo.Catalog.Type = 2)) " , (utilisateur,))

    for row in cursor:
        liste = row["path"].split('/')
        liste.pop(0)
        listedir.append(liste)
    listedir = sorted(listedir, key=lambda l: (len(l), l))
    if(['Direction Générale Groupe'] in listedir):
        return ['Consolidé']
    else:
        for row in listedir:
            if(len(row) == 1):
                liste_final.append(row)
            else:
                ind = 0
                resultat = False
                while (ind < len(liste_final) and  resultat ==  False):
                    if (all(elem in row for elem in liste_final[ind])):
                        resultat = True
                    ind = ind + 1
                if resultat == False:
                    liste_final.append(row)
        for miniliste in liste_final:
            if miniliste[0] == "Direction Générale Groupe":
                objetorigin = OBJETSITE.objects.get(nom='Consolidé')
            else :
                try:
                    print(miniliste)
                    objetorigin = OBJETSITE.objects.get(nom=miniliste[0])
                except Exception:
                    objetorigin = None
            ind = 1
            erreur = False
            while (ind < len(miniliste)  and erreur == False):
                try:
                    objetorigin = OBJETSITE.objects.get(parent=objetorigin, nom=miniliste[ind])
                except Exception:
                    objetorigin = None
                    erreur = True
                pass
                ind = ind + 1

            if(objetorigin != None):
                print('------'+str(objetorigin.ancetrenom)+'/'+str(objetorigin.nom))
                listeautorisation.append(objetorigin.id)

        return listeautorisation"""


def getlineage(elem, liste):
    if(elem.type == '1' or elem.type == '2'):
        liste.append(elem.nom)
        return (liste[::-1])
    else:
        liste.append(elem.nom)
        return getlineage(elem.parent, liste)

def verifierauthaut(liste):
    '''conn = pypyodbc.connect('Driver={SQL Server};'
                        'Server=10.10.10.63;'
                        'Database=ReportServer;'
                        'uid=sa;'
                        'pwd=Azerty@22')

    cursor = conn.cursor()
    cursor.execute("SELECT distinct dbo.Catalog.Path as path "
                   " FROM dbo.Catalog INNER JOIN "
                   " dbo.PolicyUserRole ON dbo.Catalog.PolicyID = dbo.PolicyUserRole.PolicyID INNER JOIN "
                   " dbo.Users ON dbo.PolicyUserRole.UserID = dbo.Users.UserID "
                   " WHERE SUBSTRING(dbo.Users.UserName, CHARINDEX('\\', dbo.Users.UserName)+ 1 , LEN(dbo.Users.UserName)) = ? and ((dbo.Catalog.Type = 1) or (dbo.Catalog.Type = 2)) ",
                   (utilisateur,))

    liste = []
    for row in cursor:
        row = row[0].replace('Direction Générale Groupe', 'Consolidé')
        liste.append(row)'''

    listeautorisation = OBJETSITE.objects.filter(champsbdd__in=liste)

    '''for elem in liste:
        print(elem)
        print(OBJETSITE.objects.filter(champsbdd='elem'))'''
    return listeautorisation




'''

    listeautorisation = OBJETSITE.objects.all()

    for elem in listeautorisation:
        liste1 = []
        getlineage(elem, liste1)
        liste2 = liste1[::-1]
        elem.champsbdd = '/' + '/'.join(liste2)
        elem.save()


    return 'ok'

'''