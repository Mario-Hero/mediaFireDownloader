#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Created by Mario Chen, 21.03.2022, Shenzhen
# My Github site: https://github.com/Mario-Hero

import os
import sys
import time
import requests
import threading
from urllib.parse import unquote

try:
    import wget
except ImportError:
    os.system('pip install wget')
    import wget
try:
    from bs4 import BeautifulSoup
except ImportError:
    os.system('pip install bs4')
    from bs4 import BeautifulSoup

try:
    import chardet
except ImportError:
    os.system('pip install chardet')
    import chardet

# you can change it >>>>>

#DOWNLOAD_PATH = os.getcwd()  # 文件下载位置 the download path
DOWNLOAD_PATH = 'E:\\VirtualBox\\写真待分类\\'  # 文件下载位置 the download path

# <<<<< you can change it


HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"}
DOWNLOAD_AS_GROUP = True
TARGET_PATH = 'E:\\VirtualBox\\VirtualBox\\写真\\果儿\\'
READ_TARGET_PATH = False #这里是我自己设计的部分，在爬下载链接时顺便把标题给爬了下来，用来判断硬盘里是否已经下载过该文件，读者不用管


class mediaFireDownloader:
    def __init__(self, downloadPath):
        self.GAP_TIME = 120
        self.urlList = []
        self.nowDownload = []
        self.nowDownloadName = []
        self.downloadPath = downloadPath
        self.targetPath = TARGET_PATH
        self.MAX_THREAD = 2
        self.currentList = []
        self.totalList = []
        self.waitMode = False
        self.speedDelta = 0
        self.speed = 0
        self.sleepTime = 3
        self.historyFileName = 'MediaHistory.txt'
        self.queueFileName = 'MediaQueue.txt'
        self.finishHistory = []
        self.read2Quit = False
        self.firstRun = True
        self.speedZeroTime = 0
        self.speedZeroWait = False
        self.restartDownload = False
        self.downloadFolders = []
        self.readHistory()
        self.readQueue()
        # print(self.finishHistory)

    def readQueue(self):
        if os.path.exists(os.path.join(os.getcwd(), self.queueFileName)):
            with open(os.path.join(os.getcwd(), self.queueFileName), 'r', encoding='utf-8') as queueFile:
                self.urlList = queueFile.read().splitlines()
                newUrlList = []
                [newUrlList.append(i) for i in self.urlList if not (i in newUrlList)]
                self.urlList = newUrlList.copy()
        else:
            with open(os.path.join(os.getcwd(), self.queueFileName), 'w', encoding='utf-8') as queueFile:
                pass

    def writeQueue(self):
        with open(os.path.join(os.getcwd(), self.queueFileName), 'w', encoding='utf-8') as queueFile:
            for url in self.urlList:
                if url:
                    if not (url in self.nowDownload):
                        queueFile.write(url + '\n')

    def writeHistory(self):
        with open(os.path.join(os.getcwd(), self.historyFileName), 'w', encoding='utf-8') as historyFile:
            for his in self.finishHistory:
                historyFile.write(his.strip() + '\n')

    def readHistory(self):
        if os.path.exists(os.path.join(os.getcwd(), self.historyFileName)):
            with open(os.path.join(os.getcwd(), self.historyFileName), 'r', encoding='utf-8') as historyFile:
                self.finishHistory = historyFile.read().splitlines()
                newHisList = []
                [newHisList.append(i) for i in self.finishHistory if not (i in newHisList)]
                self.finishHistory = newHisList.copy()
        else:
            with open(os.path.join(os.getcwd(), self.historyFileName), 'w', encoding='utf-8') as historyFile:
                pass

    def addUrl(self, url):
        if url:
            url = url.strip()
            if url.startswith('http'):
                if url.startswith('http://adf.ly') or url.startswith('http://ouo.io'):
                    sPos = url.find('?s=')
                    if sPos != -1:
                        url = unquote(url[sPos + 3:])
                    else:
                        url = url[url.rfind('http'):]
                '''if not url.startswith('https://www.mediafire.com'):
                    sPos = url.find('?s=')
                    if sPos != -1:
                        url = unquote(url[sPos + 3:])
                    else:
                        url = url[url.rfind('http'):]'''
                if not (url in self.urlList) and not (url in self.finishHistory):
                    # print(url)
                    self.urlList.append(url)
                    self.writeQueue()

    def printLine(self, printMessage, forever=True):
        if forever:
            sys.stdout.write('\r' + printMessage + '\n')
            sys.stdout.flush()
        else:
            sys.stdout.write('\r' + printMessage)
            sys.stdout.flush()

    def download(self, url):
        try:
            resp = requests.get(url, headers=HEADER, timeout=5).content
        except requests.exceptions.RequestException as e:
            print(e.__class__.__name__)
            self.writeQueue()
            return
        soup = BeautifulSoup(resp, 'lxml')
        if 'mediafire.' in url:
            downloadButton = soup.find('a', {'id': 'downloadButton'})
        elif 'zippyshare.' in url:
            print('Wrong url: ' + url)
            return
            downloadButton = soup.find('a', {'id': 'dlbutton'})
        else:
            print('Wrong url: ' + url)
            return
        if downloadButton:
            fileUrl = downloadButton.get('href')
            # print(url)
            fileName = fileUrl[fileUrl.rfind('/') + 1:]
            try:
                fileName = unquote(fileName)
            except:
                pass
            if '+' in fileName:
                fileName = fileName.replace('+', ' ')
            # if '\\' in fileName:
            #    fileName.replace('\\', ' ')
            path = os.path.join(self.downloadPath, fileName)
            if not os.path.exists(path):
                if not (fileName in self.nowDownloadName):
                    self.nowDownloadName.append(fileName)
                self.printLine('Downloading: ' + fileName)
                try:
                    wget.download(fileUrl, path, bar=self.bar_progress)
                except:
                    #self.nowDownloadName.remove(fileName)
                    #self.nowDownload.remove(url)
                    return
                # wget.download(fileUrl, path)
                self.printLine('Finish: ' + fileName)
                self.nowDownloadName.remove(fileName)
            else:
                self.printLine(fileName + ' already exists.')
            if not (url in self.finishHistory):
                self.finishHistory.append(url)
                self.writeHistory()
        else:
            self.printLine('The file doesn\'t exist on ' + url)

        if url in self.nowDownload:
            self.nowDownload.remove(url)
        self.writeQueue()

    def bar_progress(self, current, total, width=80):
        for i in range(len(self.totalList)):
            if total == self.totalList[i]:
                self.speedDelta += int((current - self.currentList[i]) / 1024)
                self.currentList[i] = current
                return
        if len(self.totalList) >= self.MAX_THREAD:
            self.totalList.pop(0)
            self.currentList.pop(0)
        self.totalList.append(total)
        self.currentList.append(current)

    def reportProgress(self):
        if self.nowDownload:
            self.printLine("Speed: " + str(self.speed) + ' KB/s                    ', False)

    def cycleChild(self):
        try:
            while self.urlList or self.nowDownload or self.waitMode:
                if not self.read2Quit:
                    if DOWNLOAD_AS_GROUP:
                        if self.restartDownload:
                            if self.nowDownload:
                                for url in self.nowDownload:
                                    t = threading.Thread(target=self.download, args=[url])
                                    t.setDaemon(True)
                                    t.start()
                            self.restartDownload = False
                        elif not self.nowDownload and self.urlList:
                            if self.firstRun:
                                self.firstRun = False
                            else:
                                self.totalList = []
                                self.currentList = []
                                time.sleep(self.GAP_TIME)
                            for url in self.urlList:
                                if len(self.nowDownload) < self.MAX_THREAD:
                                    self.nowDownload.append(url)
                                    t = threading.Thread(target=self.download, args=[url])
                                    t.setDaemon(True)
                                    t.start()
                                    self.urlList.remove(url)
                    else:
                        if self.restartDownload:
                            if self.nowDownload:
                                for url in self.nowDownload:
                                    t = threading.Thread(target=self.download, args=[url])
                                    t.setDaemon(True)
                                    t.start()
                            self.restartDownload = False
                        else:
                            if self.firstRun:
                                self.firstRun = False
                            else:
                                time.sleep(5)
                            for url in self.urlList:
                                if len(self.nowDownload) < self.MAX_THREAD:
                                    self.nowDownload.append(url)
                                    t = threading.Thread(target=self.download, args=[url])
                                    t.setDaemon(True)
                                    t.start()
                                    self.urlList.remove(url)
                else:
                    if not self.nowDownload:
                        break
                if not (self.urlList or self.nowDownload):
                    if not self.waitMode:
                        self.printLine('All finish. Waiting for new files...')
                else:
                    self.speed = int(self.speedDelta / self.sleepTime)
                    self.speedDelta = 0
                    self.reportProgress()
                    if self.speed == 0:
                        self.speedZeroTime += 1
                        if self.speedZeroTime >= 8:
                            self.speedZeroTime = 0
                            self.speedZeroWait = True
                            self.restartDownload = True
                            self.printLine('restart Download...')
                            break
                    else:
                        self.speedZeroTime = 0
                time.sleep(self.sleepTime)
        except KeyboardInterrupt:
            return

    def cycle(self):
        self.speedZeroWait = True
        restartTime = 0
        try:
            while self.speedZeroWait:
                if not self.firstRun:
                    self.totalList = []
                    self.currentList = []
                    #print(self.nowDownload)
                    downloadPathFileList = os.listdir(self.downloadPath)
                    for nowDownloadFile in self.nowDownloadName:
                        for downFile in downloadPathFileList:
                            if downFile.startswith(nowDownloadFile) and downFile.endswith('.tmp'):
                                os.remove(os.path.join(self.downloadPath, downFile))
                                break
                    restartTime += 1
                    if restartTime >= 5:
                        self.printLine('Restart too much time.')
                        break
                    time.sleep(int(self.GAP_TIME * 2))
                self.speedZeroWait = False
                t = threading.Thread(target=self.cycleChild)
                t.setDaemon(True)
                t.start()
                t.join()
        except KeyboardInterrupt:
            return


    def start(self):
        t = threading.Thread(target=self.cycle)
        t.setDaemon(True)
        t.start()
        while True:
            newUrl = input('\nPlease input address:\n')
            if newUrl == 'finish' or newUrl == 'exit' or newUrl == 'quit' or newUrl == 'q':
                self.read2Quit = True
                break
            self.addUrl(newUrl)
        t.join()

    def startAndWaitForInput(self):
        self.waitMode = True
        t = threading.Thread(target=self.cycle)
        t.setDaemon(True)
        t.start()
        try:
            while True:
                newUrl = input('\nPlease input address:\n')
                if newUrl == 'finish' or newUrl == 'exit' or newUrl == 'quit' or newUrl == 'q':
                    self.waitMode = False
                    self.read2Quit = True
                    break
                self.addUrl(newUrl)
            self.printLine('Waiting download to finish...')
        except KeyboardInterrupt:
            time.sleep(1)
            downloadPathFileList = os.listdir(self.downloadPath)
            for nowDownloadFile in self.nowDownloadName:
                print(nowDownloadFile)
                for downFile in downloadPathFileList:
                    if downFile.startswith(nowDownloadFile) and downFile.endswith('.tmp'):
                        os.remove(os.path.join(self.downloadPath, downFile))
                        print(downFile)
                        break
            os.system('pause')
            sys.exit(0)
        t.join()

    def waitOnly(self):
        try:
            while True:
                newUrl = input('\nPlease input address:\n')
                if newUrl == 'finish' or newUrl == 'exit' or newUrl == 'quit':
                    break
                self.addUrl(newUrl)
        except KeyboardInterrupt:
            sys.exit(0)

    def readTargetPath(self):
        if self.targetPath:
            if os.path.exists(self.targetPath):
                for root, dirs, files in os.walk(self.targetPath):
                    for name in dirs:
                        name = name.lower()
                        if not (name in self.downloadFolders):
                            self.downloadFolders.append(name)
                            if 'vol.' in name:
                                cutIn = name.rfind('vol.') + len('vol.') - 1
                                cutName = name[cutIn:][:name[cutIn:].find(' ')]
                                if not (cutName in self.downloadFolders):
                                    self.downloadFolders.append(cutName)
                            elif 'no.' in name:
                                cutIn = name.rfind('no.') + len('no.') - 1
                                cutName = name[cutIn:][:name[cutIn:].find(' ')]
                                if not (cutName in self.downloadFolders):
                                    self.downloadFolders.append(cutName)


