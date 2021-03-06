#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial

This program creates a skeleton of
a classic GUI application with a menubar,
toolbar, statusbar and a central widget.

author: Jan Bodnar
website: zetcode.com
last edited: September 2011
"""

import sys
from PyQt4 import QtGui, QtWebKit, QtCore
import folium
import os
import src.tweet
import src.io_geojson


class View(QtGui.QMainWindow):

    def __init__(self):                 #calling the parent constructor
        super(View, self).__init__()

        self.initUI()


    def initUI(self):

        self.resize(350,250)
        self.center()
        os.makedirs('temp',exist_ok=True) #for saving directory
        #textEdit = QtGui.QTextEdit()         #adding a QTextEdit as the central widget
        self.web_view = QtWebKit.QWebView()
        self.map_dir = 'temp/folium_map.html' #so it knows where to save

        #now embed the folium map
        #self.map = folium.Map(location=[-112.323914,-33.29026],zoom_start=10)
        self.map = folium.Map(location=[33.29026,-112.323914],zoom_start=10)
        self.map.save(self.map_dir)
        self.web_view.load(QtCore.QUrl(self.map_dir))

        self.setCentralWidget(self.web_view)

        #creates a toolbar to exit, along with adding a keyboard shortcut
        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        openAction = QtGui.QAction('Open Tweets',self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Load tweets for marker display in map')
        openAction.triggered.connect(self.openAndDisplayMarkers)


        #added a ready message to the status bar
        self.statusBar().showMessage('Ready')

        #creating the file menu, and adding exit as an option
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        #creating a toolbar with an exit function
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAction)
        toolbar.addAction(openAction)

        #setting the window name
        self.setWindowTitle('Tweet Map')
        self.show()

    #making it appear in the center of the screen
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def openAndDisplayMarkers(self):
        print("openAndDisplayMarkers")
        file = QtGui.QFileDialog.getOpenFileName(self,caption='Open tweet file',filter='*.json') # for only json's
        if not file: #nothing selected, can't do anything
            return;

        tweets = []
        tweet_dict = src.io_geojson.read_twitter_data(file)
        for t in tweet_dict: # for every tweet in the tweet dictionary
            tweets.append(src.tweet.Tweet(t))

        #now that you've created an list of tweets implementing the Tweet class, use the saved
        #array to actually create the markers and get the latitude/longitude values from the points:
        long_sum = 0
        lat_sum = 0
        i = 0
        for t1 in tweets: #Going through each Tweet class element
            markerPoint = [t1.latitude,t1.longitude]
            if i < 5:
                print(markerPoint)
            #now create the actual marker:
            markerToAdd = folium.Marker(markerPoint)
            markerToAdd.add_to(self.map)

            #you need to recenter the map at the mean center of the points. That means that you have to calculate the mean center
            #as you go through all the points:
            long_sum = long_sum + markerPoint[0]
            lat_sum = lat_sum + markerPoint[1]
            i = i + 1

        print(len(tweets))
        mean_center_long = long_sum/len(tweets)
        mean_center_lat = lat_sum/len(tweets)
        mean_center = [mean_center_long,mean_center_lat]
        #now change the map location to there:
        self.map.location= mean_center

        self.map.save(self.map_dir)
        self.web_view.load(QtCore.QUrl(self.map_dir))


def main():

    app = QtGui.QApplication(sys.argv)
    ex = View()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()