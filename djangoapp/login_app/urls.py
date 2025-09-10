# login_app/urls.py (Versão Corrigida e Final)
from . import views
from django.urls import path, include

# URLs do painel de perfil
profile_urlpatterns = [
    path("", views.profile, name="perfilUsuario"),
    path("add-campo/", views.areaProprietario, name="alugar-campo"),
    path("listas/", views.listacampos, name="listacampos"),
    path("relatorio/", views.relatorio_partidas, name="relatorio_partidas"),
]

# URLs principais do app
urlpatterns = [
    # Rota da tela inicial (home)
    path("", views.mainPage, name="home"),
    
    # Rotas de campos e suas interações
    path("available_places/", views.available_places, name="available_places"),
    path("campo/<int:campo_id>/", views.campo_detalhes, name="campo_detalhes"),
    path("campo/<int:campo_id>/feedback/", views.feedPage, name="feedPage"),
    
    # Rotas de partidas
    path('criar-partida/', views.criar_partida, name='criar_partida'),
    path('partida/<int:partida_id>/', views.participar_partida, name='participar_partida'),
    
    # Rotas adicionais
    path('escolher-opcao/<str:esporte>/', views.selecao_opcao, name='selecao_opcao'),
    path('reservar-espaco/', views.reservar_espaco, name='reservar_espaco'),
    path('participardois/', views.participar_dois, name='participar_dois'),
    
    # Inclusão das URLs de perfil
    path("accounts/profile/", include(profile_urlpatterns)),
]