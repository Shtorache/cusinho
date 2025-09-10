# login_app/views.py

# ==============================================================================
# IMPORTS (Limp
# ==============================================================================
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Count, Sum
from .models import Campo, Feedback
from .forms import FeedbackForm
import os # CORREÇÃO: Importa a biblioteca 'os'
from django.conf import settings # CORREÇÃO: Importa as configurações do Django


# Imports dos novos modelos e formulários
from .models import Campo, Partida, Profile, Reserva, Feedback
from .forms import UpdateUserForm, UpdateProfileForm, CampoForm, PartidaForm, ReservasForm, FeedbackForm

# Imports do Allauth (para a view de perfil)
from allauth.mfa.models import Authenticator
from allauth.mfa import app_settings as mfa_app_settings


# ==============================================================================
# VIEWS PRINCIPAIS
# ==============================================================================

def mainPage(request):
    """
    Página principal que exibe a tela de boas-vindas.
    Não precisa buscar campos do banco de dados.
    """
    # Se precisar de algum dado para o template, adicione aqui
    context = {}
    return render(request, "pages/main.html", context)


@login_required
def feedPage(request, campo_id):
    """
    Exibe e processa o formulário de feedback para um campo específico.
    """
    # Busca o campo no banco de dados
    campo = get_object_or_404(Campo, pk=campo_id)
    
    # Busca os feedbacks já existentes para este campo
    feedbacks_do_campo = Feedback.objects.filter(campo=campo).order_by('-id')

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Cria o objeto de feedback sem salvar no banco ainda
            novo_feedback = form.save(commit=False)
            # Associa o feedback ao campo e ao usuário logado
            novo_feedback.campo = campo
            novo_feedback.usuario = request.user
            # Agora salva no banco
            novo_feedback.save()
            
            messages.success(request, "Seu feedback foi enviado com sucesso!")
            return redirect('feedPage', campo_id=campo.id)
    else:
        # Se não for POST, cria um formulário em branco
        form = FeedbackForm()

    context = {
        'form': form,
        'campo': campo,
        'feedbacks': feedbacks_do_campo
    }
    return render(request, 'pages/feedPage.html', context)


def campo_detalhes(request, campo_id):
    """
    Exibe os detalhes de um campo específico e suas partidas, com filtros.
    """
    campo = get_object_or_404(Campo, pk=campo_id)
    partidas_queryset = Partida.objects.filter(campo=campo)
    
    categoria = request.GET.get('categoria')
    genero = request.GET.get('genero')
    data = request.GET.get('data')
    
    if categoria and categoria != 'todas':
        partidas_queryset = partidas_queryset.filter(categoria=categoria)
    if genero and genero != 'todos':
        partidas_queryset = partidas_queryset.filter(genero=genero)
    if data:
        partidas_queryset = partidas_queryset.filter(data=data)
    
    # CORREÇÃO: Passa a URL da imagem de capa para o contexto
    # Acessa a URL da imagem diretamente do objeto do modelo
    imagem_capa_url = campo.imagem_capa.url if campo.imagem_capa else ''

    context = {
        'campo': campo,
        'partidas_filtradas': partidas_queryset.order_by('data', 'horario'),
        'imagem_capa_url': imagem_capa_url, # Adicionado o caminho da imagem
    }
    return render(request, "pages/campo_detalhes.html", context)

# Em login_app/views.py

# ... (resto das suas views e imports) ...
from .models import Campo # Garanta que o modelo Campo está importado

@login_required
def listacampos(request):
    """
    Lista todos os campos cadastrados no banco de dados.
    """
    # Busca todos os objetos do modelo Campo
    todos_os_campos = Campo.objects.all()

    context = {
        'campos': todos_os_campos
    }
    return render(request, 'pages/listacampos.html', context)

# ==============================================================================
# VIEWS DE CRIAÇÃO E INTERAÇÃO
# ==============================================================================

@login_required
def criar_partida(request, campo_id):
    campo = get_object_or_404(Campo, pk=campo_id)
    if request.method == 'POST':
        form = PartidaForm(request.POST)
        if form.is_valid():
            partida = form.save(commit=False)
            partida.campo = campo
            partida.save()
            messages.success(request, 'Partida criada com sucesso!')
            return redirect('campo_detalhes', campo_id=campo.id)
    else:
        form = PartidaForm()
    context = {'form': form, 'campo': campo}
    return render(request, 'pages/criar_partida.html', context)


