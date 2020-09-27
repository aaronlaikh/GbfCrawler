import Ougi
import Skill
class GbfCharacter:

    def __init__(self, name):
        self.name = name
        self.skills = {}

    def setOugiEffect(self, pct, effect):
        self.ougi = Ougi.Ougi(pct, effect)

    def setSkill(self, skill, slot):
        self.skills[slot] = skill
        print(self.skills[slot])

    def setRarity(self, rarity):
        self.rarity = rarity

    def setUncap(self, uncap):
        self.uncap = uncap

    def setHP(self, hp):
        self.maxHP = hp

    def setBonusHP(self, hp):
        self.bonusHP = hp

    def setATK(self, atk):
        self.maxATK = atk

    def setBonusATK(self, atk):
        self.bonusATK = atk

    def setElement(self, element):
        self.element = element

    def setRace(self, races):
        self.races = races

    def setStyle(self, style):
        self.style = style

    def setSpecialty(self, specialties):
        self.specialty = specialties

    def setVA(self, voice):
        self.voice = voice

    def setGender(self, gender):
        self.gender = gender

    def setID(self, id):
        self.id = id

    def setCharID(self, charid):
        self.charID = charid