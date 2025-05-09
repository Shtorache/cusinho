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




def campo_detalhes(request, nome_campo):
    # Dicionário com informações dos campos
    campos = {
        "arena_flamengo": {
            "nome": "Arena Flamengo",
            "imagem_capa": "/static/images/arena_flamengo1.jpg",
            "partidas": [
                {
                    "id": 1,
                    "titulo": "Flamengo vs Vasco",
                    "data": "2025-04-10",
                    "horario": "18:00",
                    "categoria": "adulto",
                    "genero": "masculino",
                    "vagas": 5
                },
                {
                    "id": 2,
                    "titulo": "Amistoso Feminino",
                    "data": "2025-04-12",
                    "horario": "15:00",
                    "categoria": "adulto",
                    "genero": "feminino",
                    "vagas": 8
                },
                # Mais partidas...
            ]
        },
        # Outros campos...
    }

    if nome_campo not in campos:
        return render(request, "pages/erro.html", {"mensagem": "Campo não encontrado!"})

    contexto = {
        "campo": campos[nome_campo],
        "nome": campos[nome_campo]["nome"],
        "imagem_capa": request.build_absolute_uri(campos[nome_campo]["imagem_capa"]),
        "partidas_json": json.dumps(campos[nome_campo]["partidas"])
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
def participar_partida(request, partida_id):
    # Aqui você buscaria os dados da partida no banco de dados
    # Estou usando dados estáticos como exemplo
    context = {
        'esporte': 'Futebol',  # Substitua por dados reais
        'local': 'Arena Flamengo',  # Substitua por dados reais
        'jogadores': [
            {'nome': 'Jeff', 'posicao': 'Goleiro', 'presenca': 'Confirmado'},
            {'nome': 'Outro Jeff', 'posicao': 'Lateral', 'presenca': 'Confirmado'},
            {'nome': 'Cauã', 'posicao': '', 'presenca': 'Não'}
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