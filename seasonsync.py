## SeasonSync
# SeasonSync is a Python automation tool that keeps wallpapers synchronized across multiple devices. 
# The application automatically detects seasons, holidays, and special events, then updates a shared "Current" wallpaper directory that can be consumed by desktops, laptops, and digital displays on a network. 
# It supports recurring events, dynamic date calculations (Easter, Thanksgiving, Memorial Day, etc.), and centralized background management.
#
# by William McCown
# began: 02/11/2017
# last updated: 11/08/2025

import datetime
from importlib.resources import files
import json
import os
import platform
import shutil
import time
from math import ceil

if platform.system() == "Windows":
    config_file = "config.windows.json"
else:
    config_file = "config.unraid.json"

with open(config_file, "r") as f:
    config = json.load(f)

birthdays = config["birthdays"]

BACKGROUND_ROOT = config["background_root"]

EVENTS = os.path.join(
    BACKGROUND_ROOT,
    config["events_folder"]
)

SEASONS = os.path.join(
    BACKGROUND_ROOT,
    config["seasons_folder"]
)

destination = os.path.join(
    BACKGROUND_ROOT,
    config["current_folder"]
)

currentDate = time.strftime("%x")   #shows current date in MM/DD/YY form
#currentDate = ("12/11/19") #DEBUG
currentYear = time.strftime("%y")   #shows current year in YY format
today = datetime.date.today()
#today = datetime.date(2019, 2, 11) #DEBUG


def main():
    banner()
    print ("Todays date is "  + currentDate)
    print()
    currentFiles = currentGet()
    newFiles = todaysBackgrounds(currentFiles)
    if newFiles != currentFiles:
        moveFiles(newFiles)
    else:
        print()
        print("No move required")


def banner():
    print("-" * 24)
    print("|                      |")
    print("|      SeasonSync      |")
    print("|  By: William McCown  |") 
    print("|                      |")
    print("-" * 24)
    print()

def week_of_month(dt):
    """ Returns the week of the month for the specified date.
    """

    first_day = dt.replace(day=1)

    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))

def extraDays(month, day, daysBefore, daysAfter):
    #today = datetime.date.today()
    y = int(time.strftime("%Y"))
    eventDates = []

    isEvent = datetime.date (today.year, month, day)
    daysToEvent = abs(isEvent - today)
    #print (isEvent)

    currentDay = isEvent
    while daysBefore >=0:
        cdString = str(currentDay.strftime("%m/%d/%y"))
        eventDates.append(cdString)
        currentDay = currentDay - datetime.timedelta(days=1)
        daysBefore = daysBefore - 1

    currentDay = isEvent
    while daysAfter >= 0:
        cdString = str(currentDay.strftime("%m/%d/%y"))
        eventDates.append(cdString)
        currentDay = currentDay + datetime.timedelta(days=1)
        daysAfter = daysAfter - 1

    #print (eventDates)
    if time.strftime("%m/%d/%y") in eventDates:
        return currentDate

    else:
        return "00/00/00"



def calcEaster():
    print("calculating Easter...")

    y = int(time.strftime("%Y"))

    # golden year - 1
    g = y % 19

    # offset
    e = 0

    # century
    c = y / 100

    # h is (23 - Epact) mod 30
    h = (c - c/4 - (8*c+13)/25 + 19*g + 15) % 30

    # number of days from March 21 to Paschal Full Moon
    i = h - (h/28) * (1 - (h/28) * (29/(h+1)) * ((21-g)/11))

    # weekday for Paschal Full Moon (0=Sunday)
    j = (y + y/4 + i + 2 - c + c/4) % 7

    # number of days from March 21 to Sunday on or before Paschal Full Moon
    p = i - j + e

    d = int(1 + (p + 27 + (p+6)/40) % 31)
    m = int(3 + (p+26)/30)

    easterDate = datetime.date(y, m, d)

    print("Easter:", end=" ")
    print(easterDate)
    print()

    easter = extraDays(m, d, 5, 1)

    return easter

