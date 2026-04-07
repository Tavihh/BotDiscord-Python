# 🦅 BotDiscord-Python (IA & Multifuncional)

O **BotDiscord-Python** é um projeto de bot para Discord moderno, modular e altamente personalizável. Ele vai além dos comandos estáticos, utilizando a **Inteligência Artificial do Google Gemini** para interagir de forma contextual, sarcástica ou conforme a personalidade que você definir via variáveis de ambiente.

---

## 🌟 Diferenciais Pragmáticos

* **🧠 Cérebro IA (Gemini 1.5-Flash):** Interações fluidas e inteligentes que entendem o contexto das últimas mensagens do chat.
* **🎭 Personalidade Injetável:** A "alma" do bot é definida por você no `.env`. Ele pode ser um sargento ranzinza, um corvo malandro ou um assistente formal.
* **🧩 Arquitetura Modular (Cogs):** Comandos e eventos organizados em módulos separados (Economia, Interação, Emojis, Música) para facilitar a manutenção.
* **📥 Downloader Automático:** Integração com `yt-dlp` para baixar e enviar vídeos diretamente no canal de logs/downloads.
* **⚖️ Sistema de Imunidade:** Administradores e o Criador são protegidos contra comandos de "zueira" (ex: comando `exterminar`).

---

## 🛠️ Pré-requisitos

1.  **Python 3.10+**
2.  **Chave de API do Google AI:** Obtenha gratuitamente no [Google AI Studio](https://aistudio.google.com/).

---

## ⚙️ Instalação e Setup

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/Tavihh/BotDiscord-Python.git](https://github.com/Tavihh/BotDiscord-Python.git)
    cd BotDiscord-Python
    ```

2.  **Crie o ambiente virtual e instale as dependências:**
    ```bash
    python -m venv .venv
    # Ative o venv:
    # Windows: .venv\Scripts\activate
    # Linux/Mac: source .venv/bin/activate


    pip install -r requirements.txt
    ```

3.  **Configure o arquivo `.env`:**
    Crie um arquivo `.env` na raiz do projeto e preencha as chaves:
    ```env
    BOT_TOKEN=SEU_TOKEN_DISCORD
    BOT_NAME=steve
    LINK_SERVER=LINK_DO_SEU_SERVER
    CARGO_MEMBRO_ID=ID_DO_CARGO_DE_MEMBRO
    CANAL_BOAS_VINDAS=ID_DO_CANAL_DE_BOAS_VINDAS
    DONO=SEU_ID_USUARIO
    GUILD_DONO=ID_DO_SERVIDOR_PRINCIPAL
    CANAL_DOWNLOADS=ID_DO_CANAL_DE_VIDEOS
    GROQ_API_KEY=SUA_GROQ_KEY
    BOT_PERSONALITY="Você é o Steve, um bot sarcástico, pragmático e leal ao seu criador."
    ```

---

## 📋 Módulos e Funcionalidades

### 🧠 Interação & IA (Cog Interação)
* **Resposta Contextual:** O bot lê o histórico recente do chat para responder de forma coerente.
* **Comando Exterminar:** `mate o @user` inicia uma sequência de "ataque" com GIFs e chances variáveis de sucesso.
* **Gatilhos "Quinta Série":** Respostas automáticas para rimas, trocadilhos e números (mario, cinco, duvi, etc).

### 💰 Economia & Banco
* **Comandos de Banco:** `banco-saldo`, `banco-depositar`, `banco-sacar`, `banco-trabalhar`.
* **Interação Social:** `banco-transferir`, `banco-roubar` (com risco de multa) e `banco-apostar`.
* **Ranking:** Ranking local de riqueza para estimular a competição no servidor.

### 🎥 Utilidades e Emojis
* **Auto-Download:** Detecta links de vídeo e faz o upload automático (limite de 25MB).
* **Emoji-Reações:** Reações automáticas baseadas em temas (Treino, Xadrez, Música, Jogos, etc).

---

## 📂 Estrutura de Pastas
```text
├── cogs/               # Módulos lógicos (Interação, Emoji, etc)
├── midia/              # GIFs de comandos e pasta de downloads
├── Clases/             # Lógica de Banco de Dados e Configurações
├── .env                # Suas chaves secretas (Ignorado pelo Git)
├── requirements.txt    # Lista de dependências do projeto
└── index.py            # Ponto de entrada do bot
