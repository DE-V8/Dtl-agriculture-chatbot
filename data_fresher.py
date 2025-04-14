"""
Agriculture Data Freshening GUI Application

This application provides a simple interface for:
- Loading agricultural data (local files or Kaggle dataset)
- Cleaning and preprocessing the data
- Visualizing data patterns
- Exporting the processed data
- Chatting with AI about agricultural data

Requirements:
- PyQt5
- pandas
- numpy
- kagglehub (optional, for Kaggle dataset downloads)
"""

import sys
import os
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QTableView, QMessageBox, QComboBox, QTabWidget,
                            QGroupBox, QFormLayout, QLineEdit, QCheckBox, 
                            QProgressBar, QStatusBar)
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant
from PyQt5.QtGui import QFont, QColor
from chat_interface import ChatInterface

# Optional import for Kaggle dataset download
try:
    import kagglehub
    KAGGLE_AVAILABLE = True
except ImportError:
    KAGGLE_AVAILABLE = False

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
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('कृषि डेटा फ्रेशनिंग टूल (Agriculture Data Freshening Tool)')
        self.setGeometry(100, 100, 1200, 800)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Data Loading
        self.tab_load = QWidget()
        self.tabs.addTab(self.tab_load, "डेटा लोड करें (Load Data)")
        
        # Tab 2: Data Cleaning
        self.tab_clean = QWidget()
        self.tabs.addTab(self.tab_clean, "डेटा साफ करें (Clean Data)")
        
        # Tab 3: Data Export
        self.tab_export = QWidget()
        self.tabs.addTab(self.tab_export, "डेटा निर्यात करें (Export Data)")
        
        # Tab 4: AI Chat Interface
        self.chat_interface = ChatInterface()
        self.tabs.addTab(self.chat_interface, "एआई चैट (AI Chat)")
        
        # Setup each tab
        self.setup_load_tab()
        self.setup_clean_tab()
        self.setup_export_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Status bar for messages
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("तैयार (Ready)")
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
    def setup_load_tab(self):
        layout = QVBoxLayout()
        
        # Data source options
        source_group = QGroupBox("डेटा स्रोत (Data Source)")
        source_layout = QVBoxLayout()
        
        # Kaggle dataset option
        if KAGGLE_AVAILABLE:
            kaggle_layout = QHBoxLayout()
            
            kaggle_btn = QPushButton("कागले से डेटासेट डाउनलोड करें (Download Kaggle Dataset)")
            kaggle_btn.clicked.connect(self.download_kaggle_dataset)
            kaggle_layout.addWidget(kaggle_btn)
            
            source_layout.addLayout(kaggle_layout)
        else:
            kaggle_info = QLabel("कागलेहब मॉड्यूल इंस्टॉल नहीं है। कागले डाउनलोड अनुपलब्ध है। (kagglehub module not installed. Kaggle download unavailable.)")
            source_layout.addWidget(kaggle_info)
        
        # Local file option
        local_layout = QHBoxLayout()
        
        self.local_file_label = QLabel("कोई फाइल नहीं चुनी गई (No file selected)")
        browse_btn = QPushButton("फाइल ब्राउज़ करें (Browse Local Files)")
        browse_btn.clicked.connect(self.browse_files)
        
        local_layout.addWidget(browse_btn)
        local_layout.addWidget(self.local_file_label)
        
        source_layout.addLayout(local_layout)
        source_group.setLayout(source_layout)
        
        # Data preview
        preview_group = QGroupBox("डेटा प्रीव्यू (Data Preview)")
        preview_layout = QVBoxLayout()
        
        self.table_view = QTableView()
        preview_layout.addWidget(self.table_view)
        
        load_file_btn = QPushButton("चुनी गई फाइल लोड करें (Load Selected File)")
        load_file_btn.clicked.connect(self.load_selected_file)
        preview_layout.addWidget(load_file_btn)
        
        preview_group.setLayout(preview_layout)
        
        layout.addWidget(source_group)
        layout.addWidget(preview_group)
        
        self.tab_load.setLayout(layout)
    
    def setup_clean_tab(self):
        layout = QVBoxLayout()
        
        # Options for data cleaning
        clean_options = QGroupBox("सफाई विकल्प (Cleaning Options)")
        options_layout = QFormLayout()
        
        # Handle missing values
        self.missing_combo = QComboBox()
        self.missing_combo.addItems([
            "पंक्तियां हटाएं (Remove rows)", 
            "औसत से भरें (Fill with mean)", 
            "मध्यिका से भरें (Fill with median)", 
            "मोड से भरें (Fill with mode)", 
            "शून्य से भरें (Fill with zero)", 
            "कस्टम मान (Custom value)"
        ])
        options_layout.addRow("अनुपलब्ध मान (Missing Values):", self.missing_combo)
        
        self.custom_value = QLineEdit()
        options_layout.addRow("कस्टम भरने का मान (Custom Fill Value):", self.custom_value)
        
        # Remove duplicates
        self.duplicates_check = QCheckBox("डुप्लिकेट पंक्तियां हटाएं (Remove duplicate rows)")
        options_layout.addRow("", self.duplicates_check)
        
        # Outlier detection
        self.outlier_combo = QComboBox()
        self.outlier_combo.addItems([
            "कोई नहीं (None)", 
            "Z-स्कोर (Z-Score)", 
            "IQR विधि (IQR Method)"
        ])
        options_layout.addRow("आउटलायर डिटेक्शन (Outlier Detection):", self.outlier_combo)
        
        # Data normalization
        self.norm_combo = QComboBox()
        self.norm_combo.addItems([
            "कोई नहीं (None)", 
            "मिन-मैक्स स्केलिंग (Min-Max Scaling)", 
            "Z-स्कोर नॉर्मलाइजेशन (Z-Score Normalization)"
        ])
        options_layout.addRow("डेटा नॉर्मलाइजेशन (Data Normalization):", self.norm_combo)
        
        # Column selector
        self.column_combo = QComboBox()
        options_layout.addRow("इस कॉलम पर लागू करें (Apply to Column):", self.column_combo)
        
        # Apply button
        apply_btn = QPushButton("क्लीनिंग लागू करें (Apply Cleaning)")
        apply_btn.clicked.connect(self.apply_cleaning)
        
        clean_options.setLayout(options_layout)
        
        # Data view
        data_view_group = QGroupBox("डेटा व्यू (Data View)")
        data_view_layout = QVBoxLayout()
        
        self.clean_table_view = QTableView()
        data_view_layout.addWidget(self.clean_table_view)
        
        # Reset button
        reset_btn = QPushButton("मूल डेटा पर वापस जाएँ (Reset to Original Data)")
        reset_btn.clicked.connect(self.reset_data)
        data_view_layout.addWidget(reset_btn)
        
        data_view_group.setLayout(data_view_layout)
        
        layout.addWidget(clean_options)
        layout.addWidget(apply_btn)
        layout.addWidget(data_view_group)
        
        self.tab_clean.setLayout(layout)
    
    def setup_export_tab(self):
        layout = QVBoxLayout()
        
        # Export options
        export_options = QGroupBox("निर्यात विकल्प (Export Options)")
        export_layout = QFormLayout()
        
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["CSV", "Excel", "JSON", "Pickle"])
        export_layout.addRow("निर्यात प्रारूप (Export Format):", self.export_format_combo)
        
        self.export_path = QLineEdit()
        browse_export_btn = QPushButton("ब्राउज़ करें (Browse)")
        browse_export_btn.clicked.connect(self.browse_export_location)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.export_path)
        path_layout.addWidget(browse_export_btn)
        
        export_layout.addRow("निर्यात पथ (Export Path):", path_layout)
        
        export_options.setLayout(export_layout)
        
        # Export button
        export_btn = QPushButton("डेटा निर्यात करें (Export Data)")
        export_btn.clicked.connect(self.export_data)
        
        layout.addWidget(export_options)
        layout.addWidget(export_btn)
        
        self.tab_export.setLayout(layout)
    
    def download_kaggle_dataset(self):
        if not KAGGLE_AVAILABLE:
            QMessageBox.warning(self, "चेतावनी (Warning)", "कागलेहब मॉड्यूल इंस्टॉल नहीं है (kagglehub module not installed)")
            return
            
        self.status_bar.showMessage("कागले से डेटासेट डाउनलोड हो रहा है... (Downloading dataset from Kaggle...)")
        
        try:
            # Download latest version
            path = kagglehub.dataset_download("imtkaggleteam/agriculture-dataset-karnataka")
            self.dataset_path = path
            self.status_bar.showMessage(f"डेटासेट डाउनलोड हुआ: {path} (Dataset downloaded to: {path})")
            
            # List files in the downloaded dataset directory
            files = [f for f in os.listdir(path) if f.endswith(('.csv', '.xlsx', '.xls'))]
            if files:
                self.local_file_label.setText(os.path.join(path, files[0]))
                QMessageBox.information(self, "सफलता (Success)", 
                                        f"डेटासेट सफलतापूर्वक डाउनलोड हुआ: {path} (Dataset downloaded successfully to {path})")
            else:
                QMessageBox.warning(self, "चेतावनी (Warning)", 
                                    "डाउनलोड किए गए डेटासेट में कोई CSV या Excel फाइल नहीं मिली (No CSV or Excel files found in the downloaded dataset)")
        except Exception as e:
            self.status_bar.showMessage(f"डेटासेट डाउनलोड करने में त्रुटि: {str(e)} (Error downloading dataset: {str(e)})")
            QMessageBox.critical(self, "त्रुटि (Error)", f"डेटासेट डाउनलोड करने में विफल: {str(e)} (Failed to download dataset: {str(e)})")
    
    def browse_files(self):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(
            self, "डेटा फाइल चुनें (Select Data File)", "", "डेटा फाइल्स (*.csv *.xlsx *.xls);;सभी फाइल्स (*) (Data Files (*.csv *.xlsx *.xls);;All Files (*))", options=options)
        
        if filepath:
            self.local_file_label.setText(filepath)
    
    def load_selected_file(self):
        file_path = self.local_file_label.text()
        
        if file_path == "कोई फाइल नहीं चुनी गई (No file selected)" or file_path == "No file selected":
            QMessageBox.warning(self, "चेतावनी (Warning)", "कृपया पहले फाइल चुनें (Please select a file first)")
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
            self.column_combo.addItems(self.df.columns)
            
            self.status_bar.showMessage(
                f"{file_path} लोड हुआ, {len(self.df)} पंक्तियां और {len(self.df.columns)} कॉलम के साथ (Loaded {file_path} with {len(self.df)} rows and {len(self.df.columns)} columns)")
            
        except Exception as e:
            self.status_bar.showMessage(f"फाइल लोड करने में त्रुटि: {str(e)} (Error loading file: {str(e)})")
            QMessageBox.critical(self, "त्रुटि (Error)", f"फाइल लोड करने में विफल: {str(e)} (Failed to load the file: {str(e)})")
    
    def apply_cleaning(self):
        if self.df is None:
            QMessageBox.warning(self, "चेतावनी (Warning)", "कृपया पहले डेटा लोड करें (Please load data first)")
            return
            
        column = self.column_combo.currentText()
        
        try:
            # Missing values handling
            missing_option = self.missing_combo.currentText()
            
            if "Remove rows" in missing_option:
                self.df = self.df.dropna(subset=[column])
            elif "Fill with mean" in missing_option:
                if pd.api.types.is_numeric_dtype(self.df[column]):
                    self.df[column] = self.df[column].fillna(self.df[column].mean())
                else:
                    QMessageBox.warning(self, "चेतावनी (Warning)", 
                                        f"कॉलम {column} संख्यात्मक नहीं है। औसत नहीं निकाला जा सकता। (Column {column} is not numeric. Cannot compute mean.)")
            elif "Fill with median" in missing_option:
                if pd.api.types.is_numeric_dtype(self.df[column]):
                    self.df[column] = self.df[column].fillna(self.df[column].median())
                else:
                    QMessageBox.warning(self, "चेतावनी (Warning)", 
                                        f"कॉलम {column} संख्यात्मक नहीं है। मध्यिका नहीं निकाली जा सकती। (Column {column} is not numeric. Cannot compute median.)")
            elif "Fill with mode" in missing_option:
                if not self.df[column].mode().empty:
                    self.df[column] = self.df[column].fillna(self.df[column].mode()[0])
                else:
                    QMessageBox.warning(self, "चेतावनी (Warning)", 
                                        f"कॉलम {column} के लिए मोड नहीं मिला। (No mode found for column {column}.)")
            elif "Fill with zero" in missing_option:
                self.df[column] = self.df[column].fillna(0)
            elif "Custom value" in missing_option:
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
            
            if "Z-Score" in outlier_option and pd.api.types.is_numeric_dtype(self.df[column]):
                # Remove values that are more than 3 standard deviations from the mean
                z_scores = np.abs((self.df[column] - self.df[column].mean()) / self.df[column].std())
                self.df = self.df[z_scores < 3]
                
            elif "IQR Method" in outlier_option and pd.api.types.is_numeric_dtype(self.df[column]):
                # Remove values that are outside 1.5 * IQR
                Q1 = self.df[column].quantile(0.25)
                Q3 = self.df[column].quantile(0.75)
                IQR = Q3 - Q1
                self.df = self.df[~((self.df[column] < (Q1 - 1.5 * IQR)) | (self.df[column] > (Q3 + 1.5 * IQR)))]
                
            # Data normalization
            norm_option = self.norm_combo.currentText()
            
            if "Min-Max Scaling" in norm_option and pd.api.types.is_numeric_dtype(self.df[column]):
                self.df[column] = (self.df[column] - self.df[column].min()) / (self.df[column].max() - self.df[column].min())
                
            elif "Z-Score Normalization" in norm_option and pd.api.types.is_numeric_dtype(self.df[column]):
                self.df[column] = (self.df[column] - self.df[column].mean()) / self.df[column].std()
                
            # Update table view
            model = PandasModel(self.df)
            self.clean_table_view.setModel(model)
            self.table_view.setModel(model)
            
            self.status_bar.showMessage(
                f"क्लीनिंग लागू की गई। वर्तमान आकार: {self.df.shape} (Cleaning applied. Current shape: {self.df.shape})")
            
        except Exception as e:
            self.status_bar.showMessage(f"क्लीनिंग लागू करने में त्रुटि: {str(e)} (Error applying cleaning: {str(e)})")
            QMessageBox.critical(self, "त्रुटि (Error)", f"क्लीनिंग लागू करने में विफल: {str(e)} (Failed to apply cleaning: {str(e)})")
    
    def reset_data(self):
        if self.df_original is not None:
            self.df = self.df_original.copy()
            
            # Update table views
            model = PandasModel(self.df)
            self.clean_table_view.setModel(model)
            self.table_view.setModel(model)
            
            self.status_bar.showMessage("डेटा मूल रूप में रीसेट किया गया (Data reset to original)")
        else:
            QMessageBox.warning(self, "चेतावनी (Warning)", "कोई मूल डेटा उपलब्ध नहीं है (No original data available)")
    
    def browse_export_location(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, "निर्यात के लिए निर्देशिका चुनें (Select Export Directory)", options=options)
        
        if directory:
            self.export_path.setText(directory)
    
    def export_data(self):
        if self.df is None:
            QMessageBox.warning(self, "चेतावनी (Warning)", "निर्यात करने के लिए कोई डेटा नहीं है (No data to export)")
            return
            
        export_format = self.export_format_combo.currentText()
        export_dir = self.export_path.text()
        
        if not export_dir:
            QMessageBox.warning(self, "चेतावनी (Warning)", "कृपया निर्यात के लिए डायरेक्टरी निर्दिष्ट करें (Please specify an export directory)")
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
                
            self.status_bar.showMessage(f"डेटा निर्यात किया गया: {filepath} (Data exported to {filepath})")
            QMessageBox.information(self, "सफलता (Success)", 
                                    f"डेटा सफलतापूर्वक निर्यात किया गया: {filepath} (Data successfully exported to {filepath})")
            
        except Exception as e:
            self.status_bar.showMessage(f"डेटा निर्यात करने में त्रुटि: {str(e)} (Error exporting data: {str(e)})")
            QMessageBox.critical(self, "त्रुटि (Error)", f"डेटा निर्यात करने में विफल: {str(e)} (Failed to export data: {str(e)})")


def main():
    app = QApplication(sys.argv)
    window = DataFresheningApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 