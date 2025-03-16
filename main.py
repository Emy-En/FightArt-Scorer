import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View, TextInput
from config import TOKEN, GUILD_ID

import scorer


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
intents = discord.Intents.all()
client = Client(command_prefix='!', intents = intents)


# SELECT MENUS --------------------
# SELECT MENU FROM SECOND VIEW - basic info
# Menu to select finish
class finishMenu(discord.ui.Select):
    def __init__(self):
        placeholder="Finish!"
        options=[
            discord.SelectOption(label='Finish - Rough', value='ROUGH'),
            discord.SelectOption(label='Finish - Clean/Lined/Lineless', value='CLEAN'), 
        ]
        super().__init__(options=options, placeholder=placeholder, row=0)
    
    async def callback(self, interaction):
        self.view.attack.finish = scorer.Finish[self.values[0]]
        await interaction.response.defer()

# Menu to select color
class colorMenu(discord.ui.Select):
    def __init__(self):
        placeholder="Color!"
        options=[
            discord.SelectOption(label='Color - Uncolored', value='UNCOLORED'),
            discord.SelectOption(label='Color - Rough', value='ROUGH'),
            discord.SelectOption(label='Color - Clean/Lined/Lineless', value='CLEAN'), 
        ]
        super().__init__(options=options, placeholder=placeholder, row=1)
    
    async def callback(self, interaction):
        self.view.attack.color = scorer.Color[self.values[0]]
        await interaction.response.defer()

# Menu to select shading
class shadingMenu(discord.ui.Select):
    def __init__(self):
        placeholder="Shading!"
        options=[
            discord.SelectOption(label='Shading - Unshaded', value='UNSHADED'),
            discord.SelectOption(label='Shading - Minimal', value='MINIMAL'),
            discord.SelectOption(label='Shading - Fully Shaded', value='FULLY'), 
        ]
        super().__init__(options=options, placeholder=placeholder, row=2)
    
    async def callback(self, interaction):
        self.view.attack.shading = scorer.Shading[self.values[0]]
        await interaction.response.defer()

# Menu to select background
class backgroundMenu(discord.ui.Select):
    def __init__(self):
        placeholder="Background!"
        options=[
            discord.SelectOption(label='Background - None', value='NONE'),
            discord.SelectOption(label='Background - Abstract/Pattern', value='ABSTRACT'),
            discord.SelectOption(label='Background - Props', value='PROPS'), 
            discord.SelectOption(label='Background - Full Scene', value='SCENE'), 
        ]
        super().__init__(options=options, placeholder=placeholder, row=3)
    
    async def callback(self, interaction):
        self.view.attack.background = scorer.Background[self.values[0]]
        await interaction.response.defer()


# VIEWS AND MODALS ----------------
# First view : manages attack type, finish, color, background
class FirstView(discord.ui.View):
    attack: scorer.Attack = scorer.Attack()

    def __init__(self, victime: str, autresVictimes: str, attaquant: str, timeout = 180):
        super().__init__(timeout=timeout)
        # Attack options
        self.attack.victimePrincipale = victime
        self.attack.autresVictimes = autresVictimes
        self.attack.attaquant = f'@{attaquant}'

        # Attack info menu

    # Button to go next
    @discord.ui.select(
        placeholder="Attack Type!",
        options=[
            discord.SelectOption(label='Type - Traditional', value='TRADITIONAL'),
            discord.SelectOption(label='Type - Digital', value='DIGITAL'), 
            discord.SelectOption(label='Type - Animation', value='ANIMATION')
        ]
    )
    async def callback_button(self, interaction, select):
        # Get the attack type
        self.attack.attackType = scorer.AttackType[select.values[0]]

        # Go next to the special frames view if animation
        if self.attack.attackType == scorer.AttackType.ANIMATION:
            viewNext = framesView(self.attack)
            message = "Bagart! Rentrez le nombre de frames unique de votre animation !"
        # Else, just go next to the basic infos
        else:
            viewNext = SecondView(self.attack)
            message = "Bagart! Rentrez les infos basiques de votre attaque !"
        
        await interaction.response.defer()
        await interaction.followup.send(message, view=viewNext, ephemeral=True)  # New ephemeral


