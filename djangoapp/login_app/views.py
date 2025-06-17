# seu_app/views.py
import json # Garanta que 'import json' está no topo do arquivo
# Imports do Django
# No topo do seu views.py, junto com os outros imports
from collections import Counter
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import Http404

from datetime import datetime # Certifique-se que 'datetime' de 'datetime' está importado no topo do arquivo


from django.contrib import messages 
from datetime import datetime


from django.contrib import messages
from datetime import datetime



from django.contrib import messages
from datetime import datetime




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



def mapa_quadras(request):
    # Prepara os dados dos campos para serem usados no JavaScript do mapa
    # Criamos uma lista simples de dicionários
    campos_para_mapa = []
    for slug, info in campos.items():
        campos_para_mapa.append({
            'slug': slug,
            'nome': info['nome'],
            'bairro': info.get('bairro', 'Indefinido'),
            'lat': info.get('lat', 0), # Adicione lat/lng ao seu dicionário 'campos'
            'lng': info.get('lng', 0), # Adicione lat/lng ao seu dicionário 'campos'
            'imagens': info.get('imagens', []), # Adicione uma lista de imagens em 'campos'
            'url': f"/campo/{slug}/" # Exemplo de URL, ajuste conforme sua urls.py
        })
        
    context = {
        'esporte': request.GET.get('esporte', 'futebol'),
        'campos_json': json.dumps(campos_para_mapa)
    }
    return render(request, "pages/mapa_quadras.html", context)

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
# COPIE E COLE ESTE BLOCO INTEIRO, SUBSTITUINDO O SEU DICIONÁRIO campos ATUAL

# Em login_app/views.py, substitua seu dicionário 'campos' por este:

