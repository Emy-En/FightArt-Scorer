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

class Finish(Enum):
  ROUGH = 5
  CLEAN = 10 # Clean, Lined, Lineless

class Color(Enum):
  UNCOLORED = 0
  ROUGH = 5
  CLEAN = 10

class Shading(Enum):
  UNSHADED = 0
  MINIMAL = 5
  FULLY = 10

class Background(Enum):
  NONE = 0
  ABSTRACT = 5 # Pattern, Abstract
  PROPS = 10
  SCENE = 20

class Size(Enum):
  SIMPLE = 0.5
  BUST = 1
  HALF_BODY = 1.5
  FULL_BODY = 2

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
      Type : {self.attackType.name}
      ---------- BASE POINTS ----------
      Finish : {self.finish.name} - {self.finish.value}
      Color : {self.color.name} - {self.color.value}
      Shading : {self.shading.name} - {self.shading.value}
      Background : {self.background.name} - {self.background.value}
      ---------- MULTIPLIERS ----------
      Character number : x{sum([i.number for i in self.characters])}
      Character sizes : {[f'{i.number} {i.size.name}' for i in self.characters]} - avg x{self.sizeAvgMultiplier()}
      Unique Frames : {self.frames.name} - x{self.frames.value}
      ---------------------------------
      TOTAL : {self.score()}
    """

  # Cette méthode affiche un petit message à copier pour poster, vous pouvez y mettre les @ discord des gens pour tag + facilement
  def attackMessage(self):
    # Message principal
    message = f'{self.attaquant} attaque {self.victimePrincipale} pour un total de {self.score()} points !'
    # Ajout des victimes secondaires si nécessaire
    if self.autresVictimes != '':
      message += f'\nMention spéciale pour: {self.autresVictimes} !'
    return message