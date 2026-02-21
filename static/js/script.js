// ============================================================================
// CALCULADORA DAS - JavaScript Interativo
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('calculatorForm');
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('xmlFiles');
    const filesList = document.getElementById('filesList');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const calculateBtn = document.getElementById('calculateBtn');
    const loadingState = document.getElementById('loadingState');
    const resultsSection = document.getElementById('resultsSection');
    const newCalculationBtn = document.getElementById('newCalculation');
    
    let currentStep = 1;
    let uploadedFiles = [];
    
    // ========================================================================
    // FILE UPLOAD
    // ========================================================================
    
    uploadArea.addEventListener('click', (e) => {
        if (e.target !== uploadArea && e.target.closest('.file-item')) return;
        fileInput.click();
    });
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });
    
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
    
    function handleFiles(files) {
        const newFiles = Array.from(files).filter(file => {
            const isValid = file.name.endsWith('.xml') || file.name.endsWith('.zip');
            const notDuplicate = !uploadedFiles.some(f => f.name === file.name);
            return isValid && notDuplicate;
        });
        
        uploadedFiles = [...uploadedFiles, ...newFiles];
        renderFilesList();
        
        if (uploadedFiles.length > 0) {
            nextBtn.disabled = false;
        }
    }
    
    function renderFilesList() {
        if (uploadedFiles.length === 0) {
            filesList.classList.remove('active');
            filesList.innerHTML = '';
            return;
        }
        
        filesList.classList.add('active');
        filesList.innerHTML = uploadedFiles.map((file, index) => `
            <div class="file-item">
                <div class="file-info">
                    <div class="file-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                        </svg>
                    </div>
                    <div>
                        <div style="font-weight: 600; font-size: 14px;">${file.name}</div>
                        <div style="font-size: 12px; color: var(--gray-500);">${formatFileSize(file.size)}</div>
                    </div>
                </div>
                <button type="button" class="file-remove" onclick="removeFile(${index})">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
        `).join('');
    }
    
    window.removeFile = function(index) {
        uploadedFiles.splice(index, 1);
        renderFilesList();
        if (uploadedFiles.length === 0) {
            nextBtn.disabled = true;
        }
    };
    
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
    
    // ========================================================================
    // FORM NAVIGATION
    // ========================================================================
    
    nextBtn.addEventListener('click', () => {
        if (currentStep === 1 && uploadedFiles.length === 0) {
            alert('Por favor, selecione ao menos um arquivo XML');
            return;
        }
        if (currentStep < 2) {
            currentStep++;
            updateStep();
        }
    });
    
    prevBtn.addEventListener('click', () => {
        if (currentStep > 1) {
            currentStep--;
            updateStep();
        }
    });
    
    function updateStep() {
        document.querySelectorAll('.form-step').forEach((step, index) => {
            step.classList.toggle('active', index + 1 === currentStep);
        });
        prevBtn.style.display = currentStep === 1 ? 'none' : 'inline-flex';
        nextBtn.style.display = currentStep === 2 ? 'none' : 'inline-flex';
        calculateBtn.style.display = currentStep === 2 ? 'inline-flex' : 'none';
    }
    
    // ========================================================================
    // INPUT MASK RBT12 - CORRIGIDO
    // ========================================================================
    
    const rbt12Input = document.getElementById('rbt12');
    
    rbt12Input.addEventListener('input', (e) => {
        // Remove tudo que não é dígito
        let digits = e.target.value.replace(/\D/g, '');
        
        if (!digits) {
            e.target.value = '';
            return;
        }
        
        // Trata como centavos: últimos 2 dígitos são centavos
        let cents = parseInt(digits);
        let reais = Math.floor(cents / 100);
        let centavos = cents % 100;
        
        // Formata os reais com separador de milhar
        let reaisStr = reais.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        
        e.target.value = reaisStr + ',' + String(centavos).padStart(2, '0');
    });
    
    // Set current month and year
    const currentDate = new Date();
    document.getElementById('mes').value = String(currentDate.getMonth() + 1).padStart(2, '0');
    document.getElementById('ano').value = currentDate.getFullYear();
    
    // ========================================================================
    // FORM SUBMISSION
    // ========================================================================
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Converte "1.234.567,89" → "1234567.89"
        const rbt12Raw = rbt12Input.value.replace(/\./g, '').replace(',', '.');
        if (!rbt12Raw || parseFloat(rbt12Raw) <= 0) {
            alert('Por favor, informe um RBT12 válido');
            return;
        }
        
        const formData = new FormData();
        uploadedFiles.forEach(file => {
            formData.append('xmls', file);
        });
        formData.append('rbt12', rbt12Raw);
        formData.append('anexo', document.getElementById('anexo').value);
        formData.append('mes', document.getElementById('mes').value);
        formData.append('ano', document.getElementById('ano').value);
        
        form.style.display = 'none';
        loadingState.style.display = 'block';
        
        try {
            const response = await fetch('/calcular', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Erro ao processar');
            }
            
            displayResults(result);
            loadingState.style.display = 'none';
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            
        } catch (error) {
            alert('Erro ao calcular: ' + error.message);
            loadingState.style.display = 'none';
            form.style.display = 'block';
        }
    });
    
    // ========================================================================
    // DISPLAY RESULTS
    // ========================================================================
    
    function displayResults(data) {
        const statsGrid = document.getElementById('statsGrid');
        statsGrid.innerHTML = `
            <div class="stat-card">
                <div class="stat-label">Total de XMLs</div>
                <div class="stat-value">${data.stats.total_arquivos}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Notas Válidas</div>
                <div class="stat-value">${data.stats.notas_validas}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Canceladas</div>
                <div class="stat-value">${data.stats.canceladas}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Duplicadas</div>
                <div class="stat-value">${data.stats.duplicadas}</div>
            </div>
        `;
        
        document.getElementById('dasValue').textContent = `R$ ${data.valor_das_formatted}`;
        document.getElementById('aliquotaValue').textContent = `${data.aliquota_efetiva.toFixed(4)}%`;
        document.getElementById('periodoValue').textContent = data.periodo;
        document.getElementById('faturamentoBruto').textContent = `R$ ${data.faturamento_bruto_formatted}`;
        document.getElementById('deducoesValue').textContent = `R$ ${data.deducoes_formatted}`;
        document.getElementById('receitaBruta').textContent = `R$ ${data.receita_bruta_formatted}`;
        
        const cfopsTableBody = document.getElementById('cfopsTableBody');
        cfopsTableBody.innerHTML = Object.entries(data.cfops)
            .map(([cfop, dados]) => `
                <tr>
                    <td><strong>${cfop}</strong></td>
                    <td>
                        <span class="type-badge ${dados.tipo.toLowerCase()}">${dados.tipo}</span>
                    </td>
                    <td>${dados.quantidade}</td>
                    <td><strong>R$ ${dados.valor_formatted}</strong></td>
                </tr>
            `).join('');
    }
    
    // ========================================================================
    // NEW CALCULATION
    // ========================================================================
    
    newCalculationBtn.addEventListener('click', () => {
        currentStep = 1;
        uploadedFiles = [];
        form.reset();
        renderFilesList();
        updateStep();
        resultsSection.style.display = 'none';
        form.style.display = 'block';
        window.scrollTo({ top: 0, behavior: 'smooth' });
        const currentDate = new Date();
        document.getElementById('mes').value = String(currentDate.getMonth() + 1).padStart(2, '0');
        document.getElementById('ano').value = currentDate.getFullYear();
    });
});
