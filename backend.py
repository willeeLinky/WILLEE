# -*- coding: utf-8 -*-
import serial ##000
import time
from datetime import date as Date
from datetime import timedelta
# import datetime as dt
from datetime import datetime as dt
import sqlite3
import os
import logging

def readDataFromGPIO():
    for i in range(0,50): # retries to to read if it fails
        serialLink = serial.Serial('/dev/ttyS0', 1200, timeout=5, bytesize=7)  # open serial port
        bulkData = serialLink.read(
            215)  # read 215 characters ; Normally all lines are at least once is those 215 charact.
        serialLink.close()  # close port
        clearData = bulkData.decode('utf8').split('\n')
        clearData.pop()  # removing last element, probably incomplete line
        clearData.pop(0)  # removing first element, probably incomplete line
        dictOfData = dict()
        for line in clearData:
            element = line.split(' ')  # setting a space between the key name, the value, and the end of line character
            element.pop()  # removing last element of each line, usually a useless character
            try:
                dictOfData[element[0]] = element[
                    1]  # a dictionnary gets rid of potential duplicate read and keeps the last
            except IndexError:
                logging.info("ErrorInRead")
                dictOfData = dict()
                break      
        if dictOfData != dict():
            break
        else:
            logging.info("Empty data. Need to read serial again.")
            time.sleep(0.5)
    return dictOfData

def readDataEmulate():
    """Emulates data read for dev purpose, when not connected to the Linky"""
    dictOfData = dict()
    dictOfData['BASE'] = str(123)
    dictOfData['PAPP'] = str(110)
    time.sleep(2)
    return dictOfData

def createTable(sqConnection, tableName):
    """Create a table in the database called -tablename-
    Tables have the form : day_2020_03_15"""
    sqlite_create_table_query = "CREATE TABLE " + tableName + " (joiningDate int PRIMARY KEY, power INTEGER);"
    cursor = sqConnection.cursor()
    cursor.execute(sqlite_create_table_query)
    return sqConnection

def connectToDatabase(database):
    """Connecting to the database"""
    sqliteConnection = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    return sqliteConnection

def insertDataAndCommit(sqliteConnection, tableName, tuple):  # tuple is a value of power. Ex : (450,)
    """insert data in the database detail"""
    sqlite_insert_with_param = "INSERT INTO '" + tableName + "' ('joiningDate','power')  VALUES (strftime('%s','now'), ?);"
    cursor = sqliteConnection.cursor()
    cursor.execute(sqlite_insert_with_param, tuple)
    for i in range(0,50): # retries to commit if it fails
        try:
            sqliteConnection.commit()
        except sqlite3.OperationalError:
            logging.info(str("sqlite3.OperationalError: database is locked ; Attempt: "+str(i+2)))
            time.sleep(0.5)
            continue
        break
    return sqliteConnection

def readTable(sqliteConnection, tableName):
    """read the database"""
    sqlite_select_query = "SELECT * FROM " + tableName
    cursor = sqliteConnection.cursor()
    cursor = cursor.execute(sqlite_select_query)
    return cursor.fetchall()

def closeDataBase(sqliteConnection):
    sqliteConnection.close()

def checkIfTodaysTableExists(sqliteConnection):
    """Tables have the form : day_2020_03_15"""
    cursorObj = sqliteConnection.cursor()
    tableList = cursorObj.execute('SELECT name from sqlite_master where type= "table"')
    tableList = cursorObj.fetchall()
    tableList = [str(tableElement[0]) for tableElement in tableList] #fetchall returns a list table names written in unicode and encapsulated in tuples. This lines decap
    today = str("day_" + str(Date.today()).replace("-", "_"))
    newDay = False
    if today not in tableList: # TODO OBSOLETE
        newDay = True
        createTable(sqliteConnection, today)
        logging.info("Table does not exists. Creating new called " + today)
    return today, newDay

def getDBTableList(SQLConnection):
    cursorObj = SQLConnection.cursor()
    tableList = cursorObj.execute('SELECT name from sqlite_master where type= "table"')
    tableList = cursorObj.fetchall()
    tableList = [str(tableElement[0]) for tableElement in tableList] #fetchall returns a list table names written in unicode and encapsulated in tuples. This lines decap
    print('======================')
    print('List of tables :')
    for table in tableList:
        print('\t' + table)
    print('======================')
    return tableList

def create_Table_CurrentData(sqConnection):
    """"""
    tableName = "CurrentData"
    sqlite_create_table_query = "CREATE TABLE " + tableName + " (dataname VARCHAR(32) PRIMARY KEY, datavalue VARCHAR(64));"
    cursor = sqConnection.cursor()
    cursor.execute(sqlite_create_table_query)
    return sqConnection

def insertDataAndCommitTable_CurrentData(SQLConnection, dataname, value):
    tableName = "CurrentData"
    sqlite_insert_with_param = "INSERT INTO '" + tableName + "' ('dataname','datavalue')  VALUES (?, ?);"
    cursor = SQLConnection.cursor()
    cursor.execute(sqlite_insert_with_param, (dataname, value))
    for i in range(0, 50): # retries to commit if it fails
        try:
            SQLConnection.commit()
        except sqlite3.OperationalError:
            logging.info(str("sqlite3.OperationalError: database is locked ; Attempt: "+str(i+2)))
            time.sleep(0.5)
            continue
        break
    return SQLConnection

