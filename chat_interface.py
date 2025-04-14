"""
AI Chat Interface for Agriculture Data Analysis

This module provides a chat interface that allows users to:
- Chat with an AI about agricultural data
- Store chat history in JSON format
- Load and analyze agricultural data through conversation
"""

import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QPushButton, QLabel, QScrollArea, QFrame,
                            QProgressBar)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from llm_handler import LLMHandler

class ResponseWorker(QThread):
    """Worker thread for generating LLM responses"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, llm_handler, message, context=""):
        super().__init__()
        self.llm_handler = llm_handler
        self.message = message
        self.context = context
        
    def run(self):
        try:
            response = self.llm_handler.generate_response(self.message, self.context)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))

class ChatMessage(QFrame):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Add timestamp
        timestamp = QLabel(datetime.now().strftime("%H:%M:%S"))
        timestamp.setStyleSheet("color: #666; font-size: 8pt;")
        layout.addWidget(timestamp)
        
        # Add message text
        message = QLabel(text)
        message.setWordWrap(True)
        message.setStyleSheet(f"""
            QLabel {{
                color: {'#000000' if is_user else '#2c3e50'};
                font-size: 10pt;
            }}
        """)
        layout.addWidget(message)
        
        self.setLayout(layout)

class ChatInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat_history = []
        self.chat_file = "chat_history.json"
        self.llm_handler = LLMHandler()
        self.load_chat_history()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        # Scroll area for chat messages
        scroll = QScrollArea()
        scroll.setWidget(self.chat_display)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Progress bar for LLM processing
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setPlaceholderText("अपना संदेश यहाँ लिखें... (Type your message here...)")
        self.message_input.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        send_button = QPushButton("भेजें (Send)")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_button)
        
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
        
        # Display existing chat history
        self.display_chat_history()
        
    def load_chat_history(self):
        try:
            if os.path.exists(self.chat_file):
                with open(self.chat_file, 'r', encoding='utf-8') as f:
                    self.chat_history = json.load(f)
        except Exception as e:
            print(f"Error loading chat history: {e}")
            self.chat_history = []
            
    def save_chat_history(self):
        try:
            with open(self.chat_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving chat history: {e}")
            
    def display_chat_history(self):
        for message in self.chat_history:
            self.add_message_to_display(message['text'], message['is_user'])
            
    def add_message_to_display(self, text, is_user=True):
        message = ChatMessage(text, is_user)
        self.chat_display.append(f"{'You' if is_user else 'AI'}: {text}")
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
        
    def send_message(self):
        user_message = self.message_input.toPlainText().strip()
        if not user_message:
            return
            
        # Disable input while processing
        self.message_input.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Add user message to chat
        self.add_message_to_display(user_message, True)
        self.chat_history.append({
            'text': user_message,
            'is_user': True,
            'timestamp': datetime.now().isoformat()
        })
        
        # Clear input
        self.message_input.clear()
        
        # Create and start worker thread for LLM response
        self.worker = ResponseWorker(self.llm_handler, user_message)
        self.worker.finished.connect(self.handle_llm_response)
        self.worker.error.connect(self.handle_llm_error)
        self.worker.start()
        
    def handle_llm_response(self, response):
        # Add AI response to chat
        self.add_message_to_display(response, False)
        self.chat_history.append({
            'text': response,
            'is_user': False,
            'timestamp': datetime.now().isoformat()
        })
        
        # Save chat history
        self.save_chat_history()
        
        # Re-enable input
        self.message_input.setEnabled(True)
        self.progress_bar.setVisible(False)
        
    def handle_llm_error(self, error):
        # Show error message
        error_response = f"क्षमा करें, एक त्रुटि हुई: {error}\nकृपया पुनः प्रयास करें। (Sorry, an error occurred: {error}\nPlease try again.)"
        self.add_message_to_display(error_response, False)
        
        # Re-enable input
        self.message_input.setEnabled(True)
        self.progress_bar.setVisible(False) 