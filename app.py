"""
CALCULADORA DAS WEB - Backend Flask
Versão 3.0 Web - OFICIAL

Aplicação web para cálculo do DAS - Simples Nacional
Pronta para deploy em VPS Hostinger
"""

from flask import Flask, render_template, request, jsonify, send_file
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

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max
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
    '5101', '5102', '5103', '5104', '5105', '5106', '5109', '5110', '5111', '5112', '5113', '5114', '5115',
    '5116', '5117', '5118', '5119', '5120', '5122', '5123', '5124', '5125', '5401', '5402', '5403', '5405',
    '5653', '5654', '5655', '5656', '5667',
    '6101', '6102', '6103', '6104', '6105', '6106', '6107', '6108', '6109', '6110', '6111', '6112', '6113',
    '6114', '6115', '6116', '6117', '6118', '6119', '6120', '6122', '6123', '6124', '6125', '6401', '6402',
    '6403', '6404', '6653', '6654', '6655', '6656', '6667'
}

CFOPS_DEVOLUCOES = {
    '1201', '1202', '1203', '1204', '1208', '1209', '1410', '1411', '1503', '1504',
    '2201', '2202', '2203', '2204', '2208', '2209', '2410', '2411', '2503', '2504'
}

# ============================================================================
# FUNÇÕES DE PROCESSAMENTO
# ============================================================================

def calcular_aliquota_efetiva(rbt12: Decimal, anexo: str) -> Tuple[Decimal, Decimal]:
    """Calcula alíquota efetiva do Simples Nacional"""
    tabela = TABELAS_SIMPLES[anexo]
    
    for faixa in tabela:
        if rbt12 <= faixa['limite']:
            aliquota = faixa['aliquota']
            deducao = faixa['deducao']
            aliquota_efetiva = ((rbt12 * aliquota) - deducao) / rbt12
            return max(aliquota_efetiva, Decimal('0')), deducao
    
    return Decimal('0'), Decimal('0')

def formatar_br(valor: Decimal) -> str:
    """Formata valor em padrão brasileiro"""
    valor = valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    texto = f"{valor:,.2f}"
    return texto.replace(',', 'X').replace('.', ',').replace('X', '.')

def verificar_nota_cancelada(root, ns: dict) -> bool:
    """Verifica se nota foi cancelada"""
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
        
        dhEmi = ide.find('nfe:dhEmi', ns) or ide.find('nfe:dEmi', ns)
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
                itens_validos.append({
                    'cfop': cfop,
                    'valor': valor_item,
                    'tipo': tipo
                })
        
        if not itens_validos:
            return None
        
        return {
            'chave': chave,
            'data': data,
            'numero': nNF.text,
            'serie': serie,
            'itens': itens_validos
        }
    
    except Exception as e:
        print(f"[ERRO] {caminho}: {e}")
        return None

# ============================================================================
# ROTAS DA APLICAÇÃO
# ============================================================================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    """Processa XMLs e calcula DAS"""
    try:
        # Valida entrada
        if 'xmls' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        rbt12 = Decimal(request.form.get('rbt12', '0').replace('.', '').replace(',', '.'))
        anexo = request.form.get('anexo', 'ANEXO_I')
        mes_ref = request.form.get('mes', datetime.now().strftime('%m'))
        ano_ref = request.form.get('ano', datetime.now().strftime('%Y'))
        
        if rbt12 <= 0:
            return jsonify({'error': 'RBT12 inválido'}), 400
        
        # Cria diretório temporário
        temp_dir = tempfile.mkdtemp()
        
        # Salva arquivos
        files = request.files.getlist('xmls')
        xml_files = []
        
        for file in files:
            if file.filename:
                if file.filename.endswith('.zip'):
                    # Extrai ZIP
                    zip_path = os.path.join(temp_dir, secure_filename(file.filename))
                    file.save(zip_path)
                    
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    # Lista XMLs extraídos
                    for dirpath, dirnames, filenames in os.walk(temp_dir):
                        for f in filenames:
                            if f.lower().endswith('.xml'):
                                xml_files.append(os.path.join(dirpath, f))
                else:
                    # XML individual
                    filepath = os.path.join(temp_dir, secure_filename(file.filename))
                    file.save(filepath)
                    xml_files.append(filepath)
        
        if not xml_files:
            return jsonify({'error': 'Nenhum XML válido encontrado'}), 400
        
        # Processa XMLs
        notas_validas = []
        chaves_processadas = set()
        stats = {
            'total_arquivos': len(xml_files),
            'notas_validas': 0,
            'duplicadas': 0,
            'canceladas': 0
        }
        
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
                # Verifica se foi cancelada
                try:
                    tree = ET.parse(xml_path)
                    root = tree.getroot()
                    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
                    if verificar_nota_cancelada(root, ns):
                        stats['canceladas'] += 1
                except:
                    pass
        
        if not notas_validas:
            return jsonify({'error': 'Nenhuma nota válida encontrada'}), 400
        
        # Calcula totais
        faturamento_bruto = sum(
            Decimal(str(item['valor'])) for nota in notas_validas
            for item in nota['itens'] if item['tipo'] == 'V'
        )
        
        deducoes = sum(
            Decimal(str(item['valor'])) for nota in notas_validas
            for item in nota['itens'] if item['tipo'] == 'D'
        )
        
        receita_bruta = faturamento_bruto - deducoes
        
        # Calcula DAS
        aliquota_efetiva, deducao_parcela = calcular_aliquota_efetiva(rbt12, anexo)
        valor_das = (receita_bruta * aliquota_efetiva).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Agrupa por CFOP
        cfops_resumo = {}
        for nota in notas_validas:
            for item in nota['itens']:
                cfop = item['cfop']
                if cfop not in cfops_resumo:
                    cfops_resumo[cfop] = {
                        'quantidade': 0,
                        'valor': Decimal('0'),
                        'tipo': 'VENDA' if cfop in CFOPS_VENDAS else 'DEVOLUÇÃO'
                    }
                
                # Conta nota única por CFOP
                chave_unica = f"{nota['chave']}_{cfop}"
                if chave_unica not in chaves_processadas:
                    cfops_resumo[cfop]['quantidade'] += 1
                
                cfops_resumo[cfop]['valor'] += Decimal(str(item['valor']))
        
        # Limpa diretório temporário
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Retorna resultado
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
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
