from selenium import webdriver
from time import sleep
import sys
import requests
import logging
import datetime
import sqlite3
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from PyQt5.QtWidgets import QMessageBox, QGraphicsOpacityEffect
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal

profilepopup_status = [False]
tokenPopup_status = [False]
login_status = [False]
login_detail = {'username':'', 'token':''}
response_info = []
logging.basicConfig(filename="log.txt",
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("--window-size=1920,1080")
options.add_argument(f'user-agent={user_agent}')
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)

def driver_startup():
    global driver, wait
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

class DuplicateThread(QThread):
    update_progress = pyqtSignal(str)
    def __init__(self,parent=None, do_create_data=True):
        super(DuplicateThread,self).__init__(parent)

    def run(self):
        try :
            lines = open('numbers.txt','r').readlines()
            lines_set = set(lines)
            out = open('numbers.txt','w')
            for line in lines_set:
                out.write(line)
            return self.update_progress.emit('Duplicate Numbers are removed :) ')
        except :
            return self.update_progress.emit('Failed. Something went wrong.')

class TokenThread(QThread):
    update_progress = pyqtSignal(str)
    def __init__(self,parent=None, do_create_data=True, token_in='', username=''):
        super(TokenThread,self).__init__(parent)
        self.token_in = token_in
        self.username = username
        
    def run(self):
        header = {'username':self.username,'token':self.token_in}
        response = requests.post('https://whatsapp.iran.liara.run/api/users/login/',headers=header)
        # if not response.status_code == 200 :
        #     return self.update_progress.emit(f'{response.status_code} : {response.reason}')
        user = response.json()
        response_info.append(user)
        try :
            if int(user[0]['sent']) >= int(user[0]['charge']) :
                login_status[0] = False
                return self.update_progress.emit('Token Expired 🦕')
            login_status[0] = True
            return self.update_progress.emit('Token Validated ✔')

        except:
            return self.update_progress.emit('Invalid username or Token')
        
class QrThread(QThread):

    update_progress = pyqtSignal(str)
    def __init__(self,parent=None):
        super(QrThread,self).__init__(parent)
        
    def run(self):
        if login_status[0] == False :
            return self.update_progress.emit('< Insert your token first >')
        try:
            driver.get("https://web.whatsapp.com/")
            try :
                element = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[3]/div[1]/div/div/div[2]/div/div")))
            except :                                                            
                self.update_progress.emit('Could not find QRcode !')

            try :
                element = driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[3]/div[1]')
            except:
                self.update_progress.emit('Could not find QRcode !')
            element.screenshot('img/main.png')
            self.update_progress.emit('Qrcode Updated !')
        except:
            self.update_progress.emit('Can not reach Whatsapp.com !')

