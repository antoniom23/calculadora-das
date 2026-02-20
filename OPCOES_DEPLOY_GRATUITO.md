# 🌟 OPÇÕES DE DEPLOY GRATUITO - Escolha a Melhor!

## Comparação de Plataformas Gratuitas

---

## 🥇 OPÇÃO 1: RENDER.COM (RECOMENDADA!)

### ✅ Vantagens:
- ✨ Mais fácil de todas
- ✨ HTTPS automático
- ✨ Deploy via GitHub (automático)
- ✨ 750 horas/mês GRÁTIS
- ✨ Domínio incluso (.onrender.com)

### ❌ Desvantagens:
- Dorme após 15 min sem uso
- Primeiro acesso demora ~30s

### 💰 Custo: R$ 0,00

### 📖 Veja: DEPLOY_RENDER.md

---

## 🥈 OPÇÃO 2: RAILWAY.APP

### Como fazer:

#### 1. Acesse:
```
https://railway.app
```

#### 2. Login com GitHub

#### 3. Clique em "New Project"

#### 4. Selecione "Deploy from GitHub repo"

#### 5. Escolha seu repositório `calculadora-das`

#### 6. Configure:
```
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
Port: 5000
```

#### 7. Deploy automático!

### ✅ Vantagens:
- Interface bonita
- Muito rápido
- PostgreSQL grátis (se precisar)
- $5 de crédito grátis/mês

### ❌ Desvantagens:
- Créditos limitados (depois de $5, para)

### 💰 Custo: R$ 0,00 (até $5/mês de uso)

---

## 🥉 OPÇÃO 3: FLY.IO

### Como fazer:

#### 1. Instale Flyctl:
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Mac/Linux
curl -L https://fly.io/install.sh | sh
```

#### 2. Login:
```bash
fly auth signup
```

#### 3. No diretório da aplicação:
```bash
fly launch
```

#### 4. Responda:
```
App name: calculadora-das
Region: gru (São Paulo)
PostgreSQL: No
Deploy now: Yes
```

### ✅ Vantagens:
- Servidores no Brasil (mais rápido!)
- Não dorme
- 3 VMs grátis

### ❌ Desvantagens:
- Precisa terminal
- Mais complexo

### 💰 Custo: R$ 0,00

---

## 🏅 OPÇÃO 4: VERCEL (Alternativa)

### ⚠️ ATENÇÃO:
Vercel é otimizado para Next.js/frontend.
Para Flask, funciona mas com limitações.

### Como fazer:

#### 1. Crie arquivo `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

#### 2. Acesse:
```
https://vercel.com
```

#### 3. Login com GitHub

#### 4. Import Project → Selecione seu repositório

#### 5. Deploy automático!

### ✅ Vantagens:
- Super rápido (CDN global)
- Não dorme
- HTTPS automático

### ❌ Desvantagens:
- Não ideal para Flask
- Limite de 100GB/mês

### 💰 Custo: R$ 0,00

---

## 🎯 OPÇÃO 5: PYTHONANYWHERE

### Como fazer:

#### 1. Acesse:
```
https://www.pythonanywhere.com
```

#### 2. Cadastre-se (plano Beginner - grátis)

#### 3. Vá em "Web" → "Add a new web app"

#### 4. Escolha:
```
Python version: 3.10
Framework: Flask
```

