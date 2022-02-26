''''' 
import pypyodbc

from Login.models import OBJETSITE


def enfantdir(elem, liste):
    if (elem.type in ['4', '5'] ):
        liste.append(elem)
    else:
        liste_enfant = OBJETSITE.objects.filter(parent=elem)

        liste.append(elem)
        for enfant in liste_enfant:
            enfantdir(enfant, liste)

        return liste


def verifierauthConso(utilisateur):
    listedir = []
    liste_droit = []
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
                         " WHERE SUBSTRING(dbo.Users.UserName, CHARINDEX('\\', dbo.Users.UserName)+ 1 , LEN(dbo.Users.UserName)) = ? and (dbo.Catalog.Type = 1) " 
                         " and dbo.Catalog.Path like '%/Direction Générale Groupe%' "
                         " order by dbo.Catalog.Path", (utilisateur,))

    for row in cursor:
        listedir.append(row["path"])
    if(len(listedir) > 0):
        listedirectionconso = []
        enfantdir(OBJETSITE.objects.get(type='1', nom='Consolidé'), listedirectionconso)

        if('/Direction Générale Groupe' in listedir):
            return ['Consolidé', OBJETSITE.objects.get(type='1', nom='Consolidé')]
        else:
            for dir in listedir:
                liste_act = dir.split('/')
                parent = liste_act[len(liste_act) - 2]
                if(parent == 'Direction Générale Groupe'):
                    parent = 'Consolidé'
                direction =liste_act[len(liste_act) - 1]

                for elem in listedirectionconso:
                    if(elem.parent != None):
                        if(elem.parent.nom == parent and elem.nom == direction):
                            liste_droit.append(elem.id)




    return liste_droit'''''