from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'eventos'

urlpatterns = [
    # Página inicial (Tabela)
    path('', views.home, name='home'),
    # NOVA ROTA: Intercepta o login e força o uso do nosso template customizado
    path('login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    # CORREÇÃO: Mapeamento exato do nome exigido pelo menu base.html
    path('importar/', views.importar_tabela_view, name='importar_tabela'),
    
    # Endpoints de requisição assíncrona
    path('ajax/eventos/', views.eventos_ajax, name='eventos_ajax'),
    path('evento/<int:evento_id>/modal/', views.evento_detail_modal, name='evento_detail_modal'),

    # Rotas tradicionais legadas
    path('evento/<int:evento_id>/', views.evento_detail, name='evento_detail'),
    path('evento/<int:evento_id>/situacoes/', views.atualizar_situacoes, name='atualizar_situacoes'),
]
