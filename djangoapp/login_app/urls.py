from django.urls import path, include
from login_app.views import (
    mainPage,
    registerPage,
    areaProprietario,
    profile,
    listacampos,
    fazer_relatorio,
    feedPage,
    available_places,
    campo_detalhes,
    participar_partida,
    selecao_opcao,
    reservar_espaco,
    criar_partida,
    participar_dois
)

urlpatterns = [
    path("", mainPage, name="home"),
    path("accounts/profile/", mainPage, name="main"),
    path("available_places/", available_places, name="available_places"),
    path("available_places/<str:nome_campo>/", campo_detalhes, name="campo_detalhes"),
    path('partida/<int:partida_id>/', participar_partida, name='participar_partida'),
    path("signup/", registerPage, name="signup"),
    path("accounts/profile/add-campo", areaProprietario, name="alugar-campo"),
    path("accounts/profile/perfilUsuario", profile, name="perfilUsuario"),
    path("accounts/profile/listas", listacampos, name="listacampos"),
    path("accounts/profile/relatorio", fazer_relatorio, name="relatorio"),
    path("accounts/profile/feedback/<int:id>",feedPage,name="feedback"),
    path('campo/<int:id>/feedback/', feedPage, name='feedPage'),
    path('escolher-opcao/<str:esporte>/', selecao_opcao, name='selecao_opcao'),
    path('reservar-espaco/', reservar_espaco, name='reservar_espaco'),
    path('participardois/', participar_dois, name='participar_dois'),
    path('criar-partida/', criar_partida, name='criar_partida')
    
]