def calcEMSWeek():
    print("calculating EMS Week...")

    EMSWeek = "00/00/00"
    now = datetime.datetime.now()
    currentYear = now.year

    # EMS Week starts on the Sunday of the week in which May 15 falls
    startLookingDay = datetime.date(currentYear, 5, 15)

    while startLookingDay.weekday() != 6:  # Sunday
        startLookingDay = startLookingDay + datetime.timedelta(days=1)

    emsWeekStart = startLookingDay

    print("EMS Week Starts:", end=" ")
    print(emsWeekStart)
    print()

    # Return currentDate if today falls within EMS Week
    d = emsWeekStart.day
    EMSWeek = extraDays(5, d, 0, 6)

    return EMSWeek

def calcFathersDay():
    print ("calculating Fathers Day...")
    fathersDay = "00/00/00"
    now = datetime.datetime.now()
    #now = datetime.date(2017, 5, 15) #DEBUG
    currentMonth = now.month
    currentDay = now.day
    currentWeekDay = now.weekday()
    currentMonday = ""
    currentYear = now.year
    #print (now)
    #print (currentYear)
    startLookingDay = datetime.date(currentYear, 6, 1)
    startLookingWeekday = startLookingDay.weekday()
    sundayNumber = 0

    while (sundayNumber !=3):
        startLookingDay = startLookingDay + datetime.timedelta(days=1)
        startLookingWeekday = startLookingDay.weekday()
        if (startLookingWeekday == 6):
            sundayNumber += 1
                        
    fathersDay = startLookingDay

    print ("Fathers Day:", end = " ")
    print (fathersDay)
    print ()

    ## To add extra days to Fathers Day
    d = fathersDay.day
    fathersDay = extraDays(6, d, 1,0)
    
    return (fathersDay)

def calcMardiGras():
    print("calculating Mardi Gras...")

    y = int(time.strftime("%Y"))

    # Easter calculation
    g = y % 19
    e = 0
    c = y / 100

    h = (c - c/4 - (8*c+13)/25 + 19*g + 15) % 30
    i = h - (h/28) * (1 - (h/28) * (29/(h+1)) * ((21-g)/11))
    j = (y + y/4 + i + 2 - c + c/4) % 7

    p = i - j + e

    d = int(1 + (p + 27 + (p+6)/40) % 31)
    m = int(3 + (p+26)/30)

    easter = datetime.date(y, m, d)

    mardiGrasDate = easter - datetime.timedelta(days=47)

    print("Mardi Gras:", end=" ")
    print(mardiGrasDate)
    print()

    d = mardiGrasDate.day
    m = mardiGrasDate.month

    mardiGras = extraDays(m, d, 1, 5)

    return mardiGras


def calcInaugurationDay():
    print("calculating Inauguration Day...")

    currentYear = datetime.datetime.now().year

    inauguration = "00/00/00"

    if currentYear % 4 == 1:

        inaugurationDate = datetime.date(
            currentYear,
            1,
            20
        )

        print("Inauguration Day:", inaugurationDate)
        print()

        inauguration = extraDays(1, 20, 1, 0)

    else:

        print("No Inauguration Day this year")
        print()

    return inauguration

def calcKentuckyDerby():
    print ("calculating Kentucky Derby...")
    kentuckyDerby = "00/00/00"
    now = datetime.datetime.now()
    #now = datetime.date(2017, 5, 15) #DEBUG
    currentMonth = now.month
    currentDay = now.day
    currentWeekDay = now.weekday()
    currentMonday = ""
    currentYear = now.year
    #print (now)
    #print (currentYear)
    startLookingDay = datetime.date(currentYear, 5, 1)
    startLookingWeekday = startLookingDay.weekday()

    while (startLookingWeekday !=5):
        startLookingDay = startLookingDay + datetime.timedelta(days=1)
        startLookingWeekday = startLookingDay.weekday()

    kentuckyDerby = startLookingDay

    ## To add extra days to Kentucky Derby
    #d = kentuckyDerby.day
    #kentuckyDerby = extraDays(5, d, 1,0)

    print ("Kentucky Derby:", end = " ")
    print (kentuckyDerby)
    print ()
    return (kentuckyDerby)

