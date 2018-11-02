import inspect
import tkinter as tk
from tkinter.ttk import *
import functools
import time
import json
import os
import pathlib
import threading
import pytest
import requests_mock
import sys
from gw2api import GuildWars2Client


#Holds data from data.txt
dataList = []
#Holds progress of achievements from users api
achievementList = []
g2 = GuildWars2Client()

class apiWindow:
    def saveKey(self):
        key = self.apiEntry.get()
        if len(key) > 30:
            g2 = GuildWars2Client(api_key= key,version ='v2')
            fileHandler = open("key.txt","w+")
            fileHandler.write(key)
            self.master.destroy()

    def __init__(self):
        master = tk.Tk()
        self.master = master
        master.title("Enter your api key")
        master.geometry("600x100")
        master.resizable(False,False)
        self.apiEntry = tk.Entry(master,width = 70)
        self.apiEntry.place(x=15,y=30)
        self.entryBtn = tk.Button(master,text = "Save Key",command = self.saveKey)
        self.entryBtn.place(x=260,y=60)
        master.mainloop()

def buildList(idnum):
    achievement = g2.achievements.get(id=idnum)
    try:
        name = achievement['name']
        dataList.append(achievement)
        return name
    except:
        return False

class firstTimeSetup:
    def __init__(self,achievementList):
        #Creates a window to display progress on downloading personal achievement progress
        master = tk.Tk()
        self.tempwindow = master
        master.title("First time setup")
        master.geometry('400x100')
        master.resizable(False,False)

        self.progbar = Progressbar(self.tempwindow,length = 350,maximum = len(achievementList)+100)
        self.progbar.place(x=25,y=40)
        self.tempLabel = tk.Label(self.tempwindow,text = "Getting Achievements")
        self.tempLabel.place(x=10,y=15)
        self.nameLabel = tk.Label(self.tempwindow)
        self.nameLabel.place(x=20,y=60)
        self.tempwindow.update()
        
        #Assigns names to achievements in achievementsList and updates results to progressbar
        i = 1
        for x in achievementList:
            name = buildList(x['id'])
            if name:
                self.nameLabel["text"] = name
                self.progbar['value'] = i
                self.tempwindow.update()
                i+= 1
        self.nameLabel["text"] = ""
        self.tempLabel["text"] = "Saving achievements to data.txt"
        self.progbar['value'] += 100
        self.tempwindow.update()
        
        #Saves data locally so there wont be data fetching every startup
        data = open("data.txt","w+")
        json.dump(dataList,data)
        data.close()
        self.tempwindow.destroy()

