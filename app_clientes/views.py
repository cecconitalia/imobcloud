# C:\wamp64\www\ImobCloud\app_clientes\views.py
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import Cliente, Visita, Atividade, Oportunidade, Tarefa
from .serializers import ClienteSerializer, VisitaSerializer, AtividadeSerializer, OportunidadeSerializer, TarefaSerializer
from app_imoveis.models import Imovel
from core.models import PerfilUsuario
from .utils import agendar_tarefa_no_calendario

User = get_user_model()

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome_completo', 'cpf_cnpj', 'email']

    def get_queryset(self):
        base_queryset = Cliente.objects.filter(ativo=True)
        if self.request.user.is_superuser:
            return base_queryset.all()
        elif self.request.tenant:
            return base_queryset.filter(imobiliaria=self.request.tenant)
        return Cliente.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            if 'imobiliaria' in self.request.data:
                imobiliaria_id = self.request.data['imobiliaria']
                imobiliaria_obj = get_object_or_404(self.request.tenant._meta.model, pk=imobiliaria_id)
                serializer.save(imobiliaria=imobiliaria_obj)
            else:
                raise Exception("Para superusuário, a imobiliária é obrigatória.")
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR]:
            serializer.save(imobiliaria=self.request.tenant)
        else:
            raise Exception("Não foi possível associar o cliente a uma imobiliária. Tenant não identificado ou sem permissão.")


    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR] and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar este cliente.")

    def perform_destroy(self, instance):
        if self.request.user.is_superuser or (hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR] and instance.imobiliaria == self.request.tenant):
            instance.ativo = False
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise Exception("Você não tem permissão para inativar este cliente.")

    @action(detail=True, methods=['get'])
    def atividades(self, request, pk=None):
        cliente = self.get_object()
        atividades = cliente.atividades.all()
        serializer = AtividadeSerializer(atividades, many=True)
        return Response(serializer.data)


class VisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.all()
    serializer_class = VisitaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Visita.objects.all()
        elif self.request.tenant:
            return Visita.objects.filter(imobiliaria=self.request.tenant)
        return Visita.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            imovel_id = self.request.data.get('imovel')
            cliente_id = self.request.data.get('cliente')
            imovel = get_object_or_404(Imovel, pk=imovel_id)
            cliente = get_object_or_404(Cliente, pk=cliente_id)
            if 'imobiliaria' in self.request.data:
                imobiliaria_obj = get_object_or_404(self.request.tenant._meta.model, pk=self.request.data['imobiliaria'])
                serializer.save(imobiliaria=imobiliaria_obj, cliente=cliente, imovel=imovel)
            else:
                raise Exception("Para superusuário, a imobiliária é obrigatória.")
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR]:
            imovel_id = self.request.data.get('imovel')
            cliente_id = self.request.data.get('cliente')
            imovel = get_object_or_404(Imovel, pk=imovel_id, imobiliaria=self.request.tenant)
            cliente = get_object_or_404(Cliente, pk=cliente_id, imobiliaria=self.request.tenant)
            serializer.save(imobiliaria=self.request.tenant, cliente=cliente, imovel=imovel)
        else:
            raise Exception("Não foi possível associar a visita. Tenant não identificado ou inválido.")

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR] and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar esta visita.")

    def perform_destroy(self, instance):
        if self.request.user.is_superuser:
            instance.delete()
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR] and instance.imobiliaria == self.request.tenant:
            instance.delete()
        else:
            raise Exception("Você não tem permissão para excluir esta visita.")


class AtividadeViewSet(viewsets.ModelViewSet):
    queryset = Atividade.objects.all()
    serializer_class = AtividadeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Atividade.objects.all()
        elif hasattr(user, 'perfil') and user.perfil.imobiliaria:
            return Atividade.objects.filter(cliente__imobiliaria=user.perfil.imobiliaria)
        return Atividade.objects.none()

    def perform_create(self, serializer):
        cliente_id = self.request.data.get('cliente')
        cliente = get_object_or_404(Cliente, pk=cliente_id)

        if not (self.request.user.is_superuser or cliente.imobiliaria == self.request.tenant):
            raise PermissionError("Você não tem permissão para adicionar atividades a este cliente.")

        serializer.save(cliente=cliente, registrado_por=self.request.user)


