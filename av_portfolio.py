#!/usr/bin/env python3
# Fund portfolio retrival and forecast from Alpha Vantage
# Retrieves current quantity of shares from a Google sheet.
# Retreives current fund values and forecasts change in stock portfolio value using VTI and BND as proxies for overall market.
# Uses Adafruit 128x64 OLED Bonnet for Raspberry Pi[ID:3531]
# Requires getShares.py
# Issues Todo: elapsed time for percent change screen time zone issue
# James S. Lucas - 20200510
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from alpha_vantage.timeseries import TimeSeries
from time import sleep
import pytz, datetime
#import RPi.GPIO as GPIO
from getShares import getShares
from prettytable import PrettyTable

# import Adafruit_GPIO.SPI as SPI
import adafruit_ssd1306 

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

i2c = busio.I2C(board.SCL, board.SDA)

# 128x64 display with hardware I2C:
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Clear display.
disp.fill(0)
disp.show()
sleep(.1)

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
# font = ImageFont.load_default()

# Or alternatively load TTF fonts.  Make sure the .ttf font file is in the same directory as the python script.
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# JSL Load Custom Fonts
font14 = ImageFont.truetype('VCR_OSD_MONO_1.001.ttf', 14)
font16 = ImageFont.truetype('VCR_OSD_MONO_1.001.ttf', 16)
font17 = ImageFont.truetype('VCR_OSD_MONO_1.001.ttf', 17)
font18 = ImageFont.truetype('VCR_OSD_MONO_1.001.ttf', 18)
font20 = ImageFont.truetype('VCR_OSD_MONO_1.001.ttf', 20)
font22 = ImageFont.truetype('VCR_OSD_MONO_1.001.ttf', 22)
font24 = ImageFont.truetype('VCR_OSD_MONO_1.001.ttf', 24)
font26 = ImageFont.truetype('VCR_OSD_MONO_1.001.ttf', 26)

draw.text((x, 18),      "Initializing", font=font17, fill=255)
# Display image.
disp.image(image)
disp.show()
sleep(.1)

totalValueStocks = 0.0
totalValueBonds = 0.0
vtiInitial = 0.0
bndInitial = 0.0
vtiChangePct = 0.0
bndChangePct = 0.0
vtiDataTime = datetime.datetime.utcfromtimestamp(0)
bndDataTime = datetime.datetime.utcfromtimestamp(0)
menuNumber = 0
previous_menuNumber = 0
button_press_time = datetime.datetime.now()

# Input pins:
button_A = DigitalInOut(board.D5)
button_A.direction = Direction.INPUT
button_A.pull = Pull.UP

button_B = DigitalInOut(board.D6)
button_B.direction = Direction.INPUT
button_B.pull = Pull.UP

button_L = DigitalInOut(board.D27)
button_L.direction = Direction.INPUT
button_L.pull = Pull.UP

button_R = DigitalInOut(board.D23)
button_R.direction = Direction.INPUT
button_R.pull = Pull.UP

button_U = DigitalInOut(board.D17)
button_U.direction = Direction.INPUT
button_U.pull = Pull.UP

button_D = DigitalInOut(board.D22)
button_D.direction = Direction.INPUT
button_D.pull = Pull.UP

button_C = DigitalInOut(board.D4)
button_C.direction = Direction.INPUT
button_C.pull = Pull.UP

