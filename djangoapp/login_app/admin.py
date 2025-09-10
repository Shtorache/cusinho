# Em login_app/admin.py
from django.contrib import admin
from .models import Campo, Partida, Reserva, Profile, Feedback

# --- (Opcional, mas Recomendado) Melhora a visualização no Admin ---

class PartidaInline(admin.TabularInline):
    """Permite adicionar Partidas diretamente na página de um Campo."""
    model = Partida
    extra = 1  # Mostra 1 formulário extra para adicionar uma nova partida.
    fields = ('titulo', 'data', 'horario', 'esporte', 'vagas')


@admin.register(Campo)
class CampoAdmin(admin.ModelAdmin):
    """Personaliza a exibição do modelo Campo."""
    list_display = ('nome', 'bairro', 'valor_hora')
    list_filter = ('bairro',)
    search_fields = ('nome', 'bairro')
    inlines = [PartidaInline] # Adiciona o formulário de Partidas na página do Campo


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    """Personaliza a exibição do modelo Partida."""
    list_display = ('titulo', 'campo', 'data', 'horario', 'esporte')
    list_filter = ('campo', 'data', 'esporte')
    search_fields = ('titulo',)


# --- Registro dos outros modelos ---
admin.site.register(Reserva)
admin.site.register(Profile)
admin.site.register(Feedback)