def calcMemorialDay():
    print ("calculating Memorial Day...")
    MemorialDay = "00/00/00"
    now = datetime.datetime.now()
    #now = datetime.date(2017, 5, 15) #DEBUG
    currentMonth = now.month
    currentDay = now.day
    currentWeekDay = now.weekday()
    currentMonday = ""
    currentYear = now.year
    #print (now)
    #print (currentYear)
    startLookingDay = datetime.date(currentYear, 5, 31)
    startLookingWeekday = startLookingDay.weekday()

    while (startLookingWeekday !=0):
        startLookingDay = startLookingDay - datetime.timedelta(days=1)
        startLookingWeekday = startLookingDay.weekday()

    MemorialDay = startLookingDay

    ## To add extra days to Memorial Day
    d = MemorialDay.day
    MemorialDay = extraDays(5, d, 1,0)

    print ("Memorial Day:", end = " ")
    print (MemorialDay)
    print ()
    return (MemorialDay)

def calcMLKJrDay():
    MLKJrDay = "00/00/00"
    now = datetime.datetime.now()
    currentMonth = now.month
    currentDay = now.day
    currentWeekDay = now.weekday()

    if (currentMonth == 1):
        if ((currentDay >= 15) and (currentDay <= 21)):
            if (currentWeekDay == 0):
                MLKJrDay = currentDate

    return (MLKJrDay)

def calcMothersDay():
    mothersDay = "00/00/00"
    now = datetime.datetime.now()
    #now = datetime.date(2019, 5, 12) #DEBUG
    currentMonth = now.month
    currentDay = now.day
    currentWeekDay = now.weekday()
    currentSunday = ""
    #print (now)

    if (currentMonth == 5):
        #print("It's May")
        mothersDay = now
        if ((currentDay >= 8) and (currentDay <= 15)):
            #print ("Day >= 8")
            while (currentWeekDay != 6):
                #print ("running while loop")
                now = now + datetime.timedelta(days=1)
                currentWeekDay = now.weekday()
                mothersDay = now
                #print (mothersDay)
            d = mothersDay.day
            mothersDay = extraDays(5, d, 1,0)
    return (mothersDay)


def calcValentinesDay():

    valentinesDay = extraDays(2, 14, 3,1)
    return valentinesDay

def calcDaylightSavingsTime():
    print("calculating Daylight Saving Time...")

    currentYear = datetime.datetime.now().year
    dst = []

    # DST STARTS: Second Sunday in March
    marchFirst = datetime.date(currentYear, 3, 1)

    while marchFirst.weekday() != 6:  # Sunday
        marchFirst += datetime.timedelta(days=1)

    dstStart = marchFirst + datetime.timedelta(days=7)

    print("DST Starts:", dstStart)

    d = dstStart.day
    dst1 = extraDays(3, d, 1, 0)
    dst.append(dst1)

    # DST ENDS: First Sunday in November
    novemberFirst = datetime.date(currentYear, 11, 1)

    while novemberFirst.weekday() != 6:  # Sunday
        novemberFirst += datetime.timedelta(days=1)

    dstEnd = novemberFirst

    print("DST Ends:", dstEnd)
    print()

    d = dstEnd.day
    dst2 = extraDays(11, d, 1, 0)
    dst.append(dst2)

    return dst

def calcIndependanceDay():

    independanceDay = extraDays(7, 4, 3, 1)
    return independanceDay

def calcPresidentsDay():

    presidentsDay = "00/00/00"
    now = datetime.datetime.now()
    currentMonth = now.month
    currentDay = now.day
    currentWeekDay = now.weekday()

    if (currentMonth == 2):
        if ((currentDay >= 15) and (currentDay <= 21)):
            if (currentWeekDay == 0):
                presidentsDay = currentDate

    return (presidentsDay)

def calcStPatricksDay():

    stPatricksDay = extraDays(3, 17, 2, 0)
    return stPatricksDay

def calcSuperBowl():
    print ("calculating Superbowl Sunday...")
    superBowl = "00/00/00"
    now = datetime.datetime.now()
    #now = datetime.date(2017, 5, 15) #DEBUG
    currentMonth = now.month
    currentDay = now.day
    currentWeekDay = now.weekday()
    currentMonday = ""
    currentYear = now.year
    #print (now)
    #print (currentYear)
    startLookingDay = datetime.date(currentYear, 2, 1)
    startLookingWeekday = startLookingDay.weekday()

    if (startLookingWeekday == 1):
        sundayNumber = 1
    else:
        sundayNumber = 0
    

    while (sundayNumber !=2):
        startLookingDay = startLookingDay + datetime.timedelta(days=1)
        startLookingWeekday = startLookingDay.weekday()
        if (startLookingWeekday == 6):
            sundayNumber += 1
                        
    superBowl = startLookingDay

    print ("Super Bowl Sunday:", end = " ")
    print (superBowl)
    print ()

    ## To add extra days to Super Bowl Sunday
    ## d = superBowl.day
    ## superBowl = extraDays(2, d, 1,0)
    
    return (superBowl)

