"""
CALCULADORA DAS WEB - Backend Flask
Versão 3.0 Web - OFICIAL
"""

from flask import Flask, render_template, request, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
import os
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from decimal import Decimal, ROUND_HALF_UP
import zipfile
import tempfile
import shutil
import io

# ReportLab para geração de PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

# ============================================================================
# TABELAS DO SIMPLES NACIONAL
# ============================================================================

TABELAS_SIMPLES = {
    'ANEXO_I': [
        {'limite': Decimal('180000.00'), 'aliquota': Decimal('0.04'), 'deducao': Decimal('0.00')},
        {'limite': Decimal('360000.00'), 'aliquota': Decimal('0.073'), 'deducao': Decimal('5940.00')},
        {'limite': Decimal('720000.00'), 'aliquota': Decimal('0.095'), 'deducao': Decimal('13860.00')},
        {'limite': Decimal('1800000.00'), 'aliquota': Decimal('0.107'), 'deducao': Decimal('22500.00')},
        {'limite': Decimal('3600000.00'), 'aliquota': Decimal('0.143'), 'deducao': Decimal('87300.00')},
        {'limite': Decimal('4800000.00'), 'aliquota': Decimal('0.19'), 'deducao': Decimal('378000.00')},
    ],
    'ANEXO_II': [
        {'limite': Decimal('180000.00'), 'aliquota': Decimal('0.045'), 'deducao': Decimal('0.00')},
        {'limite': Decimal('360000.00'), 'aliquota': Decimal('0.078'), 'deducao': Decimal('5940.00')},
        {'limite': Decimal('720000.00'), 'aliquota': Decimal('0.10'), 'deducao': Decimal('13860.00')},
        {'limite': Decimal('1800000.00'), 'aliquota': Decimal('0.112'), 'deducao': Decimal('22500.00')},
        {'limite': Decimal('3600000.00'), 'aliquota': Decimal('0.147'), 'deducao': Decimal('85500.00')},
        {'limite': Decimal('4800000.00'), 'aliquota': Decimal('0.30'), 'deducao': Decimal('720000.00')},
    ],
    'ANEXO_III': [
        {'limite': Decimal('180000.00'), 'aliquota': Decimal('0.06'), 'deducao': Decimal('0.00')},
        {'limite': Decimal('360000.00'), 'aliquota': Decimal('0.112'), 'deducao': Decimal('9360.00')},
        {'limite': Decimal('720000.00'), 'aliquota': Decimal('0.135'), 'deducao': Decimal('17640.00')},
        {'limite': Decimal('1800000.00'), 'aliquota': Decimal('0.16'), 'deducao': Decimal('35640.00')},
        {'limite': Decimal('3600000.00'), 'aliquota': Decimal('0.21'), 'deducao': Decimal('125640.00')},
        {'limite': Decimal('4800000.00'), 'aliquota': Decimal('0.33'), 'deducao': Decimal('648000.00')},
    ],
    'ANEXO_IV': [
        {'limite': Decimal('180000.00'), 'aliquota': Decimal('0.045'), 'deducao': Decimal('0.00')},
        {'limite': Decimal('360000.00'), 'aliquota': Decimal('0.09'), 'deducao': Decimal('8100.00')},
        {'limite': Decimal('720000.00'), 'aliquota': Decimal('0.102'), 'deducao': Decimal('12420.00')},
        {'limite': Decimal('1800000.00'), 'aliquota': Decimal('0.14'), 'deducao': Decimal('39780.00')},
        {'limite': Decimal('3600000.00'), 'aliquota': Decimal('0.22'), 'deducao': Decimal('183780.00')},
        {'limite': Decimal('4800000.00'), 'aliquota': Decimal('0.33'), 'deducao': Decimal('828000.00')},
    ],
    'ANEXO_V': [
        {'limite': Decimal('180000.00'), 'aliquota': Decimal('0.155'), 'deducao': Decimal('0.00')},
        {'limite': Decimal('360000.00'), 'aliquota': Decimal('0.18'), 'deducao': Decimal('4500.00')},
        {'limite': Decimal('720000.00'), 'aliquota': Decimal('0.195'), 'deducao': Decimal('9900.00')},
        {'limite': Decimal('1800000.00'), 'aliquota': Decimal('0.205'), 'deducao': Decimal('17100.00')},
        {'limite': Decimal('3600000.00'), 'aliquota': Decimal('0.23'), 'deducao': Decimal('62100.00')},
        {'limite': Decimal('4800000.00'), 'aliquota': Decimal('0.305'), 'deducao': Decimal('540000.00')},
    ],
}