class OportunidadeViewSet(viewsets.ModelViewSet):
    queryset = Oportunidade.objects.all()
    serializer_class = OportunidadeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Oportunidade.objects.all()
        elif self.request.tenant:
            if hasattr(user, 'perfil'):
                if user.perfil.cargo == PerfilUsuario.Cargo.ADMIN:
                    return Oportunidade.objects.filter(imobiliaria=self.request.tenant)
                elif user.perfil.cargo == PerfilUsuario.Cargo.CORRETOR:
                    return Oportunidade.objects.filter(imobiliaria=self.request.tenant, responsavel=user)
            return Oportunidade.objects.none()

        return Oportunidade.objects.none()

    def perform_create(self, serializer):
        if not self.request.tenant:
             raise PermissionError("Apenas utilizadores associados a uma imobiliária podem criar oportunidades.")
        serializer.save(imobiliaria=self.request.tenant, responsavel=self.request.user)
    
    def partial_update(self, request, *args, **kwargs):
        oportunidade = self.get_object()
        fase_anterior = oportunidade.get_fase_display()
        fase_nova_key = request.data.get('fase')

        response = super().partial_update(request, *args, **kwargs)

        if fase_nova_key and fase_nova_key != oportunidade.fase:
            oportunidade.refresh_from_db()
            fase_nova = oportunidade.get_fase_display()
            
            descricao = f"Oportunidade '{oportunidade.titulo}' movida da fase '{fase_anterior}' para '{fase_nova}'."
            Atividade.objects.create(
                cliente=oportunidade.cliente,
                tipo='NOTA',
                descricao=descricao,
                registrado_por=request.user
            )
        
        return response

    @action(detail=True, methods=['post'], url_path='transferir')
    def transferir_responsavel(self, request, pk=None):
        oportunidade = self.get_object()
        user = request.user
        
        if not (user.is_superuser or (hasattr(user, 'perfil') and user.perfil.cargo == PerfilUsuario.Cargo.ADMIN) or (oportunidade.responsavel == user)):
            return Response(
                {"detail": "Você não tem permissão para transferir esta oportunidade."},
                status=status.HTTP_403_FORBIDDEN
            )

        novo_corretor_id = request.data.get('novo_corretor')
        if not novo_corretor_id:
            return Response(
                {"detail": "ID do novo corretor é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            novo_corretor = User.objects.get(pk=novo_corretor_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Novo corretor não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        corretor_anterior_nome = oportunidade.responsavel.first_name if oportunidade.responsavel else 'N/A'
        corretor_anterior_username = oportunidade.responsavel.username if oportunidade.responsavel else 'N/A'
        
        oportunidade.responsavel = novo_corretor
        oportunidade.save(update_fields=['responsavel'])
        
        descricao = f"Oportunidade '{oportunidade.titulo}' transferida de '{corretor_anterior_nome}' ({corretor_anterior_username}) para '{novo_corretor.first_name}' ({novo_corretor.username})."
        Atividade.objects.create(
            cliente=oportunidade.cliente,
            tipo='NOTA',
            descricao=descricao,
            registrado_por=user
        )

        return Response(
            {"detail": "Oportunidade transferida com sucesso."},
            status=status.HTTP_200_OK
        )


class TarefaViewSet(viewsets.ModelViewSet):
    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        oportunidade_id = self.kwargs['oportunidade_pk']
        return Tarefa.objects.filter(oportunidade_id=oportunidade_id)

    def perform_create(self, serializer):
        oportunidade = get_object_or_404(Oportunidade, pk=self.kwargs['oportunidade_pk'])
        
        user = self.request.user
        if not (user.is_superuser or (hasattr(user, 'perfil') and user.perfil.cargo == PerfilUsuario.Cargo.ADMIN) or (oportunidade.responsavel == user)):
            raise PermissionError("Você não tem permissão para adicionar tarefas a esta oportunidade.")
        
        tarefa = serializer.save(oportunidade=oportunidade, responsavel=self.request.user)
        
        descricao = f"Nova tarefa adicionada: '{tarefa.descricao}'. Prazo: {tarefa.data_conclusao}."
        Atividade.objects.create(
            cliente=oportunidade.cliente,
            tipo='TAREFA',
            descricao=descricao,
            registrado_por=self.request.user
        )

class MinhasTarefasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        
        if user.is_superuser:
            tarefas = Tarefa.objects.filter(concluida=False)
        else:
            tarefas = Tarefa.objects.filter(responsavel=user, concluida=False)
        
        serializer = TarefaSerializer(tarefas, many=True)
        return Response(serializer.data)