class mainWindow():
    def getAchievementProgress(self,idnum):
        for x in achievementList:
            if x["id"] == idnum:
                return x

    def getAchievementFromList(self,name):
        for item in self.data:
            if item["name"] == name:
                return item

    def updateLists(self):
    #sorts user achievements into 4 sub lists noncompleteList, allList, closeList, completeList
        for x in self.safeData:
            self.allList.append(x)
            progress = self.getAchievementProgress(x["id"])
            if progress["done"] == False:
                self.noncompleteList.append(x)
            else:
                self.completeList.append(x)
            if progress['current'] >= progress['max']-3:
                self.closeList.append(x)

    def setAll(self):
        self.data = dataList
        self.displayAll()

    def setClose(self):
        self.data = self.closeList
        self.displayAll()

    def setNoncomplete(self):
        self.data = self.noncompleteList
        self.displayAll()

    def setComplete(self):
        self.data = self.completeList
        self.displayAll()

    def displayAll(self):
        i = 0
        self.listBox.delete(0,tk.END)
        for item in self.data: 
            self.listBox.insert(i,item['name'])
            i += 1

    def showPage(self,x):
        name = str(self.listBox.get(self.listBox.curselection()))
        achievement = self.getAchievementFromList(name)
        progress = self.getAchievementProgress(achievement['id'])
        
        #frame for title and label
        self.nestFrame = tk.Frame(self.canvas,width = 580,height = 480,bg = "white")
        self.nestFrame.place(x=10,y=10)
        self.titleLabel = tk.Label(self.nestFrame,text = achievement["name"],bg = "white",font = (None,18))
        self.titleLabel.place(x=30,y=20)
        if achievement["description"] == "":
            descriptionText = achievement["requirement"]
        else:
            descriptionText = achievement["description"]
        self.descriptionLabel = tk.Label(self.nestFrame, text = descriptionText, bg = "white", font = (None,12), wraplength = 500, justify = "left")
        self.descriptionLabel.place(x=40,y=50)
        print("\n\nAchievement:")
        print(achievement)
        print("Bits:")
        try:
            for x in achievement['bits']:
                print(x['text'])
        except:
            print("Err")
            
        print("\nProgress:")
        print(progress)

    def __init__(self,master,dataList):
        #data will hold the working data for displaying in achievement window
        self.data = dataList
        self.safeData = dataList
        #Set of lists that will contain filtered achievements
        self.completeList = []
        self.allList = []
        self.closeList = []
        self.noncompleteList = []

        self.updateLists()
        #Main Window
        self.window = master
        self.window.title("Guild Wars 2 Achievement Tracker")
        self.window.geometry('800x500')
        self.window.resizable(False,False)

        #Achievement Window
        self.canvas = tk.Canvas(self.window,width=600,height=500, bg = 'grey')
        self.canvas.place(x=200,y=0)
        self.canvas.create_line(0,0,0,600,fill="black",width = 5)

        #List Window + Scrollbar
        self.listFrame = tk.Frame(self.window,bg = 'grey',width = 200,height = 500)
        self.listFrame.place(x=5,y=5)
        self.listBox = tk.Listbox(self.listFrame,width = 22,height = 19)
        self.scrollBar = tk.Scrollbar(self.listFrame, orient = "vertical", command = self.listBox.yview)
        self.listBox.config(yscrollcommand = self.scrollBar.set)
        self.listBox.bind('<<ListboxSelect>>',self.showPage)
        self.listBox.pack(side = "left", fill = "both",expand = 1)
        self.scrollBar.pack(side = "right", fill = "y")

        #CheckButton Boxes
        self.sSlayer = tk.IntVar()

        #Refresh List Button
        self.refreshBtn = tk.Button(text="Refresh",command = self.displayAll,width = 19)
        self.refreshBtn.place(x = 10, y = 465)

        #Top Menu
        self.menuBar = tk.Menu(self.window,tearoff = 0)

        self.viewMenu = tk.Menu(self.menuBar, tearoff = 0)
        self.viewMenu.add_command(label = "All achievements",command = self.setAll)
        self.viewMenu.add_command(label = "Close to completion", command = self.setClose)
        self.viewMenu.add_command(label = "All non-completed", command = self.setNoncomplete)
        self.viewMenu.add_command(label = "All completed", command = self.setComplete)

        self.menuBar.add_cascade(label = "View", menu = self.viewMenu)

        self.menuBar.add_command(label = "Api Key",command = apiWindow)        
        self.menuBar.add_command(label = "Quit",command = self.window.quit)

        self.window.config(menu = self.menuBar)

        self.displayAll()
        self.window.mainloop()

def main():
    #get or set the apikey to use
    try:
        apiKey = open("key.txt").read()
        #g2 = GuildWars2Client(api_key='6D2350F7-1A9C-B343-8CA5-2CB9EA6CE8FC103982B8-A207-4116-9004-8644686408F9',version='v2')
    except:
        apiWindow()

    #Creates client to get information from api
    g2 = GuildWars2Client(api_key= open("key.txt").read(),version='v2')
     
    #Launches the first time setup if list of achievements not found
    try:
        dataList = json.loads(open("data.txt").read())
        global achievementList
        achievementList = g2.accountachievements.get()

    except:
        achievementList = g2.accountachievements.get()
        firstTimeSetup(achievementList)
        dataList = json.loads(open("data.txt").read())
    
    #WIP - add categories checkboxes to bottom of listbox to sort view quickly
    #catList = g2.achievementscategories.get()
    #categoriesList = []
    #for x in catList:
    #    categoriesList.append(g2.achievementscategories.get(id = x))
    #print(categoriesList)
    window = tk.Tk()
    getMain = mainWindow(window,dataList)
main()