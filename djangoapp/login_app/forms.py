# login_app/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Profile, Campo, Reserva, Feedback, Partida

class UpdateUserForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email')

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['img']

class CampoForm(forms.ModelForm):
    class Meta:
        model = Campo
        fields = '__all__' # Inclui todos os campos do modelo Campo

class PartidaForm(forms.ModelForm):
    class Meta:
        model = Partida
        fields = ['titulo', 'data', 'horario', 'esporte', 'categoria', 'genero', 'vagas']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario': forms.TimeInput(attrs={'type': 'time'}),
        }

        # Em login_app/forms.py
from django import forms
from .models import Profile, Campo, Reserva, Feedback, Partida, User



# ADICIONE ESTA CLASSE AO SEU ARQUIVO DE FORMULÁRIOS
class ReservasForm(forms.ModelForm):
    class Meta:
        model = Reserva
        # O campo, usuário e valor_total serão definidos na view
        fields = ['dia', 'inicio', 'final']
        widgets = {
            'dia': forms.SelectDateWidget(),
            'inicio': forms.TimeInput(attrs={"type": "time"}),
            'final': forms.TimeInput(attrs={"type": "time"}),
        }

# Em login_app/forms.py
from django import forms
from .models import Profile, Campo, Reserva, Feedback, Partida, User

# ... (seus outros formulários, como UpdateUserForm, etc.) ...

# ADICIONE ESTA CLASSE AO SEU ARQUIVO DE FORMULÁRIOS
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        # O campo e o usuário serão definidos na view
        fields = ["comentario", "avaliacao"]

# Em login_app/views.py

# ... (resto das suas views e imports) ...

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