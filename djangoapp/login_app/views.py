# seu_app/views.py

# Imports do Django
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import Http404

# Imports FINAIS para a abordagem manual
from allauth.mfa.models import Authenticator
from allauth.mfa import app_settings as mfa_app_settings

# Imports da Standard Library
import json
from datetime import datetime
from decimal import Decimal

# Imports Locais (do seu app)
# ATENÇÃO: Se o modelo Partida não existir em models.py, você pode remover a linha abaixo.
# Se ele existir para outro propósito, pode manter.

from .forms import CoordenadaForm, ReservasForm, UpdateUserForm, UpdateProfileForm, DadosCampoForm, FeedbackForm
from .models import Coordenada, Profile, Reserva, DadosCampo, Feedback


def loginPage(request):
    return render(request, "account/login.html")


# ==============================================================================
# VIEW DE CADASTRO (REGISTRO) - VERSÃO CORRIGIDA E COMPLETA
# ==============================================================================
def registerPage(request):
    """
    Esta view lida com a exibição do formulário de cadastro (GET)
    e com o processamento dos dados do novo usuário (POST).
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta para "{username}" criada com sucesso! Você já pode fazer o login.')
            return redirect('account_login')
        else:
            messages.error(request, 'Não foi possível criar a conta. Por favor, verifique os erros abaixo.')
    else:
        form = UserCreationForm()
    return render(request, 'account/signup.html', {'form': form})


@login_required(redirect_field_name="account_login")
def mainPage(request):
    global reservas
    query = Coordenada.objects.all()
    coordenadas = []

    for i in query:
        coordenadas.append({"latitude": i.latitude, "longitude": i.longitude})
        
    reservas = 0
    if request.method == "POST":
        ini = datetime.strptime(request.POST.get("inicio"), "%H:%M")
        fin = datetime.strptime(request.POST.get("final"), "%H:%M")

        if fin <= ini:
            messages.error(
                request, "O horário de início deve ser antes do horário de final"
            )
        duracao = fin - ini
        duracao_em_horas = duracao.total_seconds() / 3600
        valor_por_hora = (
            50  # ALTERAR PARA QUE PEGUE O VALOR DO CAMPO ESPECÍFICO POR HORA
        )
        valor_total = duracao_em_horas * valor_por_hora

        instancia = Reserva(
            valor_total=valor_total,
        )

        form = ReservasForm(data=request.POST, instance=instancia)

        print(request.POST)
        if form.is_valid():
            form.save()
            reservas += 1
            messages.success(request, "Reservado com sucesso")
            return redirect("main")
        else:
            print(form.errors)
            messages.error(request, "Erro ao reservar campo, tente marcar outra data ou hora")

    context = {"coordenadas": json.dumps(coordenadas),
               "form": ReservasForm(),
               }
    return render(request, "pages/main.html", context)


# DICIONÁRIO DE CAMPOS E PARTIDAS (FONTE DE DADOS)
# Movido para cima para ficar antes das views que o utilizam
campos = {
    # Região Itaipuaçu
    "campo_a": {
        "nome": "Arena Itaipuaçu",
        "imagem_capa": "/static/images/arena_itaipuaçu.jpg",
        "partidas": [
            {"id": 1, "titulo": "Clássico da Região Oceânica", "data": "2025-05-15", "horario": "20:00", "categoria": "adulto", "genero": "misto", "vagas": 10},
            {"id": 2, "titulo": "Torneio de Verão Masculino", "data": "2025-06-20", "horario": "19:00", "categoria": "adulto", "genero": "masculino", "vagas": 8},
            {"id": 3, "titulo": "Escolinha de Futebol", "data": "2025-05-10", "horario": "09:00", "categoria": "infantil", "genero": "misto", "vagas": 15},
            {"id": 4, "titulo": "Liga Feminina", "data": "2025-06-05", "horario": "18:00", "categoria": "adulto", "genero": "feminino", "vagas": 12},
            {"id": 5, "titulo": "Torneio Master", "data": "2025-05-25", "horario": "16:00", "categoria": "master", "genero": "masculino", "vagas": 10}
        ],
    },
    "campo_itaipuacu_1": {
        "nome": "Arena Barroco",
        "imagem_capa": "/static/images/arena_barroco.jpg",
        "partidas": [
            {"id": 1, "titulo": "Liga Barroco", "data": "2025-04-25", "horario": "18:30", "categoria": "adulto", "genero": "masculino", "vagas": 7},
            {"id": 2, "titulo": "Treino Livre", "data": "2025-05-05", "horario": "14:00", "categoria": "livre", "genero": "misto", "vagas": 12},
            {"id": 3, "titulo": "Campeonato Feminino", "data": "2025-05-12", "horario": "19:00", "categoria": "adulto", "genero": "feminino", "vagas": 9},
            {"id": 4, "titulo": "Torneio Juvenil", "data": "2025-06-08", "horario": "15:00", "categoria": "juvenil", "genero": "misto", "vagas": 14}
        ],
    },
    # ... (restante do seu dicionário 'campos' aqui) ...
     "arena_marques": {
        "nome": "Campo Divino Esporte e Lazer",
        "imagem_capa": "/static/images/campo_divino.jpg",
        "partidas": [
            {"id": 1, "titulo": "Torneio Divino", "data": "2025-05-08", "horario": "20:00", "categoria": "adulto", "genero": "misto", "vagas": 10},
            {"id": 2, "titulo": "Aulão de Futsal", "data": "2025-04-30", "horario": "10:00", "categoria": "infantil", "genero": "misto", "vagas": 20},
            {"id": 3, "titulo": "Liga Masculina", "data": "2025-06-15", "horario": "19:30", "categoria": "adulto", "genero": "masculino", "vagas": 8},
            {"id": 4, "titulo": "Treino Feminino", "data": "2025-05-22", "horario": "18:00", "categoria": "adulto", "genero": "feminino", "vagas": 10}
        ],
    },
    "campo_palmeiras": {
        "nome": "Campo Inter Academy",
        "imagem_capa": "/static/images/campo_inter_academy.jpg",
        "partidas": [
            {"id": 1, "titulo": "Treino de Equipe", "data": "2025-05-12", "horario": "08:00", "categoria": "juvenil", "genero": "masculino", "vagas": 18},
            {"id": 2, "titulo": "Interclasses", "data": "2025-06-05", "horario": "16:00", "categoria": "juvenil", "genero": "misto", "vagas": 15},
            {"id": 3, "titulo": "Torneio Feminino Juvenil", "data": "2025-05-20", "horario": "14:00", "categoria": "juvenil", "genero": "feminino", "vagas": 12},
            {"id": 4, "titulo": "Escolinha de Futebol", "data": "2025-06-12", "horario": "09:00", "categoria": "infantil", "genero": "misto", "vagas": 20}
        ],
    },
    "arena_flamengo": {
        "nome": "Arena Flamengo",
        "imagem_capa": "/static/images/arena_flamengo1.jpg",
        "partidas": [
            {"id": 1, "titulo": "Flamengo vs Vasco", "data": "2025-04-10", "horario": "18:00", "categoria": "adulto", "genero": "masculino", "vagas": 1},
            {"id": 2, "titulo": "Amistoso Feminino", "data": "2025-04-12", "horario": "15:00", "categoria": "adulto", "genero": "feminino", "vagas": 8},
            {"id": 3, "titulo": "Torneio Masters", "data": "2025-05-20", "horario": "19:30", "categoria": "master", "genero": "masculino", "vagas": 0},
            {"id": 4, "titulo": "Pelada Mista", "data": "2025-06-08", "horario": "20:00", "categoria": "livre", "genero": "misto", "vagas": 12},
            {"id": 5, "titulo": "Treino Juvenil", "data": "2025-05-05", "horario": "16:00", "categoria": "juvenil", "genero": "masculino", "vagas": 10}
        ],
    },
    "campo_central": {
        "nome": "Arena Centro",
        "imagem_capa": "/static/images/arena centro.png",
        "partidas": [
            {"id": 1, "titulo": "Campeonato Centro", "data": "2025-04-15", "horario": "20:00", "categoria": "adulto", "genero": "masculino", "vagas": 8},
            {"id": 2, "titulo": "Pelada Semanal", "data": "2025-04-18", "horario": "19:00", "categoria": "livre", "genero": "misto", "vagas": 12},
            {"id": 3, "titulo": "Torneio Feminino", "data": "2025-05-10", "horario": "18:00", "categoria": "adulto", "genero": "feminino", "vagas": 10},
            {"id": 4, "titulo": "Escolinha de Futsal", "data": "2025-06-15", "horario": "09:00", "categoria": "infantil", "genero": "misto", "vagas": 15}
        ],
    },
    "quadra_centro": {
        "nome": "Campo Amparo Esporte Clube",
        "imagem_capa": "/static/images/amparo.jpg",
        "partidas": [
            {"id": 1, "titulo": "Torneio de Inauguração", "data": "2025-05-01", "horario": "09:00", "categoria": "livre", "genero": "misto", "vagas": 20},
            {"id": 2, "titulo": "Escolinha de Futsal", "data": "2025-05-03", "horario": "14:00", "categoria": "infantil", "genero": "misto", "vagas": 15},
            {"id": 3, "titulo": "Liga Masculina", "data": "2025-06-10", "horario": "20:00", "categoria": "adulto", "genero": "masculino", "vagas": 10},
            {"id": 4, "titulo": "Treino Feminino", "data": "2025-06-12", "horario": "19:00", "categoria": "adulto", "genero": "feminino", "vagas": 12}
        ],
    },
    "campo_c": {
        "nome": "Arena Itapeba",
        "imagem_capa": "/static/images/arena_itapeba.jpeg",
        "partidas": [
            {"id": 1, "titulo": "Liga Itapeba", "data": "2025-04-22", "horario": "19:00", "categoria": "adulto", "genero": "masculino", "vagas": 7},
            {"id": 2, "titulo": "Treino Feminino", "data": "2025-04-24", "horario": "18:00", "categoria": "adulto", "genero": "feminino", "vagas": 9},
            {"id": 3, "titulo": "Torneio Misto", "data": "2025-05-15", "horario": "20:00", "categoria": "adulto", "genero": "misto", "vagas": 12},
            {"id": 4, "titulo": "Escolinha de Futebol", "data": "2025-06-05", "horario": "14:00", "categoria": "infantil", "genero": "misto", "vagas": 18}
        ],
    },
    "campo_saojose_1": {
        "nome": "Arena São José",
        "imagem_capa": "/static/images/arena_são josé.jpg",
        "partidas": [
            {"id": 1, "titulo": "Copa São José", "data": "2025-05-25", "horario": "20:00", "categoria": "adulto", "genero": "masculino", "vagas": 6},
            {"id": 2, "titulo": "Pelada da Comunidade", "data": "2025-05-28", "horario": "19:00", "categoria": "livre", "genero": "misto", "vagas": 14},
            {"id": 3, "titulo": "Torneio Feminino", "data": "2025-06-08", "horario": "18:00", "categoria": "adulto", "genero": "feminino", "vagas": 10},
            {"id": 4, "titulo": "Torneio Master", "data": "2025-06-15", "horario": "19:30", "categoria": "master", "genero": "masculino", "vagas": 8}
        ],
    },
    "arena_jose": {
        "nome": "Quadra Inoã",
        "imagem_capa": "/static/images/quadra_inoã.jpg",
        "partidas": [
            {"id": 1, "titulo": "Torneio de Inoã", "data": "2025-06-10", "horario": "18:30", "categoria": "adulto", "genero": "masculino", "vagas": 8},
            {"id": 2, "titulo": "Aulão de Futsal", "data": "2025-06-12", "horario": "09:00", "categoria": "infantil", "genero": "misto", "vagas": 20},
            {"id": 3, "titulo": "Liga Feminina", "data": "2025-06-18", "horario": "19:00", "categoria": "adulto", "genero": "feminino", "vagas": 10},
            {"id": 4, "titulo": "Pelada Mista", "data": "2025-06-20", "horario": "20:00", "categoria": "livre", "genero": "misto", "vagas": 15}
        ],
    },
    "quadra_saojose": {
        "nome": "Quadra Poliesportiva Parque Nanci",
        "imagem_capa": "/static/images/parque_nanci.jpg",
        "partidas": [
            {"id": 1, "titulo": "Festival Esportivo", "data": "2025-05-30", "horario": "08:00", "categoria": "livre", "genero": "misto", "vagas": 25},
            {"id": 2, "titulo": "Torneio de Veteranos", "data": "2025-06-02", "horario": "19:00", "categoria": "master", "genero": "masculino", "vagas": 10},
            {"id": 3, "titulo": "Escolinha de Futebol", "data": "2025-06-05", "horario": "14:00", "categoria": "infantil", "genero": "misto", "vagas": 18},
            {"id": 4, "titulo": "Torneio Feminino", "data": "2025-06-10", "horario": "18:00", "categoria": "adulto", "genero": "feminino", "vagas": 12},
            {"id": 5, "titulo": "Liga Masculina", "data": "2025-06-15", "horario": "20:00", "categoria": "adulto", "genero": "masculino", "vagas": 10}
        ],
    },
}

# ==============================================================================
# VIEW relatorio_partidas - VERSÃO CORRIGIDA
# ==============================================================================
# seu_app/views.py

from datetime import datetime # Certifique-se que 'datetime' de 'datetime' está importado no topo do arquivo

# ... (outras views e o dicionário 'campos' aqui em cima) ...

# ==============================================================================
# VIEW relatorio_partidas - VERSÃO COM CONVERSÃO DE DATA
# ==============================================================================
# seu_app/views.py

from django.contrib import messages # Verifique se 'messages' está importado
from datetime import datetime

# ... (outras views e o dicionário 'campos' aqui em cima) ...

# ==============================================================================
# VIEW relatorio_partidas - VERSÃO COM FILTRO DE DATA ROBUSTO
# ==============================================================================
# seu_app/views.py

from django.contrib import messages
from datetime import datetime

# ... (outras views e o dicionário 'campos' aqui em cima) ...

# ==============================================================================
# VIEW relatorio_partidas - VERSÃO DE DEPURAÇÃO
# ==============================================================================
# seu_app/views.py

from django.contrib import messages
from datetime import datetime

# ... (outras views e o dicionário 'campos' aqui em cima) ...

# ==============================================================================
# VIEW relatorio_partidas - VERSÃO FINAL
# ==============================================================================
def relatorio_partidas(request):
    # 1. Prepara a lista de partidas, convertendo as datas
    todas_as_partidas = []
    for info_campo in campos.values():
        for partida_dict in info_campo['partidas']:
            partida_completa = partida_dict.copy()
            partida_completa['campo'] = info_campo['nome']
            try:
                data_obj = datetime.strptime(partida_dict['data'], '%Y-%m-%d').date()
                partida_completa['data'] = data_obj
            except (ValueError, KeyError):
                partida_completa['data'] = None
            todas_as_partidas.append(partida_completa)
            
    partidas_filtradas = todas_as_partidas

    # 2. Obtém os parâmetros de filtro da requisição
    selected_campo = request.GET.get('campo_filtro')
    selected_data_str = request.GET.get('data_filtro') 

    # 3. Aplica filtro de CAMPO (se existir)
    if selected_campo:
        partidas_filtradas = [p for p in partidas_filtradas if p['campo'] == selected_campo]
    
    # 4. Aplica filtro de DATA (se existir)
    if selected_data_str and selected_data_str.strip():
        try:
            data_filtro = datetime.strptime(selected_data_str, '%Y-%m-%d').date()
            
            # ================================================================== #
            # =================== MUDANÇA DA LÓGICA AQUI =================== #
            # Trocamos >= (maior ou igual) por == (exatamente igual)
            # ================================================================== #
            partidas_filtradas = [
                p for p in partidas_filtradas 
                if p['data'] is not None and p['data'] == data_filtro
            ]
        except ValueError:
            messages.error(request, f"O formato da data '{selected_data_str}' é inválido. Use AAAA-MM-DD.")
    
    # 5. Prepara o contexto final para o template
    campos_disponiveis = sorted(list(set(info['nome'] for info in campos.values())))
    context = {
        'partidas': partidas_filtradas,
        'campos_disponiveis': campos_disponiveis,
        'selected_campo': selected_campo,
        'selected_data': selected_data_str,
    }
    
    return render(request, 'pages/relatorio.html', context)
def available_places(request):
    regiao = request.GET.get('regiao', 'centro')
    esporte = request.GET.get('esporte', 'futebol')
    
    context = {
        'regiao': regiao,
        'esporte': esporte,
    }
    return render(request, 'pages/available_places.html', context)


def campo_detalhes(request, nome_campo):
    if nome_campo not in campos:
        raise Http404("Campo não encontrado")

    contexto = {
        "campo": campos[nome_campo],
        "nome": campos[nome_campo]["nome"],
        "imagem_capa": request.build_absolute_uri(campos[nome_campo]["imagem_capa"]),
        "partidas_json": json.dumps(campos[nome_campo]["partidas"]),
    }

    return render(request, "pages/campo_detalhes.html", contexto)


@login_required
def participar_partida(request, partida_id):
    context = {
        'esporte': 'Futebol',
        'local': 'Arena Flamengo',
        'jogadores': [
            {'nome': 'Jeff', 'posicao': 'Goleiro', 'presenca': 'Confirmado'},
            {'nome': 'Outro Jeff', 'posicao': 'Lateral', 'presenca': 'Confirmado'},
            {'nome': 'Cauã', 'posicao': '', 'presenca': 'Não'},
            {'nome': 'Lucas', 'posicao': 'Zagueiro', 'presenca': 'Confirmado'},
            {'nome': 'Mateus', 'posicao': '', 'presenca': 'Não'},
            {'nome': 'Rafael', 'posicao': 'Meio-campo', 'presenca': 'Confirmado'},
            {'nome': 'Pedro', 'posicao': '', 'presenca': 'Não'},
        ]
    }
    return render(request, 'pages/participar.html', context)


def participar_dois(request):
    esporte = request.GET.get('esporte', '')
    local = request.GET.get('local', '')
    data = request.GET.get('data', '')
    
    context = {
        'esporte': esporte,
        'local': local,
        'data': data,
    }
    return render(request, 'pages/participardois.html', context)


@staff_member_required
def areaProprietario(request):
    query = Coordenada.objects.all()
    coordenadas = []
    for i in query:
        coordenadas.append({"latitude": i.latitude, "longitude": i.longitude})
    if request.method == "POST":
        form = CoordenadaForm(request.POST)
        form_dadosCampo = DadosCampoForm(request.POST, request.FILES)
        if form.is_valid() and form_dadosCampo.is_valid():
            form_dadosCampo.save()
            form.save()
            messages.success(request, "Cadastrado com sucesso")
            return redirect("alugar-campo")
    else:
        form = CoordenadaForm()
        form_dadosCampo = DadosCampoForm()
    context = {"form": form,
               "coordenadas": json.dumps(coordenadas),
               "form_dadosCampo": form_dadosCampo
               }
    return render(request, "pages/alugarcamp.html", context)


@login_required(redirect_field_name="account_login")
def profile(request):
    if request.method == "POST":
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Seu perfil foi atualizado com sucesso")
            return redirect(to="perfilUsuario")
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    user_authenticators = Authenticator.objects.filter(user=request.user)
    mfa_is_enabled = user_authenticators.exists()
    
    authenticators_for_template = {
        "totp": None,
        "webauthn": [],
        "recovery_codes": None
    }
    for auth in user_authenticators:
        if auth.type == Authenticator.Type.TOTP:
            authenticators_for_template["totp"] = auth.wrap()
        elif auth.type == Authenticator.Type.WEBAUTHN:
            authenticators_for_template["webauthn"].append(auth.wrap())
        elif auth.type == Authenticator.Type.RECOVERY_CODES:
            authenticators_for_template["recovery_codes"] = auth.wrap()

    mfa_context = {
        "authenticators": authenticators_for_template,
        "MFA_SUPPORTED_TYPES": mfa_app_settings.SUPPORTED_TYPES,
        "is_mfa_enabled": mfa_is_enabled,
    }
    
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        **mfa_context
    }
    return render(request, "pages/profile.html", context)


@staff_member_required
def fazer_relatorio(request):
    partidas = []
    for slug, info in campos.items():
        for p in info['partidas']:
            partidas.append({
                'id': p['id'],
                'campo': info['nome'],
                'titulo': p['titulo'],
                'data': p['data'],
                'horario': p['horario'],
                'categoria': p['categoria'],
                'genero': p['genero'],
                'vagas': p['vagas'],
            })

    return render(request, "pages/relatorio.html", {
        'partidas': partidas
    })


def listacampos(request):
    query = DadosCampo.objects.all()
    query_coordenada = Coordenada.objects.all()

    coordenadas = []

    for i in query_coordenada:
        coordenadas.append({"latitude": i.latitude, "longitude": i.longitude})
    
    context = {"dadosCampo": query,
               "coordenadas": json.dumps(coordenadas)}

    return render(request, "pages/listcampos.html",context)


def feedPage(request,id):
    query = DadosCampo.objects.get(id=id)
    form = FeedbackForm()
    
    feedback = Feedback.objects.filter(campoAvaliado=query)
    
    if request.method == "POST":
        instancia = Feedback(
            nomeUsuario = request.user,
            campoAvaliado = query,
            )

        form = FeedbackForm(request.POST,instance=instancia)

        if form.is_valid():
            form.save()
            messages.success(request, "Feedback enviado com sucesso")
            
            return redirect("feedPage",id=id)

    context = {
        "dadosCampo": query,
        "form": form,
        "feedback": feedback,
    }
    return render(request,"pages/feedPage.html",context)


def selecao_opcao(request, esporte):
    local = "Quadra Principal"
    return render(request, 'pages/selecao_opcao.html', {
        'esporte': esporte.lower(),
        'local': local
    })


def reservar_espaco(request):
    return render(request, 'pages/reservar-espaco.html') 


def criar_partida(request):
    return render(request, 'pages/criar_partida.html')