def findFourthSuper(inputStr):
    t = 0
    for i in range(len(inputStr)):
        if inputStr[i] == '#':
            t += 1
            if t == 4:
                return i
    return -1


if __name__ == '__main__':
    downloader = mediaFireDownloader(DOWNLOAD_PATH)
    if len(sys.argv) == 1:
        #downloader.waitOnly()
        downloader.startAndWaitForInput()
    else:
        if READ_TARGET_PATH:
            downloader.readTargetPath()
            #print(downloader.downloadFolders)
        for file in sys.argv[1:]:
            if os.path.exists(file):
                fff = open(file, 'rb')
                data = fff.read()
                fileEncoding = chardet.detect(data).get('encoding')
                with open(file, 'r', encoding=fileEncoding) as f:
                    shouldDownload = True
                    for line in f.readlines():
                        if line.startswith('#') and READ_TARGET_PATH:
                            shouldDownload = True
                            title = line[findFourthSuper(line)+1:].strip()  #这里是我自己设计的部分，在爬下载链接时顺便把标题给爬了下来，用来判断硬盘里是否已经下载过该文件，读者不用管
                            for folder in downloader.downloadFolders:
                                if title in folder or folder in title:
                                    shouldDownload = False
                                    try:
                                        print('Not add: ' + title)
                                    except:
                                        pass
                                    break
                            if shouldDownload:
                                try:
                                    print('Add:     ' + title)
                                except:
                                    pass
                        elif shouldDownload:
                            downloader.addUrl(line)
        time.sleep(1)
        #downloader.waitOnly()
        #downloader.start()