# Get current quotes
def getQuotes():
    latest_prices_stocks = {}
    latest_prices_bonds = {}
    totalValueStocks = 0.0
    totalValueBonds = 0.0
    vtiChangePct = 0.0
    bndChangePct = 0.0
    ticker_symbols_stocks = ['FSKAX','FSMAX','FSPSX','FXAIX','VTI','VTSAX']
    ticker_symbols_bonds = ['FXNAX','VBTLX','VIPSX', 'BND']
    shares = getShares()
    time_remaining = (len(ticker_symbols_stocks) + len(ticker_symbols_bonds)) * 15
    ts = TimeSeries(key='ALPHAVANTAGE_API_KEY')
    for ticker_symbol in ticker_symbols_stocks:
        data, meta_data = ts.get_intraday(symbol=ticker_symbol,interval='1min')
        latest = max(data)
        latest_prices_stocks[ticker_symbol] = data[latest]['4. close']
        price = data[latest]['4. close']
        if ticker_symbol == 'VTI':
            vtiInitial = float(price)
        totalValueStocks = totalValueStocks + (float(price) * shares[ticker_symbol])
        #Delay after each request to prevent exceeding Alpha Vantage request limit (5 / min)
        delayLoopStart = datetime.datetime.now()
        elapsedTime = datetime.datetime.now() - delayLoopStart
        while elapsedTime.seconds <= 14:
            disp.fill(0)
            disp.show()
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            elapsedTime = datetime.datetime.now() - delayLoopStart
            time_remaining = time_remaining - 1
            draw.text((x, 18),      "Initializing", font=font17, fill=255)
            draw.text((x, 48),     str(time_remaining), font=font17, fill=255)
            # Display image.
            disp.image(image)
            disp.show()
            sleep(1)
    for ticker_symbol in ticker_symbols_bonds:
        data, meta_data = ts.get_intraday(symbol=ticker_symbol,interval='1min')
        latest = max(data)
        latest_prices_bonds[ticker_symbol] = data[latest]['4. close']
        price = data[latest]['4. close']
        if ticker_symbol == 'BND':
            bndInitial = float(price)
        totalValueBonds = totalValueBonds + (float(price) * shares[ticker_symbol])
        if ticker_symbol != 'BND':
        #Delay after each request to prevent exceeding Alpha Vantage request limit (5 / min)
        delayLoopStart = datetime.datetime.now()
        elapsedTime = datetime.datetime.now() - delayLoopStart
        while elapsedTime.seconds <= 14:
            disp.fill(0)
            disp.show()
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            elapsedTime = datetime.datetime.now() - delayLoopStart
            time_remaining = time_remaining - 1
            draw.text((x, 18),      "Initializing", font=font17, fill=255)
            draw.text((x, 48),     str(time_remaining), font=font17, fill=255)
            # Display image.
            disp.image(image)
            disp.show()
            sleep(1)
    pct_stocks = totalValueStocks / (totalValueBonds + totalValueStocks)
    pct_bonds = totalValueBonds / (totalValueBonds + totalValueStocks)
    table = PrettyTable()
    table.field_names = ["Type","Symbol","Shares","Price","Value","Percent"]
    table.align = "r"
    for ticker_symbol in ticker_symbols_stocks:
        price = latest_prices_stocks[ticker_symbol] 
        table.add_row(
                [" ", 
                ticker_symbol,
                str('{0:.3f}'.format(shares[ticker_symbol])),
                str('{0:,.2f}'.format(float(price))),
                str('{0:,.2f}'.format(float(price) * shares[ticker_symbol])),
                " "
                ]
                )
    table.add_row(["Stocks"," "," "," "," "," "])
    table.add_row(["Total Stocks"," "," "," ",str('{0:,.2f}'.format(totalValueStocks)),str('{0:,.2f}'.format(pct_stocks))])
    table.add_row([" "," "," "," "," "," "])
    table.add_row(["Bonds"," "," "," "," "," "])
    for ticker_symbol in ticker_symbols_bonds:
        price = latest_prices_bonds[ticker_symbol]
        table.add_row(
                [" ",
                    ticker_symbol,
                    str('{0:.3f}'.format(shares[ticker_symbol])),
                    str('{0:,.2f}'.format(float(price))),
                    str('{0:,.2f}'.format(float(price) * shares[ticker_symbol])),
                    " "
                ]
                )
    table.add_row(["Total Bonds"," "," "," ",str('{0:,.2f}'.format(totalValueBonds)),str('{0:,.2f}'.format(pct_bonds))])
    table.add_row([" "," "," "," "," "," "])
    table.add_row(["Grand Total"," "," "," ",str('{0:,.2f}'.format((totalValueStocks + totalValueBonds)))," "])
    dataDate = datetime.datetime.now().date()
    now = datetime.datetime.now()
    dataDateString = now.strftime('%m/%d/%y %I:%M:%S')
    print(" ")
    print("Current Quote Data Retreived: " + dataDateString)
    print(table)
    print(" ")
    return totalValueStocks, totalValueBonds, vtiInitial, bndInitial, vtiChangePct, bndChangePct, dataDate

