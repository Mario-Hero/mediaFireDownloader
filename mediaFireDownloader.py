#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Created by Mario Chen, 21.03.2022, Shenzhen
# My Github site: https://github.com/Mario-Hero

import os
import sys
import time
import threading
from urllib.parse import unquote
import datetime

try:
    import requests
except ImportError:
    os.system('pip install requests')
    import requests
    
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

DOWNLOAD_PATH = os.getcwd()  # 文件下载位置 the download path

# <<<<< you can change it


HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"}
DOWNLOAD_AS_GROUP = True

# 这里是我自己设计的部分，在爬下载链接时顺便把标题给爬了下来，用来判断硬盘里是否已经下载过该文件，读者不用管
# Here is the part designed for myself. I use title to judge whether the file has been downloaded.
TARGET_PATH = ''
READ_TARGET_PATH = False


class mediaFireDownloader:
    def __init__(self, downloadPath):
        self.GAP_TIME = 120
        self.restartTime = 0
        self.downloadDelta = 0
        self.totalDownloadSize = 0
        self.tempDownloadSize = 0
        self.urlList = []
        self.nowDownload = []
        self.nowDownloadName = []
        self.downloadPath = downloadPath
        self.targetPath = TARGET_PATH
        self.MAX_THREAD = 2
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
            for url in self.nowDownload:
                queueFile.write(url + '\n')
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

    def requestsDownload(self, url, filePath, fileName):
        count = 0
        r1 = requests.get(url, stream=True)
        totalSize = int(r1.headers['Content-Length'])
        if os.path.exists(filePath):
            tempSize = os.path.getsize(filePath)
        else:
            tempSize = 0
        tempSizeMB = int(tempSize / (1024 * 1024))
        totalSizeMB = int(totalSize / (1024 * 1024))
        self.printLine('Downloading: ' + fileName + ' ' + str(tempSizeMB) + '/' + str(totalSizeMB) + ' MB')
        self.tempDownloadSize += tempSize
        self.totalDownloadSize += totalSize
        while count < 5:
            if count != 0:
                tempSize = os.path.getsize(filePath)
            if tempSize >= totalSize:
                break
            count += 1
            # print("第[{}]次下载文件,已经下载数据大小:[{}],应下载数据大小:[{}]".format(count, tempSize, totalSize))
            headers = {"Range": f"bytes={tempSize}-{totalSize}"}
            # r = requests.get(url, stream=True, verify=False)
            r = requests.get(url, stream=True, headers=headers)
            with open(filePath, "ab") as f:
                if count != 1:
                    f.seek(tempSize)
                for chunk in r.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        tempSize += len(chunk)
                        self.downloadDelta += int(len(chunk) / 1024)
                        self.tempDownloadSize += int(len(chunk))
                        f.write(chunk)
                        f.flush()

    def printLine(self, printMessage, forever=True):
        # sys.stdout.write('\r                                                    ')
        # sys.stdout.flush()
        if forever:
            sys.stdout.write('\r' + printMessage + '                      \n')
            sys.stdout.flush()
        else:
            sys.stdout.write('\r' + printMessage + '                      ')
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
            # downloadButton = soup.find('a', {'id': 'dlbutton'})
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
                # self.printLine('Downloading: ' + fileName)
                path += '.tmp'
                try:
                    self.requestsDownload(fileUrl, path, fileName)
                    # wget.download(fileUrl, path, bar=self.bar_progress)
                except:
                    # self.nowDownloadName.remove(fileName)
                    # self.nowDownload.remove(url)
                    return
                for i in range(5):
                    try:
                        os.rename(path, path[:-4])
                        break
                    except:
                        time.sleep(0.5)
                        continue
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

    def clearDownloadSpeed(self):
        self.downloadDelta = 0
        self.tempDownloadSize = 0
        self.totalDownloadSize = 0

    def reportProgress(self):
        if self.nowDownload:
            self.speed = int(self.downloadDelta / self.sleepTime)
            self.downloadDelta = 0
            if self.totalDownloadSize != 0 and self.speed != 0:
                percentSize = int(self.tempDownloadSize / self.totalDownloadSize * 100)
                remainingSeconds = int((self.totalDownloadSize - self.tempDownloadSize) / 1024 / self.speed)
                # m, s = divmod(remainingSeconds, 60)
                # h, m = divmod(m, 60)
                # print("%d:%02d:%02d" % (h, m, s))
                self.printLine("Speed: " + str(self.speed) + ' KB/s  ' + str(percentSize) + '%  remaining: ' + str(
                    datetime.timedelta(seconds=remainingSeconds)), False)

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
                                self.clearDownloadSpeed()
                                self.restartTime = 0
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
                                self.clearDownloadSpeed()
                                self.restartTime = 0
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
                    if self.speed <= 30:  # <= 30KB/s
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
        try:
            while self.speedZeroWait:
                if not self.firstRun:
                    self.clearDownloadSpeed()
                    self.restartTime += 1
                    if self.restartTime >= 5:
                        self.printLine('Restart too much time.')
                        break
                    if not self.nowDownload:
                        self.restartDownload = False
                        time.sleep(int(self.GAP_TIME))
                    else:
                        # print(self.nowDownload)
                        time.sleep(int(self.GAP_TIME * self.restartTime))
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

    def readTargetPath(self, file):
        if self.targetPath:
            if os.path.exists(self.targetPath):
                fileName = file.split(' ')[-1].split('.')[0].lower()
                for targetFolder in os.listdir(self.targetPath):
                    if fileName in targetFolder.lower() or targetFolder.lower() in fileName:
                        self.targetPath = os.path.join(self.targetPath, targetFolder)
                        break
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
        # downloader.waitOnly()
        downloader.startAndWaitForInput()
    else:
        for file in sys.argv[1:]:
            if os.path.exists(file):
                fff = open(file, 'rb')
                data = fff.read()
                fileName = os.path.split(file)[1]
                fileEncoding = chardet.detect(data).get('encoding')
                if READ_TARGET_PATH:
                    downloader.readTargetPath(fileName)
                    # print(downloader.downloadFolders)
                with open(file, 'r', encoding=fileEncoding) as f:
                    shouldDownload = True
                    for line in f.readlines():
                        if line.startswith('#') and READ_TARGET_PATH:
                            shouldDownload = True
                            title = line[findFourthSuper(
                                line) + 1:].strip().lower()  # 这里是我自己设计的部分，在爬下载链接时顺便把标题给爬了下来，用来判断硬盘里是否已经下载过该文件，读者不用管
                            for folder in downloader.downloadFolders:
                                if title in folder.lower() or folder.lower() in title:
                                    shouldDownload = False
                                    try:
                                        print('Not add: ' + title)
                                    except:
                                        pass
                                    break
                                else:
                                    appearTime = 0
                                    for splitTitle in title.split(' '):
                                        if splitTitle in folder and (not (splitTitle in fileName)) and (
                                        not (fileName in splitTitle)):
                                            appearTime += 1
                                        if appearTime >= 1:
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
        downloader.waitOnly()
        # downloader.start()
