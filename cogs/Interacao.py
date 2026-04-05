import discord
from discord.ext import commands
from random import randint, choice
import asyncio
import google.generativeai as genai
import os
from yt_dlp import YoutubeDL
from Clases.ServerConfig import ServerConfig


# Configura a API (Pegue sua chave em: https://aistudio.google.com/)
genai.configure(api_key=os.getenv("GEMINI_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL")) # Versão rápida e leve

# --- CONFIGURAÇÃO DE RESPOSTAS (Fora da classe para não poluir) ---
RESPOSTAS_ESTATICAS = {
    ("bom dia","dia") : ["Bom dia! ☀️", "Diaa", "Buenos Dias", 'Good Dayy'],
    ("boa tarde","tarde") : ["Boa tarde! 🌞", "Tarde", "Buenas Tardes", 'Good Afternoon'],
    ('boa noite', 'vou dor', 'ja vou dor', 'fui dorm', 'partiu sono', 'gnight', 'indo de berço') : ["Boa noite!", "Noite", "Buenas Noches", 'Good Night', 'Dorme bem manin'],
    ("da adm","me da adm") : ['Nop', 'Pede pro ADM', 'Adm pra que?', 'Ta achando que aqui é bagunça?'],
    ('eae', 'oi', 'salve', 'slv', 'eai', 'opa', 'aoba', 'fala tu', 'coé') : ['Eae Manin','Chegou mais um pra festa','Salveee', 'Eae'],
    ('server ruim', 'server lixo', 'server chato', 'sv ruim', 'sv bosta', 'que sv lixo') : ['Faz melhor então','falou o bonzão','duvido falar isso na cara do ADM skks','Problema teu?','Quem te perguntou?','Falou o mestre da diversão... sqn.','A porta da rua é a serventia da casa, amigão.','Se tá ruim pra você, imagina pra quem tem que te aguentar.','Duvido falar isso na cara do ADM.'],
    ('server par', 'sv par', 'server mor', 'sv mor', 'chat par', 'chat mor', 'parou tudo') : ['Pshh, poderia ter mais membros aqui..', 'convida teus amigos pra caa deixa de ser bobo', 'realmente ta meio parado..', 'relaxa, daqui a pouco o chat volta a ativa'],
    ('alguém on', 'alguem on', 'algm on', 'alguém vivo', 'alguem vivo', 'tem alguem', 'vivo?') : ['so você e deus amigo', 'acho que ta todo mundo off', 'devem estar ocupados', 'tenta outra hora', 'Tenta gritar "PIX GRÁTIS" que aparece alguém.' ],
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

    # 1. Função de Sorteio (Membro da Classe)
    def sorteio(self, chance=3):
        return randint(1, chance) == 1

    # 2. O Decorador Correto para Cogs
    @commands.Cog.listener()
    async def on_message(self, message):
        # 1. Filtros Iniciais de Segurança
        if message.author.bot or not message.guild:
            return

        sv = ServerConfig(self.bot, message.guild)
        if message.guild.id in sv.servers_off() or message.author.id in sv.ignore_list():
            return

        texto = message.content.lower()
        canal_id = message.channel.id
        user_id = message.author.id
        membro = [m.display_name[:4].lower() for m in message.guild.members if not m.bot]

        # 2. VERIFICAÇÃO: O bot foi chamado explicitamente?
        chamou_bot = self.bn in texto or self.bot.user.mentioned_in(message)

        # 3. LÓGICA DE MEMÓRIA (ENTRADA):
        if chamou_bot:
            # Marca que este usuário está em conversa ativa neste canal
            self.conversa_ativa[canal_id] = {
                "user": user_id, 
                "tempo": asyncio.get_event_loop().time()
            }
            await self.handle_ia_or_triggers(message, texto)
            return

        # 4. O "PULO DO GATO": Contexto de conversa ativa (sem marcação)
        if canal_id in self.conversa_ativa:
            dados = self.conversa_ativa[canal_id]
            tempo_passado = asyncio.get_event_loop().time() - dados["tempo"]

            # Se for o mesmo usuário e a conversa ainda está "quente" (< 45 segundos)
            if dados["user"] == user_id and tempo_passado < 45:
                
                # --- VERIFICAÇÃO DE SAÍDA (O usuário mudou de assunto?) ---
                
                # A) Verificação por Menção (@Alguém)
                marcou_outro = message.mentions and not self.bot.user.mentioned_in(message)
                
                # B) Verificação por Iniciais (Ex: "tavi...", "sans...")
                # Só roda se não houver menção, para poupar processamento
                citou_nome_outro = False
                if not marcou_outro:
                    inicio_msg = texto[:4].strip()
                    # any() é mais rápido: para na primeira coincidência encontrada
                    citou_nome_outro = any(
                        m.display_name[:4].lower() == inicio_msg 
                        for m in message.guild.members 
                        if not m.bot and m.id != self.bot.user.id
                    )

                # Se ele chamou outra pessoa, o bot sai de fininho
                if marcou_outro or citou_nome_outro:
                    print(f"DEBUG: {message.author.name} mudou o foco. Saindo da conversa ativa.")
                    del self.conversa_ativa[canal_id]
                    return

                # --- CONTINUAÇÃO DA CONVERSA ---
                print(f"DEBUG: {message.author.name} segue falando comigo (Contexto Ativo).")
                # Reseta o timer para a conversa não expirar agora
                self.conversa_ativa[canal_id]["tempo"] = asyncio.get_event_loop().time()
                await self.handle_ia_or_triggers(message, texto)
                return
    
        gatilhos_mata = (f'{self.bn} mate a', f'{self.bn} mate o', f'{self.bn} mata o', f'{self.bn} mata a', f'{self.bn} executa')
        if any(g in texto for g in gatilhos_mata):
            # Pega o último nome da frase de forma segura
            partes = message.content.split()
            if len(partes) < 3: return # Comando incompleto
            alvo = partes[-1] 

            # 3. Sistema de Imunidade (Admins e Criador)
            # Verifica se o alvo citado é um admin ou o criador (usando ID ou nome)
            if alvo.lower() in ['sans', 'san', 'trev', 'otavio'] or any(adm in alvo for adm in sv.adm_list()):
                await message.channel.send(choice(['Não quero.', 'Mata você, eu hein.', 'Esse aí é parça, mexe com quem tá quieto.']))
                return

            # 4. Sequência de Execução
            async with message.channel.typing():
                await asyncio.sleep(1.5)
                await message.channel.send('🚨 **MODO EXTERMINADOR ATIVADO!** 🤖')
                
                await asyncio.sleep(1.5)
                await message.channel.send(f'🎯 Localizando alvo: **{alvo}**...')

            # 5. Sorteio do Resultado (80% Sucesso / 20% Falha)
            sucesso = randint(1, 5) > 1

            async with message.channel.typing():
                await asyncio.sleep(2)
                
                if sucesso:
                    if os.path.exists('midia/tiros.gif'):
                        with open('midia/tiros.gif', 'rb') as f:
                            await message.channel.send(file=discord.File(f))
                    await message.channel.send(f'💥 **RATATATATA!** {alvo} foi pro saco! 💀')
                else:
                    if os.path.exists('midia/explosao.gif'):
                        with open('midia/explosao.gif', 'rb') as f:
                            await message.channel.send(file=discord.File(f))
                    await message.channel.send('⚠️ **ERRO NO SISTEMA!** A arma explodiu na minha mão! 💥🔥')
            return

        if texto[:4] in membro:
            respostas = [
                'Esse é o mais sigma do server 🗿🍷',
                'Ihh, esse aí? É o capitão do time do arco-íris 🌈',
                'Esse é turista: aparece, solta uma pérola e some por 3 meses ✈️',
                'Se inteligência fosse dinheiro, ele estaria devendo pro banco do Bot 📉',
                'A última vez que ele trabalhou no /banco-trabalhar, o servidor caiu de susto 👷',
                'Se beleza fosse crime, ele seria a pessoa mais honesta do mundo 🙊',
                'Esse é o mais sigma do server 🗿🍷',
                'Esse é o Capitão do time do arco-íris 🌈',
                'Gente boa, mas deve pro banco 💸',
                'Aparece a cada eclipse 🌑',
                'Esse gosta de dar o bumbum em off 🍑',
                'Jesus volta antes desse cara ☁️',
                'Lenda viva (mais pra lenda) 💀',
                'Carteira some perto dele 🕵️',
                'Esse é o shape de grilo 🦗',
                'Puxa-saco oficial do ADM 🤡',
                'Esse é Turista profissional 🚶',
                'Esse Pede PIX de 1 real pro corote 🍺',
                'Inimigo n° 1 do Ban 🔨',
                'Esse pula a janela se a polícia bater 👮',
                'Se sair, ninguém percebe 🤐',
                'Só cria dívida no server 🧠'
            ]
            #Simula que está digitando
            async with message.channel.typing():
                await asyncio.sleep( 1.5 )
                await message.channel.send(choice(respostas))
            return

        # --- DOWNLOADER DE VÍDEO (Separado para organização) ---
        if texto.startswith('https://'):
            await self.handle_video_download(message)
        
        membro = [m.display_name[:4].lower() for m in message.guild.members if not m.bot]
        if texto[:4] in membro:
            respostas = [
                'Esse é o mais sigma do server 🗿🍷',
                'Ihh, esse aí? É o capitão do time do arco-íris 🌈',
                'Esse é turista: aparece, solta uma pérola e some por 3 meses ✈️',
                'Se inteligência fosse dinheiro, ele estaria devendo pro banco do Bot 📉',
                'A última vez que ele trabalhou no /banco-trabalhar, o servidor caiu de susto 👷',
                'Se beleza fosse crime, ele seria a pessoa mais honesta do mundo 🙊',
                'Esse é o mais sigma do server 🗿🍷',
                'Esse é o Capitão do time do arco-íris 🌈',
                'Gente boa, mas deve pro banco 💸',
                'Aparece a cada eclipse 🌑',
                'Esse gosta de dar o bumbum em off 🍑',
                'Jesus volta antes desse cara ☁️',
                'Lenda viva (mais pra lenda) 💀',
                'Carteira some perto dele 🕵️',
                'Esse é o shape de grilo 🦗',
                'Puxa-saco oficial do ADM 🤡',
                'Esse é Turista profissional 🚶',
                'Esse Pede PIX de 1 real pro corote 🍺',
                'Inimigo n° 1 do Ban 🔨',
                'Esse pula a janela se a polícia bater 👮',
                'Se sair, ninguém percebe 🤐',
                'Só cria dívida no server 🧠'
            ]
            #Simula que está digitando
            async with message.channel.typing():
                await asyncio.sleep( 1.5 )
                await message.channel.send(choice(respostas))
            return

        # --- LÓGICA DE RESPOSTAS RÁPIDAS (Dicionário) ---
        for gatilho, resposta in RESPOSTAS_ESTATICAS.items():
            if texto.startswith(gatilho):
                async with message.channel.typing():
                    await asyncio.sleep(1.5)
                    final_msg = choice(resposta) if isinstance(resposta, list) else resposta
                    await message.channel.send(final_msg)
                return

    async def handle_ia_or_triggers(self, message, texto):
        # Em vez de 'async with', iniciamos o typing manualmente
        await message.channel.typing()
        
        try:
            user_id = message.author.id
            guild_id = message.guild.id
            
            # IDs do .env
            try:
                criador_id = int(os.getenv('DONO', 0))
                guild_dono_id = int(os.getenv('GUILD_DONO', 0))
                criador_nome = self.bot.get_user(criador_id).display_name if criador_id else "Desconecido"
            except (ValueError, TypeError):
                criador_id, guild_dono_id = 0, 0

            relacao = f"seu criador:({criador_nome})" if user_id == criador_id else "um membro comum"
            relacao_guilda = 'Seu Servidor Principal' if guild_id == guild_dono_id else 'um servidor comum'

            pergunta_limpa = texto.replace(self.bn, "").replace(f'<@{self.bot.user.id}>', "").strip()
            if not pergunta_limpa:
                pergunta_limpa = "me deu oi ou apenas me chamou"

            mensagens = []
            async for msg in message.channel.history(limit=15):
                mensagens.append(f"{msg.author.display_name}: {msg.content}")
            
            mensagens.reverse()
            contexto_chat = "\n".join(mensagens)

            diretriz = os.getenv('BOT_PERSONALITY') or "Sarcástico e direto."
            
            prompt = (
                f"DIRETRIZES: {diretriz}\n\n"
                f"SITUAÇÃO: Falando com {relacao} no {relacao_guilda}.\n"
                f"CONTEXTO:\n{contexto_chat}\n\n"
                f"USUÁRIO: {pergunta_limpa}\n"
                f"RESPOSTA:"
            )

            # 1. Geramos o conteúdo PRIMEIRO (isso leva tempo)
            response = model.generate_content(prompt)
            
            # 2. Enviamos a mensagem (Isso deveria parar o typing automaticamente no Discord)
            if response and response.text:
                await message.channel.send(response.text)
            else:
                await message.channel.send("Fiquei sem palavras agora.")

        except Exception as e:
            print(f"❌ ERRO NO GEMINI: {e}")
            await message.channel.send("Tô com preguiça de pensar agora.")
        
        # Opcional: Se ainda persistir, o Discord simplesmente demora a atualizar o UI.
        return

    async def handle_video_download(self, message):
        video_link = message.content
        folder = "midia/downloads"

        if not os.path.exists(folder):
            os.makedirs(folder)

        if not video_link.startswith("https://www.youtube.com/"):
            return

        ydl_opts = {
            'format': 'best[ext=mp4][filesize<25M]/best',
            'outtmpl': f'{folder}/%(title).50s.%(ext)s',
            'restrictfilenames': True,
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
            'retries': 5,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                # 1. Extrai info e baixa de uma vez só (mais rápido)
                info = ydl.extract_info(video_link, download=True)
                
                if info.get('duration', 0) > 360:
                    print("⚠️ Vídeo muito longo, ignorando.")
                    return

                file_path = ydl.prepare_filename(info)

            # --- AQUI ESTAVA O ERRO: BUSCA SEGURA DO CANAL ---
            id_env = os.getenv('CANAL_DOWNLOADS')
            if not id_env:
                print("❌ ERRO: CANAL_DOWNLOADS não configurado no .env")
                return

            canal_id = int(id_env) # Converte para número!
            
            # Tenta pegar do cache, se não achar, busca no servidor do Discord
            canal = self.bot.get_channel(canal_id) or await self.bot.fetch_channel(canal_id)

            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    await canal.send(file=discord.File(f))
                
                os.remove(file_path) # Limpa o lixo do disco

        except Exception as e:
            print(f"❌ ERRO ao processar vídeo: {e}")

async def setup(bot):
    await bot.add_cog(Interacao(bot))