# Get change from initial VTI price
def getVTI(vtiInitial, vtiChangePct, vtiDataTime, mktStat, menuNumber):
    ts = TimeSeries(key='ALPHAVANTAGE_API_KEY')
    data, meta_data = ts.get_intraday(symbol='VTI',interval='1min',outputsize='full')
    latest = max(data)
    vtiTimeNowString = latest
    vtiTimeNowString = vtiTimeNowString.replace(' UTC+0000','')
    vtiTimeNow = datetime.datetime.strptime(vtiTimeNowString, '%Y-%m-%d %H:%M:%S')
    delayLoopStart = datetime.datetime.now()
    elapsedTime = datetime.datetime.now() - delayLoopStart
    while elapsedTime.seconds <= 14:
        elapsedTime = datetime.datetime.now() - delayLoopStart
        menuNumber = buttonCheck(button_A, button_B, button_C, button_U, button_D, button_L, button_R, mktStat, menuNumber)
        sleep(.01)
    if vtiTimeNow > vtiDataTime:
        price = data[latest]['4. close']
        VTI = float(price)
        vtiChangePct = (VTI - vtiInitial) / vtiInitial
        vtiDataTime = vtiTimeNow
        print("Current VTI Data Retreived VTI = " + str(VTI) + " " + str(vtiDataTime) + " Change Pct = " + str(vtiChangePct))
    else:
        print("Retrived old VTI Data, Ignoring. vtiDataTime " + str(vtiDataTime) + " vtiTimeNow " + str(vtiTimeNow))
    return vtiChangePct, vtiDataTime

# Get change from initial BND price
def getBND(bndInitial, bndChangePct, bndDataTime, mktStat, menuNumber):
    ts = TimeSeries(key='ALPHAVANTAGE_API_KEY')
    data, meta_data = ts.get_intraday(symbol='BND',interval='1min',outputsize='full')
    latest = max(data)
    bndTimeNowString = latest
    bndTimeNowString = bndTimeNowString.replace(' UTC+0000','')
    bndTimeNow = datetime.datetime.strptime(bndTimeNowString, '%Y-%m-%d %H:%M:%S')
    delayLoopStart = datetime.datetime.now()
    elapsedTime = datetime.datetime.now() - delayLoopStart
    while elapsedTime.seconds <= 14:
        elapsedTime = datetime.datetime.now() - delayLoopStart
        menuNumber = buttonCheck(button_A, button_B, button_C, button_U, button_D, button_L, button_R, mktStat, menuNumber)
        sleep(1)
    if bndTimeNow > bndDataTime:
        price = data[latest]['4. close']
        BND = float(price)
        bndChangePct = (BND - bndInitial) / bndInitial
        bndDataTime = bndTimeNow
        print("Current BND Data Retreived BND = " + str(BND) + " " + str(bndDataTime) + " Change Pct = " + str(bndChangePct))
    else:
        print("Retrived old BND Data, Ignoring. bndDataTime " + str(bndDataTime) + " bndTimeNow " + str(bndTimeNow))
    return bndChangePct, bndDataTime

def marketCheck(dataDate):
    now = datetime.datetime.now().strftime('%H%M')
    dayOfWeek = datetime.datetime.today().weekday()
    diff = datetime.date.today() - dataDate
    # Check to see if the market is open
    if '0630' <= now <= '1300' and dayOfWeek < 5:
        mktStat = 'Opn'
    else:
        mktStat = 'Clsd'
    # Get previous close quotes if 2am and Tues-Sat and it's been at least one day since last update
    if now >= '0200' and 1 < dayOfWeek < 6 and diff.days >= 0.8:
        dataToGet = 'PREV_CLOSE'
    # Get current VTI and BND if time is between 6:30am - 1:30pm M-F
    elif '0630' <= now <= '1330' and dayOfWeek < 5:
        dataToGet = 'UPDATE'
    else:
        dataToGet = 'NONE'
    return mktStat, dataToGet

