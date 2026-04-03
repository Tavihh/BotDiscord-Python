import discord


class LojaView(discord.ui.View):
    def __init__(self, bot, user, banco_classe):
        super().__init__(timeout=60)
        self.bot = bot
        self.user = user
        self.Banco = banco_classe # Passamos a classe Banco para usar aqui
        self.carrinho = []
        self.values = []

    @discord.ui.select(
        placeholder="Selecione um item para o carrinho...",
        options=[
            discord.SelectOption(label='Poção da Sorte', value='1', description='500 Oopas'),
            discord.SelectOption(label='3x+ Salário', value='2', description='500 Oopas')
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("Essa loja não é sua!", ephemeral=True)

        escolha = select.values[0]
        nomes = {'1': 'Poção da Sorte', '2': '3X+ Salário'}
        
        if escolha in self.values:
            return await interaction.response.send_message("Você já adicionou este item!", ephemeral=True)

        self.values.append(escolha)
        self.carrinho.append(nomes[escolha])
        await interaction.response.send_message(f"✅ {nomes[escolha]} adicionado ao carrinho!", ephemeral=True)

    @discord.ui.button(label="Finalizar Compra", style=discord.ButtonStyle.green)
    async def comprar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.values:
            return await interaction.response.send_message("Seu carrinho está vazio!", ephemeral=True)

        user_db = self.Banco(self.bot, self.user)
        total = len(self.values) * 500

        if user_db.saldo_user < total:
            return await interaction.response.send_message(f"Saldo insuficiente! Você precisa de {total} Oopas.", ephemeral=True)

        # Entrega dos itens
        for v in self.values:
            if v == '1': user_db.trocar_itens('pocao_sorte', user_db.pocao_sorte + 1)
            if v == '2': user_db.trocar_itens('salario3x', user_db.salario3x + 1)

        user_db.trocar_saldo_user(user_db.saldo_user - total)
        
        embed = discord.Embed(title="🛍️ Compra Realizada!", color=0x00FF00)
        embed.description = "\n".join([f"• {item}" for item in self.carrinho])
        embed.set_footer(text=f"Total pago: {total} Oopas")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.stop() # Fecha a interação da view

    @discord.ui.button(label="Fechar", style=discord.ButtonStyle.red)
    async def fechar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Loja fechada.", embed=None, view=None)
        self.stop()