def calcThanksgiving():
    print ("calculating Thanksgiving...")
    thanksgivingDay = "00/00/00"
    now = datetime.datetime.now()
    #now = datetime.date(2017, 5, 15) #DEBUG
    currentMonth = now.month
    currentDay = now.day
    currentWeekDay = now.weekday()
    currentThursday = ""
    currentYear = now.year
    #print (now)
    #print (currentYear)
    startLookingDay = datetime.date(currentYear, 11, 30)
    startLookingWeekday = startLookingDay.weekday()
    thursdayNumber = 0

    while (thursdayNumber !=1):
        startLookingDay = startLookingDay - datetime.timedelta(days=1)
        startLookingWeekday = startLookingDay.weekday()
        if (startLookingWeekday == 3):
            thursdayNumber += 1
                        
    thanksgivingDay = startLookingDay

    print ("Thanksgiving:", end = " ")
    print (thanksgivingDay)
    print ()

    ## To add extra days to Thanksgiving
    d = thanksgivingDay.day
    thanksgivingDay = extraDays(11, d, 3,1)
    
    return (thanksgivingDay)

def currentGet():
    """Find which backgrounds are currently active"""

    currentFile = os.path.join(
        destination,
        "current.txt"
    )

    currentFolder = "none"

    if os.path.exists(currentFile):

        try:
            with open(currentFile, "r") as f:
                currentFolder = f.read().strip()

            print(f"Current folder contains: {currentFolder}")

        except Exception as e:
            print(f"Current folder file is corrupted: {e}")

    else:
        print("Current folder file not available")

    print()

    return currentFolder

