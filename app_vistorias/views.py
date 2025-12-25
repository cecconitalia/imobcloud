# C:\wamp64\www\ImobCloud\app_vistorias\views.py

import os
import base64
from io import BytesIO
from PIL import Image, ImageOps
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
from django.core.files.base import ContentFile  # Import necessário para salvar o arquivo
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
def optimize_image_to_base64(path, max_size=(600, 450), quality=70):
    """
    Lê a imagem, corrige orientação (EXIF), redimensiona e retorna em Base64.
    """
    if not path:
        return None
        
    # Garante que o caminho é absoluto para o Windows/Linux
    full_path = path
    if not os.path.isabs(path):
        full_path = os.path.join(settings.MEDIA_ROOT, path)

    if not os.path.exists(full_path):
        print(f"AVISO: Imagem não encontrada no disco: {full_path}")
        return None
    
    try:
        with Image.open(full_path) as img:
            # 1. Corrige orientação baseada no EXIF (comum em fotos de celular)
            img = ImageOps.exif_transpose(img)

            # 2. Converte para RGB se necessário
            if img.mode in ('RGBA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, (0, 0), img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 3. Compatibilidade de redimensionamento (Pillow antigo vs novo)
            if hasattr(Image, 'Resampling'):
                resample_method = Image.Resampling.LANCZOS
            else:
                # Fallback para versões antigas do Pillow
                resample_method = Image.ANTIALIAS

            # 4. Redimensiona (Thumbnail mantém a proporção)
            img.thumbnail(max_size, resample_method)
            
            # 5. Salva em buffer
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=quality, optimize=True)
            
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/jpeg;base64,{img_str}"
            
    except Exception as e:
        print(f"ERRO ao processar imagem {full_path}: {str(e)}")
        return None

