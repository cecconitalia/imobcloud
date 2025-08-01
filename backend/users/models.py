from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # O modelo de usu\u00E1rio personalizado para a aplica\u00E7\u00E3o.
    # Usando AbstractUser, j\u00E1 temos campos como 'username', 'email' e 'password'.
    # Corrigindo o erro de conflito de acesso reverso com related_name.
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions '
                  'granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
