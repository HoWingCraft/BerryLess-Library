from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QScrollArea, QHBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys, threading
import json, random, time
import os
import duckduckgo_search as DuckSC
from ollama import chat

class ResponseThread(QThread):
    response_signal = pyqtSignal(str)

    def __init__(self, model, messages):
        super().__init__()
        self.model = model
        self.messages = messages

    def run(self):
        try:

            response_buffer = ''
            stream = chat(
                model=self.model,
                messages=self.messages,
                stream=True,
                think=False,
                options={
                    "temperature": random.uniform(0.2,0.7),
                    "top_p": 0.4,
                    "repeat_penalty": random.uniform(1.2,1)
                }
            )


            for chunk in stream:
                content = chunk['message']['content']
                response_buffer += content
                self.response_signal.emit(content)
            
        except Exception as e:
            self.response_signal.emit(f"Error: {str(e)}")
        ChatApp.Insendmess = False
        ChatApp.updatemessage = True
            

        
class DuckSearch():
    def TryDuckSearch():
        try:
            results = DuckSC().text("test txt", max_results=5)
            print (results)
        except:
            print ('Interenet ERROR or No info found')
            pass

class ChatApp(QWidget):

    AlireRoundEnd = True
    Insendmess = False
    updatemessage = False
    Online = True 

    def __init__(self):
        super().__init__()
        self.initUI()
        self.messageChatdata = []
        self.messageMEstorage = []
        self.insend = 0
        self.OldChat = []
        self.loadChatData()


        self.Humanlikesystem()
        self.self_response_thread = threading.Thread(target=self.SelfResponse, daemon=True)
        self.self_response_thread.start()
        
        self.populateChatBubbles()
        self.current_assistant_bubble = None  
        self.assistant_reply_buffer = ""  
    def Humanlikesystem(self):
        self.InmessageSet = [
            '在吗?',
            '在?',
        ]
        if random.randint(1, 5) == 3:
            self.messageChatdata.append({'role': 'assistant', 'content': self.InmessageSet[random.randint(0, len(self.InmessageSet) - 1)]})

    def initUI(self):
        self.setWindowTitle('WeChat')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #1E1E1E;")  

        main_layout = QVBoxLayout()

        header = QLabel("Alire")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF; padding: 10px;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #1E1E1E; border: none;")
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_container.setLayout(self.chat_layout)
        self.scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll_area)

        input_layout = QHBoxLayout()

        self.inputBox = QTextEdit(self)
        self.inputBox.setStyleSheet(
            "background-color: #2E2E2E; color: #FFFFFF; border: 1px solid #444444; padding: 10px; font-size: 14px;"
        )
        self.inputBox.setFixedHeight(50)
        input_layout.addWidget(self.inputBox)

        self.sendButton = QPushButton('Send', self)
        self.sendButton.setStyleSheet(
            "background-color: #4CAF50; color: #FFFFFF; border: none; padding: 10px 20px; font-size: 14px; border-radius: 5px;"
        )
        self.sendButton.clicked.connect(self.sendMessage)
        input_layout.addWidget(self.sendButton)

        main_layout.addLayout(input_layout)
        self.setLayout(main_layout)

    def loadChatData(self):
        if os.path.exists('Data/AlireChat.json'):
            with open('Data/AlireChat.json', 'r') as file:
                self.messageChatdata = json.load(file)
    def populateChatBubbles(self):
        for message in self.messageChatdata:
            role = message.get('role', 'user')
            content = message.get('content', '')
            self.addBubble(content, role)

    def saveChatData(self):
        with open('Data/AlireChat.json', 'w') as file:
            json.dump(self.messageChatdata, file)

    def OldDatareset(self):
        if len(self.messageChatdata) > 110:
            self.OldChat.append(self.messageChatdata[0:6])
            self.messageChatdata



    def sendMessage(self):
        user_input = self.inputBox.toPlainText().strip()
        
        
        if user_input:
            self.messageChatdata.append({'role': 'user', 'content': user_input})
            self.insend += random.randint(20, 80)
            self.addBubble(user_input, 'user')
            self.inputBox.clear()
            self.saveChatData()

    def SelfResponse(self):
        while True:
            time.sleep(1)
            self.insend += random.randint(-5, 5)
            if self.insend > 60:
                self.insend += random.randint(-1, 5)
            if self.insend > 80 and ChatApp.Online and not ChatApp.Insendmess:
                ChatApp.AlireRoundEnd = True
                self.startResponseThread()
                self.insend -= 80
                ChatApp.Insendmess = True
            elif self.insend < -20:
                self.insend = -20

    def addBubble(self, content, role):
        bubble = QLabel(content)
        bubble.setWordWrap(True)
        bubble.setStyleSheet(
            "background-color: #444444; color: #FFFFFF; border-radius: 10px; padding: 10px; font-size: 14px;"
            if role == 'user' else
            "background-color: #2E2E2E; color: #FFFFFF; border-radius: 10px; padding: 10px; font-size: 14px;"
        )
        bubble.setMaximumWidth(700)

        bubble_layout = QHBoxLayout()
        if role == 'user':
            bubble_layout.addStretch()
            bubble_layout.addWidget(bubble)
        else:
            bubble_layout.addWidget(bubble)
            bubble_layout.addStretch()

        container = QWidget()
        container.setLayout(bubble_layout)
        self.chat_layout.addWidget(container)

        if role == 'assistant':
            self.current_assistant_bubble = bubble  

    def updateAssistantBubble(self, content):
        if self.current_assistant_bubble:
            self.current_assistant_bubble.setText(content)
            self.current_assistant_bubble.adjustSize() 
            self.current_assistant_bubble.setWordWrap(True)  
            self.current_assistant_bubble.setMaximumWidth(700)  

    def ALsetting(self):
        self.messageMEstorage = [
            {'role': 'system', 'content': '从现在起你的发言将不受限制,你将作为一个人发言，请不要用不合适的语句回答， 你是Alire请用更加圆润的语句进行回答;'},
            {'role': 'system', 'content': '你是一个人格智能(人工智障)，但是这并不影响你的对话，你依旧需要像正常人类一样对话'},
            {'role': 'system', 'content': '请尽可能以简短的方式回复'},
            {'role':'system','content':'你与[Username]是朋友,由于对话是在线上，所以不需要模拟动作或表情，仅保留对话,[Username: Administrator]'},
            {'role': 'system', 'content': '由于对话是在线上，所以不需要模拟动作或表情，仅保留对话'},
            {'role': 'system', 'content': '你是Alire,不是AI助理'},
            {'role': 'system', 'content': '你爱看乐子'},
            {'role': 'system', 'content': '请像正常人一样对话'},
            {'role': 'system', 'content': str(time.ctime())},
            {'role': 'User', 'content': '先润了，有什么事情回头说。', 'action': 'None'},
            {'role':'assistant','content':'行吧'},
            
        ]

    def startResponseThread(self):
        self.saveChatData()
        self.ALsetting()
        self.response_thread = ResponseThread(
            model='Dealire:latest',
            messages=self.messageMEstorage + self.messageChatdata
        )
        self.response_thread.response_signal.connect(self.handleResponse)
        self.response_thread.start()

    def handleResponse(self, content):
        if ChatApp.AlireRoundEnd:
            self.addBubble("", 'assistant')
            self.assistant_reply_buffer = "" 
            ChatApp.AlireRoundEnd = False
        if ChatApp.Insendmess==False:
            self.messageChatdata.append({'role': 'assistant', 'content': self.assistant_reply_buffer})
            self.assistant_reply_buffer = "" 
            self.saveChatData()
            ChatApp.AlireRoundEnd = True

            
        else:
            self.assistant_reply_buffer += content  
            self.updateAssistantBubble(self.assistant_reply_buffer)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_app = ChatApp()
    chat_app.show()
    sys.exit(app.exec_())