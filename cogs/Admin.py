import discord
from discord import app_commands
from discord.ext import commands
from Clases.Server import ServerConfig
import os
from dotenv import load_dotenv
load_dotenv()

BOT = os.getenv('BOT')

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Função auxiliar para checar permissão (Pragmatismo: evita repetir código 10x)
    def tem_permissao(self, interaction: discord.Interaction, sv):
        return (interaction.user.guild_permissions.administrator or 
                interaction.user.id in sv.adm_list() or 
                interaction.user.id == os.getenv('DONO'))

    @app_commands.command(name='clear', description='Limpa mensagens do Chat')
    @app_commands.describe(quantidade='Quantas mensagens eu devo apagar?')
    async def clear(self, interaction: discord.Interaction, quantidade: int = 10):
        sv = ServerConfig(self.bot, interaction.guild)
        if not self.tem_permissao(interaction, sv):
            return await interaction.response.send_message('Você não tem permissão!', ephemeral=True)

        if not 1 <= quantidade <= 1000:
            return await interaction.response.send_message('Digite um número entre 1 e 1000', ephemeral=True)

        # Primeiro respondemos (ephemeral não é apagada pelo purge)
        await interaction.response.send_message(f'Limpando {quantidade} mensagens...', ephemeral=True)
        await interaction.channel.purge(limit=quantidade)

    @app_commands.command(name='bot-off', description='Desliga o bot no servidor')
    async def botOff(self, interaction: discord.Interaction):
        sv = ServerConfig(self.bot, interaction.guild)
        if not self.tem_permissao(interaction, sv):
            return await interaction.response.send_message('Sem permissão!', ephemeral=True)

        if interaction.guild.id in sv.servers_off():
            return await interaction.response.send_message('Já estou desligado!', ephemeral=True)
        
        sv.bot_off()
        await interaction.response.send_message('Saindo, senhor... 🫡')

    @app_commands.command(name='bot-on', description='Liga o bot no servidor')
    async def botOn(self, interaction: discord.Interaction):
        sv = ServerConfig(self.bot, interaction.guild)
        if not self.tem_permissao(interaction, sv):
            return await interaction.response.send_message('Sem permissão!', ephemeral=True)

        if interaction.guild.id not in sv.servers_off():
            return await interaction.response.send_message('Já estou ligado!', ephemeral=True)

        sv.bot_on()
        await interaction.response.send_message('Voltei!')

    @app_commands.command(name='adm_list', description='Veja quem é ADM')
    async def adm_list(self, interaction: discord.Interaction):
        sv = ServerConfig(self.bot, interaction.guild)
        if not self.tem_permissao(interaction, sv):
            return await interaction.response.send_message('Sem permissão!', ephemeral=True)

        embed = discord.Embed(title="🛡️ Lista de ADMs", color=0x00ff00)
        
        for user_id in sv.adm_list():
            user = self.bot.get_user(user_id)
            nome = user.global_name if user else f"ID: {user_id}"
            embed.add_field(name=nome, value="Acesso total", inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='add-adm', description='Adiciona alguém à ADM List')
    async def addAdm(self, interaction: discord.Interaction, quem: discord.Member):
        sv = ServerConfig(self.bot, interaction.guild)
        if not self.tem_permissao(interaction, sv):
            return await interaction.response.send_message('Sem permissão!', ephemeral=True)

        if quem.id in sv.adm_list():
            return await interaction.response.send_message('Já é ADM!', ephemeral=True)

        sv.add_adm(quem)
        await interaction.response.send_message(f'{quem.display_name} agora é meu braço direito!')

    @app_commands.command(name='remove-adm', description='Remove alguém da ADM List')
    async def removeAdm(self, interaction: discord.Interaction, quem: discord.Member):
        sv = ServerConfig(self.bot, interaction.guild)
        if not self.tem_permissao(interaction, sv):
            return await interaction.response.send_message('Sem permissão!', ephemeral=True)

        if quem.id not in sv.adm_list():
            return await interaction.response.send_message('Esse usuário não está na minha Lista de Adms!', ephemeral=True)

        sv.remove_adm(quem)
        await interaction.response.send_message(f'{quem.display_name} agora não é mais meu braço direito!')

    @app_commands.command(name='add-ignore', description='Faz o bot ignorar um usuário')
    async def addIgnore(self, interaction: discord.Interaction, quem: discord.Member):
        sv = ServerConfig(self.bot, interaction.guild)
        if not self.tem_permissao(interaction, sv):
            return await interaction.response.send_message('Sem permissão, patrão!', ephemeral=True)

        if quem.id in sv.ignore_list():
            return await interaction.response.send_message(f'{quem.display_name} já está no vácuo!', ephemeral=True)

        sv.add_ignore(quem)
        await interaction.response.send_message(f'🔇 {quem.mention} adicionado à Ignore List. Não ouço mais ele!', delete_after=15)

    @app_commands.command(name='remove-ignore', description='Volta a ouvir um usuário')
    async def removeIgnore(self, interaction: discord.Interaction, quem: discord.Member):
        sv = ServerConfig(self.bot, interaction.guild)
        if not self.tem_permissao(interaction, sv):
            return await interaction.response.send_message('Sem permissão!', ephemeral=True)

        if quem.id not in sv.ignore_list():
            return await interaction.response.send_message('Esse sujeito nem estava sendo ignorado.', ephemeral=True)

        sv.remove_ignore(quem)
        await interaction.response.send_message(f'🔊 {quem.mention} removido da Ignore List. Pode falar agora!', delete_after=15)
    
    @app_commands.command(name='ignore-list', description='Veja quem o bot está ignorando')
    async def ignoreList(self, interaction: discord.Interaction):
        sv = ServerConfig(self.bot, interaction.guild)
        if not self.tem_permissao(interaction, sv):
            return await interaction.response.send_message('Sem permissão!', ephemeral=True)

        ids = sv.ignore_list()
        if not ids:
            return await interaction.response.send_message('Não estou ignorando ninguém. Sou todo ouvidos! 🦜', ephemeral=True)

        embed = discord.Embed(title="🚫 Lista de Ignorados", color=0xff0000)
        for user_id in ids:
            user = self.bot.get_user(user_id)
            nome = user.global_name if user else f"ID: {user_id}"
            embed.add_field(name=nome, value="Status: No Vácuo", inline=False)
        
        await interaction.response.send_message(embed=embed, delete_after=30)
    
    @app_commands.command(name='cargo-add', description='Dê um cargo a um membro')
    async def cargoDar(self, interaction: discord.Interaction, quem: discord.Member, cargo: discord.Role):
        sv = ServerConfig(self.bot, interaction.guild)
        if not self.tem_permissao(interaction, sv):
            return await interaction.response.send_message('Sem permissão!', ephemeral=True)

        try:
            await quem.add_roles(cargo)
            await interaction.response.send_message(f'✅ {quem.display_name} recebeu o cargo **{cargo.name}**!')

        # 1. Erro de Hierarquia (Bot está abaixo do cargo)
        except discord.Forbidden:
            await interaction.response.send_message('❌ Eu não tenho permissão para gerenciar esse cargo (hierarquia).', ephemeral=True)
        
        # 2. O erro que você recebeu (Cargo não encontrado)
        except discord.NotFound:
            await interaction.response.send_message('❓ Erro: Esse cargo parece não existir mais neste servidor.', ephemeral=True)
            
        # 3. Erros genéricos (Para o bot não morrer por nada)
        except Exception as e:
            print(f"Erro inesperado no cargo-add: {e}")
            await interaction.response.send_message('🚨 Ocorreu um erro ao tentar dar o cargo.', ephemeral=True)
    
    @app_commands.command(name='cargo-remove', description='Retire o cargo de um membro')
    @app_commands.describe(quem='De quem você quer retirar o cargo?', cargo='Qual cargo deve ser removido?')
    async def cargoRemover(self, interaction: discord.Interaction, quem: discord.Member, cargo: discord.Role):
        sv = ServerConfig(self.bot, interaction.guild)
        
        # 1. Verificação de permissão centralizada
        if not self.tem_permissao(interaction, sv):
            return await interaction.response.send_message('❌ Você não tem autoridade para isso, patrão!', ephemeral=True)

        try:
            # 2. Tentativa de remover o cargo
            await quem.remove_roles(cargo)
            await interaction.response.send_message(f'🗑️ Cargo **{cargo.name}** removido com sucesso de {quem.display_name}.', delete_after=15)

        # --- TRATAMENTO DE ERROS (A BLINDAGEM) ---

        # Erro de Hierarquia: O cargo do bot é menor que o cargo que ele tenta tirar
        except discord.Forbidden:
            await interaction.response.send_message(
                '❌ **Erro de Hierarquia:** Não consigo remover esse cargo porque ele está **acima** do meu na lista de cargos do servidor!', 
                ephemeral=True
            )
        
        # Erro de Existência: O cargo sumiu (deletado) ou o ID é inválido
        except discord.NotFound:
            await interaction.response.send_message(
                '❓ **Erro:** Não encontrei esse cargo. Ele pode ter sido deletado recentemente.', 
                ephemeral=True
            )

        # Erro Genérico: Qualquer outra zica que aconteça
        except Exception as e:
            print(f"Erro no cargo-remove: {e}")
            await interaction.response.send_message(
                '🚨 Algo deu errado na hora de puxar o cargo. Tente novamente mais tarde.', 
                ephemeral=True
            )
            
async def setup(bot):
    await bot.add_cog(Admin(bot))