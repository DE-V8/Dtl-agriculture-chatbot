"""
Enhanced Chat Interface for Agriculture Data Analysis

This module provides an enhanced chat interface with modern UI features.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                           QPushButton, QProgressBar, QLabel, QScrollArea, 
                           QFrame, QSplitter, QComboBox, QToolButton, QMenu,
                           QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QTextCursor, QColor, QPalette
import json
import time
import pandas as pd
from typing import Optional
from llm_handler import LLMHandler

class MessageBubble(QFrame):
    """Custom widget for chat message bubbles"""
    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(
            "MessageBubble {"
            "   border-radius: 15px;"
            f"  background-color: {'#DCF8C6' if is_user else '#E8E8E8'};"
            "   padding: 15px;"  # Increased padding
            "   margin: 10px;"   # Increased margin
            "   min-width: 200px;"  # Added minimum width
            "   max-width: 800px;"  # Added maximum width
            "}"
        )
        
        layout = QVBoxLayout()
        layout.setSpacing(8)  # Added spacing between message and timestamp
        
        # Message text
        message = QLabel(text)
        message.setWordWrap(True)
        message.setStyleSheet(
            "color: #2C3E50;"
            "font-size: 14px;"  # Increased font size
            "line-height: 1.4;"  # Added line height
        )
        
        # Timestamp
        timestamp = QLabel(time.strftime("%H:%M"))
        timestamp.setStyleSheet(
            "color: #7F8C8D;"
            "font-size: 11px;"  # Slightly increased timestamp font size
            "margin-top: 5px;"
        )
        
        layout.addWidget(message)
        layout.addWidget(timestamp)
        self.setLayout(layout)

class EnhancedChatInterface(QWidget):
    """Enhanced chat interface with modern features"""
    
    data_loaded = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.llm_handler = LLMHandler()
        self.current_data = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)  # Added spacing between elements
        
        # Create header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Create chat area
        chat_splitter = QSplitter(Qt.Vertical)
        chat_splitter.setStyleSheet(
            "QSplitter::handle {"
            "   background: #E0E0E0;"
            "   height: 2px;"
            "}"
        )
        
        # Messages area
        self.messages_area = QScrollArea()
        self.messages_area.setWidgetResizable(True)
        self.messages_area.setMinimumHeight(400)  # Set minimum height
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.addStretch()
        self.messages_widget.setLayout(self.messages_layout)
        self.messages_area.setWidget(self.messages_widget)
        
        # Set style for messages area
        self.messages_area.setStyleSheet(
            "QScrollArea {"
            "   background-color: #FFFFFF;"
            "   border: 1px solid #E0E0E0;"
            "   border-radius: 5px;"
            "}"
            "QScrollBar:vertical {"
            "   border: none;"
            "   background: #F0F0F0;"
            "   width: 10px;"
            "   border-radius: 5px;"
            "}"
            "QScrollBar::handle:vertical {"
            "   background: #C0C0C0;"
            "   border-radius: 5px;"
            "}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
            "   border: none;"
            "   background: none;"
            "}"
        )
        
        chat_splitter.addWidget(self.messages_area)
        
        # Input area
        input_widget = self.create_input_area()
        chat_splitter.addWidget(input_widget)
        
        # Set stretch factors for splitter
        chat_splitter.setStretchFactor(0, 4)  # Messages area gets more space
        chat_splitter.setStretchFactor(1, 1)  # Input area gets less space
        
        main_layout.addWidget(chat_splitter)
        
        # Data status indicator
        self.data_status = QLabel("No data loaded")
        self.data_status.setStyleSheet(
            "QLabel {"
            "   color: #7F8C8D;"
            "   font-style: italic;"
            "   padding: 8px;"
            "   background: #F8F9FA;"
            "   border-radius: 4px;"
            "   margin: 5px 0px;"
            "}"
        )
        main_layout.addWidget(self.data_status)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            "QProgressBar {"
            "   border: 1px solid #E0E0E0;"
            "   border-radius: 5px;"
            "   text-align: center;"
            "   height: 20px;"
            "}"
            "QProgressBar::chunk {"
            "   background-color: #4CAF50;"
            "   border-radius: 4px;"
            "}"
        )
        main_layout.addWidget(self.progress_bar)
        
        self.setLayout(main_layout)
        
    def create_header(self) -> QWidget:
        """Create the header section"""
        header = QWidget()
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("Agricultural Data Analysis Chat")
        title.setStyleSheet(
            "font-size: 18px;"
            "font-weight: bold;"
            "color: #2C3E50;"
        )
        
        # Model selector
        self.model_selector = QComboBox()
        self.model_selector.addItems(["llama-3.2-1b-instruct", "Other models..."])
        self.model_selector.setStyleSheet(
            "QComboBox {"
            "   border: 1px solid #E0E0E0;"
            "   border-radius: 3px;"
            "   padding: 5px;"
            "}"
        )
        
        # Settings button
        settings_btn = QToolButton()
        settings_btn.setIcon(self.style().standardIcon(self.style().SP_DialogHelpButton))
        settings_btn.setPopupMode(QToolButton.InstantPopup)
        settings_menu = QMenu()
        settings_menu.addAction("Clear Chat", self.clear_chat)
        settings_menu.addAction("Export Chat", self.export_chat)
        settings_menu.addAction("Clear Loaded Data", self.clear_data)
        settings_menu.addAction("Settings", self.show_settings)
        settings_btn.setMenu(settings_menu)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.model_selector)
        header_layout.addWidget(settings_btn)
        
        header.setLayout(header_layout)
        return header
        
    def create_input_area(self) -> QWidget:
        """Create the input area"""
        input_widget = QWidget()
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)  # Added spacing
        
        # Message input
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setMinimumHeight(80)  # Increased minimum height
        self.message_input.setMaximumHeight(120)  # Increased maximum height
        self.message_input.setStyleSheet(
            "QTextEdit {"
            "   border: 1px solid #E0E0E0;"
            "   border-radius: 8px;"  # Increased border radius
            "   padding: 12px;"       # Increased padding
            "   font-size: 14px;"     # Increased font size
            "   background-color: #FFFFFF;"
            "}"
            "QTextEdit:focus {"
            "   border: 2px solid #2980B9;"
            "}"
        )
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)  # Added spacing between buttons
        
        # Stream toggle
        self.stream_toggle = QPushButton("Stream Mode: Off")
        self.stream_toggle.setCheckable(True)
        self.stream_toggle.setStyleSheet(
            "QPushButton {"
            "   background-color: #808080;"
            "   color: white;"
            "   border-radius: 8px;"  # Increased border radius
            "   padding: 10px 20px;"  # Increased padding
            "   font-size: 13px;"     # Increased font size
            "}"
            "QPushButton:checked {"
            "   background-color: #4CAF50;"
            "}"
        )
        self.stream_toggle.toggled.connect(self.toggle_stream_mode)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet(
            "QPushButton {"
            "   background-color: #2980B9;"
            "   color: white;"
            "   border-radius: 8px;"  # Increased border radius
            "   padding: 10px 30px;"  # Increased padding
            "   font-size: 14px;"     # Increased font size
            "   font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "   background-color: #3498DB;"
            "}"
        )
        self.send_button.clicked.connect(self.send_message)
        
        buttons_layout.addWidget(self.stream_toggle)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.send_button)
        
        input_layout.addWidget(self.message_input)
        input_layout.addLayout(buttons_layout)
        
        input_widget.setLayout(input_layout)
        return input_widget
        
    def load_data(self, data_path: str):
        """Load data into the chat interface"""
        try:
            self.current_data = pd.read_csv(data_path)
            self.data_status.setText(f"Data loaded: {data_path}")
            self.data_status.setStyleSheet(
                "QLabel {"
                "   color: #27AE60;"
                "   font-style: normal;"
                "   padding: 5px;"
                "}"
            )
            
            # Notify user through chat
            self.add_message(
                "मैंने डेटा प्राप्त कर लिया है। आप इस डेटा से क्या जानना चाहते हैं?\n\n"
                "I have got the data now. What would you like to know from it?",
                False
            )
            
            # Update LLM handler with the new data
            if hasattr(self.llm_handler, 'set_current_data'):
                self.llm_handler.set_current_data(self.current_data)
                
            self.data_loaded.emit()
            
        except Exception as e:
            self.data_status.setText(f"Error loading data: {str(e)}")
            self.data_status.setStyleSheet(
                "QLabel {"
                "   color: #E74C3C;"
                "   font-style: normal;"
                "   padding: 5px;"
                "}"
            )
            
    def send_message(self):
        """Send a message and get response"""
        message = self.message_input.toPlainText().strip()
        if not message:
            return
            
        # Add user message
        self.add_message(message, True)
        self.message_input.clear()
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Infinite progress
        
        # Get response
        try:
            if self.stream_toggle.isChecked():
                self.handle_streaming_response(message)
            else:
                response = self.llm_handler.generate_response(message, data=self.current_data)
                self.add_message(response, False)
        except Exception as e:
            self.add_message(f"Error: {str(e)}", False)
            
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
    def handle_streaming_response(self, message: str):
        """Handle streaming response"""
        # Create message bubble for streaming response
        response_bubble = MessageBubble("", False)
        self.messages_layout.addWidget(response_bubble)
        
        # Get streaming response
        current_text = ""
        try:
            for chunk in self.llm_handler.generate_response(message, stream=True, data=self.current_data):
                current_text += chunk
                response_bubble.findChild(QLabel).setText(current_text)
                QApplication.processEvents()  # Update UI
        except Exception as e:
            response_bubble.findChild(QLabel).setText(f"Error: {str(e)}")
            
    def add_message(self, text: str, is_user: bool):
        """Add a message bubble to the chat"""
        bubble = MessageBubble(text, is_user)
        self.messages_layout.addWidget(bubble)
        
        # Scroll to bottom
        QTimer.singleShot(100, lambda: self.messages_area.verticalScrollBar().setValue(
            self.messages_area.verticalScrollBar().maximum()
        ))
        
    def toggle_stream_mode(self, checked: bool):
        """Toggle streaming mode"""
        self.stream_toggle.setText(f"Stream Mode: {'On' if checked else 'Off'}")
        
    def clear_chat(self):
        """Clear all messages from chat"""
        while self.messages_layout.count() > 1:  # Keep the stretch at the top
            item = self.messages_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
                
    def export_chat(self):
        """Export chat history to JSON"""
        history = []
        for i in range(1, self.messages_layout.count()):  # Skip the stretch
            widget = self.messages_layout.itemAt(i).widget()
            if isinstance(widget, MessageBubble):
                message = widget.findChild(QLabel).text()
                timestamp = widget.findChildren(QLabel)[1].text()
                history.append({
                    "message": message,
                    "timestamp": timestamp,
                    "is_user": widget.property("is_user")
                })
                
        with open("chat_history.json", "w") as f:
            json.dump(history, f, indent=2)
            
    def show_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        pass
        
    def clear_data(self):
        """Clear the currently loaded data"""
        self.current_data = None
        self.data_status.setText("No data loaded")
        self.data_status.setStyleSheet(
            "QLabel {"
            "   color: #7F8C8D;"
            "   font-style: italic;"
            "   padding: 5px;"
            "}"
        )
        
        if hasattr(self.llm_handler, 'set_current_data'):
            self.llm_handler.set_current_data(None)
            
        self.add_message("Data has been cleared. I no longer have access to the previous dataset.", False) 