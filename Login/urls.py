from django.urls import path

from Login import views

urlpatterns = [
    path('', views.loggin, name='connexion'),
    path('messagerieprob', views.problemelogin, name='messagerieprob'),
    path('connexion', views.loggin),
    path('deconnexion', views.deconnexion, name='deconnexion'),
    #path('rapport/<int:pk>', views.homerap, name='rapportlog'),
    path('page/<str:pk>', views.homepage, name='pagelog'),
    ]
