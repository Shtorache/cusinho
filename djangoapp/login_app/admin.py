from django.contrib import admin
from login_app.models import Coordenada, Reserva,DadosCampo,Feedback
from .models import Profile


# Register your models here.
@admin.register(Coordenada)
class AddressAdmin(admin.ModelAdmin):
    pass


@admin.register(Reserva)
class AdressAdmin(admin.ModelAdmin):
    pass

@admin.register(DadosCampo)
class AddressAdmin(admin.ModelAdmin):
    pass

@admin.register(Feedback)
class AddressAdmin(admin.ModelAdmin):
    pass




admin.site.register(Profile)