def todaysBackgrounds(currentFiles):    #determines which folder should be current
    current = currentFiles

    daylightSavingsTime = calcDaylightSavingsTime()
    easter = calcEaster()
    EMSWeek = calcEMSWeek()
    fathersDay = calcFathersDay()
    inaugurationDay = calcInaugurationDay()
    independanceDay = calcIndependanceDay()
    kentuckyDerby = calcKentuckyDerby()
    mardiGras = calcMardiGras()
    memorialDay = calcMemorialDay()
    MLKJrDay = calcMLKJrDay()
    mothersDay = calcMothersDay()
    presidentsDay = calcPresidentsDay()
    stPatricksDay = calcStPatricksDay()
    superBowl = calcSuperBowl()
    thanksgivingDay = calcThanksgiving()
    valentinesDay = calcValentinesDay()

    newFiles = ""

    isBirthday = False

    for person in birthdays:
        if (
            today.month == person["month"]
            and today.day == person["day"]
        ):
            print(f"Today is {person['name']}'s birthday!")
            isBirthday = True
            break

    if isBirthday: #someones birthday
        newFiles = 'birthday'

        ## HOLIDAYS

    elif currentDate >= '12/28/' + currentYear and currentDate <= '12/31/' + currentYear : #new years
        newFiles = 'new years'
    elif currentDate == '01/01/' + currentYear: #new years day
        newFiles = 'new years'
    elif currentDate == inaugurationDay: #inauguration day
        newFiles = 'inauguration day'
    elif currentDate == MLKJrDay: #mlk jr
        newFiles = 'martin luther king jr day'
    elif currentDate == superBowl: #Super Bowl Sunday
        newFiles = 'super bowl sunday'
    elif currentDate == '02/02/' + currentYear: #groundhog day
        newFiles = 'groundhog day'
    elif currentDate == valentinesDay: #valentines day
        newFiles = 'valentines day'
    elif currentDate == presidentsDay: #presidents day
        newFiles = 'presidents day'
    elif currentDate in daylightSavingsTime: #dst
        newFiles = 'dst'
    elif currentDate == mardiGras: #mardi gras
        newFiles = 'mardi gras'
    elif currentDate == stPatricksDay: #st patricks day
        newFiles = 'st patricks day'
    elif currentDate == '04/13/' + currentYear: #thomas jeffersons birthday
        newFiles = 'thomas jefferson'
    elif currentDate == easter: #easter
        newFiles = 'easter'
    elif currentDate == '05/05/' + currentYear: #cinco de mayo
        newFiles = 'cinco de mayo'
    elif currentDate == mothersDay: #mothers day
        newFiles = 'mothers day'
    elif currentDate == memorialDay: #memorial day
        newFiles = 'memorial day'
    elif currentDate == kentuckyDerby: #kentucky derby
        newFiles = 'kentucky derby'
    elif currentDate >= '05/06/' + currentYear and currentDate <= '05/12/' + currentYear : #nurses week
        newFiles = 'nurses week'
    elif currentDate == EMSWeek : #ems week
        newFiles = 'ems week'
    elif currentDate == '06/06/' + currentYear: #d day
        newFiles = 'd day'
    elif currentDate == '06/14/' + currentYear: #flag day
        newFiles = 'flag day'
    elif currentDate == fathersDay: #fathers day
        newFiles = 'fathers day'
    elif currentDate == independanceDay: #independance day
        newFiles = 'independance day'
    elif currentDate == '08/31/' + currentYear: #anniversary
        newFiles = 'anniversary'
    elif currentDate == '09/11/' + currentYear: #9/11
        newFiles = 'patriot day'
    elif currentDate == '10/08/18': #columbus day
        newFiles = 'columbus day'
    elif currentDate >= '10/01/' + currentYear and currentDate <= '10/31/' + currentYear : #halloween
        newFiles = 'halloween'
    elif currentDate == '11/01/' + currentYear: #all saints day
        newFiles = 'all saints day'
    elif currentDate == '11/02/' + currentYear: #all souls day
        newFiles = 'all souls day'
    elif currentDate == '11/05/' + currentYear: #guy fawkes day
        newFiles = 'guy fawkes day'
    elif currentDate == '11/11/' + currentYear: #veterans day
        newFiles = 'veterans day'
    elif currentDate == thanksgivingDay: #thanksgiving
        newFiles = 'thanksgiving'
    elif currentDate == '12/07/' + currentYear: #pearl harbor
        newFiles = 'pearl harbor'
    elif currentDate >= '12/01/' + currentYear and currentDate <= '12/26/' + currentYear: #christmas
        newFiles = 'christmas'

        ## SEASONS

    elif currentDate >= '03/19/' + currentYear and currentDate <= '06/20/' + currentYear : #spring
        newFiles = 'spring'
    elif currentDate >= '06/21/' + currentYear and currentDate <= '09/21/' + currentYear : #summer
        newFiles = 'summer'
    elif currentDate >= '09/22/' + currentYear and currentDate <= '12/20/' + currentYear : #autumn
        newFiles = 'autumn'
    elif currentDate >= '12/21/' + currentYear and currentDate <= '12/31/' + currentYear : #winter before year end
        newFiles = 'winter'
    elif currentDate >= '01/01/' + currentYear and currentDate <= '03/18/' + currentYear : #winter after new year
        newFiles = 'winter'

    print ('Next background should be: %s' % newFiles)
    return newFiles