def link_callback(uri, rel):
    """
    Callback para ajudar o xhtml2pdf a encontrar arquivos estáticos e de mídia.
    """
    # Se já for um arquivo absoluto
    if os.path.isfile(uri):
        return uri
        
    # Resolve MEDIA_URL
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    # Resolve STATIC_URL
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        path = finders.find(uri) or uri

    # Verifica se o arquivo existe
    if not os.path.isfile(path):
        # Tenta corrigir barras invertidas no Windows
        path = path.replace('/', os.sep)
        if not os.path.isfile(path):
            return None
            
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

    @action(detail=True, methods=['post'], url_path='assinar')
    def assinar(self, request, pk=None):
        """
        Recebe a assinatura em Base64 e salva no campo correspondente (Locatário, Responsável, Proprietário).
        """
        vistoria = self.get_object()
        
        signature_data = request.data.get('assinatura')
        tipo_assinante = request.data.get('tipo_assinante')

        if not signature_data:
            return Response({"error": "Dados da assinatura não fornecidos."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not tipo_assinante:
            return Response({"error": "Tipo de assinante não informado."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decodifica Base64
            if ";base64," in signature_data:
                format, imgstr = signature_data.split(';base64,')
                ext = format.split('/')[-1]
            else:
                imgstr = signature_data
                ext = "png" # Default

            data = base64.b64decode(imgstr)
            file_name = f"assinatura_{tipo_assinante.lower()}_{vistoria.id}_{int(timezone.now().timestamp())}.{ext}"
            
            image_file = ContentFile(data, name=file_name)

            # Mapeia para o campo correto do modelo
            if tipo_assinante == 'LOCATARIO':
                vistoria.assinatura_locatario = image_file
            elif tipo_assinante == 'RESPONSAVEL':
                vistoria.assinatura_responsavel = image_file
            elif tipo_assinante == 'PROPRIETARIO':
                vistoria.assinatura_proprietario = image_file
            else:
                return Response(
                    {"error": f"Tipo de assinante '{tipo_assinante}' inválido. Use LOCATARIO, RESPONSAVEL ou PROPRIETARIO."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            vistoria.save()
            
            return Response(
                {"status": "Assinatura salva com sucesso.", "id": vistoria.id, "tipo": tipo_assinante},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": f"Erro ao processar assinatura: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='gerar-saida-da-entrada')
    def gerar_saida_da_entrada(self, request, pk=None):
        vistoria_entrada = self.get_object()

        if vistoria_entrada.tipo != 'ENTRADA':
            return Response(
                {"error": "A vistoria de origem deve ser do tipo ENTRADA."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

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
            vistoria_saida = Vistoria.objects.create(
                contrato=vistoria_entrada.contrato,
                tipo='SAIDA',
                data_vistoria=request.data.get('data_vistoria', timezone.now().date()),
                realizado_por_nome=request.user.get_full_name() or request.user.username,
                observacoes=f"Gerada automaticamente a partir da Entrada #{vistoria_entrada.id}. Favor conferir o estado atual dos itens.",
                exige_assinatura_proprietario=vistoria_entrada.exige_assinatura_proprietario
            )

            ambientes_entrada = vistoria_entrada.ambientes.all()
            for amb_ent in ambientes_entrada:
                amb_sai = Ambiente.objects.create(
                    vistoria=vistoria_saida,
                    nome=amb_ent.nome,
                    observacoes=amb_ent.observacoes
                )
                itens_entrada = amb_ent.itens.all()
                for item_ent in itens_entrada:
                    ItemVistoria.objects.create(
                        ambiente=amb_sai,
                        item=item_ent.item,
                        estado=item_ent.estado, 
                        descricao_avaria="" 
                    )

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
            
            # --- 1. Dados Contextuais ---
            endereco = "Endereço não disponível"
            bairro_cidade = ""
            imobiliaria_data = {
                'nome': "Não Informada",
                'cnpj': "-",
                'telefone': "-",
                'email': "-",
                'creci': "-"
            }
            
            contrato = vistoria.contrato
            locatario_nome = "Não informado"
            locador_nome = "Não informado"

            if contrato:
                if contrato.inquilino:
                    locatario_nome = contrato.inquilino.nome
                
                if contrato.proprietario:
                    locador_nome = contrato.proprietario.nome

                if contrato.imovel:
                    imovel = contrato.imovel
                    endereco = f"{imovel.logradouro}, {imovel.numero or 'S/N'}"
                    if imovel.complemento:
                        endereco += f" - {imovel.complemento}"
                    bairro_cidade = f"{imovel.bairro or ''} - {imovel.cidade or ''}/{imovel.estado or ''}"
                
                if contrato.imobiliaria:
                    imob = contrato.imobiliaria
                    imobiliaria_data['nome'] = imob.nome or "Imobiliária"
                    imobiliaria_data['cnpj'] = imob.cnpj or ""
                    imobiliaria_data['telefone'] = imob.telefone or ""
                    imobiliaria_data['email'] = imob.email_contato or ""
                    imobiliaria_data['creci'] = imob.creci or ""
            
            # --- 2. Assinaturas ---
            # Max size menor para assinaturas (300x100)
            ass_locatario_b64 = None
            if vistoria.assinatura_locatario:
                ass_locatario_b64 = optimize_image_to_base64(vistoria.assinatura_locatario.name, max_size=(300, 100))

            ass_responsavel_b64 = None
            if vistoria.assinatura_responsavel:
                ass_responsavel_b64 = optimize_image_to_base64(vistoria.assinatura_responsavel.name, max_size=(300, 100))

            ass_proprietario_b64 = None
            if vistoria.assinatura_proprietario:
                ass_proprietario_b64 = optimize_image_to_base64(vistoria.assinatura_proprietario.name, max_size=(300, 100))

            # --- 3. Processamento de Itens e Coleta de Fotos ---
            ambientes_data = []
            todas_fotos_anexo = []
            
            db_ambientes = vistoria.ambientes.all().prefetch_related('itens', 'itens__fotos')

            for amb in db_ambientes:
                itens_data = []
                for item in amb.itens.all():
                    fotos_item = item.fotos.all()
                    count_fotos = 0
                    
                    for foto in fotos_item:
                        if foto.imagem:
                            # Passa foto.imagem.name para garantir que o optimize resolva o path
                            # Tamanho aumentado ligeiramente para qualidade, mas mantendo compressão
                            b64 = optimize_image_to_base64(foto.imagem.name, max_size=(640, 480), quality=75)
                            
                            if b64:
                                todas_fotos_anexo.append({
                                    'ambiente': amb.nome,
                                    'item': item.item,
                                    'image_data': b64,
                                    'index': len(todas_fotos_anexo) + 1
                                })
                                count_fotos += 1
                            else:
                                print(f"Falha ao otimizar foto ID {foto.id}")

                    itens_data.append({
                        'item': item.item,
                        'estado': item.estado,
                        'descricao_avaria': item.descricao_avaria,
                        'qtd_fotos': count_fotos
                    })
                
                if itens_data:
                    ambientes_data.append({
                        'nome': amb.nome,
                        'observacoes': amb.observacoes,
                        'itens': itens_data
                    })

            # --- 4. Paginação das Fotos (4 por página) ---
            fotos_paginadas = []
            chunk_size = 4
            for i in range(0, len(todas_fotos_anexo), chunk_size):
                chunk = todas_fotos_anexo[i:i + chunk_size]
                # Preenche com None se o chunk for menor que 4 (para evitar erro de índice no template)
                while len(chunk) < 4:
                    chunk.append(None)
                fotos_paginadas.append(chunk)

            # --- HTML TEMPLATE ---
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
                            height: 1.0cm;
                            margin-left: 1.5cm;
                            margin-right: 1.5cm;
                        }
                    }
                    
                    body { font-family: Helvetica, sans-serif; font-size: 10pt; color: #333; line-height: 1.4; }
                    
                    /* Cabeçalho */
                    .header { text-align: center; border-bottom: 2px solid #444; padding-bottom: 10px; margin-bottom: 20px; }
                    .header h1 { font-size: 16pt; text-transform: uppercase; margin: 0; color: #2c3e50; }
                    .header p { font-size: 9pt; color: #7f8c8d; margin: 2px 0; }
                    
                    /* Tabelas de Dados */
                    .data-table { width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 9pt; }
                    .data-table th { background-color: #f2f2f2; text-align: left; padding: 6px; border: 1px solid #ccc; font-weight: bold; width: 25%; }
                    .data-table td { border: 1px solid #ccc; padding: 6px; }
                    
                    /* Títulos de Seção */
                    .section-title { 
                        font-size: 11pt; font-weight: bold; color: #fff; 
                        background-color: #2c3e50; padding: 5px 10px; 
                        margin-top: 20px; margin-bottom: 10px; 
                        text-transform: uppercase; border-radius: 3px;
                    }

                    /* Ambientes */
                    .ambiente-box { margin-bottom: 15px; border: 1px solid #ddd; page-break-inside: avoid; }
                    .ambiente-header { background-color: #ecf0f1; padding: 6px 10px; font-weight: bold; border-bottom: 1px solid #ddd; }
                    .item-row { padding: 5px 10px; border-bottom: 1px solid #eee; display: block; }
                    .item-row:last-child { border-bottom: none; }
                    .estado-badge { 
                        float: right; font-size: 8pt; padding: 2px 6px; border-radius: 3px; 
                        font-weight: bold; text-transform: uppercase; border: 1px solid #ccc;
                    }
                    .estado-NOVO { background: #d4edda; color: #155724; border-color: #c3e6cb; }
                    .estado-BOM { background: #cce5ff; color: #004085; border-color: #b8daff; }
                    .estado-REGULAR { background: #fff3cd; color: #856404; border-color: #ffeeba; }
                    .estado-RUIM { background: #f8d7da; color: #721c24; border-color: #f5c6cb; }
                    
                    /* Termos e Texto */
                    .legal-text { font-size: 9pt; text-align: justify; margin: 10px 0; }
                    
                    /* Assinaturas */
                    .assinaturas-wrapper { margin-top: 40px; page-break-inside: avoid; border-top: 2px solid #444; padding-top: 20px; }
                    .assinaturas-table { width: 100%; margin-top: 20px; }
                    .ass-cell { width: 33%; text-align: center; vertical-align: bottom; padding: 0 10px; }
                    .ass-line { border-top: 1px solid #000; margin-top: 5px; padding-top: 2px; font-size: 8pt; font-weight: bold; }
                    .ass-img { height: 50px; max-width: 100%; display: block; margin: 0 auto; }

                    /* PÁGINA DE FOTOS (GRID 2x2) */
                    .photo-page { page-break-before: always; }
                    .photo-grid-table { width: 100%; border-collapse: separate; border-spacing: 10px; }
                    .photo-cell { 
                        width: 50%; 
                        vertical-align: top; 
                        padding: 5px; 
                        border: 1px solid #ddd;
                        background-color: #fff;
                        height: 320px; 
                    }
                    .photo-wrapper {
                        width: 100%;
                        height: 250px; 
                        text-align: center;
                        overflow: hidden;
                        display: block;
                        margin-bottom: 5px;
                        vertical-align: middle;
                    }
                    .photo-img { 
                        max-width: 98%; 
                        max-height: 245px;
                        width: auto;
                        height: auto;
                    }
                    .photo-caption {
                        font-size: 8pt;
                        color: #555;
                        text-align: center;
                        height: 40px;
                        overflow: hidden;
                        background: #f9f9f9;
                        padding: 4px;
                        border-top: 1px solid #eee;
                    }
                </style>
            </head>
            <body>
                <div id="footerContent" style="text-align: right; color: #999; font-size: 8pt; border-top: 1px solid #eee; padding-top: 5px;">
                    Impresso em {% now "d/m/Y H:i" %} - Página <pdf:pagenumber> de <pdf:pagecount>
                </div>

                <div class="header">
                    <h1>Laudo de Vistoria de Imóvel</h1>
                    <p>{{ vistoria.get_tipo_display }} - Ref: #{{ vistoria.id }}</p>
                    <p><strong>{{ imobiliaria.nome }}</strong> - CNPJ: {{ imobiliaria.cnpj }} - CRECI: {{ imobiliaria.creci }}</p>
                </div>

                <div class="section-title">1. Identificação do Imóvel e Partes</div>
                <table class="data-table">
                    <tr>
                        <th>Imóvel:</th>
                        <td colspan="3">{{ endereco }}<br/>{{ bairro_cidade }}</td>
                    </tr>
                    <tr>
                        <th>Locador:</th>
                        <td>{{ locador }}</td>
                        <th>Locatário:</th>
                        <td>{{ locatario }}</td>
                    </tr>
                    <tr>
                        <th>Data Vistoria:</th>
                        <td>{{ vistoria.data_vistoria|date:"d/m/Y" }}</td>
                        <th>Vistoriador:</th>
                        <td>{{ vistoria.realizado_por_nome|default:"-" }}</td>
                    </tr>
                </table>

                <div class="section-title">2. Leituras de Consumo e Chaves</div>
                <table class="data-table">
                    <tr>
                        <th>Água (Hidrômetro)</th>
                        <th>Energia (Medidor)</th>
                        <th>Gás</th>
                    </tr>
                    <tr>
                        <td>{{ vistoria.leitura_agua|default:"Não medido" }}</td>
                        <td>{{ vistoria.leitura_luz|default:"Não medido" }}</td>
                        <td>{{ vistoria.leitura_gas|default:"Não medido" }}</td>
                    </tr>
                </table>
                {% if vistoria.chaves_devolvidas %}
                <div style="background: #f9f9f9; padding: 10px; border: 1px solid #ddd; font-size: 9pt; margin-bottom: 10px;">
                    <strong>Controle de Chaves:</strong><br/>
                    {{ vistoria.chaves_devolvidas|linebreaksbr }}
                </div>
                {% endif %}

                {% if vistoria.observacoes %}
                <div class="section-title">3. Observações Gerais</div>
                <div style="border: 1px solid #ccc; padding: 10px; font-size: 9pt; text-align: justify;">
                    {{ vistoria.observacoes|linebreaksbr }}
                </div>
                {% endif %}

                <div class="section-title">4. Detalhamento dos Ambientes</div>
                <p style="font-size: 8pt; color: #666; margin-bottom: 10px;">
                    Abaixo descreve-se o estado de conservação de cada item. Itens não listados consideram-se inexistentes ou não inspecionados.
                </p>

                {% for amb in ambientes_data %}
                    <div class="ambiente-box">
                        <div class="ambiente-header">{{ amb.nome }} {% if amb.observacoes %}<span style="font-weight:normal; font-size: 8pt;">({{ amb.observacoes }})</span>{% endif %}</div>
                        {% for item in amb.itens %}
                            <div class="item-row">
                                <strong>{{ item.item }}</strong>
                                <span class="estado-badge estado-{{ item.estado }}">{{ item.estado }}</span>
                                {% if item.descricao_avaria %}
                                    <br/><span style="color: #c0392b; font-size: 8pt;">Obs: {{ item.descricao_avaria }}</span>
                                {% endif %}
                                {% if item.qtd_fotos > 0 %}
                                    <span style="float: right; font-size: 7pt; color: #999; margin-right: 5px;">(Ver anexo)</span>
                                {% endif %}
                            </div>
                        {% endfor %}
                    </div>
                {% empty %}
                    <p>Nenhum ambiente cadastrado.</p>
                {% endfor %}

                <div class="section-title">5. Termo de Aceite e Responsabilidade</div>
                <div class="legal-text">
                    <p>
                        As partes declaram ter vistoriado o imóvel acima descrito e concordam que o presente laudo reflete fielmente o estado de conservação do mesmo, servindo como parte integrante do Contrato de Locação.
                    </p>
                    <p>
                        <strong>Prazo de Contestação:</strong> O Locatário dispõe de um prazo de <strong>05 (cinco) dias úteis</strong>, a contar do recebimento das chaves (na Entrada) ou da entrega deste laudo, para contestar por escrito qualquer item que julgue estar em desacordo com a realidade do imóvel. Decorrido este prazo sem manifestação, o laudo será considerado aceito em sua totalidade.
                    </p>
                    <p>
                        Para a Vistoria de Saída, o imóvel deverá ser devolvido nas mesmas condições aqui descritas, ressalvado o desgaste natural decorrente do uso normal.
                    </p>
                </div>

                {% if fotos_paginadas %}
                    <div class="section-title photo-page">6. Anexo Fotográfico</div>
                    <p style="font-size: 9pt;">Registro visual das condições do imóvel.</p>
                    
                    {% for page in fotos_paginadas %}
                        {% if not forloop.first %}<div class="photo-page"></div>{% endif %}
                        
                        <table class="photo-grid-table">
                            <tr>
                                <td class="photo-cell">
                                    {% if page.0 %}
                                    <div class="photo-wrapper"><img src="{{ page.0.image_data }}" class="photo-img"></div>
                                    <div class="photo-caption">
                                        <b>Foto {{ page.0.index }}</b> - {{ page.0.ambiente }}<br/>{{ page.0.item }}
                                    </div>
                                    {% endif %}
                                </td>
                                
                                <td class="photo-cell">
                                    {% if page.1 %}
                                    <div class="photo-wrapper"><img src="{{ page.1.image_data }}" class="photo-img"></div>
                                    <div class="photo-caption">
                                        <b>Foto {{ page.1.index }}</b> - {{ page.1.ambiente }}<br/>{{ page.1.item }}
                                    </div>
                                    {% endif %}
                                </td>
                            </tr>
                            
                            {% if page.2 or page.3 %}
                            <tr>
                                <td class="photo-cell">
                                    {% if page.2 %}
                                    <div class="photo-wrapper"><img src="{{ page.2.image_data }}" class="photo-img"></div>
                                    <div class="photo-caption">
                                        <b>Foto {{ page.2.index }}</b> - {{ page.2.ambiente }}<br/>{{ page.2.item }}
                                    </div>
                                    {% endif %}
                                </td>
                                
                                <td class="photo-cell">
                                    {% if page.3 %}
                                    <div class="photo-wrapper"><img src="{{ page.3.image_data }}" class="photo-img"></div>
                                    <div class="photo-caption">
                                        <b>Foto {{ page.3.index }}</b> - {{ page.3.ambiente }}<br/>{{ page.3.item }}
                                    </div>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endif %}
                        </table>
                        
                        {% if not forloop.last %}<pdf:nextpage />{% endif %}
                    {% endfor %}
                {% endif %}

                <pdf:nextpage /> <div class="assinaturas-wrapper">
                    <div class="section-title">7. Assinaturas</div>
                    <p style="font-size: 9pt; margin-bottom: 20px;">
                        Ao assinar abaixo, as partes validam todo o conteúdo deste documento, incluindo o relatório fotográfico acima.
                    </p>

                    <table class="assinaturas-table">
                        <tr>
                            <td class="ass-cell">
                                {% if ass_locatario_b64 %}<img src="{{ ass_locatario_b64 }}" class="ass-img">{% else %}<br/><br/>{% endif %}
                                <div class="ass-line">Locatário(a)</div>
                            </td>
                            <td class="ass-cell">
                                {% if ass_responsavel_b64 %}<img src="{{ ass_responsavel_b64 }}" class="ass-img">{% else %}<br/><br/>{% endif %}
                                <div class="ass-line">Vistoriador Responsável</div>
                            </td>
                            {% if vistoria.exige_assinatura_proprietario %}
                            <td class="ass-cell">
                                {% if ass_proprietario_b64 %}<img src="{{ ass_proprietario_b64 }}" class="ass-img">{% else %}<br/><br/>{% endif %}
                                <div class="ass-line">Proprietário(a)</div>
                            </td>
                            {% endif %}
                        </tr>
                    </table>
                </div>

            </body>
            </html>
            """

            template = Template(html_template_string)
            context = Context({
                'vistoria': vistoria,
                'endereco': endereco,
                'bairro_cidade': bairro_cidade,
                'locador': locador_nome,
                'locatario': locatario_nome,
                'imobiliaria': imobiliaria_data,
                'ambientes_data': ambientes_data, 
                'ass_locatario_b64': ass_locatario_b64,
                'ass_responsavel_b64': ass_responsavel_b64,
                'ass_proprietario_b64': ass_proprietario_b64,
                'fotos_paginadas': fotos_paginadas
            })
            html_content = template.render(context)
            
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), result, link_callback=link_callback)

            if not pdf.err:
                response = HttpResponse(result.getvalue(), content_type='application/pdf')
                filename = f"Laudo_{vistoria.tipo}_{vistoria.id}.pdf"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
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