# Optional view for frames
class framesView(discord.ui.View):
    attack: scorer.Attack = scorer.Attack()

    def __init__(self, attack: scorer.Attack, timeout = 180):
        super().__init__(timeout=timeout)
        # Attack options
        self.attack = attack

    # Button to go next
    @discord.ui.select(
        placeholder="Unique frames!",
        options=[
            discord.SelectOption(label='Unique Frames - 2 to 5', value='DEUX_A_CINQ'),
            discord.SelectOption(label='Unique Frames - 6 to 10', value='SIX_A_DIX'),
            discord.SelectOption(label='Unique Frames - 11 to 15', value='ONZE_A_QUINZE'), 
            discord.SelectOption(label='Unique Frames - 16 to 20', value='SEIZE_A_VINGT'), 
            discord.SelectOption(label='Unique Frames - 20+', value='PLUS_DE_VINGT'), 
        ]
    )
    async def callback_button(self, interaction, select):
        # Update attack
        self.attack.frames = scorer.UniqueFrames[select.values[0]]
        # Go next to the basic info menus
        view2 = SecondView(self.attack)
        await interaction.response.defer()
        await interaction.followup.send("Bagart! Rentrez les infos basiques de votre attaque !", view=view2, ephemeral=True)  # New ephemeral


# Second view : manages basic info
class SecondView(discord.ui.View):
    attack: scorer.Attack

    def __init__(self, attack: scorer.Attack, timeout = 180):
        super().__init__(timeout=timeout)
        # Attack options
        self.attack = attack
        self.add_item(finishMenu())
        self.add_item(colorMenu())
        self.add_item(shadingMenu())
        self.add_item(backgroundMenu())
    
    @discord.ui.button(label="Next", row=4)
    async def callback_button(self, interaction, button):
        # Sends to the last section (modal with character sizes)
        await interaction.response.send_modal(ModalSizes(self.attack))  # New modal

# Last view : manages validation
class finalView(discord.ui.View):
    attack: scorer.Attack

    def __init__(self, attack: scorer.Attack, timeout = 180):
        super().__init__(timeout=timeout)
        # Attack options
        self.attack = attack
    
    @discord.ui.button(label="Valider !")
    async def callback_button(self, interaction, button):
        # Sends the attack FINALLY OMG
        await interaction.response.send_message(self.attack.attackMessage())  # New ephemeral


# Modal : last input from user, manages character sizes
class ModalSizes(discord.ui.Modal):
    # Attack stored
    attack: scorer.Attack

    # Simple shaped character
    simpleShaped = discord.ui.TextInput(
        label='Nombre de personnages simple-shaped',
        placeholder='Entrez le nombre ici...',
        required=False,
    )

    # Bust/Portrait character
    bust = discord.ui.TextInput(
        label='Nombre de personnages en portrait',
        placeholder='Entrez le nombre ici...',
        required=False,
    )

    # Halfbody characters
    halfBody = discord.ui.TextInput(
        label='Nombre de personnages half-body',
        placeholder='Entrez le nombre ici...',
        required=False,
    )

    # Fullbody characters
    fullBody = discord.ui.TextInput(
        label='Nombre de personnages simple-shaped',
        placeholder='Entrez le nombre ici...',
        required=False,
    )

    def __init__(self, attack: scorer.Attack):
        self.attack = attack
        super().__init__(title="Personnages")

    async def on_submit(self, interaction: discord.Interaction):
        self.attack.characters = [
            scorer.Characters(scorer.Size.SIMPLE, int(str(self.simpleShaped) or 0)),
            scorer.Characters(scorer.Size.BUST, int(str(self.bust) or 0)),
            scorer.Characters(scorer.Size.HALF_BODY, int(str(self.halfBody) or 0)),
            scorer.Characters(scorer.Size.FULL_BODY, int(str(self.fullBody) or 0))
        ]
        lastView = finalView(self.attack)
        embed = (discord.Embed(title="Détails de l'attaque", description=self.attack.detailsAttack()))
        await interaction.response.send_message('On y est presque!', view=lastView, embed=embed, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oups, il y a eu une erreur', ephemeral=True)
        print(error)


# SLASH COMMANDS ------------------
@client.tree.command(name='attack', description="C'est l'heure de la BAGART! Utilisez cette commande pour attaquer quelqu'un")
async def attack(interaction: discord.Interaction, victim:str, othervictims: str = ''):
    # First view for type of attack
    view = FirstView(victim, othervictims, interaction.user.name)
    await interaction.response.send_message("Bagart ! Rentrez le type de votre attaque !", view=view, ephemeral=True)

# RUN BOT -------------------------
client.run(TOKEN)