import requests
from bs4 import BeautifulSoup
import GbfCharacter
import Skill
import re
import pymongo
from pprint import pprint

class GbfScraper:
    def __init__(self):
        servantList=[]
        print("scraper initialized")
        # set up db connection
        self.db = self.initializeConnection()
        self.dbChars = self.db["characters"]

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
        self.parseSupports(charDetails[3], character)
        #print(character.name, character.rarity, character.uncap, character.maxHP, character.maxATK, character.element, character.races, character.style, character.specialty, character.gender)
        #print(character.skills[1])
        #self.addToDB(character)
        pprint(vars(character))

    def addToDB(self, char):
        success = self.dbChars.insert(char.__dict__)
        print(success)

    def parseSupport(self, supportRow):
        supportCells = supportRow.find_all("td")
        skill = Skill.Skill(supportCells[1].get_text())
        skill.setType(supportCells[2].get_text())
        skill.setEffect(supportCells[3].get_text())
        return skill

    def parseSupports(self, details, char):
        supportsInfo = details.find_all("tr")
        for i in range(3, supportsInfo.__len__()):
            charSkill = self.parseSupport(supportsInfo[i])
            char.setSkill(charSkill, "support"+str(i-2))

    def parseSkill(self, skillRow):
        skillCells = skillRow.find_all("td")
        skill = Skill.Skill(skillCells[1].get_text())
        skill.setCooldown(skillCells[2].get_text())
        skill.setDuration(skillCells[3].get_text())
        skill.setType(skillCells[4].get_text())
        skill.setEffect(skillCells[5].get_text())
        return skill

    def parseSkills(self, details, char):
        skillsInfo = details.find_all("tr")
        for i in range(3, skillsInfo.__len__()):
            charSkill = self.parseSkill(skillsInfo[i])
            char.setSkill(charSkill, str(i-2))

    def parseOugi(self, details, char):
        ougiInfo = self.removeTooltips(details.find_all("td")[2].get_text()).split(' ', 1)
        char.setOugiEffect(self.convertOugi(ougiInfo[0]),ougiInfo[0]+ougiInfo[1])

    def parseDetails(self, details, char):
        # get character rarity
        self.parseRarity(details.find("div", class_="char-rarity").find("img")['src'], char)
        # get char uncap
        self.parseUncap(details.find("div", class_="char-uncap"), char)
        tables = details.find_all("table", class_="wikitable")
        self.parseStats(tables[1], char)
        self.parseExtraData(tables[3], char)
        # print(details)

    def parseExtraData(self, details, char):
        extraData = details.select("div table tbody")
        extraDataRows = extraData[0].find_all("tr")
        char.setID(extraDataRows[1].find("td").get_text())
        char.setCharID(extraDataRows[2].find("td").get_text())

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
        charStats = content.select("div table tbody")
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
                char.setRace(self.findRace(charStatRows[i].find_all("img")))
            elif "Style" in statName:
                char.setStyle(self.findStyle(charStatRows[i].find("img")))
            elif "Specialty" in statName:
                char.setSpecialty(self.findSpecialty(charStatRows[i].find_all("img")))
            elif "Gender" in statName:
                char.setGender(statData.get_text())
            elif statName == "Voice Actor":
                char.setVA(statData.get_text())

    def findStat(self, data):
        values = data.get_text().replace("(+","/").replace(")","").replace(" ", "").split("/")
        # check for fully uncapped stat. pops from list for compatibility
        # on checking bonuses with chars without 5* uncap.
        if "Fully uncapped" in data.get_text():
            index = values[1].index("Fullyuncapped")
            maxStat = values[1][:index]
            values.pop(1)
        else:
            maxStat = values[0]
        if "bonuses from Cross" in data.get_text():
            index = values[1].index("Total")
            bonusStat = values[1][:index]
        else:
            bonusStat = "0"
        return maxStat, bonusStat

    #characters can have multiple specialities
    def findSpecialty(self, item):
        spec = []
        for i in item:
            if "Label_Weapon_Sabre" in i['src']:
                spec.append("Sabre")
            if "Label_Weapon_Dagger" in i['src']:
                spec.append("Dagger")
            if "Label_Weapon_Spear" in i['src']:
                spec.append("Spear")
            if "Label_Weapon_Axe" in i['src']:
                spec.append("Axe")
            if "Label_Weapon_Staff" in i['src']:
                spec.append("Staff")
            if "Label_Weapon_Gun" in i['src']:
                spec.append("Gun")
            if "Label_Weapon_Melee" in i['src']:
                spec.append("Melee")
            if "Label_Weapon_Bow" in i['src']:
                spec.append("Bow")
            if "Label_Weapon_Harp" in i['src']:
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
        for i in item:
            if "Label_Race_Human" in i['src']:
                race.append("Human")
            if "Label_Race_Erune" in i['src']:
                race.append("Erune")
            if "Label_Race_Draph" in i['src']:
                race.append("Draph")
            if "Label_Race_Harvin" in i['src']:
                race.append("Harvin")
            if "Label_Race_Primal" in i['src']:
                race.append("Primal")
            if "Label_Race_Other" in i['src']:
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
        if "massive" in keyword.lower():
            return "450"
        elif "big" in keyword.lower():
            return "400"
        else:
            return "300"

    # convert a gbf.wiki relative hyperlink to absolute URI
    def convertLink(self, page):
        return "https://gbf.wiki" + page

    def initializeConnection(self):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["gbf-api-dev"]
        return db

    def start(self):
        listUrl = "https://gbf.wiki/All_Characters"
        page = requests.get(listUrl)
        soup = BeautifulSoup(page.content,'html.parser')
        results = soup.select("table tbody tr")
        for char in range(40,50):
            self.parseChar(results[char])

        #for x in self.dbChars.find():
        #    print(x)

        # drop db table after adding (dev only)
        #self.dbChars.drop()