#### 5. Configure WSGI:
```python
import sys
path = '/home/seuusername/calculadora-das'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

#### 6. Upload dos arquivos:
- Files → Upload
- Ou Git clone

#### 7. Reload web app

### ✅ Vantagens:
- Interface web amigável
- Terminal online
- Não precisa terminal local

### ❌ Desvantagens:
- Subdomínio longo (.pythonanywhere.com)
- Menos recursos no grátis

### 💰 Custo: R$ 0,00

---

## 📊 TABELA COMPARATIVA

| Plataforma | Facilidade | HTTPS | Domínio | Limite | Dorme? |
|------------|------------|-------|---------|--------|--------|
| **Render** | ⭐⭐⭐⭐⭐ | ✅ Auto | .onrender.com | 750h/mês | ✅ 15min |
| **Railway** | ⭐⭐⭐⭐ | ✅ Auto | .railway.app | $5/mês | ❌ |
| **Fly.io** | ⭐⭐⭐ | ✅ Auto | .fly.dev | 3 VMs | ❌ |
| **Vercel** | ⭐⭐⭐⭐ | ✅ Auto | .vercel.app | 100GB | ❌ |
| **PythonAnywhere** | ⭐⭐⭐⭐ | ✅ | .pythonanywhere.com | Básico | ❌ |

---

## 🏆 RECOMENDAÇÕES

### Para INICIANTES:
✅ **RENDER** - Mais fácil, interface visual

### Para DESENVOLVEDORES:
✅ **RAILWAY** - Bom equilíbrio

### Para PERFORMANCE:
✅ **FLY.IO** - Servidores no Brasil

### Para FRONTEND-HEAVY:
✅ **VERCEL** - Se tiver mais frontend

---

## 🎯 MINHA RECOMENDAÇÃO FINAL

### Use: **RENDER.COM**

**Por quê?**
1. ✨ Mais fácil (sem terminal)
2. ✨ Deploy automático via GitHub
3. ✨ HTTPS grátis
4. ✨ 750 horas = suficiente para rodar 24/7
5. ✨ Interface bonita e simples

**Único "problema":**
- Dorme após 15 min de inatividade
- **Solução:** Use UptimeRobot.com (grátis) para pingar a cada 5 min

---

## 🚀 COMO COMEÇAR AGORA

### Opção Mais Rápida (10 minutos):

1. **Crie conta GitHub** → https://github.com
2. **Crie repositório** → Novo repositório
3. **Upload dos arquivos** → Add files
4. **Crie conta Render** → https://render.com
5. **Conecte GitHub** → New Web Service
6. **Configure** → Python, gunicorn
7. **Deploy!** → Aguarde 3 minutos
8. **Acesse** → seu-app.onrender.com

---

## 📱 MANTER APLICAÇÃO ACORDADA (HACK GRÁTIS)

### Use UptimeRobot:

1. **Acesse:** https://uptimerobot.com
2. **Cadastre-se** (grátis)
3. **Add Monitor:**
   - Type: HTTP(s)
   - URL: https://seu-app.onrender.com
   - Interval: 5 minutes
4. **Save**

**Resultado:** Aplicação NUNCA dorme! 🎉

---

## 💡 DICA ESPECIAL: DOMÍNIO PRÓPRIO GRÁTIS

### Opção 1: Freenom (domínios .tk, .ml, .ga, .cf, .gq)
```
https://www.freenom.com
```

### Opção 2: InfinityFree (hosting + domínio)
```
https://infinityfree.net
```

### Opção 3: Registro.br (.nom.br - R$30/ano)
```
https://registro.br
```

Depois aponte para seu app no Render!

---

## 🔄 MIGRAÇÃO FÁCIL

Se você começar com Render e depois quiser mudar:

### De Render → Railway:
1. Conecte mesmo repositório GitHub
2. Deploy automático
3. Mude DNS se tiver domínio

### De Render → Fly.io:
```bash
fly launch
```
Pronto!

**Seus dados no GitHub facilitam tudo!**

---

## 📝 CHECKLIST DE DEPLOY

```
✅ Conta GitHub criada
✅ Repositório criado
✅ Arquivos enviados:
   ✅ app.py
   ✅ requirements.txt
   ✅ templates/
   ✅ static/
   ✅ render.yaml (opcional)
✅ Conta na plataforma escolhida
✅ Web Service criado
✅ Deploy concluído
✅ Aplicação testada
✅ Link compartilhado
```

---

## 🎉 CONCLUSÃO

### Você TEM opções!

Não funcionou com VPS? **Sem problema!**

Escolha uma dessas plataformas gratuitas e coloque sua aplicação no ar em **10 minutos**!

### Minha recomendação:
1. **Comece com RENDER** (mais fácil)
2. **Configure UptimeRobot** (manter acordado)
3. **Se precisar mais**, migre para Railway ou Fly.io

**Você consegue! 💪**

---

**🎯 ECCONOMIZE - Calculadora DAS**
*Múltiplas opções de deploy gratuito!*

*Escolha a que você preferir! 🚀*