def updateAndCommitTable_CurrentData(SQLConnection, dataname, value):
    sqlite_insert_with_param = '''UPDATE CurrentData SET datavalue = ? WHERE dataname = ?;'''
    cursor = SQLConnection.cursor()
    cursor.execute(sqlite_insert_with_param, (value, dataname))
    for i in range(0, 50): # retries to commit if it fails
        try:
            SQLConnection.commit()
        except sqlite3.OperationalError:
            logging.info(str("sqlite3.OperationalError: database is locked ; Attempt: "+str(i+2)))
            time.sleep(0.5)
            continue
        break
    return SQLConnection

def checkDatabaseIsNotEmptyAndFillInstead(SQLConnection, today):
    tableList = getDBTableList(SQLConnection)
    linkyData = readDataFromGPIO()
    if "BASE_daily_mean_power" not in tableList:
        create_Table_BASE_daily_mean_power(SQLConnection)
        time.sleep(1)
        insertDataAndCommitTable_BASE_daily_mean_power(SQLConnection, round(time.time()), int(linkyData['BASE']))
    if "CurrentData" not in tableList:
        create_Table_CurrentData(SQLConnection)
        time.sleep(1)
        insertDataAndCommitTable_CurrentData(SQLConnection, 'BASE', str(linkyData['BASE']))
        insertDataAndCommitTable_CurrentData(SQLConnection, 'PAPP', str(linkyData['PAPP']) )
    if today not in tableList:
        createTable(SQLConnection, today)
        time.sleep(1)
        insertDataAndCommit(SQLConnection, today, (str(int(linkyData['PAPP'])),))

def convertFromTimestampToWilleeDate(timeStamp):
    """WilleDate has the form day_2001_11_07 ; timestamp is the number of seconds elapsed since 1970"""
    day = dt.fromtimestamp(int(timeStamp)).date()
    return convertFromDateToWilleeDate(day)

def convertFromDateToWilleeDate(standardDate):
    return str("day_" + str(standardDate).replace("-", "_"))

def convertFromTimestampToDatetime(standardDate):
    return dt.fromtimestamp(int(standardDate))

def convertFromGUIInDateToTimeStamp(GUIInDate):
    date_datetimeFormat = dt(int(GUIInDate[0:4]), int(GUIInDate[5:7]), int(GUIInDate[8:10]))
    return date_datetimeFormat.timestamp()

def IndexOfClosestDate(listOfDates, targetDateString):
    targetDate = dt(int(targetDateString[0:4]), int(targetDateString[5:7]), int(targetDateString[8:10]))
    return listOfDates.index(min(listOfDates, key=lambda x: abs(x - targetDate)))

def create_Table_BASE_daily_mean_power(sqConnection): 
    """Create a table in the database called -tablename-
    Tables have the form 5632433 | 12111 (timestamp from 1970 ; BASE).
    The timestamp is bulk, taken at midnight every morning."""
    tableName = "BASE_daily_mean_power"
    sqlite_create_table_query = "CREATE TABLE " + tableName + " (instant int PRIMARY KEY, power INTEGER);"
    cursor = sqConnection.cursor()
    cursor.execute(sqlite_create_table_query)
    return sqConnection

def insertDataAndCommitTable_BASE_daily_mean_power(sqliteConnection, timestamp, powerBase):  # tuple is a value of power. Ex : (450,) 
    tableName = "BASE_daily_mean_power"
    sqlite_insert_with_param = "INSERT INTO '" + tableName + "' ('instant','power')  VALUES (?, ?);"
    cursor = sqliteConnection.cursor()
    cursor.execute(sqlite_insert_with_param, (timestamp, powerBase))
    for i in range(0, 50): # retries to commit if it fails
        try:
            sqliteConnection.commit()
        except sqlite3.OperationalError:
            logging.info(str("sqlite3.OperationalError: database is locked ; Attempt: "+str(i+2)))
            time.sleep(0.5)
            continue
        break
    return sqliteConnection



if __name__ == '__main__':

    ## CONSTANTES
    database = os.path.dirname(os.path.realpath(__file__))+'/DataBase.db'
    logFile = os.path.dirname(os.path.realpath(__file__))+'/logs_willee.log'
    logging.basicConfig(filename=logFile, level=logging.DEBUG, format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')

    ## INITIALISATION
    logging.info(str("Launching " + str(os.path.basename(__file__))))
    today = convertFromDateToWilleeDate(Date.today())
    SQLConnection = connectToDatabase(database)
    checkDatabaseIsNotEmptyAndFillInstead(SQLConnection, today)
    closeDataBase(SQLConnection)
    
    ## PROGRESSION
    while True:
        SQLConnection = connectToDatabase(database)
        linkyData = readDataFromGPIO() ##000
        #linkyData = readDataEmulate() ##000
        tableName, newDay = checkIfTodaysTableExists(SQLConnection)
        SQLConnection = insertDataAndCommit(SQLConnection, tableName, (str(int(linkyData['PAPP'])),))
        if newDay:
            insertDataAndCommitTable_BASE_daily_mean_power(SQLConnection, round(time.time()), int(linkyData['BASE']))
            records = readTable(SQLConnection, "BASE_daily_mean_power") 
            #records = readTable(SQLConnection, "BASE_daily_mean_power")  
            #print(records)
        updateAndCommitTable_CurrentData(SQLConnection, 'BASE', str(linkyData['BASE']))
        updateAndCommitTable_CurrentData(SQLConnection, 'PAPP', str(linkyData['PAPP']))
        closeDataBase(SQLConnection)

