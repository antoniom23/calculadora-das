"""
CALCULADORA DAS WEB - Backend Flask
Versao 3.0 Web - OFICIAL
"""

from flask import Flask, render_template, request, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from decimal import Decimal, ROUND_HALF_UP
import zipfile
import tempfile
import shutil
import io

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

# ============================================================================
# TABELAS DO SIMPLES NACIONAL
# ============================================================================

TABELAS_SIMPLES = {
    'ANEXO_I': [
        {'limite': Decimal('180000.00'), 'aliquota': Decimal('0.04'),  'deducao': Decimal('0.00')},
        {'limite': Decimal('360000.00'), 'aliquota': Decimal('0.073'), 'deducao': Decimal('5940.00')},
        {'limite': Decimal('720000.00'), 'aliquota': Decimal('0.095'), 'deducao': Decimal('13860.00')},
        {'limite': Decimal('1800000.00'),'aliquota': Decimal('0.107'), 'deducao': Decimal('22500.00')},
        {'limite': Decimal('3600000.00'),'aliquota': Decimal('0.143'), 'deducao': Decimal('87300.00')},
        {'limite': Decimal('4800000.00'),'aliquota': Decimal('0.19'),  'deducao': Decimal('378000.00')},
    ],
    'ANEXO_II': [
        {'limite': Decimal('180000.00'), 'aliquota': Decimal('0.045'), 'deducao': Decimal('0.00')},
        {'limite': Decimal('360000.00'), 'aliquota': Decimal('0.078'), 'deducao': Decimal('5940.00')},
        {'limite': Decimal('720000.00'), 'aliquota': Decimal('0.10'),  'deducao': Decimal('13860.00')},
        {'limite': Decimal('1800000.00'),'aliquota': Decimal('0.112'), 'deducao': Decimal('22500.00')},
        {'limite': Decimal('3600000.00'),'aliquota': Decimal('0.147'), 'deducao': Decimal('85500.00')},
        {'limite': Decimal('4800000.00'),'aliquota': Decimal('0.30'),  'deducao': Decimal('720000.00')},
    ],
    'ANEXO_III': [
        {'limite': Decimal('180000.00'), 'aliquota': Decimal('0.06'),  'deducao': Decimal('0.00')},
        {'limite': Decimal('360000.00'), 'aliquota': Decimal('0.112'), 'deducao': Decimal('9360.00')},
        {'limite': Decimal('720000.00'), 'aliquota': Decimal('0.135'), 'deducao': Decimal('17640.00')},
        {'limite': Decimal('1800000.00'),'aliquota': Decimal('0.16'),  'deducao': Decimal('35640.00')},
        {'limite': Decimal('3600000.00'),'aliquota': Decimal('0.21'),  'deducao': Decimal('125640.00')},
        {'limite': Decimal('4800000.00'),'aliquota': Decimal('0.33'),  'deducao': Decimal('648000.00')},
    ],
    'ANEXO_IV': [
        {'limite': Decimal('180000.00'), 'aliquota': Decimal('0.045'), 'deducao': Decimal('0.00')},
        {'limite': Decimal('360000.00'), 'aliquota': Decimal('0.09'),  'deducao': Decimal('8100.00')},
        {'limite': Decimal('720000.00'), 'aliquota': Decimal('0.102'), 'deducao': Decimal('12420.00')},
        {'limite': Decimal('1800000.00'),'aliquota': Decimal('0.14'),  'deducao': Decimal('39780.00')},
        {'limite': Decimal('3600000.00'),'aliquota': Decimal('0.22'),  'deducao': Decimal('183780.00')},
        {'limite': Decimal('4800000.00'),'aliquota': Decimal('0.33'),  'deducao': Decimal('828000.00')},
    ],
    'ANEXO_V': [
        {'limite': Decimal('180000.00'), 'aliquota': Decimal('0.155'), 'deducao': Decimal('0.00')},
        {'limite': Decimal('360000.00'), 'aliquota': Decimal('0.18'),  'deducao': Decimal('4500.00')},
        {'limite': Decimal('720000.00'), 'aliquota': Decimal('0.195'), 'deducao': Decimal('9900.00')},
        {'limite': Decimal('1800000.00'),'aliquota': Decimal('0.205'), 'deducao': Decimal('17100.00')},
        {'limite': Decimal('3600000.00'),'aliquota': Decimal('0.23'),  'deducao': Decimal('62100.00')},
        {'limite': Decimal('4800000.00'),'aliquota': Decimal('0.305'), 'deducao': Decimal('540000.00')},
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
# FUNCOES DE PROCESSAMENTO
# ============================================================================

def calcular_aliquota_efetiva(rbt12: Decimal, anexo: str) -> Tuple[Decimal, Decimal]:
    tabela = TABELAS_SIMPLES[anexo]
    for faixa in tabela:
        if rbt12 <= faixa['limite']:
            aliquota_efetiva = ((rbt12 * faixa['aliquota']) - faixa['deducao']) / rbt12
            return max(aliquota_efetiva, Decimal('0')), faixa['deducao']
    return Decimal('0'), Decimal('0')

def formatar_br(valor: Decimal) -> str:
    valor = valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return f"{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def formatar_cnpj(cnpj: str) -> str:
    c = cnpj.replace('.','').replace('/','').replace('-','')
    if len(c) == 14:
        return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}"
    return cnpj

def verificar_nota_cancelada(root, ns: dict) -> bool:
    infProt = root.find('.//nfe:infProt', ns)
    if infProt is not None:
        cStat = infProt.find('nfe:cStat', ns)
        if cStat is not None and cStat.text == '101':
            return True
    for evento in root.findall('.//nfe:procEventoNFe', ns):
        tpEvento = evento.find('.//nfe:tpEvento', ns)
        if tpEvento is not None and tpEvento.text == '110111':
            cStat_ev = evento.find('.//nfe:cStat', ns)
            if cStat_ev is not None and cStat_ev.text in ['135', '155']:
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
        data = (datetime.strptime(data_texto[:19], '%Y-%m-%dT%H:%M:%S')
                if 'T' in data_texto else datetime.strptime(data_texto[:10], '%Y-%m-%d'))
        nNF = ide.find('nfe:nNF', ns)
        if nNF is None:
            return None
        serie_elem = ide.find('nfe:serie', ns)
        serie = serie_elem.text if serie_elem is not None else '0'

        emit = root.find('.//nfe:emit', ns)
        cnpj, razao_social = '', ''
        if emit is not None:
            cnpj_el = emit.find('nfe:CNPJ', ns)
            nome_el = emit.find('nfe:xNome', ns)
            if cnpj_el is not None: cnpj = cnpj_el.text or ''
            if nome_el is not None: razao_social = nome_el.text or ''

        itens_validos = []
        for det in root.findall('.//nfe:det', ns):
            prod = det.find('nfe:prod', ns)
            if prod is None: continue
            cfop_el = prod.find('nfe:CFOP', ns)
            vprod_el = prod.find('nfe:vProd', ns)
            if cfop_el is None or vprod_el is None: continue
            cfop = cfop_el.text.replace('.', '')
            valor_item = Decimal(vprod_el.text)
            for tag in ['nfe:vFrete', 'nfe:vOutro']:
                el = prod.find(tag, ns)
                if el is not None and el.text:
                    valor_item += Decimal(el.text)
            tipo = 'V' if cfop in CFOPS_VENDAS else ('D' if cfop in CFOPS_DEVOLUCOES else None)
            if tipo:
                itens_validos.append({'cfop': cfop, 'valor': valor_item, 'tipo': tipo})

        if not itens_validos:
            return None

        return {
            'chave': chave, 'data': data,
            'numero': int(nNF.text), 'serie': serie,
            'cnpj': cnpj, 'razao_social': razao_social,
            'itens': itens_validos
        }
    except Exception as e:
        print(f"[ERRO] {caminho}: {e}")
        return None

def agrupar_por_serie(notas_validas: list) -> dict:
    series = {}
    for nota in notas_validas:
        s = nota['serie']
        if s not in series:
            series[s] = []
        series[s].append(nota)
    resultado = {}
    for serie, notas in sorted(series.items()):
        notas_ord = sorted(notas, key=lambda x: x['numero'])
        resultado[serie] = {
            'quantidade': len(notas_ord),
            'primeira_numero': notas_ord[0]['numero'],
            'primeira_data': notas_ord[0]['data'].strftime('%d/%m/%Y'),
            'ultima_numero': notas_ord[-1]['numero'],
            'ultima_data': notas_ord[-1]['data'].strftime('%d/%m/%Y'),
        }
    return resultado

def montar_detalhamento(notas_validas: list) -> dict:
    """
    Retorna dict: cfop -> { tipo, total, itens: [{data, numero, cfop, chave, valor}] }
    Cada nota pode ter múltiplos itens com o mesmo CFOP — todos aparecem.
    """
    det = {}
    for nota in notas_validas:
        for item in nota['itens']:
            cfop = item['cfop']
            if cfop not in det:
                det[cfop] = {
                    'tipo': 'VENDA' if cfop in CFOPS_VENDAS else 'DEVOLUCAO',
                    'total': Decimal('0'),
                    'itens': []
                }
            det[cfop]['total'] += Decimal(str(item['valor']))
            det[cfop]['itens'].append({
                'data': nota['data'].strftime('%d/%m/%Y'),
                'numero': str(nota['numero']).zfill(6),
                'cfop': cfop,
                'chave': nota['chave'],
                'valor': float(item['valor']),
                'valor_formatted': formatar_br(Decimal(str(item['valor'])))
            })
    # Ordena itens por data e número
    for cfop in det:
        det[cfop]['itens'].sort(key=lambda x: (x['data'][6:10]+x['data'][3:5]+x['data'][:2], x['numero']))
        det[cfop]['total_formatted'] = formatar_br(det[cfop]['total'])
        det[cfop]['quantidade'] = len(det[cfop]['itens'])
        det[cfop]['total'] = float(det[cfop]['total'])
    return dict(sorted(det.items()))

# ============================================================================
# GERACAO DO PDF - FONTE MONOESPAÇADA
# ============================================================================

def gerar_pdf(dados: dict) -> bytes:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # Usa landscape A4 para caber chave de acesso (44 chars)
    W, H = landscape(A4)
    buffer = io.BytesIO()
    c = rl_canvas.Canvas(buffer, pagesize=landscape(A4))

    FONT = 'Courier'
    FONT_B = 'Courier-Bold'
    SZ = 8       # tamanho base
    SZ_T = 9     # titulos
    SZ_H = 10    # cabecalho principal
    LH = 11      # line height
    ML = 30      # margem esquerda
    MR = 30      # margem direita
    y = [H - 35]

    # Largura util
    UW = W - ML - MR
    # Chars que cabem por linha com Courier 8pt (~6px por char)
    CHARS = int(UW / (SZ * 0.601))

    def nova_pagina():
        c.showPage()
        y[0] = H - 35

    def check(needed=LH*2):
        if y[0] < 40 + needed:
            nova_pagina()

    def txt(texto, size=SZ, bold=False, x=None):
        check()
        c.setFont(FONT_B if bold else FONT, size)
        c.drawString(x if x is not None else ML, y[0], texto)
        y[0] -= LH

    def sep(char='='):
        check()
        c.setFont(FONT, SZ)
        c.drawString(ML, y[0], char * CHARS)
        y[0] -= LH

    def br(n=1):
        y[0] -= (LH * 0.5) * n

    # =========================================================
    # CABECALHO
    # =========================================================
    sep('=')
    txt('RELATORIO DE CALCULO DO DAS - SIMPLES NACIONAL', size=SZ_H, bold=True)
    sep('=')
    br()

    cnpj_raw = dados.get('cnpj', '')
    razao    = dados.get('razao_social', '')
    if cnpj_raw or razao:
        txt('IDENTIFICACAO DO CONTRIBUINTE', bold=True)
        sep('-')
        if cnpj_raw:
            txt(f"CNPJ         : {formatar_cnpj(cnpj_raw)}")
        if razao:
            txt(f"Razao Social : {razao}")
        sep('-')
        br()

    txt(f"Periodo de Apuracao : {dados.get('periodo', '-')}")
    txt(f"Anexo Utilizado     : {dados.get('anexo','').replace('_',' ')}")
    txt(f"Data de Geracao     : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    sep('=')
    br()

    # =========================================================
    # ESTATISTICAS
    # =========================================================
    txt('ESTATISTICAS DE PROCESSAMENTO', bold=True)
    sep('-')
    stats = dados.get('stats', {})
    txt(f"Total de XMLs encontrados  : {stats.get('total_arquivos',0):>8}")
    txt(f"Notas validas processadas  : {stats.get('notas_validas',0):>8}")
    txt(f"Notas canceladas (ignor.)  : {stats.get('canceladas',0):>8}")
    txt(f"Notas duplicadas (ignor.)  : {stats.get('duplicadas',0):>8}")
    sep('-')
    br()

    # =========================================================
    # RESUMO POR CFOP
    # =========================================================
    txt('RESUMO POR CFOP', bold=True)
    sep('-')
    txt(f"{'CFOP':<8} | {'Qtd Notas':<12} | {'Valor Total':>22}", bold=True)
    sep('-')
    for cfop, d in sorted(dados.get('cfops', {}).items()):
        tipo_label = '(VENDA)' if d.get('tipo','') in ['VENDA','V'] else '(DEVOLUCAO)'
        txt(f"{cfop:<8} | {d.get('quantidade',0):<12} | R$ {d.get('valor_formatted','0,00'):>18}  {tipo_label}")
    sep('-')
    br()

    # =========================================================
    # APURACAO
    # =========================================================
    txt('APURACAO DO FATURAMENTO', bold=True)
    sep('=')
    txt(f"(+) Faturamento Bruto (Vendas) : R$ {dados.get('faturamento_bruto_formatted','0,00'):>22}")
    txt(f"(-) Deducoes (Devolucoes)      : R$ {dados.get('deducoes_formatted','0,00'):>22}")
    sep('-')
    txt(f"(=) RECEITA BRUTA DO MES       : R$ {dados.get('receita_bruta_formatted','0,00'):>22}", bold=True)
    sep('=')
    br()

    # =========================================================
    # CALCULO DAS
    # =========================================================
    txt('CALCULO DO DAS (SIMPLES NACIONAL)', bold=True)
    sep('=')
    txt(f"Anexo                    : {dados.get('anexo','').replace('_',' ')}")
    txt(f"RBT12 (Receita 12 meses) : R$ {dados.get('rbt12_formatted','0,00'):>22}")
    txt(f"Parcela a Deduzir        : R$ {dados.get('deducao_parcela_formatted','0,00'):>22}")
    txt(f"Aliquota Efetiva         : {dados.get('aliquota_efetiva',0):.4f}%")
    sep('-')
    txt(f"VALOR DO DAS A RECOLHER  : R$ {dados.get('valor_das_formatted','0,00'):>22}", size=SZ_T, bold=True)
    sep('=')
    br()

    # =========================================================
    # NOTAS POR SERIE
    # =========================================================
    series = dados.get('series', {})
    if series:
        txt('NOTAS POR SERIE', bold=True)
        sep('-')
        txt(f"{'Serie':<8} | {'Qtd':>6} | {'Primeira NF':>12} | {'Data':>12} | {'Ultima NF':>12} | {'Data':>12}", bold=True)
        sep('-')
        for serie, info in sorted(series.items()):
            txt(
                f"{serie:<8} | {info['quantidade']:>6} | "
                f"{str(info['primeira_numero']):>12} | {info['primeira_data']:>12} | "
                f"{str(info['ultima_numero']):>12} | {info['ultima_data']:>12}"
            )
        sep('-')
        br()

    # =========================================================
    # DETALHAMENTO POR CFOP
    # =========================================================
    detalhamento = dados.get('detalhamento', {})
    if detalhamento:
        sep('=')
        txt('DETALHAMENTO POR CFOP', size=SZ_T, bold=True)
        sep('=')

        COL_DATA  = 12
        COL_NUM   =  8
        COL_CFOP  =  6
        COL_CHAVE = 44
        COL_VAL   = 14
        # header fixo
        HEADER = (
            f"{'Data':<{COL_DATA}} | "
            f"{'Numero':>{COL_NUM}} | "
            f"{'CFOP':>{COL_CFOP}} | "
            f"{'Chave de Acesso':<{COL_CHAVE}} | "
            f"{'Valor':>{COL_VAL}}"
        )

        for cfop, d in sorted(detalhamento.items()):
            br()
            tipo_label = 'VENDAS' if d.get('tipo','') in ['VENDA','V'] else 'DEVOLUCOES'
            check(LH * 5)
            txt(f"CFOP {cfop} - {tipo_label}", bold=True, size=SZ_T)
            txt(f"Total: R$ {d.get('total_formatted','0,00')} | Quantidade: {d.get('quantidade',0)} notas")
            sep('-')
            txt(HEADER, bold=True)
            sep('-')
            for item in d.get('itens', []):
                check()
                linha = (
                    f"{item['data']:<{COL_DATA}} | "
                    f"{item['numero']:>{COL_NUM}} | "
                    f"{item['cfop']:>{COL_CFOP}} | "
                    f"{item['chave']:<{COL_CHAVE}} | "
                    f"R$ {item['valor_formatted']:>{COL_VAL-3}}"
                )
                txt(linha)
            sep('-')

    # =========================================================
    # RODAPE
    # =========================================================
    br()
    sep('=')
    txt('Base Legal: Lei Complementar n. 123/2006 e Resolucao CGSN n. 140/2018', size=7)
    txt('Este e um calculo estimativo. Consulte seu contador para validacao final.', size=7)
    sep('=')

    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# ============================================================================
# ROTAS
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
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({'error': 'Dados invalidos'}), 400
        pdf_bytes = gerar_pdf(dados)
        periodo = dados.get('periodo', 'resultado').replace('/', '-')
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"DAS_{periodo}.pdf"
        )
    except Exception as e:
        import traceback; traceback.print_exc()
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
            return jsonify({'error': 'RBT12 invalido'}), 400

        temp_dir = tempfile.mkdtemp()
        files = request.files.getlist('xmls')
        xml_files = []

        for file in files:
            if not file.filename: continue
            if file.filename.endswith('.zip'):
                zip_path = os.path.join(temp_dir, secure_filename(file.filename))
                file.save(zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zr:
                    for member in zr.namelist():
                        if member.lower().endswith('.xml'):
                            zr.extract(member, temp_dir)
                            xml_files.append(os.path.join(temp_dir, member))
                os.remove(zip_path)
            else:
                fp = os.path.join(temp_dir, secure_filename(file.filename))
                file.save(fp)
                xml_files.append(fp)

        if not xml_files:
            return jsonify({'error': 'Nenhum XML valido encontrado'}), 400

        notas_validas = []
        chaves_processadas = set()
        stats = {'total_arquivos': len(xml_files), 'notas_validas': 0, 'duplicadas': 0, 'canceladas': 0}
        cnpj_emit, razao_emit = '', ''

        for xml_path in xml_files:
            nota = processar_xml(xml_path)
            if nota:
                if not cnpj_emit and nota.get('cnpj'):
                    cnpj_emit = nota['cnpj']
                    razao_emit = nota['razao_social']
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
            return jsonify({'error': 'Nenhuma nota valida encontrada'}), 400

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
                        'tipo': 'VENDA' if cfop in CFOPS_VENDAS else 'DEVOLUCAO'
                    }
                chave_unica = f"{nota['chave']}_{cfop}"
                if chave_unica not in chaves_unicas_cfop:
                    cfops_resumo[cfop]['quantidade'] += 1
                    chaves_unicas_cfop.add(chave_unica)
                cfops_resumo[cfop]['valor'] += Decimal(str(item['valor']))

        series = agrupar_por_serie(notas_validas)
        detalhamento = montar_detalhamento(notas_validas)

        return jsonify({
            'success': True,
            'cnpj': cnpj_emit,
            'cnpj_formatted': formatar_cnpj(cnpj_emit),
            'razao_social': razao_emit,
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
                    'quantidade': d['quantidade'],
                    'valor': float(d['valor']),
                    'valor_formatted': formatar_br(d['valor']),
                    'tipo': d['tipo']
                }
                for cfop, d in sorted(cfops_resumo.items())
            },
            'series': series,
            'detalhamento': detalhamento
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
