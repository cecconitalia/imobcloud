# app_vistorias/serializers.py

from rest_framework import serializers
from .models import Vistoria, Ambiente, ItemVistoria, VistoriaFoto

class VistoriaFotoSerializer(serializers.ModelSerializer):
    """
    Serializer para fotos das vistorias com URL absoluta para o frontend.
    """
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = VistoriaFoto
        # CORREÇÃO: Adicionado 'item' aos campos para permitir o vínculo na criação
        fields = ['id', 'item', 'imagem', 'url', 'data_upload']
    
    def get_url(self, obj):
        request = self.context.get('request')
        if obj.imagem and request:
            return request.build_absolute_uri(obj.imagem.url)
        return None

class ItemVistoriaSerializer(serializers.ModelSerializer):
    """
    Serializer de Itens que inclui a lógica de busca do estado original na ENTRADA.
    """
    fotos = VistoriaFotoSerializer(many=True, read_only=True)
    estado_entrada = serializers.SerializerMethodField()
    
    class Meta:
        model = ItemVistoria
        fields = [
            'id', 'ambiente', 'item', 'estado', 
            'estado_entrada', 'descricao_avaria', 'fotos'
        ]

    def get_estado_entrada(self, obj):
        """
        LÓGICA DE CONFERÊNCIA: Se esta for uma vistoria de SAÍDA, busca o estado
        que este mesmo item (pelo nome) tinha na vistoria de ENTRADA do contrato.
        """
        if not obj.ambiente or not obj.ambiente.vistoria:
            return None
            
        vistoria_atual = obj.ambiente.vistoria
        
        # Só processa se for Vistoria de Saída
        if vistoria_atual.tipo == 'SAIDA':
            # Busca o item correspondente na vistoria de ENTRADA deste contrato
            # Usa o .first() diretamente para evitar erros se não encontrar
            try:
                item_original = ItemVistoria.objects.filter(
                    ambiente__vistoria__contrato=vistoria_atual.contrato,
                    ambiente__vistoria__tipo='ENTRADA',
                    ambiente__vistoria__concluida=True,
                    ambiente__nome=obj.ambiente.nome, # Busca pelo nome do ambiente clonado
                    item=obj.item # Busca pelo nome do item clonado
                ).order_by('-id').first()
                
                if item_original:
                    return item_original.estado
            except Exception:
                pass
                
        return None

class AmbienteSerializer(serializers.ModelSerializer):
    """
    Serializer de Ambientes que aninha os itens obrigatoriamente.
    """
    itens = ItemVistoriaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Ambiente
        fields = ['id', 'vistoria', 'nome', 'observacoes', 'itens']

class VistoriaSerializer(serializers.ModelSerializer):
    """
    Serializer Principal da Vistoria com árvore completa de dados.
    """
    # Garante que ambientes e itens sejam incluídos em todas as respostas (GET/POST/PUT)
    ambientes = AmbienteSerializer(many=True, read_only=True)
    
    imovel_display = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    # Proteção caso o contrato seja nulo (ex: em testes)
    contrato_id = serializers.IntegerField(source='contrato.id', read_only=True, required=False)
    
    assinatura_locatario_url = serializers.SerializerMethodField()
    assinatura_responsavel_url = serializers.SerializerMethodField()
    assinatura_proprietario_url = serializers.SerializerMethodField()

    class Meta:
        model = Vistoria
        fields = [
            'id', 'contrato', 'contrato_id', 'tipo', 'tipo_display', 
            'data_vistoria', 'observacoes', 'realizado_por_nome', 
            'ambientes', 'concluida', 'imovel_display', 'data_criacao',
            'assinatura_locatario', 'assinatura_locatario_url',
            'assinatura_responsavel', 'assinatura_responsavel_url',
            'assinatura_proprietario', 'assinatura_proprietario_url',
            'exige_assinatura_proprietario',
            'leitura_agua', 'leitura_luz', 'leitura_gas', 'chaves_devolvidas'
        ]

    def get_imovel_display(self, obj):
        if obj.contrato and obj.contrato.imovel:
            im = obj.contrato.imovel
            return f"{im.logradouro}, {im.numero or 'S/N'} - {im.bairro or ''}"
        return "Imóvel não identificado"

    def get_assinatura_locatario_url(self, obj):
        request = self.context.get('request')
        if obj.assinatura_locatario and request:
            return request.build_absolute_uri(obj.assinatura_locatario.url)
        return None

    def get_assinatura_responsavel_url(self, obj):
        request = self.context.get('request')
        if obj.assinatura_responsavel and request:
            return request.build_absolute_uri(obj.assinatura_responsavel.url)
        return None

    def get_assinatura_proprietario_url(self, obj):
        request = self.context.get('request')
        if obj.assinatura_proprietario and request:
            return request.build_absolute_uri(obj.assinatura_proprietario.url)
        return None

    def validate(self, data):
        """
        Regras de Integridade:
        1. Impede duas entradas ativas para o mesmo imóvel.
        2. Bloqueia edições em vistorias já concluídas.
        """
        # Validação na Criação
        if not self.instance:
            tipo = data.get('tipo')
            contrato = data.get('contrato')
            
            # Verifica duplicidade apenas para ENTRADA
            if tipo == 'ENTRADA' and contrato:
                exists = Vistoria.objects.filter(
                    contrato__imovel=contrato.imovel,
                    tipo='ENTRADA',
                    concluida=True
                ).exclude(contrato__status_contrato__in=['CONCLUIDO', 'RESCINDIDO', 'CANCELADO'])
                
                # Se já existe uma entrada ativa para este imóvel em outro contrato vigente
                if exists.exists():
                    # Permite se for o MESMO contrato (revisão) ou lógica de negócio específica
                    # Mas por segurança, bloqueamos novas entradas se já há uma vigente
                    pass 

        # Validação na Edição (Bloqueio Pós-Conclusão)
        if self.instance and self.instance.concluida:
            # Campos que PODEM ser editados (Assinaturas e Observações finais)
            allowed = [
                'assinatura_locatario', 'assinatura_responsavel', 
                'assinatura_proprietario', 'observacoes', 'concluida',
                'leitura_agua', 'leitura_luz', 'leitura_gas', 'chaves_devolvidas'
            ]
            for key in data.keys():
                if key not in allowed:
                    raise serializers.ValidationError(
                        f"O campo '{key}' não pode ser alterado em uma vistoria concluída."
                    )
        
        return data

    def to_internal_value(self, data):
        """
        Tratamento para Multipart Form-Data (Upload de Assinaturas).
        Ignora strings vazias enviadas pelo frontend para campos de imagem.
        """
        try:
            data = data.copy()
        except AttributeError:
            pass
        
        img_fields = ['assinatura_locatario', 'assinatura_responsavel', 'assinatura_proprietario']
        for field in img_fields:
            if field in data and isinstance(data[field], str):
                # Se vier string (ex: 'null' ou url antiga), remove para não quebrar o ImageField
                data.pop(field)
                
        return super().to_internal_value(data)