CFOPS_VENDAS = {
    '5101','5102','5103','5104','5105','5106','5109','5110','5111','5112','5113','5114','5115',
    '5116','5117','5118','5119','5120','5122','5123','5124','5125','5401','5402','5403','5405',
    '5653','5654','5655','5656','5667',
    '6101','6102','6103','6104','6105','6106','6107','6108','6109','6110','6111','6112','6113',
    '6114','6115','6116','6117','6118','6119','6120','6122','6123','6124','6125','6401','6402',
    '6403','6404','6653','6654','6655','6656','6667'
}

CFOPS_DEVOLUCOES = {
    '1201','1202','1203','1204','1208','1209','1410','1411','1503','1504',
    '2201','2202','2203','2204','2208','2209','2410','2411','2503','2504'
}

# ============================================================================
# FUNÇÕES DE PROCESSAMENTO
# ============================================================================

def calcular_aliquota_efetiva(rbt12: Decimal, anexo: str) -> Tuple[Decimal, Decimal]:
    tabela = TABELAS_SIMPLES[anexo]
    for faixa in tabela:
        if rbt12 <= faixa['limite']:
            aliquota = faixa['aliquota']
            deducao = faixa['deducao']
            aliquota_efetiva = ((rbt12 * aliquota) - deducao) / rbt12
            return max(aliquota_efetiva, Decimal('0')), deducao
    return Decimal('0'), Decimal('0')

def formatar_br(valor: Decimal) -> str:
    valor = valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    texto = f"{valor:,.2f}"
    return texto.replace(',', 'X').replace('.', ',').replace('X', '.')

def verificar_nota_cancelada(root, ns: dict) -> bool:
    infProt = root.find('.//nfe:infProt', ns)
    if infProt is not None:
        cStat = infProt.find('nfe:cStat', ns)
        if cStat is not None and cStat.text == '101':
            return True
    eventos = root.findall('.//nfe:procEventoNFe', ns)
    for evento in eventos:
        tpEvento = evento.find('.//nfe:tpEvento', ns)
        if tpEvento is not None and tpEvento.text == '110111':
            cStat_evento = evento.find('.//nfe:cStat', ns)
            if cStat_evento is not None and cStat_evento.text in ['135', '155']:
                return True
    return False

def processar_xml(caminho: str) -> Optional[Dict]:
    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
    try:
        tree = ET.parse(caminho)
        root = tree.getroot()
        if verificar_nota_cancelada(root, ns):
            return None
        infNFe = root.find('.//nfe:infNFe', ns)
        if infNFe is None:
            return None
        chave = infNFe.attrib.get('Id', '').replace('NFe', '')
        if len(chave) != 44:
            return None
        ide = root.find('.//nfe:ide', ns)
        if ide is None:
            return None
        _dhEmi = ide.find('nfe:dhEmi', ns)
        dhEmi = _dhEmi if _dhEmi is not None else ide.find('nfe:dEmi', ns)
        if dhEmi is None:
            return None
        data_texto = dhEmi.text
        if 'T' in data_texto:
            data = datetime.strptime(data_texto[:19], '%Y-%m-%dT%H:%M:%S')
        else:
            data = datetime.strptime(data_texto[:10], '%Y-%m-%d')
        nNF = ide.find('nfe:nNF', ns)
        if nNF is None:
            return None
        serie_elem = ide.find('nfe:serie', ns)
        serie = serie_elem.text if serie_elem is not None else '0'
        itens_validos = []
        for det in root.findall('.//nfe:det', ns):
            prod = det.find('nfe:prod', ns)
            if prod is None:
                continue
            cfop_elem = prod.find('nfe:CFOP', ns)
            vProd_elem = prod.find('nfe:vProd', ns)
            if cfop_elem is None or vProd_elem is None:
                continue
            cfop = cfop_elem.text.replace('.', '')
            valor_item = Decimal(vProd_elem.text)
            vFrete_elem = prod.find('nfe:vFrete', ns)
            if vFrete_elem is not None and vFrete_elem.text:
                valor_item += Decimal(vFrete_elem.text)
            vOutro_elem = prod.find('nfe:vOutro', ns)
            if vOutro_elem is not None and vOutro_elem.text:
                valor_item += Decimal(vOutro_elem.text)
            tipo = None
            if cfop in CFOPS_VENDAS:
                tipo = 'V'
            elif cfop in CFOPS_DEVOLUCOES:
                tipo = 'D'
            if tipo:
                itens_validos.append({'cfop': cfop, 'valor': valor_item, 'tipo': tipo})
        if not itens_validos:
            return None
        return {'chave': chave, 'data': data, 'numero': nNF.text, 'serie': serie, 'itens': itens_validos}
    except Exception as e:
        print(f"[ERRO] {caminho}: {e}")
        return None

