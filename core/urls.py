from django.urls import path
# A importação de UserProfileView foi removida porque não está a ser utilizada.
# from .views import UserProfileView 

# A lista de urlpatterns provavelmente está vazia, o que é correto se não
# tiver nenhum endpoint específico no app core.
urlpatterns = [
    # A linha que usava UserProfileView foi removida.
    # path('profile/', UserProfileView.as_view(), name='user_profile'),
]