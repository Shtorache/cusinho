from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CoordenadaForm, ReservasForm, UpdateUserForm, UpdateProfileForm, DadosCampoForm,FeedbackForm
from .models import Coordenada, Profile, Reserva, DadosCampo, Feedback
import json
from datetime import datetime
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required

def loginPage(request):
    return render(request, "account/login.html")

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

def available_places(request):
    # Obter parâmetros da URL
    regiao = request.GET.get('regiao', 'centro')
    esporte = request.GET.get('esporte', 'futebol')
    
    context = {
        'regiao': regiao,
        'esporte': esporte,
    }
    return render(request, 'pages/available_places.html', context)




from django.shortcuts import render, get_object_or_404
from django.http import Http404
import json

def campo_detalhes(request, nome_campo):
    # Dicionário com todas as chaves usadas nas URLs
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

    # Região Centro
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

    # Região São José
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

    # Se a chave não existir, retorna 404 em vez de erro de template
    if nome_campo not in campos:
        raise Http404("Campo não encontrado")

    # Monta o contexto para o template genérico de detalhes
    contexto = {
        "campo": campos[nome_campo],
        "nome": campos[nome_campo]["nome"],
        "imagem_capa": request.build_absolute_uri(campos[nome_campo]["imagem_capa"]),
        "partidas_json": json.dumps(campos[nome_campo]["partidas"]),
    }

    return render(request, "pages/campo_detalhes.html", contexto)



@login_required
def participar_partida(request, partida_id):
    return render(request, 'pages/participar.html', {'partida_id': partida_id})

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

def registerPage(request):

    return render(request, "account/signup.html")

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
        profile = Profile.objects.get(user=request.user)
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=profile)
        print(request.user)
        print(profile)
        if user_form.is_valid() and profile_form.is_valid():
            print(profile_form.cleaned_data)
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile is updated successfully")
            return redirect(to="perfilUsuario")
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(
        request,
        "pages/profile.html",
        {"user_form": user_form, "profile_form": profile_form},
    )



@staff_member_required
def fazer_relatorio(request):
    # Buscar todas as reservas
    reservas = Reserva.objects.all().order_by('dia', 'inicio')
    # Calcular o total de todas as reservas
    total_valor = Decimal('0.00')
    for reserva in reservas:
        try:
            total_valor += Decimal(str(reserva.valor_total))
        except Exception as e:
            print(f"Error processing reserva {reserva.id}: {e}")
            print(f"valor_total: {reserva.valor_total}, type: {type(reserva.valor_total)}")
    
    context = {
        'reservas': reservas,
        'total_valor': total_valor,
    }
    
    return render(request, "pages/relatorio.html", context)

# views.py
from django.shortcuts import render

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
            {'nome': 'Thiago', 'posicao': 'Atacante', 'presenca': 'Confirmado'},
            {'nome': 'João', 'posicao': '', 'presenca': 'Não'},
            {'nome': 'Felipe', 'posicao': 'Lateral', 'presenca': 'Confirmado'},
            {'nome': 'Ana', 'posicao': 'Meio-campo', 'presenca': 'Confirmado'},
            {'nome': 'Beatriz', 'posicao': '', 'presenca': 'Não'},
            {'nome': 'Camila', 'posicao': 'Atacante', 'presenca': 'Confirmado'},
            {'nome': 'Daniela', 'posicao': '', 'presenca': 'Não'},
            {'nome': 'Fernanda', 'posicao': 'Zagueira', 'presenca': 'Confirmado'},
            {'nome': 'Gabriela', 'posicao': '', 'presenca': 'Não'},
        ]
    }
    return render(request, 'pages/participar.html', context)


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
            campoAvaliado = query ,
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
        'esporte': esporte.lower(),  # sempre em minúsculo
        'local': local
    })




def reservar_espaco(request):
    return render(request, 'pages/reservar-espaco.html') 

def criar_partida(request):
    return render(request, 'pages/criar_partida.html')