def writeMessage(totalValueStocks, totalValueBonds, vtiChangePct, vtiDataTime, bndChangePct, bndDataTime, mktStat, menuNumber):
    forecastStocks = totalValueStocks * (1.0 + vtiChangePct)
    forecastBonds = totalValueBonds * (1.0 + bndChangePct)
    forecastTotalValue = forecastStocks + forecastBonds
    forecastPctBonds = forecastBonds / forecastTotalValue
    forecastDuration = (1500000 - forecastTotalValue)/(forecastTotalValue * .06 + 24000)
    forecastYears, forecastMonths = divmod(forecastDuration, 1)
    forecastMonths = forecastMonths * 12
    vtiElapsedTime = datetime.datetime.utcnow() - vtiDataTime
    timezoneLocal = pytz.timezone('America/Los_Angeles')
    utc = pytz.utc
    vtiDataTimeLocal = utc.localize(vtiDataTime).astimezone(timezoneLocal)
    if forecastYears > 1:
        yearsText = " Yrs "
    else:
        yearsText = " Yr "
    if forecastMonths > 1:
        monthsText = " Mnths "
    else:
        monthsText = " Mnth "

    messages = []
    messages.append('${:,.0f}'.format(forecastTotalValue))                                                           #0
    messages.append('{0:.1f}'.format(vtiChangePct*100) +"%" + " " + mktStat)                                         #1
    messages.append('{0:.1f}'.format(forecastPctBonds*100) + "%")                                                    #2
    messages.append(str(vtiElapsedTime))                                                                             #3
    messages.append(vtiDataTimeLocal.strftime("%m/%d/%y"))                                                           #4
    messages.append(vtiDataTimeLocal.strftime("%I:%M %p"))                                                           #5
    if forecastYears == 0:
        messages.append('{0:.0f}'.format(forecastMonths) + monthsText)                                                #6
    elif forecastMonths == 0:
        messages.append('{0:.0f}'.format(forecastYears) + yearsText)                                                  #6
    else:
        messages.append('{0:.0f}'.format(forecastYears) + yearsText + '{0:.0f}'.format(forecastMonths) + monthsText)  #6

    # Menu numbers:
    #  0: Forecast Value
    #  1: Market Change % and Market Status
    # 11: Market Change % and Market Status
    #  2: Percent Bonds
    #  3: Time to 1.0 M
    #  4: All
    #  5: Blank

    if menuNumber == 0:
        # Display Forecast Value
        disp.fill(0)
        disp.show()
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((x, 0),        "Portfolio Value", font=font14, fill=255)
        draw.text((x, 32),        messages[0], font=font22, fill=255)
        # Display image.
        disp.image(image)
        disp.show()
        sleep(.05)

    if menuNumber == 1:
        # Display Market Change % and Market Status
        disp.fill(0)
        disp.show()
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((x, 0),        "Daily Gain", font=font14, fill=255)
        draw.text((x, 18),        messages[1], font=font18, fill=255)
        draw.text((x, 48),        messages[3], font=font14, fill=255)
        # draw.text((x, 48),        messages[4], font=font18, fill=255)
        # Display image.
        disp.image(image)
        disp.show()
        sleep(.05)

    if menuNumber == 11:
        # Display Market Change %, Market Status and Date & Time of close
        disp.fill(0)
        disp.show()
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((x, 0),        "Daily Gain", font=font14, fill=255)
        draw.text((x, 16),        messages[1], font=font18, fill=255)
        draw.text((x, 32),        messages[4], font=font18, fill=255)
        draw.text((x, 48),        messages[5], font=font18, fill=255)
        # Display image.
        disp.image(image)
        disp.show()
        sleep(.05)

    if menuNumber == 2:
        # Display Percent Bonds
        disp.fill(0)
        disp.show()
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((x,0),         "Bond Holdings", font=font16, fill=255)
        draw.text((x, 32),        messages[2], font=font20, fill=255)
        # Display image.
        disp.image(image)
        disp.show()
        sleep(.05)

    if menuNumber == 3:
        # Display Time to $1.0M
        disp.fill(0)
        disp.show() 
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((x,0),         "Time to $1.5M", font=font16, fill=255)
        draw.text((x,32),        messages[6], font=font16, fill=255)
        # Display image.
        disp.image(image)
        disp.show()
        sleep(.05)

    if menuNumber == 4:
        # All Display
        disp.fill(0)
        disp.show()
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((x,0),         messages[0], font=font18, fill=255)
        draw.text((x,16),        messages[1], font=font18, fill=255)
        draw.text((x,32),        messages[2], font=font18, fill=255)
        draw.text((x,48),        messages[6], font=font18, fill=255)
        # Display image.
        disp.image(image)
        disp.show()
        sleep(.05)

    if menuNumber == 5:
        # Blank display
        disp.fill(0)
        disp.show()
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        sleep(.05)

    #if menuNumber == 99:
        #Cycling display
        #cycleList = [0, 1, 2, 3, 4]
        #i = 0
        #while i < 6:
            #writeMessage(
                    #totalValueStocks,
                    #totalValueBonds,
                    #vtiChangePct,
                    #vtiDataTime,
                    #bndChangePct,
                    #bndDataTime,
                    #mktStat,
                    #cycleList[i]
                    #)
            #sleep(5)
            #i += 1

    return

