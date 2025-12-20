from rest_framework import serializers
from .models import Vistoria, Ambiente, ItemVistoria, VistoriaFoto

# --- FOTOS ---
class VistoriaFotoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = VistoriaFoto
        fields = ['id', 'imagem', 'url', 'data_upload']
    
    def get_url(self, obj):
        request = self.context.get('request')
        if obj.imagem and request:
            return request.build_absolute_uri(obj.imagem.url)
        return None

# --- ITENS ---
class ItemVistoriaSerializer(serializers.ModelSerializer):
    fotos = VistoriaFotoSerializer(many=True, read_only=True)
    
    class Meta:
        model = ItemVistoria
        fields = ['id', 'ambiente', 'item', 'estado', 'descricao_avaria', 'fotos']

# --- AMBIENTES ---
class AmbienteSerializer(serializers.ModelSerializer):
    itens = ItemVistoriaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Ambiente
        fields = ['id', 'vistoria', 'nome', 'observacoes', 'itens']

# --- VISTORIA (PRINCIPAL) ---
class VistoriaSerializer(serializers.ModelSerializer):
    ambientes = AmbienteSerializer(many=True, read_only=True)
    
    # Campos de exibição (Read Only)
    contrato_display = serializers.CharField(source='contrato.id', read_only=True) 
    imovel_display = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    # URLs para leitura das assinaturas no frontend
    assinatura_locatario_url = serializers.SerializerMethodField()
    assinatura_responsavel_url = serializers.SerializerMethodField()
    assinatura_proprietario_url = serializers.SerializerMethodField()

    class Meta:
        model = Vistoria
        fields = [
            'id', 'contrato', 'tipo', 'tipo_display', 'data_vistoria', 'observacoes', 
            'realizado_por_nome', 'ambientes', 'concluida', 
            'contrato_display', 'imovel_display', 'data_criacao',
            # Campos de Assinatura e Configuração
            'assinatura_locatario', 'assinatura_locatario_url',
            'assinatura_responsavel', 'assinatura_responsavel_url',
            'assinatura_proprietario', 'assinatura_proprietario_url',
            'exige_assinatura_proprietario'
        ]

    # --- Helpers de Exibição ---
    def get_imovel_display(self, obj):
        if obj.contrato and obj.contrato.imovel:
            if obj.contrato.imovel.logradouro:
                return f"{obj.contrato.imovel.logradouro}, {obj.contrato.imovel.numero or 'S/N'}"
            return f"Imóvel #{obj.contrato.imovel.id}"
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

    # --- VALIDAÇÃO DE REGRAS DE NEGÓCIO ---
    def validate(self, data):
        """
        1. Valida o Ciclo Entrada -> Saída (Impedir Entrada sobre Entrada).
        2. Valida Bloqueio de Edição após Conclusão.
        """
        
        # --- REGRA 1: CICLO DE ENTRADA/SAÍDA ---
        # Só verifica se estiver CRIANDO uma vistoria (instance é None)
        if not self.instance:
            tipo_novo = data.get('tipo')
            contrato = data.get('contrato')

            if tipo_novo == 'ENTRADA' and contrato:
                # Busca a última movimentação (Entrada ou Saída) deste IMÓVEL
                # Note que usamos contrato__imovel para pegar vistorias de QUALQUER contrato desse imóvel
                ultima_movimentacao = Vistoria.objects.filter(
                    contrato__imovel=contrato.imovel,
                    tipo__in=['ENTRADA', 'SAIDA']
                ).order_by('-id').first() # Pega a mais recente criada

                if ultima_movimentacao and ultima_movimentacao.tipo == 'ENTRADA':
                    # Se a última foi ENTRADA, significa que não houve SAÍDA ainda.
                    raise serializers.ValidationError({
                        "tipo": (
                            f"Este imóvel já possui uma Vistoria de Entrada ativa (ID #{ultima_movimentacao.id}). "
                            "É necessário realizar a Vistoria de Saída do inquilino anterior antes de iniciar uma nova Entrada."
                        )
                    })

        # --- REGRA 2: BLOQUEIO DE EDIÇÃO (CONCLUÍDA) ---
        if self.instance and self.instance.concluida:
            
            sig_fields = ['assinatura_locatario', 'assinatura_responsavel', 'assinatura_proprietario']
            
            # Bloqueia alteração de assinaturas já existentes
            for sig in sig_fields:
                if sig in data:
                    valor_atual = getattr(self.instance, sig)
                    if valor_atual:
                        raise serializers.ValidationError(
                            f"A vistoria está concluída e a '{sig}' já foi registrada. Não é permitido alterá-la."
                        )

            # Campos permitidos para edição pós-conclusão
            campos_permitidos = [
                'assinatura_locatario', 
                'assinatura_responsavel', 
                'assinatura_proprietario',
                'concluida',            
                'observacoes',          
                'realizado_por_nome',   
                'data_vistoria',        
                'exige_assinatura_proprietario'
            ]
            
            for campo in data.keys():
                if campo not in campos_permitidos:
                    valor_atual = getattr(self.instance, campo, None)
                    valor_novo = data.get(campo)
                    
                    if str(valor_atual) != str(valor_novo):
                        raise serializers.ValidationError(
                            f"Vistoria CONCLUÍDA. O campo '{campo}' não pode ser alterado."
                        )
        
        return data

    # --- CORREÇÃO PARA MULTIPART FORM DATA ---
    def to_internal_value(self, data):
        try:
            data = data.copy()
        except AttributeError:
            pass 

        campos_imagem = ['assinatura_locatario', 'assinatura_responsavel', 'assinatura_proprietario']

        for campo in campos_imagem:
            if campo in data:
                valor = data.get(campo)
                if isinstance(valor, str):
                    try:
                        del data[campo]
                    except:
                        data.pop(campo, None)
        
        return super().to_internal_value(data)