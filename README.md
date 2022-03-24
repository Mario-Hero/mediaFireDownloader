# mediaFireDownloader 

这是一个MediaFire文件队列下载的Python脚本。

通常情况下，我们可以用浏览器下载MediaFire的文件，但是不能同时下载过多文件，所以只能几个几个地慢慢手动下载，比较费时间，所以我设计了这样一个Python脚本，可以自动下载，省去了手动操作。

目前采用两个为一组的下载方式，每组之间暂停2分钟，来避免服务器将下载速度归零。这样的下载速度可以保持在1MB/s以上。速度归零后过段时间会重启下载。

支持断点续传。可以随时关闭。

This is a Python script for downloading files from MediaFire.

Generally, we can download files from MediaFire with the browser, but we can't download too many files at the same time, so we can only download them slowly and manually. Therefore, I designed a Python script, which can download automatically without manual operation.

At present, the script download two files as group at the same time, and each group is suspended for 2 minutes to avoid the server making the download speed to zero. In this way, the download speed can be maintained above 1MB / s. After the speed returns to zero, the download will be restarted later.
Support breakpoint resume download. The script can be closed at any time.

## 依赖 Dependency

Python 3

bs4, chardet (如果没有安装，该脚本会自动安装。If the packages are not installed, the script will automatically install them)

## 用法 Usage

修改脚本mediaFireDownloader.py开头的DOWNLOAD_PATH参数来设置下载位置。默认下载位置是脚本所在文件夹。

打开mediaFireDownloader.py，粘贴MediaFire链接，回车即可开始下载。MediaFire链接形如https://www.mediafire.com/file/r7b9sl4kftqhapu/220206836a.7z/file.

或者把写有链接的txt文件拖入mediaFireDownloader.py，即可把文件添加进下载队列。下次打开mediaFireDownloader.py后会直接开始下载。txt文件要求一行一个链接。

下载时输入quit或q回车，即可不再继续下载，程序会在当前下载完成后退出。

Edit the script *mediaFireDownloader.py*, set DOWNLOAD_PATH parameter to the download location. The default download location is the folder where the script is located.
Open *mediaFireDownloader.py*, paste the mediafire link, and press enter to start downloading. The MediaFire link looks like https://www.mediafire.com/file/r7b9sl4kftqhapu/220206836a.7z/file.

Or drag a text file into *mediaFireDownloader.py*, the links in text file will be added to the download queue. Next time you open the *mediaFireDownloader.py*, it will start downloading directly. One link per line in the text file.

When downloading, type quit or q then press enter to stop downloading. The program will exit after the current download is completed.

## 其他 Others

支持http://adf.ly 和 http://ouo.io 开头且后面包含完整下载地址的链接，比如：

http://ouo.io/st/xR4hnRab/?s=https%3A%2F%2Fwww.mediafire.com%2Ffile%2Fajfymwsr4b5z3nx%2FPure_Media_Vol.080.rar%2Ffile

和

http://adf.ly/18509119/https://www67.zippyshare.com/v/Ot4UpfVo/file.html

后续可能会支持更多网盘，但是应该需要安装selenium.

Support http://adf.ly and http://ouo.io which contain download address, such as:
http://ouo.io/st/xR4hnRab/?s=https%3A%2F%2Fwww.mediafire.com%2Ffile%2Fajfymwsr4b5z3nx%2FPure_Media_Vol.080.rar%2Ffile
and
http://adf.ly/18509119/https://www67.zippyshare.com/v/Ot4UpfVo/file.html
More network disks may be supported in the future, but selenium should be used.

## License

The project is released under MIT License.
