import discord
from discord.ext import commands
from discord import app_commands # Necessário para Slash Commands
import os
from Clases.InviteConfig import InviteConfig

class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Usando getenv com fallback para evitar erros de NoneType
        self.cargo_membro_id = int(os.getenv("CARGO_MEMBRO_ID", 0))
        self.meta_convites = 5

    # Transformando em Slash Command
    @app_commands.command(name='postar-registro', description='Posta a mensagem de registro de convites (Dono apenas)')
    @app_commands.checks.has_permissions(administrator=True)
    async def postar_registro(self, interaction: discord.Interaction):
        # Verificação de ID do Dono
        dono_id = int(os.getenv('DONO', 0))
        if interaction.user.id != dono_id:
            await interaction.response.send_message("❌ **Acesso Negado.**", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎫 Sistema de Convites",
            description=(
                f"Clique no botão abaixo para pegar seu **Link de Convite Único**.\n\n"
                f"Ao trazer **{self.meta_convites} amigos** para o servidor, "
                f"você ganhará automaticamente o cargo <@&{self.cargo_membro_id}>!"
            ),
            color=discord.Color.blue()
        )
        
        view = RegistroView(self.bot)
        # Em Slash Commands usamos interaction.response ou interaction.channel.send
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Painel enviado com sucesso!", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot: return
        
        inv_db = InviteConfig(self.bot, member.guild)
        try:
            invites_atuais = await member.guild.invites()
            for inv_disc in invites_atuais:
                dados = inv_db.buscar_dono_do_convite(inv_disc.code)
                
                if dados and inv_disc.uses > dados['usos_atuais']:
                    # 1. Atualiza banco e identifica os envolvidos
                    res = inv_db.adicionar_uso(inv_disc.code)
                    user_id_dono = int(res['user_id'])
                    total_usos = res['usos_atuais']
                    dono = member.guild.get_member(user_id_dono)

                    # 2. Aviso silencioso na DM do dono (Feedback de progresso)
                    if dono:
                        try:
                            progresso = f"{total_usos:02d}/{self.meta_convites:02d}"
                            await dono.send(f"✅ **+1 Recruta!** {member.name} entrou pelo seu link. Progresso: **{progresso}**")
                        except: pass

                    # 3. VERIFICA A META (O grande anúncio público)
                    if total_usos >= self.meta_convites and res['meta_batida'] == 0:
                        cargo = member.guild.get_role(self.cargo_membro_id)
                        
                        if cargo and dono:
                            try:
                                await dono.add_roles(cargo)
                                inv_db.set_meta_batida(user_id_dono)
                                
                                # DM de comemoração
                                await dono.send(f"🎖️ **MISSÃO CUMPRIDA!** Você atingiu a meta e agora é um **{cargo.name}**!")

                                # ANÚNCIO PÚBLICO (Apenas para quem completou a meta)
                                canal_id = os.getenv('CANAL_BOAS_VINDAS')
                                canal_boas_vindas = member.guild.get_channel(int(canal_id)) if canal_id else member.guild.system_channel
                                
                                if canal_boas_vindas:
                                    await canal_boas_vindas.send(
                                        f"🎊 **NOVO MEMBRO OFICIAL!** 🎊\n"
                                        f"Parabéns {dono.mention}! Você recrutou 5 combatentes e agora possui o cargo **{cargo.name}**! 🫡"
                                    )
                            except Exception as e:
                                print(f"Erro ao premiar membro: {e}")
                    
                    break # Encontrou o convite, encerra o loop
        except Exception as e:
            print(f"Erro ao rastrear convite: {e}")

# --- VIEW COM O BOTÃO (Mantém igual, mas ajuste o interaction) ---
class RegistroView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Gerar meu Link", style=discord.ButtonStyle.green, custom_id="gerar_invite")
    async def gerar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. Avisa o Discord que você recebeu o clique (isso impede o "Interação Falhou")
        await interaction.response.defer(ephemeral=True) 

        inv_db = InviteConfig(self.bot, interaction.guild)
        codigo_salvo = inv_db.buscar_convite(interaction.user.id)

        if codigo_salvo:
            link = f"https://discord.gg/{codigo_salvo}"
            # Como já demos defer(), usamos followup
            await interaction.followup.send(f"Você já tem um link: {link}", ephemeral=True)
            return

        canal = interaction.guild.system_channel or interaction.channel
        try:
            invite = await canal.create_invite(max_age=0, max_uses=0, unique=True, reason=f"Convite de {interaction.user.name}")
            inv_db.registrar_convite(interaction.user.id, invite.code)
            
            try:
                await interaction.user.send(f"🚀 **Seu link exclusivo:** {invite.url}")
                await interaction.followup.send("Mandei o link na sua DM! 📩", ephemeral=True)
            except:
                # Se a DM falhar, entregamos o link por aqui mesmo (já que é efêmero)
                await interaction.followup.send(f"Sua DM está fechada, então toma seu link por aqui: {invite.url}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send("Erro ao criar link. Verifique minhas permissões.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Invite(bot))