def buttonCheck(button_A, button_B, button_C, button_U, button_D, button_L, button_R, mktStat, menuNumber):
    global previous_menuNumber
    global button_press_time

    elapsed_time = datetime.datetime.now() - button_press_time

    if elapsed_time.total_seconds() > 30:
        if menuNumber != 5:
            previous_menuNumber = menuNumber
            menuNumber = 5

    # Note Normally OPEN switch so use not
    if not button_C.value:
        # Joystick button Display all
        button_press_time = datetime.datetime.now()
        if menuNumber < 4:
            previous_menuNumber = menuNumber
            menuNumber = 4
        else:
            menuNumber = previous_menuNumber
    elif not button_A.value:
        # Lower left button. Blank Display
        button_press_time = datetime.datetime.now()
        if menuNumber != 5:
            previous_menuNumber = menuNumber
            menuNumber = 5
    elif not button_B.value:
        # Upper ritght button. Turn display back on
        button_press_time = datetime.datetime.now()
        menuNumber = previous_menuNumber
    elif not button_D.value:
        # Joystick down. Advance up to next menu.
        button_press_time = datetime.datetime.now()
        if menuNumber == 0:
            menuNumber = 1
        elif menuNumber == 1 or menuNumber == 11:
            menuNumber = 2
        elif menuNumber == 2:
            menuNumber = 3
        elif menuNumber == 3:
            menuNumber = 4
        elif menuNumber == 4:
            menuNumber = 0
    elif not button_U.value:
        # Joystick up. Advance down to next menu.
        button_press_time = datetime.datetime.now()
        if menuNumber == 4:
            menuNumber = 3
        elif menuNumber == 3:
            menuNumber = 2
        elif menuNumber == 2:
            menuNumber = 1
        elif menuNumber == 1 or menuNumber == 11:
            menuNumber = 0
        elif menuNumber == 0:
            menuNumber = 4
    elif not button_L.value or not button_R.value:
        # Joystick left or right. Go between menu 1 and 11.
        button_press_time = datetime.datetime.now()
        if menuNumber == 1:
            menuNumber = 11
        elif menuNumber == 11:
            menuNumber = 1
    if (
        not button_U.value or not button_D.value 
        or not button_L.value or not button_R.value 
        or not button_C.value or not button_A.value 
        or not button_B.value or menuNumber == 5):
            writeMessage(totalValueStocks, totalValueBonds, vtiChangePct, vtiDataTime, bndChangePct, bndDataTime, mktStat, menuNumber)
    return menuNumber

try:
    totalValueStocks, totalValueBonds, vtiInitial, bndInitial, vtiChangePct, bndChangePct, dataDate = getQuotes()
    mktStat, dataToGet = marketCheck(dataDate)
    vtiChangePct, vtiDataTime = getVTI(vtiInitial, vtiChangePct, vtiDataTime, mktStat, menuNumber)
    bndChangePct, bndDataTime = getBND(bndInitial, bndChangePct, bndDataTime, mktStat, menuNumber)
    writeMessage(totalValueStocks, totalValueBonds, vtiChangePct, vtiDataTime, bndChangePct, bndDataTime, mktStat, menuNumber)
    while 1:
        mktStat, dataToGet = marketCheck(dataDate)
        if dataToGet == 'PREV_CLOSE':
            totalValueStocks, totalValueBonds, vtiInitial, bndInitial, vtiChangePct, bndChangePct, dataDate = getQuotes()
            writeMessage(totalValueStocks, totalValueBonds, vtiChangePct, vtiDataTime, bndChangePct, bndDataTime, mktStat, menuNumber)
        if dataToGet == 'UPDATE':
            vtiChangePct, vtiDataTime = getVTI(vtiInitial, vtiChangePct, vtiDataTime, mktStat, menuNumber)
            bndChangePct, bndDataTime = getBND(bndInitial, bndChangePct, bndDataTime, mktStat, menuNumber)
            if vtiChangePct > 0.09 or bndChangePct > 0.09:
                menuNumber = 0
            writeMessage(totalValueStocks, totalValueBonds, vtiChangePct, vtiDataTime, bndChangePct, bndDataTime,  mktStat, menuNumber)
        writeMessage(totalValueStocks, totalValueBonds, vtiChangePct, vtiDataTime, bndChangePct, bndDataTime, mktStat, menuNumber)
        # Delay for a bit but continue to check for button press
        delayLoopStart = datetime.datetime.now()
        elapsedTime = datetime.datetime.now() - delayLoopStart
        while elapsedTime.seconds <= 600:
            elapsedTime = datetime.datetime.now() - delayLoopStart
            menuNumber = buttonCheck(button_A, button_B, button_C, button_U, button_D, button_L, button_R, mktStat, menuNumber)
            sleep(.01)
        menuNumber = buttonCheck(button_A, button_B, button_C, button_U, button_D, button_L, button_R, mktStat, menuNumber)

except KeyboardInterrupt:
    # Clear display. CLEARING DISPLAY DOES NOT SEEM TO BE WORKING
    disp.fill(0)
    disp.show()
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    sleep(.4)