class SendThread(QThread):
    update_progress = pyqtSignal(str)
    error_handler = pyqtSignal(str)
    progress = pyqtSignal(int)
    def __init__(self,parent=None, token_in='', username=''):
        super(SendThread,self).__init__(parent)

        self.total = 100
        self.token_in = token_in
        self.username = username
        self.is_paused = False
        self.is_killed = False
        
        
    def run(self):
        con = sqlite3.connect("test.db")
        cur = con.cursor()
        if login_status[0] == False :
            return self.update_progress.emit('< Insert your token first >')
        # con = sqlite3.connect("test.db")
        # cur = con.cursor()
        # params = (self.token_in,self.username)
        # user = cur.execute("SELECT * FROM user WHERE user_token==? AND username==?",params).fetchall()
        sent = response_info[0][0]['sent']
        charge = response_info[0][0]['charge']
        if  sent >= charge:
            return self.update_progress.emit(f'< You sent {sent} messages. Buy new token plz >')
        sleep(3)
        with open('message.txt','r',encoding='utf-8') as text:
            message = """""".join(text.readlines())
            print(message)
        phone_numbers = open("numbers.txt").read().split("\n")
        sent_count = 0
        faliled_count = 0
        if len(phone_numbers) == 0:
            return self.update_progress.emit('Please Add New Phone Numbers')
        
        for phone in phone_numbers:
            if phone == '' :
                return self.update_progress.emit('Empty line ! ')
            while self.is_paused:
                sleep(1)
                self.update_progress.emit('Paused')
                if self.is_paused == False :
                    break
            if self.is_killed :
                self.update_progress.emit('Cancel')
                break
            if sent >= charge:
                return self.update_progress.emit(f'< You sent {charge} messages. Buy new token plz >')
            pn = phone
            self.update_progress.emit('sending to : '+ pn)
            url = f'https://web.whatsapp.com/send?phone=+98{phone[1:]}'
            sleep(3)
            try:
                driver.get(url)
                try:
                    driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[3]/div[1]/div/div/div[1]/div[1]')
                    self.update_progress.emit('You are not Login !')
                except:
                    try :
                        element = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button')))
                        print('here')
                        driver.find_element(By.XPATH , 
                                            '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p').send_keys(message)
                        print('here2')
                        sleep(1)
                        driver.find_element(By.XPATH,
                                            '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button').click()
                        self.update_progress.emit('Sent 😊')
                        sent_count += 1 
                        # cur.execute("UPDATE user SET charge=charge+1 WHERE user_token =? ",params[0])
                        # con.commit()
                        headers = {'token':response_info[0][0]['token']}
                        response = requests.post('https://whatsapp.iran.liara.run/api/users/send/', headers=headers)
                        if response.status_code == 200 :
                            with open('sent-numbers.txt', 'a') as f:
                                f.write(pn + "\n")
                        else :
                            self.update_progress.emit('Internal server error !') 
                    except: 
                        with open('failed.txt','a') as failed :
                            failed.write(pn + "\n")
                        self.update_progress.emit('Could not find Send button ! \n or Contact not found !')           
                        faliled_count += 1
            except:
                with open('failed.txt','a') as failed :
                    failed.write(pn + "\n")
                self.update_progress.emit("Contact dosen't exist ! ")
                faliled_count += 1
        self.update_progress.emit(f"""\n <<<  Done  >>>\n\tsent : {sent_count}\n\tfaled : {faliled_count} """)


class ProfilePopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        if login_status[0] == False :
            return ''
        # con = sqlite3.connect("test.db")
        # cur = con.cursor()
        # params = (login_detail['token'],login_detail['username'])
        # user = cur.execute("SELECT * FROM user WHERE user_token==? AND username==?",params).fetchall()
        _translate = QtCore.QCoreApplication.translate
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setFixedSize(400,300)
        headers = {'token':login_detail['token']}
        response = requests.post('https://whatsapp.iran.liara.run/api/users/info/',headers=headers)
        data = response.json()
        response_info[0][0] = data
        print(response_info)
        self.setWindowTitle('profile')
        self.setWindowIcon(QtGui.QIcon("img/profile-icon.png"))
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setAutoFillBackground(True)
        self.setStyleSheet('''
            ProfilePopup {
                background: rgba(64, 64, 64, 64);
                
            }
            QWidget#container {
                border: 2px solid darkGray;
                border-radius: 4px;
                background: rgb(64, 64, 64);
                text-align: center;
            }
            QWidget#container > QLabel {
                color: white;
                font-family : "Lucida Console", "Courier New", monospace;
            }
            QLabel#title {
                font-size: 25pt;
            }
            QLabel {
                text-align: center;
            }
            QPushButton {
            border: 2px solid #8f8f91;
            border-radius: 6px;
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #f6f7fa, stop: 1 #dadbde);
            min-width: 80px;
            }
        ''')
        fullLayout = QtWidgets.QVBoxLayout(self)    

        self.container = QtWidgets.QWidget(
            autoFillBackground=True, objectName='container')
        fullLayout.addWidget(self.container, alignment=QtCore.Qt.AlignCenter)
        self.container.setFixedSize(380,280)
        self.container.autoFillBackground()

        buttonSize = self.fontMetrics().height()
   
        title = QtWidgets.QLabel(self.container)
        title.setGeometry(QtCore.QRect(20,10,200,35))
        title.setStyleSheet("font-size : 20px;text-align: left;")
        title.setText(_translate("maiwindow" ,"Profile"))
        
        username_label = QtWidgets.QLabel(self.container)
        username_label.setGeometry(QtCore.QRect(20,60,90,30))
        username_label.setText(_translate("maiwindow" ,"Username : "))
        
        fullLayout.addWidget(self.container)
        username = data.get('username')
        
        username_val = QtWidgets.QLabel(self.container)
        username_val.setGeometry(QtCore.QRect(100,60,260,30))
        username_val.setAlignment(QtCore.Qt.AlignCenter)
        username_val.setText(_translate("maiwindow" ,f"{username}"))
        
        token_label = QtWidgets.QLabel(self.container)
        token_label.setGeometry(QtCore.QRect(20,90,90,30))
        token_label.setText(_translate("maiwindow" ,"Token : "))
        token = data.get('token')
        token_val = QtWidgets.QLabel(self.container)
        token_val.setGeometry(QtCore.QRect(100,90,260,30))
        token_val.setAlignment(QtCore.Qt.AlignCenter)
        token_val.setText(_translate("maiwindow" ,f"{token}"))
        
        total_label = QtWidgets.QLabel(self.container)
        total_label.setGeometry(QtCore.QRect(20,120,90,30))
        total_label.setText(_translate("maiwindow" ,"Total : "))
        total = data.get('charge')
        total_val = QtWidgets.QLabel(self.container)
        total_val.setGeometry(100,120,260,30)
        total_val.setAlignment(QtCore.Qt.AlignCenter)
        total_val.setText(_translate("maiwindow" ,f"{total}"))
        
        sent_label = QtWidgets.QLabel(self.container)
        sent_label.setGeometry(20,150,90,30)
        sent_label.setText(_translate("maiwindow" ,"Sent : "))
        sent = data.get('sent')
        sent_val = QtWidgets.QLabel(self.container)
        sent_val.setGeometry(100,150,260,30)
        sent_val.setAlignment(QtCore.Qt.AlignCenter)
        sent_val.setText(_translate("maiwindow" ,f"{sent}"))   
             
        exp_date_label = QtWidgets.QLabel(self.container)
        exp_date_label.setGeometry(20,180,90,30)
        exp_date_label.setText(_translate("maiwindow" ,"EXP date : "))
        
        exp_date_val = QtWidgets.QLabel(self.container)
        parsed_datetime = datetime.datetime.fromisoformat(data.get('exp_date').replace('Z', '+03:30'))
        exp_date = parsed_datetime.strftime('%Y-%m-%d %H:%M:%S') #
        exp_date_val.setGeometry(100,180,260,30)
        exp_date_val.setAlignment(QtCore.Qt.AlignCenter)
        exp_date_val.setText(_translate("maiwindow" ,f"{exp_date}"))
        
        okButtton = QtWidgets.QPushButton(self.container)
        okButtton.setGeometry(130,230,100,25)
        okButtton.setText(_translate("maiwindow" ,"OK"))
        okButtton.setAutoDefault(True)
        okButtton.setDefault(True)
        okButtton.clicked.connect(self.accept)
        self.loop = QtCore.QEventLoop(self)

    def accept(self):

        self.loop.exit(False)
        profilepopup_status[0] = False

    def exec_(self):
        tokenPopup_status[0] = False
        self.show()
        res = self.loop.exec_()
        self.hide()
        return res
    

class LoginPopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        if tokenPopup_status[0] == True :
            return ''
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setFixedSize(350,240)
        self.setWindowTitle('Token')
        self.setWindowIcon(QtGui.QIcon('img/token-icon.png'))
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setAutoFillBackground(True)
        self.setStyleSheet('''
            LoginPopup {
                background: rgba(64, 64, 64, 64);
            }
            QWidget#container {
                border: 2px solid darkGray;
                border-radius: 4px;
                background: rgb(64, 64, 64);
            }
            QWidget#container > QLabel {
                color: white;
            }
            QLabel#title {
                font-size: 20pt;
            }
            QPushButton {
            border: 2px solid #8f8f91;
            border-radius: 6px;
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #f6f7fa, stop: 1 #dadbde);
            min-width: 80px;
            }
        ''')
        fullLayout = QtWidgets.QVBoxLayout(self)

        self.container = QtWidgets.QWidget(
            autoFillBackground=True, objectName='container')
        fullLayout.addWidget(self.container, alignment=QtCore.Qt.AlignCenter)
        self.container.setSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

        buttonSize = self.fontMetrics().height()

        layout = QtWidgets.QVBoxLayout(self.container)
        layout.setContentsMargins(
            buttonSize * 2, buttonSize, buttonSize * 2, buttonSize)

        title = QtWidgets.QLabel(
            'Enter your token', 
            objectName='title', alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addWidget(QtWidgets.QLabel('Username'))
        self.usernameEdit = QtWidgets.QLineEdit()
        layout.addWidget(self.usernameEdit)
        layout.addWidget(QtWidgets.QLabel('Token'))
        self.tokenEdit = QtWidgets.QLineEdit()
        layout.addWidget(self.tokenEdit)
        
        buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.okButton = buttonBox.button(buttonBox.Ok)
        self.okButton.setEnabled(False)

        self.usernameEdit.textChanged.connect(self.checkInput)
        self.tokenEdit.textChanged.connect(self.checkInput)
        self.usernameEdit.returnPressed.connect(lambda:self.tokenEdit.setFocus())
        self.tokenEdit.returnPressed.connect(self.accept)

        # parent.installEventFilter(self)

        self.loop = QtCore.QEventLoop(self)
        self.usernameEdit.setFocus()


    def validateToken(self):
        # login_detail['username'] = self.usernameEdit.text()
        # login_detail['token'] = self.tokenEdit.text()
        self.tokenThread = TokenThread(token_in=login_detail['token'],username=login_detail['username'])
        self.tokenThread.start()
        self.tokenThread.update_progress.connect(self.token_notif)
        
    def token_notif(self,message):
        self.msg = QMessageBox()
        self.msg.setWindowIcon(QtGui.QIcon('img/info_icon.png'))
        self.msg.setFixedSize(300,200)
        self.msg.setStyleSheet("""background : #9C9C9C;font-family : "Lucida Console", "Courier New", monospace;""")
        self.msg.setText(message)
        self.msg.setWindowTitle("Info")
        self.msg.setStandardButtons(QMessageBox.Ok)
        self.msg.exec()
        
    def checkInput(self):
        self.okButton.setEnabled(bool(self.username() and self.token()))

    def username(self):
        return self.usernameEdit.text()

    def token(self):
        return self.tokenEdit.text()

    def accept(self):
        if self.username() and self.token():
            login_detail['username'] = self.usernameEdit.text()
            login_detail['token'] = self.tokenEdit.text()
            self.tokenThread = TokenThread(token_in=login_detail['token'],username=login_detail['username'])
            self.tokenThread.start()
            self.tokenThread.update_progress.connect(self.token_notif)
            self.loop.exit(True)
            tokenPopup_status[0] = False

    def reject(self):
        self.loop.exit(False)
        tokenPopup_status[0] = False

    def eventFilter(self, source, event):
        if event.type() == event.Resize:
            self.setGeometry(source.rect())
        return super().eventFilter(source, event)
    def exec_(self):
        self.show()
        # self._raise()
        res = self.loop.exec_()
        self.hide()
        return res
        
        
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 500)
        # MainWindow.setWindowTitle('WhatsApp')
        MainWindow.setMinimumSize(QtCore.QSize(1200, 500))
        MainWindow.setMaximumSize(QtCore.QSize(1200, 500))
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setWindowIcon(QtGui.QIcon('img/logo.png'))

        ####################  verticalLayout_1  left Menu ####################
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 171, 511))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.menu = QtWidgets.QWidget(self.verticalLayoutWidget)
        self.menu.setObjectName("menu")
        ####################  loginButton ####################
        self.loginButton = QtWidgets.QPushButton(self.menu)
        self.loginButton.setGeometry(QtCore.QRect(20, 10, 131, 71))
        self.loginButton.setObjectName("loginButton")
        self.loginButton.clicked.connect(self.loginUI)
        ####################  profButton ####################
        self.profButton = QtWidgets.QPushButton(self.menu)
        self.profButton.setGeometry(QtCore.QRect(20, 100, 131, 71))
        self.profButton.setObjectName("profButton")
        self.profButton.clicked.connect(self.profUI)
        if login_status[0] == False :
            self.profButton.setDisabled(True)
        ####################  exitButton ####################
        self.exitButton = QtWidgets.QPushButton(self.menu)
        self.exitButton.setGeometry(QtCore.QRect(20,440, 131, 31))
        self.exitButton.setObjectName("exitButton")
        self.exitButton.clicked.connect(self.exitUI)

        ####################  aboutButton ####################
        self.aboutButton = QtWidgets.QPushButton(self.menu)
        self.aboutButton.setGeometry(QtCore.QRect(20, 280, 131, 71))
        self.aboutButton.setObjectName("aboutButton")
        ####################  logoutButton ####################
        self.logoutButton = QtWidgets.QPushButton(self.menu)
        self.logoutButton.setGeometry(QtCore.QRect(20, 190, 131, 71))
        self.logoutButton.setObjectName("logoutButton")
        self.logoutButton.clicked.connect(self.logoutUI)
        if login_status[0] == False :
            self.logoutButton.setDisabled(True)
        ####################  verticalLayout_2  Right side ####################
        self.verticalLayout.addWidget(self.menu)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(179, 0, 1200, 500))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.main = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.main.setObjectName("main")
        effect = QGraphicsOpacityEffect(self.main)
        self.main.setGraphicsEffect(effect)

        ####################  usage   ####################
        self.usage = QtWidgets.QLabel(self.main)
        self.usage.setGeometry(QtCore.QRect(290, 190, 410, 100))
        self.usage.setObjectName("usage")
        self.usage.setStyleSheet('''font-family : "Lucida Console", "Courier New", monospace; font-size : 20px; color:white''')
        ####################  label   ####################
        self.label = QtWidgets.QLabel(self.main)
        self.label.setGeometry(QtCore.QRect(250, 140, 71, 31))
        self.label.setObjectName("label")
        self.label.setStyleSheet('''font-family : "Lucida Console", "Courier New", monospace; font-size : 20px; color:white''')
        
        self.author = QtWidgets.QLabel(self.main)
        self.author.setGeometry(QtCore.QRect(100, 455, 61, 16))
        self.author.setObjectName("author")
        self.author.setStyleSheet('''font-family : "Lucida Console", "Courier New", monospace; font-size : 15px; color:white''')
        self.verticalLayout_2.addWidget(self.main)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QtWidgets.QMessageBox
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # Buttons Actions

    def loginUI(self):
        _translate = QtCore.QCoreApplication.translate
        self.verticalLayout_2.removeWidget(self.main)
        # configure Buttons
        self.loginButton.setDisabled(True)
        self.profButton.setEnabled(True)
        self.aboutButton.setEnabled(True)
        if login_status[0] == False :
            self.logoutButton.setDisabled(True)
            self.profButton.setDisabled(True)
        else :
            self.logoutButton.setEnabled(True)
        ######################################
        self.main = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.main.setObjectName("main")
        
        #############      sendButton     ###################
        self.sendButton = QtWidgets.QPushButton(self.main)
        self.sendButton.setGeometry(QtCore.QRect(10, 10, 141, 51))
        self.sendButton.setObjectName("sendButton")
        self.sendButton.clicked.connect(self.sendUI)
        
        #############      refreshButton     ###################
        self.refreshButton = QtWidgets.QPushButton(self.main)
        self.refreshButton.setGeometry(QtCore.QRect(170, 10, 141, 51))
        self.refreshButton.setObjectName("refreshButton")
        self.refreshButton.clicked.connect(self.qr_update)
        
        #############      tokenButton     ###################
        self.tokenButton = QtWidgets.QPushButton(self.main)
        self.tokenButton.setGeometry(QtCore.QRect(340, 10, 141, 51))
        self.tokenButton.setObjectName("tokenButton")
        self.tokenButton.clicked.connect(self.tokenUI)
        self.tokenButton.setEnabled(True)
        #############      qrlabel     ####################
        self.qrlabel = QtWidgets.QLabel(self.main)
        self.qrlabel.setGeometry(QtCore.QRect(6, 80, 1181, 500))
        self.qrlabel.maximumSize()
        self.qrlabel.setScaledContents(True)
        self.qrlabel.setText("")
        self.qrlabel.setStyleSheet("background-image : url(img/main.png);")
        self.qrlabel.resize(1000, 438)
        self.qrlabel.setObjectName("qrlabel")
        ##########################################
        self.verticalLayout_2.addWidget(self.main) 
        self.status_label = QtWidgets.QLabel(self.main)
        self.status_label.setGeometry(QtCore.QRect(500, 0, 71, 31))
        self.status_label.setObjectName("status_label")
        self.status_label.setFixedSize(200,70)
        self.status_label.setStyleSheet('''font-family : "Lucida Console", "Courier New", monospace; font-size : 15px; color:red''')        
        self.status_label.setText(_translate("MainWindow", "You are not Login X "))
        if login_status[0] == True:
            self.status_label.setStyleSheet('''font-family : "Lucida Console", "Courier New", monospace; font-size : 15px; color:green''')
            self.status_label.setText(_translate("MainWindow", "Loged in ✔"))
        self.sendButton.setText(_translate("MainWindow", "Send"))
        self.refreshButton.setText(_translate("MainWindow", "Refresh"))
        self.tokenButton.setText(_translate("MainWindow", "Token"))
        
        
    def qr_update(self,message): 
        if login_status[0] == False :
             return self.error_handler('Insert your token first')
        #############      Login Thread     ####################
        self.login = QrThread()
        self.login.start()
        self.login.update_progress.connect(self.error_handler)
        if self.login.isRunning():
            self.tokenButton.setDisabled(True)  
            self.aboutButton.setDisabled(True)
            self.logoutButton.setDisabled(True)
            self.sendButton.setDisabled(True)
            self.refreshButton.setStyleSheet("background-color : rgba(89, 99, 110, 1);")
        self.verticalLayout_2.addWidget(self.main)
        self.login.finished.connect(self.qr_image)


    def qr_image(self):
        self.loginButton.setEnabled(True)
        self.sendButton.setEnabled(True)
        self.tokenButton.setEnabled(True)
        self.profButton.setEnabled(True)
        self.aboutButton.setEnabled(True)
        self.logoutButton.setEnabled(True)
        self.refreshButton.setStyleSheet("background-color : rgba(52, 58, 64, 1);")
        self.qrlabel.resize(1000, 438)
        self.qrlabel.setObjectName("qrlabel")
        self.qrlabel.setStyleSheet("background-image : url(img/main.png);")
        self.verticalLayout_2.addWidget(self.main) 
    
    def sendUI(self):
        self.logoutButton.setDisabled(True)
        self.loginButton.setEnabled(True)
        self.sendButton.setEnabled(True)
        _translate = QtCore.QCoreApplication.translate
        self.verticalLayout_2.removeWidget(self.main)
        self.main = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.main.setObjectName("main")
        self.main.setStyleSheet("QPushButton:pressed {background-color : rgba(64, 64, 64, 0.75);}")
        scroll_bar = QtWidgets.QScrollBar()
        scroll_bar.setStyleSheet("background : #3a5c50;")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.main)
        self.plainTextEdit.setStyleSheet('background : #3A4147; color : white;')
        self.plainTextEdit.setVerticalScrollBar(scroll_bar)
        self.plainTextEdit.setGeometry(QtCore.QRect(100, 85, 685, 261))
        self.plainTextEdit.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.plainTextEdit.setFrameShadow(QtWidgets.QFrame.Plain)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.plainTextEdit.setReadOnly(True)

        ############     Remove duplicate        #############
        self.duplicateButton = QtWidgets.QPushButton(self.main)
        self.duplicateButton.setGeometry(QtCore.QRect(100, 10, 250, 71))
        self.duplicateButton.setObjectName("duplicateButton")
        self.duplicateButton.setText(_translate("MainWindow", "Remove duplicate numbers"))
        self.duplicateButton.clicked.connect(self.duplicate_progress)

        #############      cancelButton     ####################
        self.cancelButton = QtWidgets.QPushButton(self.main)
        self.cancelButton.setGeometry(QtCore.QRect(100, 350, 125, 61))
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.setText(_translate("MainWindow", "Cancel"))
        self.cancelButton.setDisabled(True)
        self.cancelButton.clicked.connect(self.cancel_progress)
        #############      startButton     ####################
        self.startButton = QtWidgets.QPushButton(self.main)
        self.startButton.setGeometry(QtCore.QRect(240, 350, 125, 61))
        self.startButton.setObjectName("startButton")
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.startButton.clicked.connect(self.start_progress)
        #############      pauseButton     ####################
        self.pauseButton = QtWidgets.QPushButton(self.main)
        self.pauseButton.setGeometry(QtCore.QRect(380, 350, 125, 61))
        self.pauseButton.setObjectName("pauseButton")
        self.pauseButton.setText(_translate("MainWindow", "Pause"))
        self.pauseButton.clicked.connect(self.pause_progress)
        self.pauseButton.setDisabled(True)
        
        self.resumeButton = QtWidgets.QPushButton(self.main)
        self.resumeButton.setGeometry(QtCore.QRect(520, 350, 125, 61))
        self.resumeButton.setObjectName("resumeButton")
        self.resumeButton.setText(_translate("MainWindow", "Resume"))
        self.resumeButton.pressed.connect(self.resume_progress)
        self.resumeButton.setDisabled(True)

        self.clearButton = QtWidgets.QPushButton(self.main)
        self.clearButton.setGeometry(QtCore.QRect(660, 350, 125, 61))
        self.clearButton.setObjectName("clearButton")
        self.clearButton.setText(_translate("MainWindow", "Clear"))
        self.clearButton.pressed.connect(self.clear_progress)
        self.verticalLayout_2.addWidget(self.main)

    def duplicate_progress(self):
        self.duplicate = DuplicateThread()
        self.duplicate.start()
        self.duplicate.update_progress.connect(self.error_handler)

    def clear_progress(self):
        self.plainTextEdit.clear()

    def resume_progress(self):
        self.send.is_paused = False
    
    def pause_progress(self):
        self.cancelButton.setEnabled(True)
        self.resumeButton.setEnabled(True)
        self.send.is_paused = True

    def cancel_progress(self) :
        try :
            self.startButton.setEnabled(True)
            self.send.is_paused = False
            self.send.is_killed = True
            self.send.exit()
        except :
            pass
        finally:
            self.resumeButton.setDisabled(True)
            self.pauseButton.setDisabled(True)
            self.cancelButton.setDisabled(True)
            
    def start_progress(self):
        try :
            self.pauseButton.setEnabled(True)
            self.resumeButton.setEnabled(True)
            self.cancelButton.setEnabled(True)
            self.send = SendThread(token_in=login_detail['token'],username=login_detail['username'])
            self.send.start()
            self.send.update_progress.connect(self.logger)
        except:
            pass
        finally:
            self.startButton.setDisabled(True)
        
        
    def logger(self,message):
        try :
            self.plainTextEdit.appendPlainText(message)
        except:
            pass
    def error_handler(self,message):    
        self.msg = QMessageBox()
        self.msg.setWindowIcon(QtGui.QIcon('img/info_icon.png'))
        self.msg.setStyleSheet("""background : #9C9C9C;font-family : "Lucida Console", "Courier New", monospace;""")
        self.msg.setFixedSize(300,250)
        self.msg.setText(message)
        self.msg.setWindowTitle("Info")
        self.msg.setStandardButtons(QMessageBox.Ok)
        self.msg.exec()

    def tokenUI(self):
        if tokenPopup_status[0] == True:
            return ''
        if login_status[0] == True:
            return ''
        _translate = QtCore.QCoreApplication.translate
        dialog = LoginPopup()
        tokenPopup_status[0] = True
        try :
            if dialog.exec_():
                pass 
        except:
            pass     
        finally:
            sleep(2)
            if login_status[0] == True:
                self.status_label.setStyleSheet('''font-family : "Lucida Console", "Courier New", monospace; font-size : 15px; color:green''')
                self.status_label.setText(_translate("MainWindow", "Loged in ✔"))
                self.logoutButton.setEnabled(True)
                self.profButton.setEnabled(True)
            elif login_status[0] == False:
                self.status_label.setStyleSheet('''font-family : "Lucida Console", "Courier New", monospace; font-size : 15px; color:red''')
                self.status_label.setText(_translate("MainWindow", "You are not Login X"))
                              
   
    def logoutUI(self): 
        _translate = QtCore.QCoreApplication.translate
        self.logoutmsg = QMessageBox.question(self.centralwidget,'Logout','Are you sure you want to logout?',QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if self.logoutmsg == QMessageBox.Yes:
            try :
                driver.close()
                self.status_label.setStyleSheet('''font-family : "Lucida Console", "Courier New", monospace; font-size : 15px; color:red''')
                self.status_label.setText(_translate("MainWindow", "You are not Login X "))            
                login_status[0] = False
                login_detail['username'] = ''
                login_detail['token'] = ''
                response_info = []
                
            except:
                pass
            finally:
                driver_startup()
        else:
            pass
    

    def profUI(self):
        if profilepopup_status[0] == True :
            return ''
        dialog = ProfilePopup()
        profilepopup_status[0] = True
        if dialog.exec_():
            pass
        
    def exitUI(self):
        self.exitmsg = QMessageBox.question(self.centralwidget,'Exit','Are you sure you want to close the window?',QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if self.exitmsg == QMessageBox.Yes:
            sys.exit(app.exec_())
            # login_status[0] = False
        else:
            pass
            
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "WhatsApp"))
        MainWindow.setWindowIcon(QtGui.QIcon("img/logo.png"))
        self.loginButton.setText(_translate("MainWindow", "Login"))
        self.profButton.setText(_translate("MainWindow", "Profile"))
        self.exitButton.setText(_translate("MainWindow", "exit"))
        self.aboutButton.setText(_translate("MainWindow", "About"))
        self.logoutButton.setText(_translate("MainWindow", "Logout"))
        self.usage.setText(_translate("MainWindow", "<html><head/><body><p>1. Put your numbers to numbers.txt file</p><p>2. Insert your token</p><p>3. Send message</p></body></html>"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:11pt;\">Usage : </span></p></body></html>"))
        self.author.setText(_translate("MainWindow", "Alizare0017"))

# (64,145,108)
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setStyleSheet('''
    QMainWindow {
        background-image : url(img/gradient.png);
        font-size : 100px;
        width: 10px; /* when vertical */
        height: 10px; /* when horizontal */
    }
    QMessageBox {
        color : white;
        font-family : "Lucida Console", "Courier New", monospace;
    }
    
    QPushButton {
        border: 4px solid #343a40;
        border-radius: 10px;
        font-family : "Lucida Console", "Courier New", monospace;
        font-size : 15px;
        background-color: #343a40;
        color : white;                    
        min-width: 80px;
        border-style: outset;
        border-width: 2px;
        border-color: #495057
    }
    QPushButton:pressed {
    background-color : rgba(52, 58, 64, 0.75);
    }
    ''')
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

