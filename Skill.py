class Skill:
    def __init__(self, name):
        self.name = name
        self.effect = ""
        self.buffs = {}

    def __str__(self):
        return self.name + ": (" + self.cooldown + " / " + self.duration + " " + self.effect

    def setCooldown(self, turns):
        self.cooldown = turns

    def setDuration(self, turns):
        self.duration = turns

    #TTD: determine different effects and set flags based on buffs/debuffs
    def setEffect(self, effect):
        self.effect = effect