campos = {
    # Região Itaipuaçu
    "campo_a": {
        "nome": "Arena Itaipuaçu",
        "bairro": "Itaipuaçu",
        "imagem_capa": "/static/images/arena_itaipuaçu.jpg",
        "partidas": [
            {"id": 1, "titulo": "Desafio das Praias: Itaipuaçu vs Recanto", "data": "2025-07-12", "horario": "16:00", "esporte": "Futebol", "categoria": "adulto", "genero": "masculino", "vagas": 14},
            {"id": 2, "titulo": "Circuito Maricaense de Vôlei - Etapa Itaipuaçu", "data": "2025-07-19", "horario": "10:00", "esporte": "Vôlei", "categoria": "adulto", "genero": "misto", "vagas": 16},
            {"id": 3, "titulo": "Escolinha de Futebol 'Futuro Craque'", "data": "2025-07-05", "horario": "09:00", "esporte": "Futebol", "categoria": "infantil", "genero": "misto", "vagas": 20},
            {"id": 4, "titulo": "Torneio de Vôlei Feminino", "data": "2025-07-26", "horario": "11:00", "esporte": "Vôlei", "categoria": "adulto", "genero": "feminino", "vagas": 12},
            {"id": 5, "titulo": "Racha dos Veteranos da Orla", "data": "2025-07-08", "horario": "19:30", "esporte": "Futebol", "categoria": "master", "genero": "masculino", "vagas": 10},
            {"id": 6, "titulo": "Treino Aberto de Vôlei 4x4", "data": "2025-07-15", "horario": "18:00", "esporte": "Vôlei", "categoria": "livre", "genero": "misto", "vagas": 16},
        ],
    },
    "campo_itaipuacu_1": {
        "nome": "Arena Barroco",
        "bairro": "Itaipuaçu",
        "imagem_capa": "/static/images/arena_barroco.jpg",
        "partidas": [
            {"id": 1, "titulo": "Copa Barroco de Futebol", "data": "2025-07-18", "horario": "20:30", "esporte": "Futebol", "categoria": "adulto", "genero": "masculino", "vagas": 10},
            {"id": 2, "titulo": "Treino da Seleção Feminina de Maricá", "data": "2025-07-07", "horario": "19:00", "esporte": "Futebol", "categoria": "adulto", "genero": "feminino", "vagas": 15},
            {"id": 3, "titulo": "Amistoso Juvenil: Barroco vs Flamengo", "data": "2025-07-12", "horario": "15:00", "esporte": "Futebol", "categoria": "juvenil", "genero": "misto", "vagas": 14},
            {"id": 4, "titulo": "Liga Master de Futebol +40", "data": "2025-07-21", "horario": "21:00", "esporte": "Futebol", "categoria": "master", "genero": "masculino", "vagas": 8},
            {"id": 5, "titulo": "Festival de Basquete Escolar", "data": "2025-08-02", "horario": "09:30", "esporte": "Basquete", "categoria": "infantil", "genero": "misto", "vagas": 25},
        ],
    },
    "arena_marques": {
        "nome": "Campo Divino Esporte e Lazer",
        "bairro": "Marques de Maricá",
        "imagem_capa": "/static/images/campo_divino.jpg",
        "partidas": [
            {"id": 1, "titulo": "Copa Divino de Futebol", "data": "2025-07-11", "horario": "20:00", "esporte": "Futebol", "categoria": "adulto", "genero": "misto", "vagas": 14},
            {"id": 2, "titulo": "Aulão de Basquete para Crianças", "data": "2025-07-05", "horario": "10:00", "esporte": "Basquete", "categoria": "infantil", "genero": "misto", "vagas": 20},
            {"id": 3, "titulo": "Liga de Empresas - Etapa Final", "data": "2025-07-25", "horario": "19:30", "esporte": "Futebol", "categoria": "adulto", "genero": "masculino", "vagas": 14},
            {"id": 4, "titulo": "Treino Aberto Feminino de Vôlei", "data": "2025-07-14", "horario": "18:30", "esporte": "Vôlei", "categoria": "adulto", "genero": "feminino", "vagas": 12},
            {"id": 5, "titulo": "Torneio de Pais e Filhos", "data": "2025-07-27", "horario": "11:00", "esporte": "Futebol", "categoria": "livre", "genero": "misto", "vagas": 22},
        ],
    },
    "campo_palmeiras": {
        "nome": "Campo Inter Academy",
        "bairro": "Centro",
        "imagem_capa": "/static/images/campo_inter_academy.jpg",
        "partidas": [
            {"id": 1, "titulo": "Peneira de Novos Talentos Sub-17", "data": "2025-07-13", "horario": "09:00", "esporte": "Futebol", "categoria": "juvenil", "genero": "masculino", "vagas": 30},
            {"id": 2, "titulo": "Campeonato Interbairros Juvenil", "data": "2025-07-20", "horario": "16:00", "esporte": "Futebol", "categoria": "juvenil", "genero": "misto", "vagas": 22},
            {"id": 3, "titulo": "Final da Copa Maricá Feminina Sub-20", "data": "2025-07-27", "horario": "14:00", "esporte": "Futebol", "categoria": "juvenil", "genero": "feminino", "vagas": 22},
            {"id": 4, "titulo": "Clínica de Futebol com Ex-Jogadores", "data": "2025-08-03", "horario": "10:00", "esporte": "Futebol", "categoria": "infantil", "genero": "misto", "vagas": 40},
        ],
    },
    "arena_flamengo": {
        "nome": "Arena Flamengo",
        "bairro": "Flamengo",
        "imagem_capa": "/static/images/arena_flamengo1.jpg",
        "partidas": [
            {"id": 1, "titulo": "Desafio dos Veteranos: Flamengo vs Vasco", "data": "2025-07-12", "horario": "18:00", "esporte": "Futebol", "categoria": "master", "genero": "masculino", "vagas": 14},
            {"id": 2, "titulo": "Torneio 3x3 de Basquete de Rua", "data": "2025-07-19", "horario": "15:00", "esporte": "Basquete", "categoria": "adulto", "genero": "misto", "vagas": 1},
            {"id": 3, "titulo": "Amistoso da Seleção Master de Maricá", "data": "2025-07-22", "horario": "19:30", "esporte": "Futebol", "categoria": "master", "genero": "masculino", "vagas": 14},
            {"id": 4, "titulo": "Racha Semanal da Comunidade", "data": "2025-07-09", "horario": "20:00", "esporte": "Futebol", "categoria": "livre", "genero": "misto", "vagas": 0},
            {"id": 5, "titulo": "Treino de Arremessos - Basquete", "data": "2025-07-16", "horario": "17:00", "esporte": "Basquete", "categoria": "juvenil", "genero": "misto", "vagas": 10},
        ],
    },
    "campo_central": {
        "nome": "Arena Centro",
        "bairro": "Centro",
        "imagem_capa": "/static/images/arena centro.png",
        "partidas": [
            {"id": 1, "titulo": "Finais dos Jogos Abertos de Maricá", "data": "2025-08-09", "horario": "20:00", "esporte": "Futebol", "categoria": "adulto", "genero": "masculino", "vagas": 10},
            {"id": 2, "titulo": "Torneio de Vôlei de Aniversário da Cidade", "data": "2025-08-10", "horario": "10:00", "esporte": "Vôlei", "categoria": "livre", "genero": "misto", "vagas": 12},
            {"id": 3, "titulo": "Final da Liga Feminina de Futebol", "data": "2025-08-09", "horario": "18:30", "esporte": "Futebol", "categoria": "adulto", "genero": "feminino", "vagas": 10},
            {"id": 4, "titulo": "Apresentação da Escolinha de Basquete", "data": "2025-08-10", "horario": "15:00", "esporte": "Basquete", "categoria": "infantil", "genero": "misto", "vagas": 30},
            {"id": 5, "titulo": "Campeonato de Tênis de Duplas", "data": "2025-08-11", "horario": "19:00", "esporte": "Tênis", "categoria": "livre", "genero": "misto", "vagas": 20},
        ],
    },
    "quadra_centro": {
        "nome": "Campo Amparo Esporte Clube",
        "bairro": "Centro",
        "imagem_capa": "/static/images/amparo.jpg",
        "partidas": [
            {"id": 1, "titulo": "Taça Amparo de Futebol", "data": "2025-07-14", "horario": "20:00", "esporte": "Futebol", "categoria": "adulto", "genero": "masculino", "vagas": 10},
            {"id": 2, "titulo": "Aula de Vôlei para Terceira Idade", "data": "2025-07-15", "horario": "09:00", "esporte": "Vôlei", "categoria": "master", "genero": "misto", "vagas": 16},
            {"id": 3, "titulo": "Treino do time principal - Amparo FC", "data": "2025-07-17", "horario": "19:00", "esporte": "Futebol", "categoria": "adulto", "genero": "masculino", "vagas": 12},
            {"id": 4, "titulo": "Torneio de Tênis", "data": "2025-07-19", "horario": "14:00", "esporte": "Tênis", "categoria": "livre", "genero": "misto", "vagas": 24},
        ],
    },
    "campo_c": {
        "nome": "Arena Itapeba",
        "bairro": "Itapeba",
        "imagem_capa": "/static/images/arena_itapeba.jpeg",
        "partidas": [
            {"id": 1, "titulo": "Campeonato de Rua de Itapeba", "data": "2025-07-26", "horario": "16:00", "esporte": "Futebol", "categoria": "adulto", "genero": "masculino", "vagas": 14},
            {"id": 2, "titulo": "Treino Físico Comunitário para Atletas", "data": "2025-07-08", "horario": "07:00", "esporte": "Vôlei", "categoria": "livre", "genero": "misto", "vagas": 25},
            {"id": 3, "titulo": "Torneio de Vôlei Misto", "data": "2025-07-20", "horario": "15:00", "esporte": "Vôlei", "categoria": "livre", "genero": "misto", "vagas": 20},
            {"id": 4, "titulo": "Escolinha de Futebol do Bairro", "data": "2025-07-12", "horario": "09:00", "esporte": "Futebol", "categoria": "infantil", "genero": "misto", "vagas": 18},
        ],
    },
    "campo_saojose_1": {
        "nome": "Arena São José",
        "bairro": "São José do Imbassaí",
        "imagem_capa": "/static/images/arena_são josé.jpg",
        "partidas": [
            {"id": 1, "titulo": "Copa Integração São José", "data": "2025-07-25", "horario": "20:00", "esporte": "Futebol", "categoria": "adulto", "genero": "masculino", "vagas": 14},
            {"id": 2, "titulo": "Racha dos Comerciantes Locais", "data": "2025-07-16", "horario": "19:30", "esporte": "Futebol", "categoria": "livre", "genero": "misto", "vagas": 14},
            {"id": 3, "titulo": "Amistoso Feminino São José vs Inoã", "data": "2025-07-27", "horario": "16:00", "esporte": "Futebol", "categoria": "adulto", "genero": "feminino", "vagas": 14},
            {"id": 4, "titulo": "Torneio de Tênis de Duplas", "data": "2025-08-03", "horario": "17:00", "esporte": "Tênis", "categoria": "livre", "genero": "misto", "vagas": 16},
        ],
    },
    "arena_jose": {
        "nome": "Quadra Inoã",
        "bairro": "Inoã",
        "imagem_capa": "/static/images/quadra_inoã.jpg",
        "partidas": [
            {"id": 1, "titulo": "Supercopa Inoã de Futebol", "data": "2025-07-19", "horario": "18:30", "esporte": "Futebol", "categoria": "adulto", "genero": "masculino", "vagas": 10},
            {"id": 2, "titulo": "Festival de Basquete Juvenil", "data": "2025-07-20", "horario": "09:00", "esporte": "Basquete", "categoria": "juvenil", "genero": "misto", "vagas": 20},
            {"id": 3, "titulo": "Liga Feminina de Vôlei", "data": "2025-07-26", "horario": "19:00", "esporte": "Vôlei", "categoria": "adulto", "genero": "feminino", "vagas": 14},
            {"id": 4, "titulo": "Pelada Mista dos Moradores", "data": "2025-07-23", "horario": "20:30", "esporte": "Futebol", "categoria": "livre", "genero": "misto", "vagas": 15},
        ],
    },
    "quadra_saojose": {
        "nome": "Quadra Poliesportiva Parque Nanci",
        "bairro": "Parque Nanci",
        "imagem_capa": "/static/images/parque_nanci.jpg",
        "partidas": [
            {"id": 1, "titulo": "Festival de Vôlei do Parque Nanci", "data": "2025-07-13", "horario": "09:00", "esporte": "Vôlei", "categoria": "livre", "genero": "misto", "vagas": 25},
            {"id": 2, "titulo": "Torneio de Veteranos do Basquete", "data": "2025-07-14", "horario": "19:00", "esporte": "Basquete", "categoria": "master", "genero": "masculino", "vagas": 10},
            {"id": 3, "titulo": "Torneio Escolar de Basquete", "data": "2025-07-28", "horario": "14:00", "esporte": "Basquete", "categoria": "infantil", "genero": "misto", "vagas": 50},
            {"id": 4, "titulo": "Copa de Vôlei Feminino", "data": "2025-08-02", "horario": "18:00", "esporte": "Vôlei", "categoria": "adulto", "genero": "feminino", "vagas": 12},
            {"id": 5, "titulo": "Campeonato Municipal de Basquete", "data": "2025-08-04", "horario": "20:00", "esporte": "Basquete", "categoria": "adulto", "genero": "masculino", "vagas": 14},
        ],
    },
}



