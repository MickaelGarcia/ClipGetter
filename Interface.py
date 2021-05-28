import os
import re
import sys
import logging
import webbrowser
from qtpy.QtGui import QIcon
from functools import partial
from qtpy import QtWidgets, QtCore
from DownloadTools.discordcleen import get_logs
from DownloadTools.Twichdl import get_clip, download, slugify

if not os.path.isdir("Logs"):
    os.mkdir("Logs")

logging.basicConfig(filename='Logs\Logs_.log', filemode='w', encoding='utf-8', format='%(asctime)s %(message)s',level=logging.INFO)
Path = "\\".join(os.path.abspath(__file__).split("\\")[:-1]).replace("z", "Z")+"\\Logs\\Logs_.log"
logging.info("Log Path : %s" %(Path))

CLIP_PATTERNS = [
    r'(?P<slug>[A-Za-z]+)([0-9 \-]+)',
    r'^https://www.twitch.tv/\w+/clip/(?P<slug>[A-Za-z]+)([0-9 \-]+)',
    r'^https://clips.twitch.tv/(?P<slug>[A-Za-z]+)([0-9 \-]+)']

styleSheet = '''
QMenuBar::item { background-color: #505050; color: #ffffff; }
QMenuBar::item:selected { background-color: #3c3c3c; }
QMenuBar::item:pressed { background: rgb(46,46,46); }
QMenu {background-color: #5d5d5d; }
QMenu::item { background-color: #505050; color: #ffffff}
QMenu::item:selected { background-color: #3c3c3c; color: rgb(255,255,255); }
QWidget { color: #ffffff; padding: 2px;  background: #5d5d5d; }
QHeaderView::section { color: #ffffff; padding: 2px; height:20px; border: 0px solid #567dbc; background: #5d5d5d; }
QTreeWidget { color: #ffffff; padding: 2px; height:20px; border: 0px solid #567dbc; background: #444444; }
QProgressBar:horizontal {border: 1px solid gray; border-radius: 3px; background: white; padding: 1px; }
QProgressBar::chunk:horizontal { background: #0b84ce;}
 '''

GET_CLIP_Data = {}
TO_DOWNLOAD_Data = {}

def closed_fonction(open_logs):
    logging.info("Application Closed.")
    try:
        if open_logs.isChecked() == True:
            os.startfile('Logs\Logs_.log')
    except:pass

class Worker(QtCore.QThread):
    updateProgress = QtCore.Signal(int)

    def __init__(self, clip_list):
        QtCore.QThread.__init__(self)
        self.clip_list = clip_list

    def run(self):
        for nb, x in enumerate(self.clip_list):
            self.updateProgress.emit(nb+1)
            for pattern in CLIP_PATTERNS:
                match = re.match(pattern, x)
            if match:
                clip_slug = match.group('slug')
                clip = get_clip(clip_slug)
                if clip is not None:
                    GET_CLIP_Data[x] = clip
                else:
                    logging.info("Clip {} may not exist".format(x))

class DownloadWorker(QtCore.QThread):
    updateProgress = QtCore.Signal(int)

    def __init__(self, downlaod, target):
        QtCore.QThread.__init__(self)
        self.download = downlaod
        self.target = target

    def run(self):
        i = 0
        if type(self.download) is dict:
            for key, value in self.download.items():
                logging.info("Start dwonlading => %s." %(value["title"]))
                self.updateProgress.emit(i+1)
                logs = download(key, self.target)
                if logs is not None:
                    logging.warning(logs)
                logging.info("Download Complete.")
                i += 1
        elif type(self.download) is list:
            for key in self.download:
                logging.info("Start dwonlading")
                self.updateProgress.emit(i+1)
                logs = download(key, self.target)
                if logs is not None:
                    logging.warning(logs)
                logging.info("Download Complete.")
                i += 1

