from enhanced_chat_interface import EnhancedChatInterface

class PandasModel(QAbstractTableModel):
    """Class to populate a table view with a pandas dataframe"""
    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]
