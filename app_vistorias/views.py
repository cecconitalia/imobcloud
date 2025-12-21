import os
import base64
from io import BytesIO
from PIL import Image
from datetime import date

from rest_framework import viewsets, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse
from django.template import Context, Template
from django.utils import timezone
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

from .models import Vistoria, Ambiente, ItemVistoria, VistoriaFoto
from .serializers import (
    VistoriaSerializer, 
    AmbienteSerializer, 
    ItemVistoriaSerializer, 
    VistoriaFotoSerializer
)

# --- FUNÇÃO AUXILIAR DE OTIMIZAÇÃO DE IMAGEM ---
def optimize_image_to_base64(path, max_size=(1024, 1024), quality=80):
    """
    Lê a imagem, redimensiona mantendo a proporção e retorna em Base64.
    Essencial para não estourar a memória ao gerar PDFs com muitas fotos.
    """
    if not path or not os.path.exists(path):
        return None
    
    try:
        with Image.open(path) as img:
            # Tratamento de transparência para PNG/WEBP
            if img.mode in ('RGBA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, (0, 0), img)
                img = background
            
            # Redimensiona mantendo a proporção (Thumbnail respeita aspect ratio)
            img.thumbnail(max_size)
            
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=quality)
            
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/jpeg;base64,{img_str}"
            
    except Exception as e:
        print(f"Erro ao otimizar imagem {path}: {str(e)}")
        return None

def link_callback(uri, rel):
    """
    Callback para ajudar o xhtml2pdf a encontrar arquivos estáticos e de mídia.
    """
    if os.path.isfile(uri): return uri
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        path = finders.find(uri) or uri
    if not os.path.isfile(path):
        path = path.replace('/', os.sep)
        if not os.path.isfile(path): return None
    return path

# --- VIEWSETS ---