class interface(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(interface, self).__init__(*args, **kwargs)

        #-------------------------------------#
        #              BASE UI                #
        #-------------------------------------#
        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        self.layout = QtWidgets.QVBoxLayout()
        widget.setLayout(self.layout)
        self.setWindowTitle('Clips Downloader')
        root = os.path.dirname(__file__)
        icon_image = os.path.join(root, "icon.ico")
        self.setWindowIcon(QIcon(icon_image))
        self.setStyleSheet(styleSheet)

        #-------------------------------------#
        #               Menus                 #
        #-------------------------------------#
        self.fileMenu = self.menuBar().addMenu('Files')
        find_loges = self.fileMenu.addAction('Set Discord logs')
        self.downloadAll = self.fileMenu.addAction('Download All')
        self.openLogs = QtWidgets.QAction('Auto open logs',self.fileMenu, checkable=True)
        self.fileMenu.addAction(self.openLogs)
        
        #-------------------------------------#
        #               Spliter               #
        #-------------------------------------#
        centralLayout = QtWidgets.QHBoxLayout()
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        centralLayout.addWidget(splitter) 
        self.layout.addLayout(centralLayout)

        #-------------------------------------#
        #           Get clip Widgets          #
        #-------------------------------------#  
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout()
        left_widget.setLayout(left_layout)
        get_label = QtWidgets.QLabel('Clips Found :')
        self.get_list = QtWidgets.QTreeWidget()
        self.get_list.setSortingEnabled(True)
        self.get_list.setHeaderLabels(['Streamer', 'Cliper', 'Date', 'Clip name', 'Link'])
        self.get_list.setColumnHidden(4, True)
        self.get_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        #-------------------------------------#
        #        Download cli Widgets         #
        #-------------------------------------# 
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout()
        right_widget.setLayout(right_layout)
        to_download_label = QtWidgets.QLabel('Clips in download queue :')
        self.downlaod_list = QtWidgets.QTreeWidget()
        self.downlaod_list.setSortingEnabled(True)
        self.downlaod_list.setHeaderLabels(['Streamer', 'Cliper', 'Date', 'Clip name', 'Link'])
        self.downlaod_list.setColumnHidden(4, True)
        self.downlaod_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        #-------------------------------------#
        #             Set Layout              #
        #-------------------------------------# 
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        left_layout.addWidget(get_label)
        left_layout.addWidget(self.get_list)
        right_layout.addWidget(to_download_label)
        right_layout.addWidget(self.downlaod_list)

        #-------------------------------------#
        #            Connecte event           #
        #-------------------------------------#
        find_loges.triggered.connect(self.add_clips)
        self.downloadAll.triggered.connect(self.download_all)

        #-------------------------------------#
        #             ProgressBar             #
        #-------------------------------------#
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setStyleSheet('QProgressBar {color: black}')
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.progressBar)
        self.progressBar.hide()
        
        self.dwnloadBar = QtWidgets.QProgressBar()
        self.dwnloadBar.setStyleSheet('QProgressBar {color: black}')
        self.dwnloadBar.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.dwnloadBar)
        self.dwnloadBar.hide()
        #-------------------------------------#
        #               Execute               #
        #-------------------------------------#
        self.execute_download = QtWidgets.QPushButton("Execute")
        self.execute_download.clicked.connect(self.download_selected_list)
        self.layout.addWidget(self.execute_download)
        
        #-------------------------------------#
        #           Right click Menu          #
        #-------------------------------------#
        self.get_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.get_list.customContextMenuRequested.connect(self.on_get_menu)
        self.popMenu = QtWidgets.QMenu(self)
        open_action = QtWidgets.QAction(self)
        open_action.setText("Open in browser")
        open_action.triggered.connect(self.get_in_browser)
        self.popMenu.addAction(open_action)

        to_queue = QtWidgets.QAction(self)
        to_queue.setText("To Download Queue")
        to_queue.triggered.connect(self.to_download_queue)
        self.popMenu.addAction(to_queue)
        #------------------------------------#
        self.downlaod_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.downlaod_list.customContextMenuRequested.connect(self.on_download_menu)
        self.out_menu = QtWidgets.QMenu(self)
        open_action1 = QtWidgets.QAction(self)
        open_action1.setText("Open in browser")
        open_action1.triggered.connect(self.download_in_browser)
        self.out_menu.addAction(open_action1)

        to_list = QtWidgets.QAction(self)
        to_list.setText("Remove from download Queue")
        to_list.triggered.connect(self.to_get_list)
        self.out_menu.addAction(to_list)
        #------------------------------------#
        #              Methodes              #
        #------------------------------------#

    # Right clic Menu pose click on get widget
    def on_get_menu(self, point):
        self.popMenu.exec_(self.get_list.mapToGlobal(point))

    # Right clic Menu pose click on download widget
    def on_download_menu(self, point):
        self.out_menu.exec_(self.downlaod_list.mapToGlobal(point))
    
    # Populate Get widget with discord Logs
    def add_clips(self):
        
        global GET_CLIP_Data
        GET_CLIP_Data = {}

        filters = "Text files (*.txt)"
        file_dialog = QtWidgets.QFileDialog()
        logs_files = QtWidgets.QFileDialog.getOpenFileName(file_dialog, "Discord text logs", "", filters)

        if type(logs_files) is list or type(logs_files) is tuple:
            logs_files = logs_files[0]
        else:
            logs_files = logs_files
        if not logs_files:
            logging.info("Operation Set Discord Canceled.")
        elif logs_files:
            logging.info("Start Geting Data from file : %s" %(logs_files))
            self.get_list.clear()
            if len(logs_files) >= 0:
                self.clips_list = get_logs(logs_files)
                self.progressBar.setRange(0, len(self.clips_list))
                self.progressBar.show()
                self.worker = Worker(self.clips_list)
                self.worker.updateProgress.connect(self.setProgress)
                self.worker.finished.connect(self.populate_get_clip)
                self.worker.start()
                print(GET_CLIP_Data)
                self.fileMenu.setEnabled(False)
            else:
                logging.warning("Discord logs are invalid !")
                
    def populate_get_clip(self):
        global GET_CLIP_Data
        for key, value in GET_CLIP_Data.items():
            broadcaster = value['broadcaster']['displayName']
            cliper = value['curator']['displayName']
            date = value['createdAt'].replace('Z', '').replace('T', '_')
            clip_name = value['title']
            link = value['videoQualities'][0]['sourceURL']
            QtWidgets.QTreeWidgetItem(self.get_list, [broadcaster, cliper, date, clip_name, key])
        logging.info("Data Stored")
        self.progressBar.hide()
        self.fileMenu.setEnabled(True)

    # Set items to download widget
    def to_download_queue(self):
        items = self.get_list.selectedItems()
        for x in items:
            TO_DOWNLOAD_Data[x.text(4)] = GET_CLIP_Data[x.text(4)]
            del GET_CLIP_Data[x.text(4)]
            QtWidgets.QTreeWidgetItem(self.downlaod_list, [x.text(0), x.text(1), x.text(2), x.text(3), x.text(4)])
            self.get_list.takeTopLevelItem(self.get_list.indexOfTopLevelItem(x))
    
    # Set items to get widget
    def to_get_list(self):
        items = self.downlaod_list.selectedItems()
        for x in items:
            GET_CLIP_Data[x.text(4)] = TO_DOWNLOAD_Data[x.text(4)]
            del TO_DOWNLOAD_Data[x.text(4)]
            QtWidgets.QTreeWidgetItem(self.get_list, [x.text(0), x.text(1), x.text(2), x.text(3), x.text(4)])
            self.downlaod_list.takeTopLevelItem(self.downlaod_list.indexOfTopLevelItem(x))
    
    # open item in browser
    def get_in_browser(self):
        selected = self.get_list.selectedItems()
        for x in selected:
            link = x.text(4)
            try:
                webbrowser.open(link)
            except: pass

    def download_in_browser(self):
        selected = self.downlaod_list.selectedItems()
        for x in selected:
            link = x.text(4)
            try:
                webbrowser.open(link)
            except: pass
    
    def setProgress (self, progress):
        precent_data = str(round((float(progress)*100.0/float(len(self.clips_list))), 2))
        self.progressBar.setFormat('Get Clips Data : {}%'.format(precent_data)) 
        self.progressBar.setValue(progress)

    # Execute download form download widgets
    def download_selected_list(self):
        global TO_DOWNLOAD_Data
        self.target_dir = QtWidgets.QFileDialog.getExistingDirectory()
        if self.target_dir == '':
            logging.info("Download Queue exectution canceled")
        else:
            self.dwnloadBar.setRange(0, len(TO_DOWNLOAD_Data))
            self.dwnloadBar.show()
            self.downlaodWorker = DownloadWorker(TO_DOWNLOAD_Data, self.target_dir)
            self.downlaodWorker.updateProgress.connect(self.downloadProgress)
            self.downlaodWorker.start()
            self.downlaod_list.setEnabled(False)
            self.execute_download.setEnabled(False)
            self.get_list.setEnabled(False)
            self.downlaod_list.setEnabled(False)
            self.downlaodWorker.finished.connect(self.downloadFinished)
        
    def downloadProgress(self, progress):
        global TO_DOWNLOAD_Data
        precent_data = str(round((float(progress)*100.0/float(len(TO_DOWNLOAD_Data))), 2))
        self.dwnloadBar.setFormat("Downlaod Clips : {}%".format(precent_data)) 
        self.dwnloadBar.setValue(progress)

    def downloadFinished(self):
        self.dwnloadBar.hide()
        self.execute_download.setEnabled(True)
        self.get_list.setEnabled(True)
        self.downlaod_list.setEnabled(True)
        self.execute_download.setEnabled(True)

    # Download all clips from discord logs
    def download_all(self):
        filters = "Text files (*.txt)"
        file_dialog = QtWidgets.QFileDialog()
        logs_files = QtWidgets.QFileDialog.getOpenFileName(file_dialog, "Discord text logs", "", filters)
        if not logs_files:
            logging.info("Donwload All Canceled.")
        elif logs_files:
            if type(logs_files) is list or type(logs_files) is tuple:
                logs_files = logs_files[0]
            else: pass
            clips = get_logs(logs_files)
            target_dir = QtWidgets.QFileDialog.getExistingDirectory()
            if len(clips) == 0:
                logging.info("No clips found in files {}.".format(logs_files))
            elif not target_dir:
                logging.info("Operation Canceled.")
            else:
                self.dwnloadBar.setRange(0, len(clips))
                self.dwnloadBar.show()
                DownloadWorker(clips, target_dir)
                self.downlaodWorker = DownloadWorker(clips, target_dir)
                self.downlaodWorker.updateProgress.connect(partial(self.downloadAllProgress, clips))
                self.downlaodWorker.start()
                self.downlaod_list.setEnabled(False)
                self.execute_download.setEnabled(False)
                self.downlaodWorker.finished.connect(self.downloadFinished)
                
    def downloadAllProgress(self, clips, progress):
        global TO_DOWNLOAD_Data
        precent_data = str(round((float(progress)*100.0/float(len(clips))), 2))
        self.dwnloadBar.setFormat("Downlaod Clips : {}%".format(precent_data)) 
        self.dwnloadBar.setValue(progress)

application = QtWidgets.QApplication(sys.argv)
window = interface()
window.show()
application.aboutToQuit.connect(partial(closed_fonction, window.openLogs))
sys.exit(application.exec_())