def moveFiles(newFiles):   # move files into 'current' folder if needed
    movingFiles = newFiles
    movingFolder = ""
    if movingFiles == 'birthday': #someones birthday
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Birthday")

        ## HOLIDAYS

    elif movingFiles == 'new years': #new years
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "New Years")
    elif movingFiles == 'inauguration day': #inauguration day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Inauguration Day")
    elif movingFiles == 'martin luther king jr day': #MLK Jr
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "MLKJr")
    elif movingFiles == 'super bowl sunday': #super bowl sunday
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Super Bowl")
    elif movingFiles == 'groundhog day': #groundhog day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Groundhog Day")
    elif movingFiles == 'valentines day': #valentines day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Valentines Day")
    elif movingFiles == 'presidents day': #presidents day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Presidents Day")
    elif movingFiles == 'mardi gras': #mardi gras
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Mardi Gras")
    elif movingFiles == 'dst': #daylight savings time
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "DST")
    elif movingFiles == 'st patricks day': #st patricks day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "St Patricks Day")
    elif movingFiles == 'thomas jefferson': #thomas jeffersons birthday
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Thomas Jefferson")
    elif movingFiles == 'easter': #easter
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Easter")
    elif movingFiles == 'cinco de mayo': #cinco de mayo
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Cinco de Mayo")
    elif movingFiles == 'nurses week': #nurses week
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Nurses Week")
    elif movingFiles == 'ems week': #ems week
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "EMS Week")
    elif movingFiles == 'kentucky derby': #ems week
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Kentucky Derby")
    elif movingFiles == 'mothers day': #mothers day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Mothers Day")
    elif movingFiles == 'memorial day': #memorial day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Memorial Day")
    elif movingFiles == 'd day': #d day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "D Day")
    elif movingFiles == 'flag day': #flag day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Flag Day")
    elif movingFiles == 'fathers day': #fathers day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Fathers Day")
    elif movingFiles == 'independance day': #independance day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Independance Day")
    elif movingFiles == 'anniversary': #anniversary
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Anniversary")
    elif movingFiles == 'patriot day': #9/11
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Patriot Day")
    elif movingFiles == 'columbus day': #columbus day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Columbus Day")
    elif movingFiles == 'halloween': #halloween
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Halloween")
    elif movingFiles == 'all saints day': #all saints day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "All Saints Day")
    elif movingFiles == 'all souls day': #all souls day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "All Souls Day")
    elif movingFiles == 'guy fawkes day': #guy fawkes day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Guy Fawkes Day")
    elif movingFiles == 'veterans day': #veterans day
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Veterans Day")
    elif movingFiles == 'thanksgiving': #thanksgiving
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Thanksgiving")
    elif movingFiles == 'pearl harbor': #pearl harbor
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Pearl Harbor")
    elif movingFiles == 'christmas': #christmas
        movingFolder = os.path.join(BACKGROUND_ROOT, "Events", "Christmas")

                    ## SEASONS

    elif movingFiles == 'spring': #spring
        movingFolder = os.path.join(BACKGROUND_ROOT, "Seasons", "Spring")
    elif movingFiles == 'summer': #summer
        movingFolder = os.path.join(BACKGROUND_ROOT, "Seasons", "Summer")
    elif movingFiles == 'autumn': #autumn
        movingFolder = os.path.join(BACKGROUND_ROOT, "Seasons", "Autumn")
    elif movingFiles == 'winter': #winter
        movingFolder = os.path.join(BACKGROUND_ROOT, "Seasons", "Winter")

    print(destination)

    oldFileList = os.listdir(destination)
    numberOldFiles = 0
    print()
    print ('Removing the following files from ', destination)
    print("-" * 40)

    for files in oldFileList:      #delete the old backgrounds

        numberOldFiles += 1
        print(files)

        fullPath = os.path.join(destination, files)

        try:
            if os.path.isfile(fullPath):
                os.remove(fullPath)
            elif os.path.isdir(fullPath):
                shutil.rmtree(fullPath)
        except OSError as e:
            print(f"Error deleting {fullPath}: {e}")

    try:
        shutil.rmtree(
            os.path.join(destination, "Portrait")
        )
    except OSError:
        pass
    print ()
    print (numberOldFiles, ' old files removed')


    newFileList = os.listdir(movingFolder)
    print()
    print ('Adding the following files:')
    print("-" * 40)
    numberNewFiles = 0
    for files in newFileList:     #move the new backgrounds
        print (files)
        numberNewFiles += 1
        path = os.path.join(movingFolder, files)
        dst = os.path.join(destination, files)
        if (files != "Thumbs.db"):
            try :
                shutil.copy(path, dst)
            except:
                shutil.copytree(path, dst)
    print (numberNewFiles, ' new files added')
    writeFile(movingFiles)
    print ('Move completed')
    print ('Good job Mr. McCown')

def writeFile(movingFiles):

    currentFile = os.path.join(
        destination,
        "current.txt"
    )

    with open(currentFile, "w") as f:
        f.write(movingFiles)

    print()
    print("'Current' File updated")
    print()


main()
