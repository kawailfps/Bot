import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import os

# --- CONFIGURATION ---
# Sur Koyeb, tu créeras une variable d'environnement nommée DISCORD_TOKEN
TOKEN = "MTQ1Njc2MTM4MDA4NTQzNjQ0OA.G8jV4V.HRVkAItXx7yeSTW96jxxjpE39ibC5TbWdmk0G4"
ID_CATEGORIE_TICKETS = 1456749652303941632
ID_SALON_PANEL = 1456749709044486347

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- VUE : BOUTONS DANS LE TICKET ---
class TicketActions(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Traiter le ticket", style=discord.ButtonStyle.success, custom_id="claim_btn")
    async def claim(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            description=f"👨‍💻 **{interaction.user.display_name}** traite votre ticket. Merci de patienter.",
            color=discord.Color.green()
        )
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(embed=embed)

    @discord.ui.button(label="Fermer le ticket", style=discord.ButtonStyle.danger, custom_id="close_btn")
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Fermeture du ticket en cours...")
        await interaction.channel.delete()

# --- VUE : MENU DE SÉLECTION DU PANEL ---
class TicketDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Problème", emoji="⚠️", description="Signaler un bug ou un souci"),
            discord.SelectOption(label="Aide", emoji="❓", description="Besoin d'aide sur le serveur"),
            discord.SelectOption(label="Autre/Partenariat", emoji="🤝", description="Demandes diverses"),
        ]
        super().__init__(placeholder="Choisissez une catégorie...", options=options, custom_id="ticket_select")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(ID_CATEGORIE_TICKETS)
        
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{self.values[0]}-{interaction.user.name}",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }
        )

        await interaction.response.send_message(f"✅ Ticket ouvert ici : {ticket_channel.mention}", ephemeral=True)
        
        embed = discord.Embed(
            title="Support Client",
            description=f"Bienvenue {interaction.user.mention} !\nCatégorie : **{self.values[0]}**\n\nUtilisez les boutons ci-dessous pour gérer le ticket.",
            color=discord.Color.blue()
        )
        await ticket_channel.send(embed=embed, view=TicketActions())

class PanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

# --- ÉVÉNEMENT : DÉMARRAGE ET ENVOI AUTO ---
@bot.event
async def on_ready():
    print(f"Bot en ligne : {bot.user}")
    
    # Persistance des vues
    bot.add_view(PanelView())
    bot.add_view(TicketActions())

    channel = bot.get_channel(ID_SALON_PANEL)
    if channel:
        # Anti-renvoi : vérifie si le panel est déjà là
        async for message in channel.history(limit=20):
            if message.author == bot.user and message.embeds:
                print("Le panel existe déjà dans le salon.")
                return
        
        embed = discord.Embed(
            title="Ouvrir un Ticket",
            description="Sélectionnez une option ci-dessous pour contacter le staff.",
            color=discord.Color.blue()
        )
        await channel.send(embed=embed, view=PanelView())
        print("Nouveau panel envoyé.")

bot.run(TOKEN)
