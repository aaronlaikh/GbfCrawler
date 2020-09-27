class Ougi:
    def __init__(self, pct, effect):
        self.percentage = pct
        #TTD: determine type of buff from effect text
        self.effect = effect

    def __str__(self):
        return self.percentage + "% " + self.effect