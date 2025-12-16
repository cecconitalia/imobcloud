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
    
    contrato_display = serializers.CharField(source='contrato.id', read_only=True) 
    imovel_display = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    # URLs para leitura no frontend
    assinatura_locatario_url = serializers.SerializerMethodField()
    assinatura_responsavel_url = serializers.SerializerMethodField()

    class Meta:
        model = Vistoria
        fields = [
            'id', 'contrato', 'tipo', 'tipo_display', 'data_vistoria', 'observacoes', 
            'realizado_por_nome', 'ambientes', 'concluida', 
            'contrato_display', 'imovel_display', 'data_criacao',
            'assinatura_locatario', 'assinatura_locatario_url',
            'assinatura_responsavel', 'assinatura_responsavel_url'
        ]

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

    # =========================================================================
    # CORREÇÃO DO ERRO 400 (BAD REQUEST)
    # Este método intercepta os dados antes da validação.
    # Se o frontend enviar uma string (URL) nos campos de assinatura em vez de um arquivo,
    # nós removemos esse campo dos dados para que o Django ignore (e não tente validar).
    # =========================================================================
    def to_internal_value(self, data):
        # Tenta copiar os dados para torná-los mutáveis (caso seja QueryDict)
        try:
            data = data.copy()
        except AttributeError:
            pass # Se já for dict, segue

        # Campos que podem causar erro se receberem string/URL
        campos_imagem = ['assinatura_locatario', 'assinatura_responsavel']

        for campo in campos_imagem:
            if campo in data:
                valor = data.get(campo)
                # Se o valor for uma string (ex: "http://localhost..."), removemos do payload
                # Isso impede que o serializer tente validar uma URL como se fosse um arquivo binário.
                if isinstance(valor, str):
                    try:
                        del data[campo]
                    except:
                        data.pop(campo, None)
        
        return super().to_internal_value(data)