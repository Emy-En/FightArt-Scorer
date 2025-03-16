# FightArt Scorer Bot

The FightArt Scorer Bot is a Discord bot whose goal is to rate drawing attacks for an event in a specific Discord server.

## Commands

### /attack

- **Input** : *[victim]\* [otherVictims]*
This command has 1 required input to specify the main person we are attacking, and 1 optional input to mention other people that are being attacked. It consists of a series of SelectMenus that are used to fill in information about the attack, like its type, finish, color, shading and background properties. It also allows choosing multiple characters with different sizes, calculating the points according to an average.

### /details

- **Input** *[id]\** :
This command allows getting attack details using its attack ID. The ID is generated using the parameters and stored in an int, which is then used to find what the parameters were.

## Install

### Dependencies

This bot needs discord.py to function. Run the following command in the source folder to install everything that is required.

```bash
pip install -r ./requirements.txt
```

### Config

Create a config.py file in the source folder, and fill in those informations:

```py
GUILD_ID = # Your main guild ID here for testing
TOKEN = # Your bot token
```