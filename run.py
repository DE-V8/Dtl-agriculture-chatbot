"""
Run script for Agriculture Data Freshening Application
"""

import sys
from PyQt5.QtWidgets import QApplication
from data_fresher import DataFresheningApp

def main():
    # Create QApplication instance first
    app = QApplication(sys.argv)
    
    # Then create and show the main window
    window = DataFresheningApp()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 