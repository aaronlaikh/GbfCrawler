import requests
from bs4 import BeautifulSoup
import GbfCharacter
import Skill
import re

class GbfScraper:
    def __init__(self):
        servantList=[]
        print("scraper initialized")

    def parseChar(self, char):
        charRow = char.find_all("td")
        charUrl = self.convertLink(charRow[2].find('a')['href'])
        #parse character details page
        page = requests.get(charUrl)
        soup = BeautifulSoup(page.content, 'html.parser')
        charDetails = soup.find_all("div", class_="character__details")
        character = GbfCharacter.GbfCharacter(charDetails[0].find("div", class_="char-name").get_text())
        self.parseDetails(charDetails[0], character)
        self.parseOugi(charDetails[1], character)
        self.parseSkills(charDetails[2], character)
        #print(character.name, character.rarity, character.uncap, character.maxHP, character.maxATK, character.element, character.races, character.style, character.specialty, character.gender)
        #print(character.skills[1])
        print(vars(character))

    def parseSkill(self, skillRow):
        skillCells = skillRow.find_all("td")
        skill = Skill.Skill(skillCells[1].get_text())
        skill.setCooldown(skillCells[2].get_text())
        skill.setDuration(skillCells[3].get_text())
        skill.setEffect(skillCells[5].get_text())
        return skill

    def parseSkills(self, details, char):
        skillsInfo = details.find_all("tr")
        for i in range(3, skillsInfo.__len__()):
            charSkill = self.parseSkill(skillsInfo[i])
            char.setSkill(charSkill, i-2)

    def parseOugi(self, details, char):
        ougiInfo = self.removeTooltips(details.find_all("td")[2].get_text()).split('%')
        if ougiInfo.__len__() > 1:
            percentage = ougiInfo[0]
            char.setOugiEffect(percentage,ougiInfo[1])
        else:
            char.setOugiEffect(self.convertOugi(ougiInfo[0]),ougiInfo[0])

    def parseDetails(self, details, char):
        # get character rarity
        self.parseRarity(details.find("div", class_="char-rarity").find("img")['src'], char)
        # get char uncap
        self.parseUncap(details.find("div", class_="char-uncap"), char)
        self.parseStats(details.find_all("div", class_="tabber")[1], char)
        # print(details)

    def parseRarity(self, img, char):
        if "Rarity_SSR.png" in img:
            char.setRarity("SSR")
        elif "Rarity_SR.png" in img:
            char.setRarity("SR")
        else:
            char.setRarity("R")

    def parseUncap(self, content, char):
        uncapDetails = content.find("img")
        if uncapDetails != None:
            char.setUncap("5")
        elif uncapDetails == None and char.rarity=="R":
            char.setUncap("3")
        else:
            char.setUncap("4")

    def parseStats(self, content, char):
        #character stats
        statTable = content.find_all("div", class_="tabbertab")[0]
        charStats = statTable.select("div table tbody")
        charStatRows = charStats[0].find_all("tr")
        for i in range(1, charStatRows.__len__()):
            statName = charStatRows[i].find("th").get_text()
            statData = charStatRows[i].find("td")
            #self.statsSwitcher(charStatRows[i].find("th").get_text(), '1000', character)
            if statName == "MAX HP":
                maxHP, bonusHP = self.findStat(statData)
                char.setHP(maxHP)
                char.setBonusHP(bonusHP)
            elif statName == "MAX ATK":
                maxATK, bonusATK = self.findStat(statData)
                char.setATK(maxATK)
                char.setBonusATK(bonusATK)
            elif statName == "Element":
                char.setElement(self.findElement(charStatRows[i].find("img")))
            elif "Race" in statName:
                char.setRace(self.findRace(charStatRows[i].find("img")))
            elif "Style" in statName:
                char.setStyle(self.findStyle(charStatRows[i].find("img")))
            elif "Specialty" in statName:
                char.setSpecialty(self.findSpecialty(charStatRows[i].find("img")))
            elif "Gender" in statName:
                char.setGender(statData.get_text())
            elif statName == "Voice Actor":
                char.setVA(statData.get_text())

    def findStat(self, data):
        values = re.split(r'\W+',re.sub(r"\s+", "", data.get_text()))
        if "Fullyuncapped" in data.get_text():
            maxStat = values[1].replace("FullyuncappedHPatMAXlevel", "").replace("FullyuncappedATKatMAXlevel", "")
        else:
            maxStat = values[0]
        if "bonusesfromCross" in data.get_text():
            bonusStat = values[2].replace("TotalHPbonusesfromCross", "").replace("TotalATKbonusesfromCross", "")
        else:
            bonusStat = 0
        return maxStat, bonusStat

    #characters can have multiple specialities
    def findSpecialty(self, item):
        spec = []
        if "Label_Weapon_Sabre" in item['src']:
            spec.append("Sabre")
        if "Label_Weapon_Dagger" in item['src']:
            spec.append("Dagger")
        if "Label_Weapon_Spear" in item['src']:
            spec.append("Spear")
        if "Label_Weapon_Axe" in item['src']:
            spec.append("Axe")
        if "Label_Weapon_Staff" in item['src']:
            spec.append("Staff")
        if "Label_Weapon_Gun" in item['src']:
            spec.append("Gun")
        if "Label_Weapon_Melee" in item['src']:
            spec.append("Melee")
        if "Label_Weapon_Bow" in item['src']:
            spec.append("Bow")
        if "Label_Weapon_Harp" in item['src']:
            spec.append("Harp")
        return spec

    def findStyle(self, item):
        if "Label_Type_Attack" in item['src']:
            return "Attack"
        elif "Label_Type_Defense" in item['src']:
            return "Defense"
        elif "Label_Type_Special" in item['src']:
            return "Special"
        elif "Label_Type_Balanced" in item['src']:
            return "Balanced"
        elif "Label_Type_Heal" in item['src']:
            return "Heal"

    #characters can have multiple races (units with multiple chars).
    def findRace(self, item):
        race = []
        if "Label_Race_Human" in item['src']:
            race.append("Human")
        if "Label_Race_Erune" in item['src']:
            race.append("Erune")
        if "Label_Race_Draph" in item['src']:
            race.append("Draph")
        if "Label_Race_Harvin" in item['src']:
            race.append("Harvin")
        if "Label_Race_Primal" in item['src']:
            race.append("Primal")
        if "Label_Race_Other" in item['src']:
            race.append("Other")
        return race

    def findElement(self, item):
        if "Label_Element_Fire" in item['src']:
            return "Fire"
        elif "Label_Element_Water" in item['src']:
            return "Water"
        elif "Label_Element_Earth" in item['src']:
            return "Earth"
        elif "Label_Element_Wind" in item['src']:
            return "Wind"
        elif "Label_Element_Light" in item['src']:
            return "Light"
        elif "Label_Element_Dark" in item['src']:
            return "Dark"
        else:
            return "None"
#    def statsSwitcher(self, stat, value, character):
#        switcher = {
#            'MAX HP': lambda: character.setHP(value),
#            'MAX ATK': lambda: character.setATK(value),
#            'Element': lambda:
#        }
#        return switcher.get(stat, lambda: "Invalid arg")()

    #TTD: add more possible tooltip text
    # replace any tooltip-related wiki text.
    def removeTooltips(self, str):
        return str.replace("[1]", " ")

    def convertOugi(self, data):
        keyword = data.split(" ")[0]
        if keyword.lower() == "massive":
            return "450"
        elif keyword.lower() == "big":
            return "400"
        else:
            return "300"

    # convert a gbf.wiki relative hyperlink to absolute URI
    def convertLink(self, page):
        return "https://gbf.wiki" + "/Arulumaya"#page


    def start(self):
        listUrl = "https://gbf.wiki/All_Characters"
        page = requests.get(listUrl)
        soup = BeautifulSoup(page.content,'html.parser')
        results = soup.select("table tbody tr")
        for char in range(1,2):
            self.parseChar(results[char])

