import discord
from discord.ext import commands
from discord import app_commands
from random import randint, choice
import asyncio
import os
from yt_dlp import YoutubeDL
from Clases.ServerConfig import ServerConfig
from groq import Groq

# --- CONFIGURAÇÃO DE RESPOSTAS ESTÁTICAS ---
RESPOSTAS_ESTATICAS = {
    ("bom dia","dia") : ["Bom dia! ☀️", "Diaa", "Buenos Dias", 'Good Dayy'],
    ("boa tarde","tarde") : ["Boa tarde! 🌞", "Tarde", "Buenas Tardes", 'Good Afternoon'],
    ('boa noite', 'vou dor', 'ja vou dor', 'fui dorm', 'partiu sono', 'gnight', 'indo de berço') : ["Boa noite!", "Noite", "Buenas Noches", 'Good Night', 'Dorme bem manin'],
    ("da adm","me da adm") : ['Nop', 'Pede pro ADM', 'Adm pra que?', 'Ta achando que aqui é bagunça?'],
    ('eae', 'oi', 'salve', 'slv', 'eai', 'opa', 'aoba', 'fala tu', 'coé') : ['Eae Manin','Chegou mais um pra festa','Salveee', 'Eae'],
    ('server ruim', 'server lixo', 'server chato', 'sv ruim', 'sv bosta', 'que sv lixo') : ['Faz melhor então','falou o bonzão','duvido falar isso na cara do ADM skks','Problema teu?','Quem te perguntou?','Falou o mestre da diversão... sqn.','A porta da rua é a serventia da casa, amigão.','Se tá ruim pra você, imagina pra quem tem que te aguentar.','Duvido falar isso na cara do ADM.'],
    ('fodase', 'foda-se', 'fds', 'foda se') : ['Desfoda-se'],
    ("duvi"): [ "Meu pau no seu ouvido.", "Duvidou? No meu pirulito você rodou."],
    "mario" : ["Aquele que te pegou atrás do armário?", "Conheço, é primo daquele que te comeu no vestiário."],
    "cinco" : ["Meu pau no seu brinco."],
    "seis" : ["Meu pau que te fez."],
    "sete" : ["Meu pau que te derrete."],
    "oito" : ["Meu pau no seu biscoito."],
    "dez" : ["Meu pau nos seus pés."],
}

class Interacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bn = os.getenv('BOT').lower()
        self.conversa_ativa = {}
        self.diretriz = {
            'padrao': os.getenv('BOT_PERSONALITY', "Sarcástico e direto."), 
            'alternativa': None
        }

        # --- CONFIGURAÇÃO GROQ (Substituindo IA Local) ---
        print("⚡ Conectando ao motor GroqCloud (Llama 3.1 70B)...")
        self.client_groq = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.modelo_groq = "llama-3.3-70b-specdec"
        print("✅ Conectado ao GroqCloud!")
    @commands.Cog.listener()

    # --- COMANDO PARA MUDAR (Muda a Alternativa) ---
    @app_commands.command(name='set-personalidade', description='Muda a personalidade da IA (Dono apenas)')
    async def set_personalidade(self, interaction: discord.Interaction, nova_diretriz: str):
        dono_id = int(os.getenv('DONO', 0))
        if interaction.user.id != dono_id:
            await interaction.response.send_message("❌ **Só o Boss mexe no meu bico.**", ephemeral=True)
            return
        
        self.diretriz['alternativa'] = nova_diretriz
        await interaction.response.send_message(f"✅ **Personalidade alterada!** Agora eu sou: `{nova_diretriz[:50]}...`")

    # --- COMANDO PARA VOLTAR (Limpa a Alternativa) ---
    @app_commands.command(name='reset-personalidade', description='Volta para a personalidade original')
    async def reset_personalidade(self, interaction: discord.Interaction):
        dono_id = int(os.getenv('DONO', 0))
        if interaction.user.id != dono_id:
            await interaction.response.send_message("❌ **Acesso Negado.**", ephemeral=True)
            return
            
        self.diretriz['alternativa'] = None
        await interaction.response.send_message("🔄 **Zeca Urubu de volta ao posto!** Diretriz padrão reativada.")

    async def on_message(self, message):
        # 1. Filtros Iniciais
        if message.author.bot or not message.guild:
            return

        sv = ServerConfig(self.bot, message.guild)
        if message.guild.id in sv.servers_off() or message.author.id in sv.ignore_list():
            return

        texto = message.content.lower()
        canal_id = message.channel.id
        user_id = message.author.id

        # 2. Lógica de Chamada/Conversa Ativa
        chamou_bot = self.bn in texto or self.bot.user.mentioned_in(message)

        if chamou_bot:
            self.conversa_ativa[canal_id] = {"user": user_id, "tempo": asyncio.get_event_loop().time()}
            await self.handle_ia_or_triggers(message, texto)
            return

        if canal_id in self.conversa_ativa:
            dados = self.conversa_ativa[canal_id]
            if dados["user"] == user_id and (asyncio.get_event_loop().time() - dados["tempo"]) < 45:
                # Se marcar outro, sai da conversa
                if message.mentions and not self.bot.user.mentioned_in(message):
                    del self.conversa_ativa[canal_id]
                    return
                
                self.conversa_ativa[canal_id]["tempo"] = asyncio.get_event_loop().time()
                await self.handle_ia_or_triggers(message, texto)
                return

        # 3. Gatilhos "Mata"
        gatilhos_mata = (f'{self.bn} mate a', f'{self.bn} mate o', f'{self.bn} mata o', f'{self.bn} mata a', f'{self.bn} executa')
        if any(g in texto for g in gatilhos_mata):
            partes = message.content.split()
            if len(partes) >= 3:
                alvo = partes[-1]
                if alvo.lower() in ['sans', 'san', 'trev', 'otavio'] or any(adm in alvo for adm in sv.adm_list()):
                    await message.channel.send(choice(['Não quero.', 'Mata você, eu hein.', 'Esse aí é parça.']))
                else:
                    await self.executar_comando_mata(message, alvo)
                return

        # 4. Respostas Rápidas (Dicionário)
        for gatilho, resposta in RESPOSTAS_ESTATICAS.items():
            match = any(texto.startswith(g) for g in gatilho) if isinstance(gatilho, tuple) else texto.startswith(gatilho)
            if match:
                async with message.channel.typing():
                    await asyncio.sleep(1.2)
                    await message.reply(choice(resposta) if isinstance(resposta, list) else resposta)
                return

        # 5. Respostas sobre membros (Zueira)
        membros_iniciais = [m.display_name[:4].lower() for m in message.guild.members if not m.bot]
        if texto[:4] in membros_iniciais:
            respostas_zueira = [
                'Esse é o mais sigma do server 🗿🍷', 'Capitão do time do arco-íris 🌈', 
                'Gente boa, mas deve pro banco 💸', 'Aparece a cada eclipse 🌑',
                'Só cria dívida no server 🧠', ' Shape de grilo 🦗'
            ]
            async with message.channel.typing():
                await asyncio.sleep(1.5)
                await message.channel.send(choice(respostas_zueira))
            return

        # 6. Download de Vídeo
        if texto.startswith('https://'):
            await self.handle_video_download(message)

    async def executar_comando_mata(self, message, alvo):
        async with message.channel.typing():
            await message.channel.send('🚨 **MODO EXTERMINADOR ATIVADO!** 🤖')
            await asyncio.sleep(1.5)
            await message.channel.send(f'🎯 Localizando alvo: **{alvo}**...')
            sucesso = randint(1, 5) > 1
            await asyncio.sleep(2)
            if sucesso:
                await message.channel.send(f'💥 **RATATATATA!** {alvo} foi pro saco! 💀')
            else:
                await message.channel.send('⚠️ **ERRO NO SISTEMA!** A arma explodiu na minha mão! 💥🔥')

    async def handle_ia_or_triggers(self, message, texto):
        async with message.channel.typing():
            try:
                # Mantendo suas regras de Dono e Guilda
                dono_id = int(os.getenv('DONO') or 0)
                guild_dono_id = int(os.getenv('GUILD_DONO') or 0)
                
                relacao = 'Criador' if message.author.id == dono_id else 'Membro'
                server = 'Seu Servidor' if message.guild.id == guild_dono_id else 'Outro Servidor'
                
                # Histórico (Contexto)
                contexto = [msg async for msg in message.channel.history(limit=15)]
                contexto_texto = "\n".join([
                    f"{m.author.display_name}: {m.content}" 
                    for m in reversed(contexto) 
                    if not m.author.bot
                ])

                diretriz_ativa = self.diretriz['alternativa'] or self.diretriz['padrao']
                

                # Seu Prompt original preservado
                prompt = (
                    f"SISTEMA: Você é o personagem descrito abaixo. Responda apenas como ele, sem narrações entre parênteses e sem explicar suas ações.\n"
                    f"DIRETRIZES: {diretriz_ativa}\n"
                    f"CONTEXTO DO CHAT:\n{contexto_texto}\n"
                    f"SITUAÇÃO: Você está falando com o {relacao} em {server}.\n"
                    f"USUÁRIO: {texto}\n"
                    f"RESPOSTA CURTA:"
                )

                # --- CHAMADA DA API GROQ (Substituindo o Executor Local) ---
                # Como é uma API externa, usamos o executor para não travar o bot
                loop = asyncio.get_event_loop()
                
                def call_groq():
                    completion = self.client_groq.chat.completions.create(
                        model=self.modelo_groq,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=150, # Aumentei um pouco pois a API aguenta
                        top_p=1,
                        stream=False,
                    )
                    return completion.choices[0].message.content

                res_texto = await loop.run_in_executor(None, call_groq)
                
                await message.reply(res_texto or "Tô sem bateria pra pensar.")

            except Exception as e:
                print(f"❌ ERRO GROQ: {e}")
                await message.reply("Deu um teto preto aqui na API do Groq.")
    
    async def handle_video_download(self, message):
        video_link = message.content
        if not video_link.startswith("https://www.youtube.com/"): return
        
        folder = "midia/downloads"
        if not os.path.exists(folder): os.makedirs(folder)

        ydl_opts = {
            'format': 'best[ext=mp4][filesize<25M]/best',
            'outtmpl': f'{folder}/%(title).50s.%(ext)s',
            'quiet': True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_link, download=True)
                file_path = ydl.prepare_filename(info)
                canal_id = int(os.getenv('CANAL_DOWNLOADS', 0))
                canal = self.bot.get_channel(canal_id) or await self.bot.fetch_channel(canal_id)

                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        await canal.send(file=discord.File(f))
                    os.remove(file_path)
        except Exception as e:
            print(f"❌ ERRO DOWNLOAD: {e}")

async def setup(bot):
    await bot.add_cog(Interacao(bot))