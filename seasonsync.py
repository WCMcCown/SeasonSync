## SeasonSync
# SeasonSync is a Python automation tool that keeps wallpapers synchronized across multiple devices. 
# The application automatically detects seasons, holidays, and special events, then updates a shared "Current" wallpaper directory that can be consumed by desktops, laptops, and digital displays on a network. 
# It supports recurring events, dynamic date calculations (Easter, Thanksgiving, Memorial Day, etc.), and centralized background management.
#
# by William McCown
# began: 02/11/2017
# last updated: 11/08/2025

import datetime, json, time, os, shutil, smtplib
from math import ceil

with open('config.json') as f:
    config = json.load(f)

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
#currentDate = ("12/19 /19") #DEBUG
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
    y = int(time.strftime("%Y"))
    # golden year - 1
    g = y % 19
    # offset
    e = 0
    # century
    c = y/100
    # h is (23 - Epact) mod 30
    h = (c-c/4-(8*c+13)/25+19*g+15)%30
    # number of days from March 21 to Paschal Full Moon
    i = h-(h/28)*(1-(h/28)*(29/(h+1))*((21-g)/11))
    # weekday for Paschal Full Moon (0=Sunday)
    j = (y+y/4+i+2-c+c/4)%7
    # number of days from March 21 to Sunday on or before Paschal Full Moon
    # p can be from -6 to 28
    p = i-j+e
    d = int(1+(p+27+(p+6)/40)%31)
    m = int(3+(p+26)/30)
    #print(y, m, d)
    #easter = datetime.date(y,m,d)
    easter = extraDays(m, d, 5,1)
    return (easter)

def calcEMSWeek():
    print ("calculating EMS Week...")
    EMSWeek = "00/00/00"
    now = datetime.datetime.now()
    #now = datetime.date(2017, 5, 15) #DEBUG
    currentMonth = now.month
    currentDay = now.day
    currentWeekDay = now.weekday()
    currentMonday = ""
    currentYear = now.year
    #print (now)
    #print (currentYear)
    startLookingDay = datetime.date(currentYear, 5, 15)

    if (currentMonth == 5):
        #print("It's May")
        if (currentDay >= 15):
            EMSWeek = startLookingDay
            #print ("Day >= 15")
            while (currentWeekDay != 6):
                #print ("running while loop")
                EMSWeek = EMSWeek + datetime.timedelta(days=1)
                currentWeekDay = EMSWeek.weekday()
                #EMSWeek = now
                #print (EMSWeek)
            d = EMSWeek.day
            #print(d)
            EMSWeek = extraDays(5, d, 0,6)

    print ()
    #print (EMSWeek)
    return (EMSWeek)

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
    y = int(time.strftime("%Y"))
    # golden year - 1
    g = y % 19
    # offset
    e = 0
    # century
    c = y/100
    # h is (23 - Epact) mod 30
    h = (c-c/4-(8*c+13)/25+19*g+15)%30
    # number of days from March 21 to Paschal Full Moon
    i = h-(h/28)*(1-(h/28)*(29/(h+1))*((21-g)/11))
    # weekday for Paschal Full Moon (0=Sunday)
    j = (y+y/4+i+2-c+c/4)%7
    # number of days from March 21 to Sunday on or before Paschal Full Moon
    # p can be from -6 to 28
    p = i-j+e
    d = int(1+(p+27+(p+6)/40)%31)
    m = int(3+(p+26)/30)
    #print(y, m, d)
    easter = datetime.date(y,m,d)
    #easter = datetime.date(d + "/" + m + "/" + y)
    mardiGras = easter - datetime.timedelta(days=47)
    d = mardiGras.day
    m = mardiGras.month
    #print (m,d)
    mardiGras = extraDays(m,d,1,5)
    return (mardiGras)


def calcInaugurationDay():
    inaugurationDay = "00/00/00"
    y = int(time.strftime("%Y"))
    dayMonth = str(time.strftime("%m/%d/"))
    if (y - 1789) % 4 == 0 and dayMonth == "01/20/":
        inaugurationDay = currentDate

    return (inaugurationDay)

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

    dst = []
    now = datetime.datetime.now()
    #now = datetime.date(2019, 3, 10) #DEBUG
    currentMonth = now.month
    currentDay = now.day
    currentWeekDay = now.weekday()

    if (currentMonth == 3):
        #print ("It's March")
        if ((currentDay >= 8) and (currentDay <= 15)):
            #print ("It's DST range")
            d = currentDay
            #print (d)
            while (currentWeekDay != 6):
                #print ("running while loop")
                now = now + datetime.timedelta(days=1)
                currentWeekDay = now.weekday()
                dstday = now
                #print (day)
                d = dstday.day
            dst1 = extraDays(3, d, 1,0)
            dst.append(dst1)

    if (currentMonth == 11):
        if ((currentDay >= 1) and (currentDay <= 7)):
            d = currentDay
            while (currentWeekDay != 6):
                #print ("running while loop")
                now = now + datetime.timedelta(days=1)
                currentWeekDay = now.weekday()
                dstday = now
                #print (day)
                d = dstday.day
            dst2 = extraDays(11, d, 1,0)
            dst.append(dst2)


    #print (dst)
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

def currentGet():   #find which backgrounds are in current folder

    f=("%scurrent.txt" % destination)
    currentFile = 'current.txt'
    currentInfo = ("")
    currentFolder = 'none'

    if os.path.exists(f): # if the text file is there
        try:
            f=open(destination + 'current.txt', 'r')    #see if there is a current txt file
            currentFolder = f.read()
            f.close
            currentInfo = ('Current folder contains: %s' % currentFolder)
        except:
            currentInfo = ('Current folder file is corrupted')

    else:       # if the text file id not there
        currentInfo = ('Current folder file not available')
    print (currentInfo)
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
    birthday = [ '03/13/' + currentYear,
                 '12/01/' + currentYear,
                 '12/04/' + currentYear,
                 '12/11/' + currentYear,
                ]
    if currentDate in birthday: #someones birthday
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
    elif currentDate >= '10/01/' + currentYear and currentDate <= '10/31' + currentYear : #halloween
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

    oldFileList = os.listdir(destination)
    numberOldFiles = 0
    print()
    print ('Removing the following files:')
    print("-" * 40)
    for files in oldFileList:      #delete the old backgrounds
        numberOldFiles += 1
        print(files)
        try:
            os.remove(destination + files)
            shutil.rmtree(destination + files)
        except OSError:
            pass

    try:
        shutil.rmtree(destination + '/Portrait')
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
        path = movingFolder + "/" + files
        dst = destination + "/" + files
        if (files != "Thumbs.db"):
            try :
                shutil.copy(path, dst)
            except:
                shutil.copytree(path, dst)
    print (numberNewFiles, ' new files added')
    writeFile(movingFiles)
    print ('Move completed')
    print ('Good job Mr. McCown')

def writeFile(movingFiles):       # makes new file with current folder
    currentBackgrounds = movingFiles
    f=open(destination + 'current.txt', 'w')
    f.truncate()
    f.write (currentBackgrounds)
    f.close
    print('\n')
    print("'Current' File updated")
    print()


main()
