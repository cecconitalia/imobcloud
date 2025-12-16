import os
import base64
from io import BytesIO
from PIL import Image  # Necessário para otimização

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

# --- FUNÇÃO AUXILIAR DE OTIMIZAÇÃO (Trata o quadrado preto) ---
def optimize_image_to_base64(path, max_size=(600, 600), quality=70):
    """
    Lê uma imagem, redimensiona, comprime e retorna em Base64 para inserir no PDF.
    Trata a transparência (PNG) colando sobre um fundo branco antes de salvar como JPEG.
    """
    if not path or not os.path.exists(path):
        return None
    
    try:
        with Image.open(path) as img:
            
            # --- CORREÇÃO DA TRANSPARÊNCIA (Resolve o Quadrado Preto) ---
            if img.mode in ('RGBA', 'P'):
                # Cria uma nova imagem branca (RGB) com o mesmo tamanho
                background = Image.new('RGB', img.size, (255, 255, 255))
                # Cola a imagem original na nova imagem, usando a máscara de transparência (Alpha)
                background.paste(img, (0, 0), img)
                img = background
            # --- FIM DA CORREÇÃO ---
            
            # Redimensiona mantendo a proporção (Thumbnail)
            img.thumbnail(max_size)
            
            buffer = BytesIO()
            # Salva como JPEG (Comprimido e otimizado para web/pdf)
            img.save(buffer, format="JPEG", quality=quality)
            
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/jpeg;base64,{img_str}"
            
    except Exception as e:
        print(f"Erro ao otimizar imagem {path}: {str(e)}")
        return None

