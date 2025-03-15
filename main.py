import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
from config import TOKEN, GUILD_ID

# GUILD ---------------------------
GUILD = discord.Object(GUILD_ID)

# BOT ITSELF ----------------------
# Behaviour
class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        try:
            synced = await self.tree.sync(guild=GUILD)
            print(f'Synced {len(synced)} commands to main guild!')
        except Exception as e:
            print(f'Error syncing commands...')

# Permissions
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
client = Client(command_prefix='!', intents = intents)


# SLASH COMMANDS ------------------
class View2(discord.ui.View):
    @discord.ui.select(
        options=[
            discord.SelectOption(label='HalfBody', value='uwu'),
            discord.SelectOption(label='FullBody', value='a'), 
            discord.SelectOption(label='Bust', value='b')
        ]
    )
    async def select_callback(self, interaction, select): # the function called when the user is done selecting options
        await interaction.response.send_message(f"uwu") 


class View(discord.ui.View):
    @discord.ui.select(
        placeholder="Attack Type!",
        options=[
            discord.SelectOption(label='Traditionnel', value='TRADITIONAL'),
            discord.SelectOption(label='Numérique', value='DIGITAL'), 
            discord.SelectOption(label='Animation', value='ANIMATION')
        ]
    )
    async def select_callback(self, interaction, select): # the function called when the user is done selecting options
        view2 = View2()
        await interaction.response.send_message(f"Awesome! I like {select.values[0]} too!", view=view2) 


@client.tree.command(name='attack', description="C'est l'heure de la BAGART! Utilisez cette commande pour attaquer quelqu'un", guild = GUILD)
async def attack(interaction: discord.Interaction, victime:str, autresvictimes: str):
    view = View()
    view2 = View2()
    await interaction.response.send_message("Bagart ! Veuillez choisir type d'attaque :", view=view, ephemeral=True)


# RUN BOT -------------------------
client.run(TOKEN)