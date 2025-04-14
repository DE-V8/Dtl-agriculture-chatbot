"""
Main Application for Agriculture Data Analysis

This module provides the main application window with enhanced chat interface.
"""

import sys
import os
import pandas as pd
import numpy as np
import kagglehub
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QTableView, QMessageBox, QComboBox, QTabWidget,
                            QGroupBox, QFormLayout, QLineEdit, QCheckBox, 
                            QProgressBar, QStatusBar)
from PyQt5.QtCore import Qt, QAbstractTableModel, QSortFilterProxyModel, QVariant
from PyQt5.QtGui import QFont, QColor
from enhanced_chat_interface import EnhancedChatInterface

class PandasModel(QAbstractTableModel):
    """Class to populate a table view with a pandas dataframe"""
    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            if role == Qt.BackgroundRole and self._data.iloc[index.row(), index.column()] == '':
                return QColor(255, 200, 200)
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[section]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(self._data.index[section])
        return QVariant()

class DataFresheningApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = None
        self.df_original = None
        self.dataset_path = None
        # Initialize chat interface
        self.chat_interface = EnhancedChatInterface()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Agriculture Data Freshening Tool')
        self.setGeometry(100, 100, 1200, 800)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Data Loading
        self.tab_load = QWidget()
        self.tabs.addTab(self.tab_load, "Load Data")
        
        # Tab 2: Data Cleaning
        self.tab_clean = QWidget()
        self.tabs.addTab(self.tab_clean, "Clean Data")
        
        # Tab 3: Data Visualization
        self.tab_viz = QWidget()
        self.tabs.addTab(self.tab_viz, "Visualize Data")
        
        # Tab 4: Data Export
        self.tab_export = QWidget()
        self.tabs.addTab(self.tab_export, "Export Data")
        
        # Tab 5: Enhanced AI Chat
        chat_tab = EnhancedChatInterface()
        self.tabs.addTab(chat_tab, "AI Chat")
        
        # Setup each tab
        self.setup_load_tab()
        self.setup_clean_tab()
        self.setup_viz_tab()
        self.setup_export_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Status bar for messages
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
    def setup_load_tab(self):
        layout = QVBoxLayout()
        
        # Data source options
        source_group = QGroupBox("Data Source")
        source_layout = QVBoxLayout()
        
        # Kaggle dataset option
        kaggle_layout = QHBoxLayout()
        
        kaggle_btn = QPushButton("Download Kaggle Dataset")
        kaggle_btn.clicked.connect(self.download_kaggle_dataset)
        kaggle_layout.addWidget(kaggle_btn)
        
        source_layout.addLayout(kaggle_layout)
        
        # Local file option
        local_layout = QHBoxLayout()
        
        self.local_file_label = QLabel("No file selected")
        browse_btn = QPushButton("Browse Local Files")
        browse_btn.clicked.connect(self.browse_files)
        
        local_layout.addWidget(browse_btn)
        local_layout.addWidget(self.local_file_label)
        
        source_layout.addLayout(local_layout)
        source_group.setLayout(source_layout)
        
        # Data preview
        preview_group = QGroupBox("Data Preview")
        preview_layout = QVBoxLayout()
        
        self.table_view = QTableView()
        preview_layout.addWidget(self.table_view)
        
        load_file_btn = QPushButton("Load Selected File")
        load_file_btn.clicked.connect(self.load_selected_file)
        preview_layout.addWidget(load_file_btn)
        
        preview_group.setLayout(preview_layout)
        
        layout.addWidget(source_group)
        layout.addWidget(preview_group)
        
        self.tab_load.setLayout(layout)
    
    def setup_clean_tab(self):
        layout = QVBoxLayout()
        
        # Options for data cleaning
        clean_options = QGroupBox("Cleaning Options")
        options_layout = QFormLayout()
        
        # Handle missing values
        self.missing_combo = QComboBox()
        self.missing_combo.addItems(["Remove rows", "Fill with mean", "Fill with median", "Fill with mode", "Fill with zero", "Custom value"])
        options_layout.addRow("Handle Missing Values:", self.missing_combo)
        
        self.custom_value = QLineEdit()
        options_layout.addRow("Custom Fill Value:", self.custom_value)
        
        # Remove duplicates
        self.duplicates_check = QCheckBox("Remove duplicate rows")
        options_layout.addRow("", self.duplicates_check)
        
        # Outlier detection
        self.outlier_combo = QComboBox()
        self.outlier_combo.addItems(["None", "Z-Score", "IQR Method"])
        options_layout.addRow("Outlier Detection:", self.outlier_combo)
        
        # Data normalization
        self.norm_combo = QComboBox()
        self.norm_combo.addItems(["None", "Min-Max Scaling", "Z-Score Normalization"])
        options_layout.addRow("Data Normalization:", self.norm_combo)
        
        # Column selector
        self.column_combo = QComboBox()
        options_layout.addRow("Apply to Column:", self.column_combo)
        
        # Apply button
        apply_btn = QPushButton("Apply Cleaning")
        apply_btn.clicked.connect(self.apply_cleaning)
        
        clean_options.setLayout(options_layout)
        
        # Data view
        data_view_group = QGroupBox("Data View")
        data_view_layout = QVBoxLayout()
        
        self.clean_table_view = QTableView()
        data_view_layout.addWidget(self.clean_table_view)
        
        # Reset button
        reset_btn = QPushButton("Reset to Original Data")
        reset_btn.clicked.connect(self.reset_data)
        data_view_layout.addWidget(reset_btn)
        
        data_view_group.setLayout(data_view_layout)
        
        layout.addWidget(clean_options)
        layout.addWidget(apply_btn)
        layout.addWidget(data_view_group)
        
        self.tab_clean.setLayout(layout)
    
    def setup_viz_tab(self):
        layout = QVBoxLayout()
        
        # Chart type selection
        viz_options = QGroupBox("Visualization Options")
        viz_layout = QFormLayout()
        
        self.chart_combo = QComboBox()
        self.chart_combo.addItems(["Bar Chart", "Line Chart", "Scatter Plot", "Histogram", "Box Plot"])
        viz_layout.addRow("Chart Type:", self.chart_combo)
        
        self.x_axis_combo = QComboBox()
        viz_layout.addRow("X-Axis:", self.x_axis_combo)
        
        self.y_axis_combo = QComboBox()
        viz_layout.addRow("Y-Axis:", self.y_axis_combo)
        
        viz_options.setLayout(viz_layout)
        
        # Placeholder for the chart
        chart_group = QGroupBox("Chart")
        chart_layout = QVBoxLayout()
        
        chart_placeholder = QLabel("Chart will appear here")
        chart_placeholder.setAlignment(Qt.AlignCenter)
        chart_layout.addWidget(chart_placeholder)
        
        chart_group.setLayout(chart_layout)
        
        # Generate chart button
        gen_chart_btn = QPushButton("Generate Chart")
        gen_chart_btn.clicked.connect(self.generate_chart)
        
        layout.addWidget(viz_options)
        layout.addWidget(gen_chart_btn)
        layout.addWidget(chart_group)
        
        self.tab_viz.setLayout(layout)
    
    def setup_export_tab(self):
        layout = QVBoxLayout()
        
        # Export options
        export_options = QGroupBox("Export Options")
        export_layout = QFormLayout()
        
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["CSV", "Excel", "JSON", "Pickle"])
        export_layout.addRow("Export Format:", self.export_format_combo)
        
        self.export_path = QLineEdit()
        browse_export_btn = QPushButton("Browse")
        browse_export_btn.clicked.connect(self.browse_export_location)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.export_path)
        path_layout.addWidget(browse_export_btn)
        
        export_layout.addRow("Export Path:", path_layout)
        export_options.setLayout(export_layout)
        
        # Buttons container
        buttons_layout = QHBoxLayout()
        
        # Export button
        export_btn = QPushButton("निर्यात डेटा (Export Data)")
        export_btn.clicked.connect(self.export_data)
        export_btn.setStyleSheet(
            "QPushButton {"
            "   background-color: #4CAF50;"
            "   color: white;"
            "   border-radius: 5px;"
            "   padding: 8px 15px;"
            "   min-width: 150px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #45a049;"
            "}"
        )
        buttons_layout.addWidget(export_btn)
        
        # Send to AI button
        send_to_ai_btn = QPushButton("एआई चैटबॉट में डेटा जोड़ें\n(Add Data to AI Chatbot)")
        send_to_ai_btn.setStyleSheet(
            "QPushButton {"
            "   background-color: #2980B9;"
            "   color: white;"
            "   border-radius: 5px;"
            "   padding: 8px 15px;"
            "   min-width: 200px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #3498DB;"
            "}"
        )
        send_to_ai_btn.clicked.connect(self.send_data_to_ai)
        buttons_layout.addWidget(send_to_ai_btn)
        
        layout.addWidget(export_options)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        self.tab_export.setLayout(layout)
    
    def download_kaggle_dataset(self):
        self.status_bar.showMessage("Downloading dataset from Kaggle...")
        
        try:
            # Download latest version
            path = kagglehub.dataset_download("imtkaggleteam/agriculture-dataset-karnataka")
            self.dataset_path = path
            self.status_bar.showMessage(f"Dataset downloaded to: {path}")
            
            # List files in the downloaded dataset directory
            files = [f for f in os.listdir(path) if f.endswith(('.csv', '.xlsx', '.xls'))]
            if files:
                self.local_file_label.setText(os.path.join(path, files[0]))
                QMessageBox.information(self, "Success", f"Dataset downloaded successfully to {path}")
            else:
                QMessageBox.warning(self, "Warning", "No CSV or Excel files found in the downloaded dataset")
        except Exception as e:
            self.status_bar.showMessage(f"Error downloading dataset: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to download dataset: {str(e)}")
    
    def browse_files(self):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Data File", "", "Data Files (*.csv *.xlsx *.xls);;All Files (*)", options=options)
        
        if filepath:
            self.local_file_label.setText(filepath)
    
    def load_selected_file(self):
        file_path = self.local_file_label.text()
        
        if file_path == "No file selected":
            QMessageBox.warning(self, "Warning", "Please select a file first")
            return
            
        try:
            if file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(file_path)
                
            # Keep a copy of the original data
            self.df_original = self.df.copy()
            
            # Update table view
            model = PandasModel(self.df)
            self.table_view.setModel(model)
            self.clean_table_view.setModel(model)
            
            # Update column selections
            self.column_combo.clear()
            self.x_axis_combo.clear()
            self.y_axis_combo.clear()
            
            self.column_combo.addItems(self.df.columns)
            self.x_axis_combo.addItems(self.df.columns)
            self.y_axis_combo.addItems(self.df.columns)
            
            self.status_bar.showMessage(f"Loaded {file_path} with {len(self.df)} rows and {len(self.df.columns)} columns")
            
        except Exception as e:
            self.status_bar.showMessage(f"Error loading file: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load the file: {str(e)}")
    
    def apply_cleaning(self):
        if self.df is None:
            QMessageBox.warning(self, "Warning", "Please load data first")
            return
            
        column = self.column_combo.currentText()
        
        try:
            # Missing values handling
            missing_option = self.missing_combo.currentText()
            
            if missing_option == "Remove rows":
                self.df = self.df.dropna(subset=[column])
            elif missing_option == "Fill with mean":
                self.df[column] = self.df[column].fillna(self.df[column].mean())
            elif missing_option == "Fill with median":
                self.df[column] = self.df[column].fillna(self.df[column].median())
            elif missing_option == "Fill with mode":
                self.df[column] = self.df[column].fillna(self.df[column].mode()[0])
            elif missing_option == "Fill with zero":
                self.df[column] = self.df[column].fillna(0)
            elif missing_option == "Custom value":
                custom_val = self.custom_value.text()
                if custom_val:
                    try:
                        # Try to convert to float if possible
                        custom_val = float(custom_val)
                    except ValueError:
                        pass  # Keep as string if not convertible
                    self.df[column] = self.df[column].fillna(custom_val)
                    
            # Remove duplicates
            if self.duplicates_check.isChecked():
                self.df = self.df.drop_duplicates()
                
            # Outlier detection
            outlier_option = self.outlier_combo.currentText()
            
            if outlier_option == "Z-Score" and pd.api.types.is_numeric_dtype(self.df[column]):
                # Remove values that are more than 3 standard deviations from the mean
                z_scores = np.abs((self.df[column] - self.df[column].mean()) / self.df[column].std())
                self.df = self.df[z_scores < 3]
                
            elif outlier_option == "IQR Method" and pd.api.types.is_numeric_dtype(self.df[column]):
                # Remove values that are outside 1.5 * IQR
                Q1 = self.df[column].quantile(0.25)
                Q3 = self.df[column].quantile(0.75)
                IQR = Q3 - Q1
                self.df = self.df[~((self.df[column] < (Q1 - 1.5 * IQR)) | (self.df[column] > (Q3 + 1.5 * IQR)))]
                
            # Data normalization
            norm_option = self.norm_combo.currentText()
            
            if norm_option == "Min-Max Scaling" and pd.api.types.is_numeric_dtype(self.df[column]):
                self.df[column] = (self.df[column] - self.df[column].min()) / (self.df[column].max() - self.df[column].min())
                
            elif norm_option == "Z-Score Normalization" and pd.api.types.is_numeric_dtype(self.df[column]):
                self.df[column] = (self.df[column] - self.df[column].mean()) / self.df[column].std()
                
            # Update table view
            model = PandasModel(self.df)
            self.clean_table_view.setModel(model)
            self.table_view.setModel(model)
            
            self.status_bar.showMessage(f"Cleaning applied. Current shape: {self.df.shape}")
            
        except Exception as e:
            self.status_bar.showMessage(f"Error applying cleaning: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to apply cleaning: {str(e)}")
    
    def reset_data(self):
        if self.df_original is not None:
            self.df = self.df_original.copy()
            
            # Update table views
            model = PandasModel(self.df)
            self.clean_table_view.setModel(model)
            self.table_view.setModel(model)
            
            self.status_bar.showMessage("Data reset to original")
        else:
            QMessageBox.warning(self, "Warning", "No original data available")
    
    def generate_chart(self):
        QMessageBox.information(self, "Information", "Chart generation will be implemented in a future version")
    
    def browse_export_location(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, "Select Export Directory", options=options)
        
        if directory:
            self.export_path.setText(directory)
    
    def export_data(self):
        if self.df is None:
            QMessageBox.warning(self, "Warning", "No data to export")
            return
            
        export_format = self.export_format_combo.currentText()
        export_dir = self.export_path.text()
        
        if not export_dir:
            QMessageBox.warning(self, "Warning", "Please specify an export directory")
            return
            
        try:
            filename = f"agriculture_data_freshened.{export_format.lower()}"
            if export_format == "Excel":
                filename = "agriculture_data_freshened.xlsx"
            elif export_format == "Pickle":
                filename = "agriculture_data_freshened.pkl"
                
            filepath = os.path.join(export_dir, filename)
            
            if export_format == "CSV":
                self.df.to_csv(filepath, index=False)
            elif export_format == "Excel":
                self.df.to_excel(filepath, index=False)
            elif export_format == "JSON":
                self.df.to_json(filepath, orient='records')
            elif export_format == "Pickle":
                self.df.to_pickle(filepath)
                
            self.status_bar.showMessage(f"Data exported to {filepath}")
            QMessageBox.information(self, "Success", f"Data successfully exported to {filepath}")
            
        except Exception as e:
            self.status_bar.showMessage(f"Error exporting data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
    
    def send_data_to_ai(self):
        """Send the current data to AI chatbot"""
        if self.df is None:
            QMessageBox.warning(self, "Warning", "No data loaded. Please load data first.")
            return
            
        try:
            # Create a temporary CSV file from the current dataframe
            temp_file = "temp_data_for_ai.csv"
            self.df.to_csv(temp_file, index=False)
            
            # Load the data into the chat interface
            self.chat_interface.load_data(temp_file)
            
            # Switch to the chat tab
            self.tabs.setCurrentWidget(self.chat_interface)
            
            # Clean up the temporary file
            try:
                os.remove(temp_file)
            except:
                pass  # Ignore cleanup errors
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to send data to AI chatbot: {str(e)}"
            )

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = DataFresheningApp()
    window.show()
    
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main() 