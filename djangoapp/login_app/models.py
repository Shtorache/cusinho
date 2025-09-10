# login_app/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Campo(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    bairro = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255, blank=True)
    imagem_capa = models.ImageField(upload_to='campos_capas/', null=True, blank=True)
    telefone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    valor_hora = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    tipo_esporte = models.CharField(
        max_length=50, 
        choices=[('futebol', 'Futebol'), ('basquete', 'Basquete'), ('volei', 'Vôlei'), ('tenis', 'Tênis')], 
        null=True, blank=True
    )
    def __str__(self): return self.nome

class Partida(models.Model):
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE, related_name='partidas')
    titulo = models.CharField(max_length=200)
    data = models.DateField()
    horario = models.TimeField()
    esporte = models.CharField(max_length=50)
    categoria = models.CharField(max_length=50)
    genero = models.CharField(max_length=50)
    vagas = models.PositiveIntegerField()
    def __str__(self): return f"{self.titulo} em {self.campo.nome}"

class Reserva(models.Model):
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE, related_name='reservas')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    dia = models.DateField()
    inicio = models.TimeField()
    final = models.TimeField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def clean(self):
        overlapping = Reserva.objects.filter(campo=self.campo, dia=self.dia, inicio__lt=self.final, final__gt=self.inicio).exclude(pk=self.pk)
        if overlapping.exists(): raise ValidationError(_("Este horário já está reservado para esta quadra."))

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    img = models.ImageField(default="default.jpg", upload_to="profile_pics")
    def __str__(self): return f"{self.user.username}'s Profile"

class Feedback(models.Model):
    campo = models.ForeignKey(Campo, related_name="avaliacoes", on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, related_name="feedbacks", on_delete=models.CASCADE)
    comentario = models.TextField()
    ESTRELAS_CHOICES = [(1, "★☆☆☆☆"),(2, "★★☆☆☆"),(3, "★★★☆☆"),(4, "★★★★☆"),(5, "★★★★★")]
    avaliacao = models.PositiveSmallIntegerField(default=5, choices=ESTRELAS_CHOICES)
    def __str__(self): return f"Feedback de {self.usuario.username} para {self.campo.nome}"