class VistoriaViewSet(viewsets.ModelViewSet):
    serializer_class = VistoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Vistoria.objects.all() 
        
        # Filtro de permissão por Imobiliária (Multi-tenant)
        if hasattr(user, 'imobiliaria') and user.imobiliaria:
             queryset = queryset.filter(contrato__imobiliaria=user.imobiliaria)
        elif hasattr(user, 'perfil') and hasattr(user.perfil, 'imobiliaria') and user.perfil.imobiliaria:
             queryset = queryset.filter(contrato__imobiliaria=user.perfil.imobiliaria)

        # Filtros de Query Params
        contrato_id = self.request.query_params.get('contrato')
        tipo = self.request.query_params.get('tipo')
        search = self.request.query_params.get('search')
        concluida = self.request.query_params.get('concluida')

        if contrato_id: queryset = queryset.filter(contrato_id=contrato_id)
        if tipo: queryset = queryset.filter(tipo=tipo)
        if concluida is not None:
            is_concluida = concluida.lower() == 'true'
            queryset = queryset.filter(concluida=is_concluida)

        if search:
            queryset = queryset.filter(
                Q(observacoes__icontains=search) |
                Q(contrato__id__icontains=search) |
                Q(realizado_por_nome__icontains=search) |
                Q(contrato__imovel__logradouro__icontains=search)
            )
        return queryset.order_by('-data_vistoria', '-id')

    @action(detail=True, methods=['post'], url_path='gerar-saida-da-entrada')
    def gerar_saida_da_entrada(self, request, pk=None):
        """
        Gera uma Vistoria de SAÍDA baseada na estrutura de uma Vistoria de ENTRADA (pk).
        Copia Ambientes e Itens para agilizar a conferência.
        """
        vistoria_entrada = self.get_object()

        if vistoria_entrada.tipo != 'ENTRADA':
            return Response(
                {"error": "A vistoria de origem deve ser do tipo ENTRADA."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Verifica se já existe uma saída em aberto para este contrato
        saida_existente = Vistoria.objects.filter(
            contrato=vistoria_entrada.contrato,
            tipo='SAIDA',
            concluida=False
        ).first()

        if saida_existente:
            return Response(
                {"error": f"Já existe uma vistoria de saída em andamento (ID {saida_existente.id}).", "id": saida_existente.id}, 
                status=status.HTTP_409_CONFLICT
            )

        try:
            # 2. Cria a Vistoria de Saída (Cabeçalho)
            vistoria_saida = Vistoria.objects.create(
                contrato=vistoria_entrada.contrato,
                tipo='SAIDA',
                data_vistoria=request.data.get('data_vistoria', timezone.now().date()),
                realizado_por_nome=request.user.get_full_name() or request.user.username,
                observacoes=f"Gerada automaticamente a partir da Entrada #{vistoria_entrada.id}. Favor conferir o estado atual dos itens.",
                exige_assinatura_proprietario=vistoria_entrada.exige_assinatura_proprietario
            )

            # 3. Clona a estrutura (Ambientes e Itens)
            ambientes_entrada = vistoria_entrada.ambientes.all()
            for amb_ent in ambientes_entrada:
                # Cria Ambiente na Saída
                amb_sai = Ambiente.objects.create(
                    vistoria=vistoria_saida,
                    nome=amb_ent.nome,
                    observacoes=amb_ent.observacoes
                )

                # Cria Itens no Ambiente (Mantendo estado para referência ou resetando)
                # Aqui optamos por manter o estado da entrada como referência inicial
                itens_entrada = amb_ent.itens.all()
                for item_ent in itens_entrada:
                    ItemVistoria.objects.create(
                        ambiente=amb_sai,
                        item=item_ent.item,
                        estado=item_ent.estado, 
                        descricao_avaria="" # Limpa avarias para forçar nova verificação
                    )

            # Retorna os dados da nova vistoria
            serializer = self.get_serializer(vistoria_saida)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Erro ao gerar vistoria de saída: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='gerar-laudo')
    def gerar_laudo(self, request, pk=None):
        try:
            vistoria = self.get_object()
            
            # --- Dados Contextuais ---
            endereco = "Endereço não disponível"
            imobiliaria_data = {
                'nome': "Não Informada",
                'cnpj': "-",
                'telefone': "-",
                'email': "-",
            }
            
            if vistoria.contrato and vistoria.contrato.imovel:
                imovel = vistoria.contrato.imovel
                endereco = f"{imovel.logradouro}, {imovel.numero or 'S/N'}, {imovel.bairro or ''} - {imovel.cidade or ''}/{imovel.estado or ''}"
                
                if vistoria.contrato.imobiliaria:
                    imob = vistoria.contrato.imobiliaria
                    imobiliaria_data['nome'] = imob.nome or "Nome não cadastrado"
                    imobiliaria_data['cnpj'] = imob.cnpj or "-"
                    imobiliaria_data['telefone'] = imob.telefone or "-"
                    imobiliaria_data['email'] = imob.email_contato or "-"
            
            # --- Otimização de Assinaturas ---
            ass_locatario_b64 = None
            if vistoria.assinatura_locatario:
                ass_locatario_b64 = optimize_image_to_base64(vistoria.assinatura_locatario.path, max_size=(300, 100))

            ass_responsavel_b64 = None
            if vistoria.assinatura_responsavel:
                ass_responsavel_b64 = optimize_image_to_base64(vistoria.assinatura_responsavel.path, max_size=(300, 100))

            ass_proprietario_b64 = None
            if vistoria.assinatura_proprietario:
                ass_proprietario_b64 = optimize_image_to_base64(vistoria.assinatura_proprietario.path, max_size=(300, 100))

            # --- Preparação dos Ambientes e Fotos ---
            ambientes_data = []
            db_ambientes = vistoria.ambientes.all().prefetch_related('itens', 'itens__fotos')

            for amb in db_ambientes:
                itens_data = []
                for item in amb.itens.all():
                    fotos_data = []
                    for foto in item.fotos.all():
                        if foto.imagem:
                            # 800x800 é suficiente para PDF A4 e economiza processamento
                            b64 = optimize_image_to_base64(foto.imagem.path, max_size=(800, 800), quality=75)
                            if b64:
                                fotos_data.append(b64)
                    
                    itens_data.append({
                        'item': item.item,
                        'estado': item.estado,
                        'descricao_avaria': item.descricao_avaria,
                        'fotos': fotos_data
                    })
                
                if itens_data: # Só adiciona ambiente se tiver itens
                    ambientes_data.append({
                        'nome': amb.nome,
                        'observacoes': amb.observacoes,
                        'itens': itens_data
                    })

            # ======================================================
            # TEMPLATE HTML (CORREÇÃO DE SINTAXE DE PÁGINA)
            # ======================================================
            html_template_string = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    @page { 
                        size: A4; 
                        margin: 1.5cm;
                        margin-bottom: 2cm;
                        
                        @frame footer_frame {
                            -pdf-frame-content: footerContent;
                            bottom: 0cm;
                            height: 1.5cm;
                            margin-left: 1.5cm;
                            margin-right: 1.5cm;
                        }
                    }
                    body { font-family: Helvetica, sans-serif; font-size: 10pt; color: #2c3e50; line-height: 1.4; }
                    
                    .header-container { border-bottom: 2px solid #2980b9; padding-bottom: 10px; margin-bottom: 20px; }
                    .main-title { font-size: 18pt; font-weight: 700; color: #2980b9; text-transform: uppercase; }
                    .sub-title { font-size: 10pt; color: #7f8c8d; }

                    .section-box { margin-bottom: 20px; }
                    .section-title { 
                        font-size: 11pt; font-weight: 700; color: #fff; 
                        background-color: #34495e; padding: 5px 10px; 
                        margin-bottom: 10px; border-radius: 2px;
                    }

                    .info-table { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
                    .info-table td { padding: 4px; vertical-align: top; }
                    .label { font-weight: bold; color: #555; width: 130px; }
                    
                    /* Ambiente e Itens */
                    .ambiente-section { page-break-inside: avoid; margin-bottom: 15px; border: 1px solid #bdc3c7; border-radius: 4px; overflow: hidden; }
                    .ambiente-header { 
                        background-color: #ecf0f1; padding: 8px; 
                        font-size: 12pt; font-weight: bold; color: #2c3e50;
                        border-bottom: 1px solid #bdc3c7;
                    }
                    .ambiente-obs { padding: 8px; font-style: italic; font-size: 9pt; background: #fff; border-bottom: 1px solid #eee; }

                    .item-row { padding: 10px; border-bottom: 1px solid #eee; background-color: #fff; }
                    .item-row:last-child { border-bottom: none; }
                    
                    .item-title { font-weight: bold; font-size: 10pt; color: #333; }
                    .item-state { float: right; font-weight: bold; font-size: 9pt; padding: 2px 6px; border-radius: 3px; background: #dfe6e9; color: #2d3436; }
                    .item-obs { margin-top: 5px; color: #e74c3c; font-size: 9pt; }

                    /* Fotos */
                    .photos-grid { margin-top: 10px; text-align: left; }
                    .photo-container { display: inline-block; width: 32%; margin-right: 1%; margin-bottom: 5px; vertical-align: top; }
                    .photo-img { width: 100%; height: auto; border: 1px solid #ddd; padding: 2px; }

                    /* Assinaturas */
                    .assinaturas-box { margin-top: 30px; page-break-inside: avoid; }
                    .ass-table { width: 100%; margin-top: 20px; }
                    .ass-cell { text-align: center; width: 33%; vertical-align: bottom; padding: 0 10px; }
                    .ass-img { max-width: 100%; height: 50px; display: block; margin: 0 auto; }
                    .ass-line { border-top: 1px solid #333; margin-top: 5px; padding-top: 5px; font-size: 8pt; font-weight: bold; }
                </style>
            </head>
            <body>
                <div id="footerContent" style="text-align: right; color: #999; font-size: 8pt;">
                    Página <pdf:pagenumber> de <pdf:pagecount>
                </div>

                <div class="header-container">
                    <div class="main-title">Laudo de Vistoria - {{ vistoria.get_tipo_display }}</div>
                    <div class="sub-title">Ref: #{{ vistoria.id }} | Data: {{ vistoria.data_vistoria|date:"d/m/Y" }}</div>
                </div>
                
                <div class="section-box">
                    <div class="section-title">DADOS DO IMÓVEL E CONTRATO</div>
                    <table class="info-table">
                        <tr><td class="label">Imóvel:</td><td>{{ imovel_endereco }}</td></tr>
                        <tr><td class="label">Contrato:</td><td>#{{ vistoria.contrato.id }}</td></tr>
                        <tr><td class="label">Imobiliária:</td><td>{{ imobiliaria.nome }} ({{ imobiliaria.telefone }})</td></tr>
                        <tr><td class="label">Vistoriador:</td><td>{{ vistoria.realizado_por_nome|default:"-" }}</td></tr>
                    </table>
                </div>

                {% if vistoria.observacoes %}
                <div class="section-box">
                    <div class="section-title">OBSERVAÇÕES GERAIS</div>
                    <div style="padding: 10px; background: #f9f9f9; border: 1px solid #eee;">
                        {{ vistoria.observacoes|linebreaksbr }}
                    </div>
                </div>
                {% endif %}

                <div class="section-box">
                    <div class="section-title">DETALHAMENTO DOS AMBIENTES</div>
                    
                    {% for amb in ambientes_data %}
                        <div class="ambiente-section">
                            <div class="ambiente-header">{{ amb.nome }}</div>
                            {% if amb.observacoes %}
                                <div class="ambiente-obs">Obs: {{ amb.observacoes }}</div>
                            {% endif %}

                            {% for item in amb.itens %}
                                <div class="item-row">
                                    <div>
                                        <span class="item-title">{{ item.item }}</span>
                                        <span class="item-state">{{ item.estado }}</span>
                                    </div>
                                    {% if item.descricao_avaria %}
                                        <div class="item-obs">Avarias/Obs: {{ item.descricao_avaria }}</div>
                                    {% endif %}

                                    {% if item.fotos %}
                                        <div class="photos-grid">
                                            {% for foto_b64 in item.fotos %}
                                                <div class="photo-container">
                                                    <img src="{{ foto_b64 }}" class="photo-img">
                                                </div>
                                            {% endfor %}
                                        </div>
                                    {% endif %}
                                </div>
                            {% endfor %}
                        </div>
                    {% empty %}
                        <p style="text-align: center; color: #999;">Nenhum ambiente registrado nesta vistoria.</p>
                    {% endfor %}
                </div>

                <div class="assinaturas-box">
                    <div class="section-title">ASSINATURAS</div>
                    <p style="font-size: 8pt; text-align: justify; margin-bottom: 10px;">
                        As partes declaram ter vistoriado o imóvel e concordam que o presente laudo reflete fielmente o estado de conservação do mesmo.
                    </p>
                    <table class="ass-table">
                        <tr>
                            <td class="ass-cell">
                                {% if ass_responsavel_b64 %}<img src="{{ ass_responsavel_b64 }}" class="ass-img">{% endif %}
                                <div class="ass-line">Vistoriador</div>
                            </td>
                            <td class="ass-cell">
                                {% if ass_locatario_b64 %}<img src="{{ ass_locatario_b64 }}" class="ass-img">{% endif %}
                                <div class="ass-line">Locatário</div>
                            </td>
                            {% if vistoria.exige_assinatura_proprietario %}
                            <td class="ass-cell">
                                {% if ass_proprietario_b64 %}<img src="{{ ass_proprietario_b64 }}" class="ass-img">{% endif %}
                                <div class="ass-line">Proprietário</div>
                            </td>
                            {% endif %}
                        </tr>
                    </table>
                </div>
                
                <div style="text-align: center; font-size: 7pt; color: #ccc; margin-top: 30px;">
                    Gerado digitalmente por ImobCloud em {% now "d/m/Y H:i" %}
                </div>
            </body>
            </html>
            """

            template = Template(html_template_string)
            context = Context({
                'vistoria': vistoria,
                'imovel_endereco': endereco,
                'ambientes_data': ambientes_data, 
                'ass_locatario_b64': ass_locatario_b64,
                'ass_responsavel_b64': ass_responsavel_b64,
                'ass_proprietario_b64': ass_proprietario_b64,
                'imobiliaria': imobiliaria_data
            })
            html_content = template.render(context)
            
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), result, link_callback=link_callback)

            if not pdf.err:
                response = HttpResponse(result.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="Laudo_{vistoria.id}.pdf"'
                return response
            
            return Response({"error": f"Erro PDF: {pdf.err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AmbienteViewSet(viewsets.ModelViewSet):
    serializer_class = AmbienteSerializer
    permission_classes = [IsAuthenticated]
    queryset = Ambiente.objects.all()

class ItemVistoriaViewSet(viewsets.ModelViewSet):
    serializer_class = ItemVistoriaSerializer
    permission_classes = [IsAuthenticated]
    queryset = ItemVistoria.objects.all()

class VistoriaFotoViewSet(viewsets.ModelViewSet):
    serializer_class = VistoriaFotoSerializer
    permission_classes = [IsAuthenticated]
    queryset = VistoriaFoto.objects.all()
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    @action(detail=False, methods=['POST'], url_path='upload-lote')
    def upload_lote(self, request):
        item_id = request.data.get('item')
        fotos = request.FILES.getlist('foto') or request.FILES.getlist('fotos')
        if not item_id or not fotos: return Response({'detail': 'Dados incompletos.'}, status=400)
        try:
            item = ItemVistoria.objects.get(id=item_id)
            res = [VistoriaFoto.objects.create(item=item, imagem=f) for f in fotos]
            return Response(VistoriaFotoSerializer(res, many=True, context={'request':request}).data, status=201)
        except Exception as e: return Response({'detail': str(e)}, status=500)