@login_required
def participar_partida(request, partida_id):
    partida = get_object_or_404(Partida, pk=partida_id)
    # Aqui você pode adicionar a lógica para registrar a participação do usuário
    context = {'partida': partida}
    return render(request, 'pages/participar.html', context)


@login_required
def reservar_espaco(request):
    # Lógica para a página de reserva
    context = {}
    return render(request, 'pages/reservar_espaco.html', context)


# ==============================================================================
# VIEWS DE PERFIL E ÁREA RESTRITA
# ==============================================================================

@login_required
def profile(request):
    if request.method == "POST":
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect("perfilUsuario")
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)
    # Lógica do MFA mantida
    # ...
    context = {"user_form": user_form, "profile_form": profile_form}
    return render(request, "pages/profile.html", context)


@staff_member_required
def areaProprietario(request):
    """
    View para proprietários cadastrarem novos campos.
    Agora usa o formulário unificado 'CampoForm'.
    """
    if request.method == "POST":
        form = CampoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Campo cadastrado com sucesso!")
            return redirect("home")
    else:
        form = CampoForm()
    context = {"form": form}
    return render(request, "pages/alugarcamp.html", context)


@staff_member_required
def relatorio_partidas(request):
    """
    Gera um relatório estatístico de partidas buscando dados do banco.
    """
    queryset = Partida.objects.select_related('campo').all()
    
    # Lógica de filtros (pode ser expandida)
    campo_filtro_id = request.GET.get('campo_filtro')
    if campo_filtro_id:
        queryset = queryset.filter(campo_id=campo_filtro_id)
    
    # Estatísticas com o ORM do Django
    stats = {
        'quadra_mais_utilizada': Campo.objects.annotate(num_partidas=Count('partidas')).order_by('-num_partidas').first(),
        'esporte_mais_praticado': Partida.objects.values('esporte').annotate(total=Count('esporte')).order_by('-total').first(),
    }
    
    context = {
        'partidas': queryset,
        'campos_disponiveis': Campo.objects.all(),
        'stats': stats,
    }
    return render(request, 'pages/relatorio.html', context)


# ==============================================================================
# VIEWS ADICIONAIS (PLACEHOLDERS)
# ==============================================================================
# As views abaixo são mantidas, mas você pode querer dar uma funcionalidade real a elas no futuro.

# Em login_app/views.py
import json
from django.urls import reverse
from .models import Campo # Garanta que o modelo Campo está importado

# Em login_app/views.py

def available_places(request):
    esporte_filtrado = request.GET.get('esporte')
    campos_do_banco = Campo.objects.all()

    if esporte_filtrado:
        campos_do_banco = campos_do_banco.filter(tipo_esporte=esporte_filtrado)

    campos_para_mapa = []
    for campo in campos_do_banco:
        # CORREÇÃO: Gera a URL para o arquivo estático da imagem
        caminho_imagem = os.path.join(settings.STATIC_URL, "images", campo.imagem_capa.name)
        
        campos_para_mapa.append({
            'id': campo.id,
            'nome': campo.nome,
            'regiao': campo.bairro.lower().replace(' ', '_').replace('ã', 'a').replace('ç', 'c'),
            'lat': float(campo.latitude), # Acessando diretamente o campo
            'lng': float(campo.longitude), # Acessando diretamente o campo
            'imagens': [caminho_imagem] if campo.imagem_capa else [],
            'url': reverse('campo_detalhes', args=[campo.id])
        })
        
    context = {
        'campos_json': json.dumps(campos_para_mapa)
    }
    return render(request, "pages/available_places.html", context)

def selecao_opcao(request, esporte):
    # Exemplo de lógica: filtrar campos por esporte
    # campo_por_esporte = Campo.objects.filter(tipo_esporte=esporte)
    context = {'esporte': esporte}
    return render(request, 'pages/selecao_opcao.html', context)

def participar_dois(request):
    context = {}
    return render(request, 'pages/participardois.html', context)

# As views loginPage e registerPage foram removidas, pois o django-allauth cuida disso.
# A view fazer_relatorio foi removida e sua funcionalidade unificada em relatorio_partidas.