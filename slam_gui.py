from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
import os
import subprocess

docker_cmd = "docker run --env=\"DISPLAY\" " \
                "--net=host " \
                "--volume=\"$HOME/.Xauthority:/root/.Xauthority:rw\" " \
                 "--env=\"QT_X11_NO_MITSHM=1\"" \
                " -v /tmp/.X11-unix:/tmp/.X11-unix:ro -it --rm --name slam_from_qt " \
                "-v /home:/out_home {} " \
                " /bin/bash -c \"cd root && /bin/bash /root/run_{}.sh {}\""



slam_types = ["全部", "基于滤波器", "特征法", "直接法", "多传感器融合"]
type2algos = {"全部": ["vins_mono", "dso", "svo", "okvis", "orb_slam", "lsd_slam", "rovio", "basalt", "ice_ba", "msckf"],
              "基于滤波器": [],
              "特征法": ["orb_slam"],
              "直接法": ["lsd_slam", "dso"],
              "多传感器融合": ["vins_mono", "svo", "okvis", "rovio", "basalt", "ice_ba", "msckf"]}

algo2image = {algo:"freshorange/ros_slam_image:19-8-13" for algo in ["dso", "svo", "okvis", "orb_slam", "lsd_slam", "rovio", "ice_ba"]}
algo2image.update({algo:"freshorange/ros_slam_image:kinetic_19-8-13" for algo in ["vins_mono", "msckf"]})
algo2image.update({algo:"freshorange/no_ros_slam:basalt-v2" for algo in ["basalt"]})

algo2datasets = {"vins_mono":["euroc", "eth-aslcla", "ar_box"],
                 "dso":["monoVO"],
                 "svo":["airground_rig"],
                 "okvis":["euroc"],
                 "orb_slam":["tum", "kitti", "euroc"],
                 "lsd_slam":["lsd_room"],
                 "rovio":["euroc"],
                 "basalt":["euroc", "tumvi"],
                 "ice_ba":["euroc"],
                 "msckf":["euroc"]}

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.originalPalette = QApplication.palette()

        font = QFont("Consolas")
        pointsize = font.pointSize()
        font.setPixelSize(pointsize * 160 / 72)
        app.setFont(font)

        self.datasetLayout = None # 初始化

        styleComboBox = QComboBox()
        styleComboBox.addItems(slam_types)

        styleLabel = QLabel("分类:")
        styleLabel.setBuddy(styleComboBox)

        self.buttonsGroupBox = self.createSlamButtonsByAlgos(type2algos["全部"])

        styleComboBox.activated[str].connect(self.onChangeType)

        topLayout = QHBoxLayout()
        topLayout.addWidget(styleLabel)
        topLayout.addWidget(styleComboBox)
        topLayout.addStretch(1)

        buttomLayout = QVBoxLayout()
        self.runButton = QPushButton("运行")
        self.runButton.clicked.connect(self.onClickRun)
        buttomLayout.addWidget(self.runButton)
        self.cancelButton = QPushButton("终止运行")
        self.cancelButton.clicked.connect(self.onClickCancel)
        self.cancelButton.setEnabled(False)
        buttomLayout.addWidget(self.cancelButton)
        buttomLayout.addStretch(1)

        self.datasetLayout = QHBoxLayout()
        self.datasetComboBox = QComboBox()
        self.datasetComboBox.addItems(algo2datasets['vins_mono'])
        self.datasetComboBox.activated[str].connect(self.onChangeDataset)
        datasetLabel = QLabel("数据集:")
        datasetLabel.setBuddy(self.datasetComboBox)
        self.datasetLayout.addWidget(datasetLabel)
        self.datasetLayout.addWidget(self.datasetComboBox)
        self.datasetLayout.addStretch(1)


        # 整体布局
        self.mainLayout = QGridLayout()
        self.mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        self.mainLayout.addWidget(self.buttonsGroupBox, 1, 0, 3, 4)
        self.mainLayout.addLayout(self.datasetLayout, 4, 0, 1, 4)
        self.mainLayout.addLayout(buttomLayout, 5, 0, 1, 4)
        self.mainLayout.setRowStretch(1, 1)
        self.mainLayout.setRowStretch(2, 1)
        self.mainLayout.setColumnStretch(0, 1)
        self.mainLayout.setColumnStretch(1, 1)
        self.setLayout(self.mainLayout)

        self.setWindowTitle("Slam算法演示")
        self.changeStyle('Fusion')

        self.slamProcess = ""

    def onClickRun(self):
        if self.runButton.isEnabled():
            print("run slam")
            self.slamProcess = subprocess.Popen(docker_cmd.format(algo2image[self.algoSelected], self.algoSelected, self.datasetComboBox.currentText().lower()), shell=True)
            self.runButton.setEnabled(False)
            self.cancelButton.setEnabled(True)

    def onClickCancel(self):
        if self.cancelButton.isEnabled():
            p = subprocess.Popen("docker stop --time 1 slam_from_qt", shell=True)
            self.cancelButton.setEnabled(False)
            self.runButton.setEnabled(True)

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        QApplication.setPalette(QApplication.style().standardPalette())
        #QApplication.setPalette(self.originalPalette)

    def onChangeType(self, typeName):
        algos = type2algos[typeName]
        self.mainLayout.removeWidget(self.buttonsGroupBox)
        self.buttonsGroupBox.deleteLater()
        self.buttonsGroupBox = self.createSlamButtonsByAlgos(algos)
        self.mainLayout.addWidget(self.buttonsGroupBox, 1, 0, 3, 4)
        print("changed")

    def onChangeDataset(self, datasetName):
        self.dataset = datasetName.lower()
        print("changed dataset: self.dataset")

    def createSlamButtonsByAlgos(self, algos):
        buttonsGroupBox = QGroupBox("算法")

        radioButtons = []
        for i, algo in enumerate(algos):
            radioButtons.append(QRadioButton(algo))
            radioButtons[i].toggled.connect(self.on_radio_button_toggled)
        if len(algos) > 0:
            radioButtons[0].setChecked(True)
            self.algoSelected = algos[0]

        layout = QGridLayout()
        for i, rb in enumerate(radioButtons):
            layout.addWidget(rb, i // 3, i % 3, 1, 1)
        buttonsGroupBox.setLayout(layout)

        return buttonsGroupBox

    def on_radio_button_toggled(self):
        radiobutton = self.sender()
        if radiobutton.isChecked():
            self.algoSelected = radiobutton.text()
            print(self.algoSelected)
            if self.datasetLayout != None:
                self.datasetComboBox.clear()
                self.datasetComboBox.addItems(algo2datasets[self.algoSelected])
            else:
                print(self.datasetLayout)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())
