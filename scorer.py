from dataclasses import dataclass, field
from typing import List
from enum import Enum
import statistics


# Les classes ci-dessous sont des Enums, qui permettent d'utiliser spécifiquement les données qu'on veut
# En plus ça permet de stocker facilement les valeurs hehe
class AttackType(Enum):
    TRADITIONAL = 'traditional'
    DIGITAL = 'digital'
    ANIMATION = 'animation'
    def _index_list():
        return [AttackType.TRADITIONAL, AttackType.DIGITAL, AttackType.ANIMATION]

class Finish(Enum):
    ROUGH = 5
    CLEAN = 10 # Clean, Lined, Lineless
    def _index_list():
        return [Finish.ROUGH, Finish.CLEAN]

class Color(Enum):
    UNCOLORED = 0
    ROUGH = 5
    CLEAN = 10
    def _index_list():
        return [Color.UNCOLORED, Color.ROUGH, Color.CLEAN]

class Shading(Enum):
    UNSHADED = 0
    MINIMAL = 5
    FULLY = 10
    def _index_list():
        return [Shading.UNSHADED, Shading.MINIMAL, Shading.FULLY]

class Background(Enum):
    NONE = 0
    ABSTRACT = 5 # Pattern, Abstract
    PROPS = 10
    SCENE = 20
    def _index_list():
        return [Background.NONE, Background.ABSTRACT, Background.PROPS, Background.SCENE]

class Size(Enum):
    SIMPLE = 0.5
    BUST = 1
    HALF_BODY = 1.5
    FULL_BODY = 2
    def _index_list():
        return [Size.SIMPLE, Size.BUST, Size.HALF_BODY, Size.FULL_BODY]

@dataclass
class Characters:
    size: Size
    number: int

class UniqueFrames(Enum): # Pour animation
    PAS_ANIME = 1
    DEUX_A_CINQ = 1.5
    SIX_A_DIX = 2
    ONZE_A_QUINZE = 3
    SEIZE_A_VINGT = 4
    PLUS_DE_20 = 5
    def _index_list():
        return [UniqueFrames.PAS_ANIME, UniqueFrames.DEUX_A_CINQ, UniqueFrames.SIX_A_DIX, UniqueFrames.ONZE_A_QUINZE, UniqueFrames.SEIZE_A_VINGT, UniqueFrames.PLUS_DE_20]

# Cette classe stocke des infos sur l'attaque que vous voulez faire
@dataclass
class Attack:
    attackType: AttackType = AttackType.TRADITIONAL
    finish: Finish = Finish.ROUGH
    color: Color = Color.UNCOLORED
    shading: Shading = Shading.UNSHADED
    background: Background = Background.NONE
    characters: list[Characters] = field(default_factory=list)
    frames: UniqueFrames = UniqueFrames.PAS_ANIME
    attaquant: str = 'NAME1'
    victimePrincipale: str = 'NAME2'
    autresVictimes: str = ''
    message:str = ''

    # Cette méthode permet de calculer la moyenne des personnages
    # Le truc moche dans la parenthèse transforme un [Characters(s1, 3), Characters(s2, 1)] en [s1.score, s1.score, s1.score, s2.score] pour faire la moyenne
    def sizeAvgMultiplier(self):
        return statistics.fmean([i.size.value for i in self.characters for _ in range(i.number)])


    # Cette méthode calcule le total de points
    def score(self):
        # Permettent de faire une moyenne des tailles puis de calculer
        sizeAvg = self.sizeAvgMultiplier()
        nbCharacters = sum([i.number for i in self.characters])
        # Si l'attaque est animée alors fully shaded vaut 5 de plus
        shading = self.shading.value
        if self.attackType == AttackType.ANIMATION and self.shading == Shading.FULLY:
            shading += 5
        # Calcul final, somme du finish/color/shading/bg * les multipliers nbCharacters/sizeCharacters/nbFrames
        return (self.finish.value + self.color.value + shading + self.background.value) * nbCharacters * sizeAvg * self.frames.value

    # Cette méthode affiche le détail de l'attaque
    def detailsAttack(self):
        return f"""
        Attack Id : {hex(self.encodeId())}
        Type : {self.attackType.name}
        ---------- BASE POINTS ----------
        Finish : {self.finish.name} - {self.finish.value}
        Color : {self.color.name} - {self.color.value}
        Shading : {self.shading.name} - {self.shading.value}
        Background : {self.background.name} - {self.background.value}
        ---------- MULTIPLIERS ----------
        Character number : x{sum([i.number for i in self.characters])}
        Character sizes : {[f'{i.number} {i.size.name}' for i in self.characters]} - avg x{self.sizeAvgMultiplier():.2f}
        Unique Frames : {self.frames.name} - x{self.frames.value}
        ---------------------------------
        TOTAL : {self.score():.2f}
        """

    # Cette méthode affiche un petit message à copier pour poster, vous pouvez y mettre les @ discord des gens pour tag + facilement
    def attackMessage(self):
        # Message principal
        message = f'<@{self.attaquant}> attaque {self.victimePrincipale} pour un total de {self.score():.2f} points !'
        # Ajout des victimes secondaires si nécessaire
        if self.autresVictimes != '':
            message += f'\nMention spéciale pour: {self.autresVictimes} !\n'
        return message
    
    def encodeId(self):
        # Start with 1 for easier bit operations and checking if decoding went right
        id = 1
        # Encoding attack info
        for e in [self.attackType, self.finish, self.color, self.shading, self.background, self.frames]:
            id <<= 5
            id |= type(e)._index_list().index(e)
        # Encoding characters info
        for c in self.characters:
            id <<= 6
            id |= c.number
        return id

    def decodeId(id):
        # Takes an enum and an index (read in the id) and returns the corresponding Enum item
        def decode(E, n):
            return E(E._index_list()[n])
        # New attack
        a = Attack()
        # Decoding character sizes
        a.characters = [Characters(i, 0) for i in list(Size)]
        for i in range(4):
            a.characters[3-i].number = id % (2**6)
            id >>= 6
        # Decoding attack information
        a.frames = decode(UniqueFrames, id % (2**5))
        id >>= 5
        a.background = decode(Background, id % (2**5))
        id >>= 5
        a.shading = decode(Shading, id % (2**5))
        id >>= 5
        a.color = decode(Color, id % (2**5))
        id >>= 5
        a.finish = decode(Finish, id % (2**5))
        id >>= 5
        a.attackType = decode(AttackType, id % (2**5))
        id >>= 5
        # Should be left with only a 1, if not then wrong encoding
        if id == 1:
            return a
        else:
            raise Exception("Input id is not a valid id")


    