# Cole esta versão ÚNICA e CORRETA no seu views.py

# login_app/views.py

from collections import Counter, defaultdict
# ... outros imports ...

# Em login_app/views.py

@staff_member_required
def relatorio_partidas(request):
    """
    Gera um relatório estatístico de partidas. 
    Esta view é 'stateless' - ela recria tudo do zero a cada requisição.
    """
    # --- 1. FONTE DE DADOS: Sempre recriada do zero ---
    todas_as_partidas = []
    for info_campo in campos.values():
        for p in info_campo['partidas']:
            # Usar .copy() garante que não modificamos o dicionário original 'campos'
            partida_completa = p.copy()
            partida_completa['campo'] = info_campo['nome']
            try:
                # Converte a data para um objeto, garantindo consistência
                partida_completa['data'] = datetime.strptime(p['data'], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                partida_completa['data'] = datetime.now().date()
            
            todas_as_partidas.append(partida_completa)

    # --- 2. FILTROS ---
    selected_campo = request.GET.get('campo_filtro', '')
    selected_data_str = request.GET.get('data_filtro', '')
    partidas_filtradas = todas_as_partidas

    if selected_campo:
        partidas_filtradas = [p for p in partidas_filtradas if p['campo'] == selected_campo]
    
    if selected_data_str:
        try:
            data_filtro = datetime.strptime(selected_data_str, '%Y-%m-%d').date()
            partidas_filtradas = [p for p in partidas_filtradas if p['data'] >= data_filtro]
        except (ValueError, TypeError):
            pass

    # --- 3. CÁLCULOS: Sempre feitos com base nos dados frescos ---
    # O dicionário 'stats' é sempre novo a cada requisição
    stats = {
        'quadra_mais_utilizada': None, 'horario_pico_pessoas': None,
        'esporte_mais_praticado': None, 'categoria_popular': None,
        'distribuicao_genero': [], 'total_usuarios': 0,
    }

    if partidas_filtradas:
        # Todos os cálculos usam a lista 'partidas_filtradas' recém-criada
        contagem_quadras = Counter(p['campo'] for p in partidas_filtradas)
        if contagem_quadras:
            stats['quadra_mais_utilizada'] = {'nome': contagem_quadras.most_common(1)[0][0], 'partidas': contagem_quadras.most_common(1)[0][1]}

        horarios_por_vagas = defaultdict(int)
        for p in partidas_filtradas:
            horarios_por_vagas[p['horario']] += p['vagas']
        if horarios_por_vagas:
            horario_top = max(horarios_por_vagas.items(), key=lambda item: item[1])
            stats['horario_pico_pessoas'] = {'horario': horario_top[0], 'participantes': horario_top[1]}

        contagem_esportes = Counter(p.get('esporte', 'Não definido') for p in partidas_filtradas)
        if contagem_esportes:
            esporte_top = contagem_esportes.most_common(1)[0]
            stats['esporte_mais_praticado'] = {'nome': esporte_top[0], 'partidas': esporte_top[1]}

        contagem_categoria = Counter(p['categoria'] for p in partidas_filtradas)
        if contagem_categoria:
            categoria_top = contagem_categoria.most_common(1)[0]
            stats['categoria_popular'] = {'nome': categoria_top[0], 'partidas': categoria_top[1]}

        stats['distribuicao_genero'] = [{'genero': g, 'total': t} for g, t in Counter(p['genero'] for p in partidas_filtradas).items()]
        stats['total_usuarios'] = sum(p['vagas'] for p in partidas_filtradas)

    # --- 4. CONTEXTO: Sempre novo ---
    campos_disponiveis = sorted(list(set(info['nome'] for info in campos.values())))
    context = {
        'partidas': partidas_filtradas,
        'campos_disponiveis': campos_disponiveis,
        'selected_campo': selected_campo,
        'selected_data': selected_data_str,
        'stats': stats,
    }
    return render(request, 'pages/relatorio.html', context)


def available_places(request):
    """
    Esta view renderiza a página de locais disponíveis.
    """
    # No futuro, você pode adicionar lógica aqui para buscar dados do banco
    # e enviar para o template através do dicionário 'context'.
    context = {} 
    
    # A linha abaixo é a mais importante: ela renderiza seu template.
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