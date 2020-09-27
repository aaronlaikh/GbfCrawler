class Ougi:
    def __init__(self, pct, effect):
        self.percentage = pct
        #TTD: determine type of buff from effect text
        self.effect = effect
        self.buffs = {}

    def __str__(self):
        return self.percentage + "% " + self.effect

    def __repr__(self):
        return str(vars(self))