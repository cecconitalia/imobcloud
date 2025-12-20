import os
import base64
from io import BytesIO
from PIL import Image

from rest_framework import viewsets, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse
from django.template import Context, Template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

from .models import Vistoria, Ambiente, ItemVistoria, VistoriaFoto
from .serializers import (
    VistoriaSerializer, 
    AmbienteSerializer, 
    ItemVistoriaSerializer, 
    VistoriaFotoSerializer
)

# --- FUNÇÃO AUXILIAR DE OTIMIZAÇÃO ---
def optimize_image_to_base64(path, max_size=(1024, 1024), quality=80):
    """
    Lê a imagem, redimensiona mantendo a proporção e retorna em Base64.
    """
    if not path or not os.path.exists(path):
        return None
    
    try:
        with Image.open(path) as img:
            # Tratamento de transparência
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
        
        if hasattr(user, 'imobiliaria') and user.imobiliaria:
             queryset = queryset.filter(contrato__imobiliaria=user.imobiliaria)
        elif hasattr(user, 'perfil') and hasattr(user.perfil, 'imobiliaria') and user.perfil.imobiliaria:
             queryset = queryset.filter(contrato__imobiliaria=user.perfil.imobiliaria)

        contrato_id = self.request.query_params.get('contrato')
        tipo = self.request.query_params.get('tipo')
        search = self.request.query_params.get('search')

        if contrato_id: queryset = queryset.filter(contrato_id=contrato_id)
        if tipo: queryset = queryset.filter(tipo=tipo)
        if search:
            queryset = queryset.filter(
                Q(observacoes__icontains=search) |
                Q(contrato__id__icontains=search) |
                Q(realizado_por_nome__icontains=search) |
                Q(contrato__imovel__logradouro__icontains=search)
            )
        return queryset.order_by('-data_vistoria')

    @action(detail=True, methods=['get'], url_path='gerar-laudo')
    def gerar_laudo(self, request, pk=None):
        try:
            vistoria = self.get_object()
            
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
            
            # --- DADOS OTIMIZADOS ---
            
            ass_locatario_b64 = None
            if vistoria.assinatura_locatario:
                ass_locatario_b64 = optimize_image_to_base64(vistoria.assinatura_locatario.path, max_size=(250, 80))

            ass_responsavel_b64 = None
            if vistoria.assinatura_responsavel:
                ass_responsavel_b64 = optimize_image_to_base64(vistoria.assinatura_responsavel.path, max_size=(250, 80))

            ass_proprietario_b64 = None
            if vistoria.assinatura_proprietario:
                ass_proprietario_b64 = optimize_image_to_base64(vistoria.assinatura_proprietario.path, max_size=(250, 80))

            ambientes_data = []
            db_ambientes = vistoria.ambientes.all().prefetch_related('itens', 'itens__fotos')

            for amb in db_ambientes:
                itens_data = []
                for item in amb.itens.all():
                    fotos_data = []
                    for foto in item.fotos.all():
                        if foto.imagem:
                            # 1024x1024 para qualidade alta no PDF
                            b64 = optimize_image_to_base64(foto.imagem.path, max_size=(1024, 1024), quality=80)
                            if b64:
                                fotos_data.append(b64)
                    
                    itens_data.append({
                        'item': item.item,
                        'estado': item.estado,
                        'descricao_avaria': item.descricao_avaria,
                        'fotos': fotos_data
                    })
                
                ambientes_data.append({
                    'nome': amb.nome,
                    'observacoes': amb.observacoes,
                    'itens': itens_data
                })

            # ======================================================
            # TEMPLATE HTML (Quebra de página por ambiente)
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
                    }
                    body { font-family: Helvetica, sans-serif; font-size: 10pt; color: #2c3e50; line-height: 1.4; }
                    
                    .main-title { 
                        font-size: 20pt; font-weight: 700; color: #34495e; 
                        margin-bottom: 5px; border-bottom: 2px solid #34495e; 
                        padding-bottom: 5px;
                    }

                    .summary-table { width: 100%; margin-bottom: 15px; border-collapse: collapse; }
                    .summary-table td { padding: 5px 0; font-size: 9pt; }
                    .summary-table tr:nth-child(even) { background-color: #f7f9fc; }
                    .summary-label { font-weight: bold; width: 120px; color: #34495e; }
                    .summary-value { padding-left: 10px; }
                    
                    .imob-info { border: 1px solid #dfe6e9; padding: 10px; margin-bottom: 20px; background-color: #f8f9fa; font-size: 9pt; }
                    .imob-info-title { font-weight: 700; color: #34495e; margin-bottom: 5px; border-bottom: 1px dashed #ccc; padding-bottom: 3px; }
                    
                    .obs-gerais { margin-bottom: 20px; padding: 10px; border: 1px solid #dfe6e9; background-color: #f8f9fa; border-radius: 4px; }
                    .obs-gerais-title { font-weight: bold; color: #34495e; margin-bottom: 5px; font-size: 10pt; }

                    /* ALTERAÇÃO: Força quebra de página antes de cada ambiente */
                    .ambiente-section { 
                        page-break-before: always; 
                        margin-top: 0px;
                    }
                    
                    .ambiente-title { 
                        background-color: #556070; color: white; padding: 8px 12px; 
                        font-size: 14pt; font-weight: 700; margin-bottom: 15px;
                        border-radius: 4px;
                    }

                    .item-container {
                        margin-bottom: 20px;
                        border-bottom: 2px solid #ecf0f1;
                        padding-bottom: 15px;
                        page-break-inside: avoid; /* Tenta não quebrar o item no meio */
                    }

                    .item-header {
                        font-size: 12pt;
                        font-weight: bold;
                        color: #2c3e50;
                        margin-bottom: 5px;
                        background-color: #ecf0f1;
                        padding: 5px;
                    }
                    
                    .item-status { 
                        font-size: 9pt; font-weight: bold; text-transform: uppercase; 
                        float: right; color: #555;
                    }

                    .item-desc {
                        font-size: 10pt; color: #555; margin-bottom: 10px; padding: 0 5px;
                        font-style: italic;
                    }

                    /* Fotos Grandes e sem distorção */
                    .photo-block {
                        text-align: center;
                        margin-bottom: 15px;
                    }
                    
                    .photo-img {
                        width: auto;
                        max-width: 100%;
                        max-height: 400px; /* ~ Metade da página A4 */
                        border: 1px solid #ccc;
                        border-radius: 4px;
                    }

                    /* Assinaturas */
                    .assinaturas-wrapper { margin-top: 40px; page-break-inside: avoid; page-break-before: always; }
                    .table-assinaturas { width: 100%; border-collapse: collapse; }
                    .td-assinatura { text-align: center; vertical-align: top; padding: 0 10px; width: 33%; }
                    .ass-img { height: 45px; width: auto; margin-bottom: 5px; } 
                    .ass-line { border-top: 1px solid #000; padding-top: 5px; font-weight: bold; font-size: 8pt; color: #333; }
                    .ass-placeholder { height: 45px; color: #ccc; font-size: 7pt; display: block; padding-top: 15px; }
                    
                    .page-footer { 
                        position: fixed; bottom: 0; left: 0; right: 0;
                        text-align: center; font-size: 7pt; color: #aaa;
                        border-top: 1px solid #eee; padding-top: 5px;
                    }
                </style>
            </head>
            <body>
                <div class="main-title">LAUDO DE VISTORIA</div>
                
                <div class="imob-info">
                    <div class="imob-info-title">IMOBILIÁRIA RESPONSÁVEL</div>
                    <strong>Nome:</strong> {{ imobiliaria.nome }} <br>
                    <strong>CNPJ:</strong> {{ imobiliaria.cnpj }} &nbsp;|&nbsp; 
                    <strong>Telefone:</strong> {{ imobiliaria.telefone }} &nbsp;|&nbsp;
                    <strong>Email:</strong> {{ imobiliaria.email }}
                </div>

                <table class="summary-table">
                    <tr>
                        <td class="summary-label">Imóvel:</td>
                        <td class="summary-value">{{ imovel_endereco }}</td>
                    </tr>
                    <tr>
                        <td class="summary-label">Tipo:</td>
                        <td class="summary-value">{{ vistoria.get_tipo_display }}</td>
                    </tr>
                    <tr>
                        <td class="summary-label">Data:</td>
                        <td class="summary-value">{{ vistoria.data_vistoria|date:"d/m/Y" }}</td>
                    </tr>
                </table>

                <div class="obs-gerais">
                    <div class="obs-gerais-title">Observações Gerais:</div>
                    <p style="margin: 0; font-style: normal; font-size: 9pt; color: #555;">{{ vistoria.observacoes|default:"Nenhuma observação geral." }}</p>
                </div>

                {% for amb in ambientes_data %}
                    <div class="ambiente-section">
                        <div class="ambiente-title">{{ amb.nome|upper }}</div>
                        {% if amb.observacoes %}
                           <p style="margin: 0 0 15px 5px; font-style: italic; color: #666;">Obs: {{ amb.observacoes }}</p>
                        {% endif %}

                        {% for item in amb.itens %}
                            <div class="item-container">
                                <div class="item-header">
                                    {{ item.item }}
                                    <span class="item-status">ESTADO: {{ item.estado }}</span>
                                </div>
                                <div class="item-desc">
                                    <strong>Detalhes:</strong> {{ item.descricao_avaria|default:"Sem avarias relatadas." }}
                                </div>

                                {% if item.fotos %}
                                    {% for foto_b64 in item.fotos %}
                                        <div class="photo-block">
                                            <img src="{{ foto_b64 }}" class="photo-img">
                                        </div>
                                    {% endfor %}
                                {% endif %}
                            </div>
                        {% endfor %}
                    </div>
                {% endfor %}

                <div class="assinaturas-wrapper">
                    <div class="termos-ciencia">
                        <h3 style="border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-bottom: 10px;">Termo de Ciência</h3>
                        <p style="font-size: 8pt; text-align: justify; margin-bottom: 20px;">
                            As partes declaram que o presente Laudo de Vistoria reflete fielmente o estado de conservação do imóvel na data indicada.
                            As assinaturas digitais aqui coletadas possuem validade legal e comprovam a ciência e concordância com o conteúdo deste documento e suas imagens anexas.
                        </p>
                    </div>

                    <table class="table-assinaturas">
                        <tr>
                            <td class="td-assinatura">
                                {% if ass_responsavel_b64 %}
                                    <img src="{{ ass_responsavel_b64 }}" class="ass-img">
                                {% else %}
                                    <div class="ass-placeholder">(Pendente)</div>
                                {% endif %}
                                <div class="ass-line">Vistoriador</div>
                            </td>
                            
                            <td class="td-assinatura">
                                {% if ass_locatario_b64 %}
                                    <img src="{{ ass_locatario_b64 }}" class="ass-img">
                                {% else %}
                                    <div class="ass-placeholder">(Pendente)</div>
                                {% endif %}
                                <div class="ass-line">Locatário</div>
                            </td>

                            {% if vistoria.exige_assinatura_proprietario %}
                            <td class="td-assinatura">
                                {% if ass_proprietario_b64 %}
                                    <img src="{{ ass_proprietario_b64 }}" class="ass-img">
                                {% else %}
                                    <div class="ass-placeholder">(Pendente)</div>
                                {% endif %}
                                <div class="ass-line">Proprietário</div>
                            </td>
                            {% endif %}
                        </tr>
                    </table>
                </div>
                
                <div class="page-footer">Gerado por ImobCloud</div>
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