# ============================================================================
# GERAÇÃO DE PDF
# ============================================================================

def gerar_pdf(dados: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    COR_PRINCIPAL = colors.HexColor('#667eea')
    COR_ESCURA = colors.HexColor('#1a1a2e')
    COR_CINZA = colors.HexColor('#f8f9fa')
    COR_VERDE = colors.HexColor('#10b981')
    COR_VERMELHO = colors.HexColor('#ef4444')

    style_titulo = ParagraphStyle('Titulo', parent=styles['Normal'],
        fontSize=22, fontName='Helvetica-Bold',
        textColor=COR_PRINCIPAL, alignment=TA_LEFT, spaceAfter=4)
    style_subtitulo = ParagraphStyle('SubTitulo', parent=styles['Normal'],
        fontSize=10, fontName='Helvetica',
        textColor=colors.HexColor('#666666'), alignment=TA_LEFT, spaceAfter=2)
    style_secao = ParagraphStyle('Secao', parent=styles['Normal'],
        fontSize=12, fontName='Helvetica-Bold',
        textColor=COR_ESCURA, spaceBefore=16, spaceAfter=8)
    style_label = ParagraphStyle('Label', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#888888'))
    style_valor = ParagraphStyle('Valor', parent=styles['Normal'],
        fontSize=14, fontName='Helvetica-Bold',
        textColor=COR_ESCURA)
    style_das = ParagraphStyle('DAS', parent=styles['Normal'],
        fontSize=28, fontName='Helvetica-Bold',
        textColor=COR_PRINCIPAL, alignment=TA_CENTER)
    style_rodape = ParagraphStyle('Rodape', parent=styles['Normal'],
        fontSize=8, fontName='Helvetica',
        textColor=colors.HexColor('#aaaaaa'), alignment=TA_CENTER)

    story = []

    # Cabeçalho
    story.append(Paragraph("ECCONOMIZE", style_titulo))
    story.append(Paragraph("Calculadora DAS Profissional - Simples Nacional", style_subtitulo))
    story.append(HRFlowable(width="100%", thickness=2, color=COR_PRINCIPAL, spaceAfter=12))

    # Info período
    periodo_data = [
        ['Período de Referência', 'Anexo', 'Gerado em'],
        [
            dados.get('periodo', '-'),
            dados.get('anexo', '-').replace('_', ' '),
            datetime.now().strftime('%d/%m/%Y %H:%M')
        ]
    ]
    t_periodo = Table(periodo_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
    t_periodo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COR_CINZA),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#888888')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,1), 11),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,1), [colors.white]),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_periodo)
    story.append(Spacer(1, 16))

    # Stats notas
    story.append(Paragraph("Resumo dos Arquivos", style_secao))
    stats = dados.get('stats', {})
    stats_data = [
        ['Total de XMLs', 'Notas Válidas', 'Canceladas', 'Duplicadas'],
        [
            str(stats.get('total_arquivos', 0)),
            str(stats.get('notas_validas', 0)),
            str(stats.get('canceladas', 0)),
            str(stats.get('duplicadas', 0)),
        ]
    ]
    t_stats = Table(stats_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    t_stats.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COR_CINZA),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#888888')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,1), 16),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_stats)
    story.append(Spacer(1, 16))

    # Valor DAS em destaque
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#dddddd'), spaceAfter=12))
    story.append(Paragraph("Valor do DAS a Recolher", style_secao))

    das_table_data = [
        [
            Paragraph("VALOR DO DAS", ParagraphStyle('x', parent=styles['Normal'],
                fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#888888'), alignment=TA_CENTER)),
            Paragraph("Alíquota Efetiva", ParagraphStyle('x', parent=styles['Normal'],
                fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#888888'), alignment=TA_CENTER)),
            Paragraph("RBT12", ParagraphStyle('x', parent=styles['Normal'],
                fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#888888'), alignment=TA_CENTER)),
        ],
        [
            Paragraph(f"R$ {dados.get('valor_das_formatted','0,00')}", ParagraphStyle('x', parent=styles['Normal'],
                fontSize=22, fontName='Helvetica-Bold', textColor=COR_PRINCIPAL, alignment=TA_CENTER)),
            Paragraph(f"{dados.get('aliquota_efetiva', 0):.4f}%", ParagraphStyle('x', parent=styles['Normal'],
                fontSize=18, fontName='Helvetica-Bold', textColor=COR_ESCURA, alignment=TA_CENTER)),
            Paragraph(f"R$ {dados.get('rbt12_formatted','0,00')}", ParagraphStyle('x', parent=styles['Normal'],
                fontSize=14, fontName='Helvetica-Bold', textColor=COR_ESCURA, alignment=TA_CENTER)),
        ]
    ]
    t_das = Table(das_table_data, colWidths=[6*cm, 5*cm, 5.5*cm])
    t_das.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#eef2ff')),
        ('BACKGROUND', (1,0), (-1,-1), COR_CINZA),
        ('BOX', (0,0), (-1,-1), 1, COR_PRINCIPAL),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_das)
    story.append(Spacer(1, 16))

    # Detalhamento
    story.append(Paragraph("Detalhamento do Cálculo", style_secao))
    detalhe_data = [
        ['Descrição', 'Valor'],
        ['Faturamento Bruto (Vendas)', f"R$ {dados.get('faturamento_bruto_formatted','0,00')}"],
        ['Deduções (Devoluções)', f"- R$ {dados.get('deducoes_formatted','0,00')}"],
        ['Receita Bruta', f"R$ {dados.get('receita_bruta_formatted','0,00')}"],
    ]
    t_detalhe = Table(detalhe_data, colWidths=[11*cm, 5.5*cm])
    t_detalhe.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COR_PRINCIPAL),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('FONTNAME', (0,1), (-1,-2), 'Helvetica'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#eef2ff')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, COR_CINZA]),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_detalhe)
    story.append(Spacer(1, 16))

    # Tabela CFOPs
    story.append(Paragraph("Resumo por CFOP", style_secao))
    cfop_header = [['CFOP', 'Tipo', 'Quantidade', 'Valor Total']]
    cfop_rows = []
    for cfop, d in sorted(dados.get('cfops', {}).items()):
        cfop_rows.append([
            cfop,
            d.get('tipo', ''),
            str(d.get('quantidade', 0)),
            f"R$ {d.get('valor_formatted', '0,00')}"
        ])
    cfop_data = cfop_header + cfop_rows
    t_cfop = Table(cfop_data, colWidths=[3*cm, 5*cm, 4*cm, 4.5*cm])
    row_styles = [
        ('BACKGROUND', (0,0), (-1,0), COR_PRINCIPAL),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('ALIGN', (2,0), (-1,-1), 'CENTER'),
        ('ALIGN', (3,0), (3,-1), 'RIGHT'),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COR_CINZA]),
    ]
    # Colorir badge tipo
    for i, row in enumerate(cfop_rows, start=1):
        if row[1] == 'VENDA':
            row_styles.append(('TEXTCOLOR', (1,i), (1,i), COR_VERDE))
        else:
            row_styles.append(('TEXTCOLOR', (1,i), (1,i), COR_VERMELHO))
        row_styles.append(('FONTNAME', (1,i), (1,i), 'Helvetica-Bold'))

    t_cfop.setStyle(TableStyle(row_styles))
    story.append(t_cfop)
    story.append(Spacer(1, 24))

    # Rodapé
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#dddddd'), spaceAfter=8))
    story.append(Paragraph(
        "Base Legal: Lei Complementar n. 123/2006 e Resolucao CGSN n. 140/2018",
        style_rodape))
    story.append(Paragraph(
        "Este e um calculo estimativo. Consulte seu contador para validacao final.",
        style_rodape))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ============================================================================
# ROTAS DA APLICAÇÃO
# ============================================================================

@app.route('/')
def index():
    response = make_response(render_template('index.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/gerar-pdf', methods=['POST'])
def gerar_pdf_route():
    """Recebe os dados do resultado e retorna um PDF"""
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({'error': 'Dados inválidos'}), 400
        pdf_bytes = gerar_pdf(dados)
        periodo = dados.get('periodo', 'resultado').replace('/', '-')
        filename = f"DAS_{periodo}.pdf"
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/calcular', methods=['POST'])
def calcular():
    try:
        if 'xmls' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        rbt12_str = request.form.get('rbt12', '0').strip()
        rbt12 = Decimal(rbt12_str) if rbt12_str else Decimal('0')
        anexo = request.form.get('anexo', 'ANEXO_I')
        mes_ref = request.form.get('mes', datetime.now().strftime('%m'))
        ano_ref = request.form.get('ano', datetime.now().strftime('%Y'))

        if rbt12 <= 0:
            return jsonify({'error': 'RBT12 inválido'}), 400

        temp_dir = tempfile.mkdtemp()
        files = request.files.getlist('xmls')
        xml_files = []

        for file in files:
            if file.filename:
                if file.filename.endswith('.zip'):
                    zip_path = os.path.join(temp_dir, secure_filename(file.filename))
                    file.save(zip_path)
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        for member in zip_ref.namelist():
                            if member.lower().endswith('.xml'):
                                zip_ref.extract(member, temp_dir)
                                xml_files.append(os.path.join(temp_dir, member))
                    os.remove(zip_path)
                else:
                    filepath = os.path.join(temp_dir, secure_filename(file.filename))
                    file.save(filepath)
                    xml_files.append(filepath)

        if not xml_files:
            return jsonify({'error': 'Nenhum XML válido encontrado'}), 400

        notas_validas = []
        chaves_processadas = set()
        stats = {'total_arquivos': len(xml_files), 'notas_validas': 0, 'duplicadas': 0, 'canceladas': 0}

        for xml_path in xml_files:
            nota = processar_xml(xml_path)
            if nota:
                if nota['chave'] not in chaves_processadas:
                    notas_validas.append(nota)
                    chaves_processadas.add(nota['chave'])
                    stats['notas_validas'] += 1
                else:
                    stats['duplicadas'] += 1
            else:
                try:
                    tree2 = ET.parse(xml_path)
                    root2 = tree2.getroot()
                    ns2 = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
                    if verificar_nota_cancelada(root2, ns2):
                        stats['canceladas'] += 1
                except:
                    pass

        shutil.rmtree(temp_dir, ignore_errors=True)

        if not notas_validas:
            return jsonify({'error': 'Nenhuma nota válida encontrada'}), 400

        faturamento_bruto = sum(
            (Decimal(str(item['valor'])) for nota in notas_validas
             for item in nota['itens'] if item['tipo'] == 'V'), Decimal('0'))

        deducoes = sum(
            (Decimal(str(item['valor'])) for nota in notas_validas
             for item in nota['itens'] if item['tipo'] == 'D'), Decimal('0'))

        receita_bruta = faturamento_bruto - deducoes
        aliquota_efetiva, deducao_parcela = calcular_aliquota_efetiva(rbt12, anexo)
        valor_das = (receita_bruta * aliquota_efetiva).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        cfops_resumo = {}
        chaves_unicas_cfop = set()
        for nota in notas_validas:
            for item in nota['itens']:
                cfop = item['cfop']
                if cfop not in cfops_resumo:
                    cfops_resumo[cfop] = {
                        'quantidade': 0, 'valor': Decimal('0'),
                        'tipo': 'VENDA' if cfop in CFOPS_VENDAS else 'DEVOLUÇÃO'
                    }
                chave_unica = f"{nota['chave']}_{cfop}"
                if chave_unica not in chaves_unicas_cfop:
                    cfops_resumo[cfop]['quantidade'] += 1
                    chaves_unicas_cfop.add(chave_unica)
                cfops_resumo[cfop]['valor'] += Decimal(str(item['valor']))

        return jsonify({
            'success': True,
            'stats': stats,
            'periodo': f"{mes_ref}/{ano_ref}",
            'anexo': anexo,
            'rbt12': float(rbt12),
            'rbt12_formatted': formatar_br(rbt12),
            'faturamento_bruto': float(faturamento_bruto),
            'faturamento_bruto_formatted': formatar_br(faturamento_bruto),
            'deducoes': float(deducoes),
            'deducoes_formatted': formatar_br(deducoes),
            'receita_bruta': float(receita_bruta),
            'receita_bruta_formatted': formatar_br(receita_bruta),
            'aliquota_efetiva': float(aliquota_efetiva * 100),
            'deducao_parcela': float(deducao_parcela),
            'deducao_parcela_formatted': formatar_br(deducao_parcela),
            'valor_das': float(valor_das),
            'valor_das_formatted': formatar_br(valor_das),
            'cfops': {
                cfop: {
                    'quantidade': dados['quantidade'],
                    'valor': float(dados['valor']),
                    'valor_formatted': formatar_br(dados['valor']),
                    'tipo': dados['tipo']
                }
                for cfop, dados in sorted(cfops_resumo.items())
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