def link_callback(uri, rel):
    """Auxiliar para xhtml2pdf encontrar arquivos estáticos."""
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
                
                # NOVO: Busca e preenche dados da Imobiliária (Assumindo a estrutura do modelo)
                if vistoria.contrato.imobiliaria:
                    imob = vistoria.contrato.imobiliaria
                    imobiliaria_data['nome'] = imob.nome or "Nome não cadastrado"
                    imobiliaria_data['cnpj'] = imob.cnpj or "-"
                    imobiliaria_data['telefone'] = imob.telefone or "-"
                    imobiliaria_data['email'] = imob.email or "-"
            
            # --- PREPARAÇÃO DE DADOS OTIMIZADOS ---
            
            # 1. Otimizar Assinaturas
            ass_locatario_b64 = None
            if vistoria.assinatura_locatario:
                ass_locatario_b64 = optimize_image_to_base64(vistoria.assinatura_locatario.path, max_size=(250, 80), quality=70)

            ass_responsavel_b64 = None
            if vistoria.assinatura_responsavel:
                ass_responsavel_b64 = optimize_image_to_base64(vistoria.assinatura_responsavel.path, max_size=(250, 80), quality=70)

            # 2. Otimizar Fotos dos Ambientes
            ambientes_data = []
            db_ambientes = vistoria.ambientes.all().prefetch_related('itens', 'itens__fotos')

            for amb in db_ambientes:
                itens_data = []
                for item in amb.itens.all():
                    fotos_data = []
                    for foto in item.fotos.all():
                        if foto.imagem:
                            # Redimensiona para 400x400 (suficiente para grade no PDF) e qualidade 60
                            b64 = optimize_image_to_base64(foto.imagem.path, max_size=(400, 400), quality=60)
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
            # TEMPLATE HTML PROFISSIONAL V4 (Com Grade de Fotos Compacta)
            # ======================================================
            html_template_string = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    @page { 
                        size: A4; 
                        margin: 1cm; 
                    }
                    body { font-family: Helvetica, sans-serif; font-size: 10pt; color: #2c3e50; line-height: 1.4; }
                    
                    /* Título Principal */
                    .main-title { 
                        font-size: 20pt; font-weight: 700; color: #34495e; 
                        margin-bottom: 5px; border-bottom: 2px solid #34495e; 
                        padding-bottom: 5px;
                    }

                    /* Tabela de Resumo (Dados Principais) */
                    .summary-table { width: 100%; margin-bottom: 15px; border-collapse: collapse; }
                    .summary-table td { padding: 5px 0; font-size: 9pt; }
                    .summary-table tr:nth-child(even) { background-color: #f7f9fc; } /* Zebra stripes */
                    .summary-label { font-weight: bold; width: 120px; color: #34495e; }
                    .summary-value { padding-left: 10px; }
                    
                    /* Dados Imobiliária */
                    .imob-info { border: 1px solid #dfe6e9; padding: 10px; margin-bottom: 20px; background-color: #f8f9fa; font-size: 9pt; }
                    .imob-info-title { font-weight: 700; color: #34495e; margin-bottom: 5px; border-bottom: 1px dashed #ccc; padding-bottom: 3px; }
                    
                    /* Observações Gerais */
                    .obs-gerais { margin-bottom: 20px; padding: 10px; border: 1px solid #dfe6e9; background-color: #f8f9fa; border-radius: 4px; }
                    .obs-gerais-title { font-weight: bold; color: #34495e; margin-bottom: 5px; font-size: 10pt; }

                    /* Ambientes */
                    .ambiente-section { page-break-after: avoid; }
                    .ambiente-title { 
                        background-color: #556070; color: white; padding: 6px 10px; 
                        font-size: 12pt; font-weight: 700; margin-top: 15px; margin-bottom: 10px;
                        border-radius: 4px;
                    }

                    /* Itens */
                    .item-block { 
                        margin-bottom: 15px; 
                        padding: 10px; 
                        border: 1px solid #ecf0f1; 
                        page-break-inside: avoid; 
                        border-radius: 4px;
                    }
                    .item-name { font-weight: 600; font-size: 10pt; color: #2c3e50; display: inline-block; width: 70%; }
                    .item-status { 
                        float: right; font-size: 8pt; font-weight: 700; text-transform: uppercase; 
                        padding: 2px 5px; border-radius: 3px; color: white; margin-top: -3px; 
                    }
                    
                    .bg-NOVO { background-color: #27ae60; }
                    .bg-BOM { background-color: #3498db; }
                    .bg-REGULAR { background-color: #f1c40f; color: #333; }
                    .bg-RUIM { background-color: #e74c3c; }
                    .bg-INOPERANTE { background-color: #333; }

                    .obs-item-text { font-style: italic; color: #555; font-size: 9pt; margin-top: 5px; }

                    /* Grade de Fotos OTIMIZADA (3 fotos por linha) */
                    .fotos-table { 
                        width: 100%; 
                        margin-top: 10px; 
                        border-collapse: collapse; 
                        table-layout: fixed; 
                    }
                    .foto-cell { 
                        width: 33.33%; /* 3 por linha */
                        padding: 3px; 
                        text-align: center; 
                        height: 120px; /* Altura fixa para visualização uniforme */
                        vertical-align: top;
                    }
                    .foto-img { 
                        width: 100%; /* Ocupa 100% da célula */
                        height: 110px; /* Altura fixa menor */
                        object-fit: cover; 
                        border: 1px solid #ccc; 
                        border-radius: 4px;
                    }
                    
                    /* TERMOS DE CIÊNCIA */
                    .termos-ciencia { 
                        margin-top: 30px; 
                        padding: 15px; 
                        border: 1px solid #99a3ad;
                        background-color: #ecf0f1;
                        page-break-before: auto; /* Tenta quebrar, mas não força sempre */
                    }
                    .termos-ciencia h3 { 
                        font-size: 11pt; 
                        color: #34495e; 
                        margin: 0 0 10px 0; 
                        text-align: center; 
                        border-bottom: 1px solid #bdc3c7; 
                        padding-bottom: 5px; 
                    }
                    .termos-ciencia p { font-size: 8.5pt; margin-bottom: 10px; }

                    /* ASSINATURAS */
                    .assinaturas-wrapper { margin-top: 40px; page-break-inside: avoid; }
                    .table-assinaturas { width: 100%; border-collapse: collapse; }
                    .td-assinatura { width: 50%; text-align: center; vertical-align: top; padding: 0 40px; }
                    .ass-img { height: 45px; width: auto; margin-bottom: 5px; } 
                    .ass-line { border-top: 1px solid #000; padding-top: 5px; font-weight: bold; font-size: 9pt; color: #333; }
                    .ass-placeholder { height: 45px; color: #ccc; font-size: 8pt; display: block; padding-top: 15px; }
                    
                    /* Rodapé da Página */
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
                        <td class="summary-label">Tipo de Vistoria:</td>
                        <td class="summary-value">{{ vistoria.get_tipo_display }} (Contrato #{{ vistoria.contrato.id }})</td>
                    </tr>
                    <tr>
                        <td class="summary-label">Data da Vistoria:</td>
                        <td class="summary-value">{{ vistoria.data_vistoria|date:"d/m/Y" }}</td>
                    </tr>
                    <tr>
                        <td class="summary-label">Vistoriador:</td>
                        <td class="summary-value">{{ vistoria.realizado_por_nome|default:"Não informado" }}</td>
                    </tr>
                    <tr>
                        <td class="summary-label">Data de Conclusão:</td>
                        <td class="summary-value">{{ vistoria.data_criacao|date:"d/m/Y H:i" }}</td>
                    </tr>
                </table>

                <div class="obs-gerais">
                    <div class="obs-gerais-title">Observações Gerais (Vistoria, Chaves e Acessos):</div>
                    <p style="margin: 0; font-style: normal; font-size: 9pt; color: #555;">{{ vistoria.observacoes|default:"Nenhuma observação geral registrada." }}</p>
                </div>

                {% for amb in ambientes_data %}
                    <div class="ambiente-section">
                        <div class="ambiente-title">{{ amb.nome|upper }}</div>
                        
                        {% if amb.observacoes %}
                           <p style="margin-top: -5px; font-style: italic; color: #666; font-size: 9pt;">Obs. do Ambiente: {{ amb.observacoes }}</p>
                        {% endif %}

                        {% for item in amb.itens %}
                            <div class="item-block">
                                <div class="item-header">
                                    <span class="item-name">{{ item.item }}</span>
                                    <span class="item-status bg-{{ item.estado }}">{{ item.estado }}</span>
                                </div>
                                
                                <div class="obs-item-text">
                                    <strong>Descrição das Avarias:</strong> {% if item.descricao_avaria %}{{ item.descricao_avaria }}{% else %}Estado conforme o esperado / Sem avarias descritas.{% endif %}
                                </div>

                                {% if item.fotos %}
                                    <table class="fotos-table">
                                        <tr>
                                        {% for foto_b64 in item.fotos %}
                                            <td class="foto-cell">
                                                <img src="{{ foto_b64 }}" class="foto-img">
                                            </td>
                                            {% if forloop.counter|divisibleby:3 and not forloop.last %}</tr><tr>{% endif %}
                                        {% endfor %}
                                        </tr>
                                    </table>
                                {% endif %}
                            </div>
                        {% endfor %}
                    </div>
                {% endfor %}

                <div class="termos-ciencia">
                    <h3>Termo de Ciência e Responsabilidade</h3>
                    <p>1. O LOCATÁRIO e o VISTORIADOR declaram, sob as penas da lei, que o presente Laudo de Vistoria reflete fielmente o estado de conservação e uso do imóvel na data de sua realização.</p>
                    <p>2. Quaisquer divergências relativas ao estado do imóvel no momento da entrega (Vistoria de Entrada) deverão ser formalmente comunicadas à Imobiliária em até 72 (setenta e duas) horas após a assinatura deste documento. Após este prazo, o presente Laudo será considerado aceito em sua totalidade, servindo como único documento de referência para futuras comparações.</p>
                    <p>3. As assinaturas digitais coletadas neste documento possuem valor legal, de acordo com o Art. 10, § 2º, da Medida Provisória nº 2.200-2/2001 (ICP-Brasil), e validam a concordância de ambas as partes com o conteúdo deste Laudo.</p>
                </div>

                <div class="assinaturas-wrapper">
                    <table class="table-assinaturas">
                        <tr>
                            <td class="td-assinatura">
                                {% if ass_responsavel_b64 %}
                                    <img src="{{ ass_responsavel_b64 }}" class="ass-img">
                                {% else %}
                                    <div class="ass-placeholder">(Aguardando assinatura digital)</div>
                                {% endif %}
                                <div class="ass-line">Vistoriador / Imobiliária</div>
                            </td>
                            <td class="td-assinatura">
                                {% if ass_locatario_b64 %}
                                    <img src="{{ ass_locatario_b64 }}" class="ass-img">
                                {% else %}
                                    <div class="ass-placeholder">(Aguardando assinatura digital)</div>
                                {% endif %}
                                <div class="ass-line">Locatário / Cliente</div>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div class="page-footer">Documento gerado por ImobCloud - Sistema de Gestão Imobiliária</div>
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

# ViewSets Padrão mantidos inalterados
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