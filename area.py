from PyQt5 import QtWidgets, QtCore

import globals_
from ui import GetIcon

# Sets up the Area Options Menu
class AreaOptionsDialog(QtWidgets.QDialog):
    """
    Dialog which lets you choose among various area options from tabs
    """

    def __init__(self):
        """
        Creates and initializes the tab dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(globals_.trans.string('AreaDlg', 0))
        self.setWindowIcon(GetIcon('area'))

        self.tabWidget = QtWidgets.QTabWidget()
        self.LoadingTab = LoadingTab()
        self.TilesetsTab = TilesetsTab()
        self.tabWidget.addTab(self.TilesetsTab, globals_.trans.string('AreaDlg', 1))
        self.tabWidget.addTab(self.LoadingTab, globals_.trans.string('AreaDlg', 2))

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)


class LoadingTab(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.timer = QtWidgets.QSpinBox()
        self.timer.setRange(0, 999)
        self.timer.setToolTip(globals_.trans.string('AreaDlg', 4))
        self.timer.setValue(globals_.Area.timeLimit + 200)

        self.entrance = QtWidgets.QSpinBox()
        self.entrance.setRange(0, 255)
        self.entrance.setToolTip(globals_.trans.string('AreaDlg', 6))
        self.entrance.setValue(globals_.Area.startEntrance)

        self.toadHouseType = QtWidgets.QComboBox()
        self.toadHouseType.addItems(globals_.trans.stringList('AreaDlg', 33))
        self.toadHouseType.setCurrentIndex(globals_.Area.toadHouseType)

        self.wrap = QtWidgets.QCheckBox(globals_.trans.string('AreaDlg', 7))
        self.wrap.setToolTip(globals_.trans.string('AreaDlg', 8))
        self.wrap.setChecked(globals_.Area.wrapFlag)

        self.credits = QtWidgets.QCheckBox(globals_.trans.string('AreaDlg', 34))
        self.credits.setToolTip(globals_.trans.string('AreaDlg', 35))
        self.credits.setChecked(globals_.Area.creditsFlag)

        self.ambush = QtWidgets.QCheckBox(globals_.trans.string('AreaDlg', 36))
        self.ambush.setToolTip(globals_.trans.string('AreaDlg', 37))
        self.ambush.setChecked(globals_.Area.ambushFlag)

        self.unk1 = QtWidgets.QCheckBox(globals_.trans.string('AreaDlg', 38))
        self.unk1.setToolTip(globals_.trans.string('AreaDlg', 39))
        self.unk1.setChecked(globals_.Area.unkFlag1)

        self.unk2 = QtWidgets.QCheckBox(globals_.trans.string('AreaDlg', 40))
        self.unk2.setToolTip(globals_.trans.string('AreaDlg', 41))
        self.unk2.setChecked(globals_.Area.unkFlag2)

        self.unk3 = QtWidgets.QSpinBox()
        self.unk3.setRange(0, 999)
        self.unk3.setToolTip(globals_.trans.string('AreaDlg', 43))
        self.unk3.setValue(globals_.Area.unkVal1)

        self.unk4 = QtWidgets.QSpinBox()
        self.unk4.setRange(0, 999)
        self.unk4.setToolTip(globals_.trans.string('AreaDlg', 45))
        self.unk4.setValue(globals_.Area.unkVal2)

        settingsLayout = QtWidgets.QFormLayout()
        settingsLayout.addRow(globals_.trans.string('AreaDlg', 3), self.timer)
        settingsLayout.addRow(globals_.trans.string('AreaDlg', 5), self.entrance)
        settingsLayout.addRow(globals_.trans.string('AreaDlg', 32), self.toadHouseType)
        settingsLayout.addRow(self.wrap)
        settingsLayout.addRow(self.credits)
        settingsLayout.addRow(self.ambush)
        settingsLayout.addRow(self.unk1)
        settingsLayout.addRow(self.unk2)
        settingsLayout.addRow(globals_.trans.string('AreaDlg', 42), self.unk3)
        settingsLayout.addRow(globals_.trans.string('AreaDlg', 44), self.unk4)

        Layout = QtWidgets.QVBoxLayout()
        Layout.addLayout(settingsLayout)
        Layout.addStretch(1)
        self.setLayout(Layout)


class TilesetsTab(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setMinimumWidth(384)

        # Set up each tileset
        self.widgets = []
        self.trees = []
        self.lineEdits = []
        self.itemDict = [{}, {}, {}, {}]
        self.noneItems = []

        for slot in range(4):
            # Create the main widget
            widget = QtWidgets.QWidget()
            self.widgets.append(widget)

            # Create the tree widget
            tree = QtWidgets.QTreeWidget()
            tree.setColumnCount(2)
            # hardcoded initial width because the default width
            # is too small
            tree.setColumnWidth(0, 192)
            tree.setHeaderLabels([globals_.trans.string('AreaDlg', 28), globals_.trans.string('AreaDlg', 29)])  # ['Name', 'File']
            tree.setIndentation(16)
            if slot == 0:
                handler = self.handleTreeSel0
            elif slot == 1:
                handler = self.handleTreeSel1
            elif slot == 2:
                handler = self.handleTreeSel2
            else:
                handler = self.handleTreeSel3
            tree.itemSelectionChanged.connect(handler)
            self.trees.append(tree)

            # Add "None" entry
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, globals_.trans.string('AreaDlg', 15))  # 'None'
            tree.addTopLevelItem(item)
            self.noneItems.append(item)

            # Keep an unsorted list for the textbox autocomplete
            tilesetList = []

            # Add entries for each tileset
            def ParseCategory(items):
                """
                Parses a list of strings and returns a tuple of QTreeWidgetItem's
                """
                nodes = []
                for item in items:
                    node = QtWidgets.QTreeWidgetItem()

                    # Check if it's a tileset or a category
                    if isinstance(item[1], str):
                        # It's a tileset
                        node.setText(0, item[1])
                        node.setText(1, item[0])
                        node.setToolTip(0, item[1])
                        node.setToolTip(1, item[0])
                        self.itemDict[slot][item[0]] = node
                        tilesetList.append(item[0])
                    else:
                        # It's a category
                        node.setText(0, item[0])
                        node.setToolTip(0, item[0])
                        node.setFlags(QtCore.Qt.ItemIsEnabled)
                        children = ParseCategory(item[1])
                        for cnode in children:
                            node.addChild(cnode)
                    nodes.append(node)
                return tuple(nodes)

            categories = ParseCategory(globals_.TilesetNames[slot][0])
            tree.addTopLevelItems(categories)

            # Create the line edit
            line = QtWidgets.QLineEdit()
            line.textChanged.connect(eval('self.handleTextEdit%d' % slot))
            line.setCompleter(QtWidgets.QCompleter(tilesetList))
            line.setPlaceholderText(globals_.trans.string('AreaDlg', 30))  # '(None)'
            self.lineEdits.append(line)
            line.setText(eval('globals_.Area.tileset%d' % slot))
            self.handleTextEdit(slot)
            # Above line: For some reason, PyQt doesn't automatically call
            # the handler if (globals_.Area.tileset%d % slot) == ''

            # Create the layout and add it to the widget
            L = QtWidgets.QGridLayout()
            L.addWidget(tree, 0, 0, 1, 2)
            L.addWidget(QtWidgets.QLabel(globals_.trans.string('AreaDlg', 31, '[slot]', slot)), 1, 0)  # 'Tilesets (Pa[slot])'
            L.addWidget(line, 1, 1)
            L.setRowStretch(0, 1)
            widget.setLayout(L)

        # Set up the tab widget
        T = QtWidgets.QTabWidget()
        T.setTabPosition(T.West)
        T.setUsesScrollButtons(False)
        T.addTab(self.widgets[0], globals_.trans.string('AreaDlg', 11))  # 'Standard Suite'
        T.addTab(self.widgets[1], globals_.trans.string('AreaDlg', 12))  # 'Stage Suite'
        T.addTab(self.widgets[2], globals_.trans.string('AreaDlg', 13))  # 'Background Suite'
        T.addTab(self.widgets[3], globals_.trans.string('AreaDlg', 14))  # 'Interactive Suite'
        L = QtWidgets.QVBoxLayout()
        L.addWidget(T)
        self.setLayout(L)

    # Tree handlers
    def handleTreeSel0(self):
        self.handleTreeSel(0)

    def handleTreeSel1(self):
        self.handleTreeSel(1)

    def handleTreeSel2(self):
        self.handleTreeSel(2)

    def handleTreeSel3(self):
        self.handleTreeSel(3)

    def handleTreeSel(self, slot):
        """
        Handles changes to the selections in all tree widgets
        """
        selItems = self.trees[slot].selectedItems()
        if len(selItems) != 1: return
        item = selItems[0]

        value = str(item.text(1))
        self.lineEdits[slot].setText(value)

    # Line-edit handlers
    def handleTextEdit0(self):
        self.handleTextEdit(0)

    def handleTextEdit1(self):
        self.handleTextEdit(1)

    def handleTextEdit2(self):
        self.handleTextEdit(2)

    def handleTextEdit3(self):
        self.handleTextEdit(3)

    def handleTextEdit(self, slot):
        """
        Handles changes made to the line-edit widgets
        """
        self.trees[slot].clearSelection()
        txt = str(self.lineEdits[slot].text())

        if (txt in self.itemDict[slot]) or (txt == ''):
            # Collapse all
            for i in range(self.trees[slot].topLevelItemCount()):
                self.trees[slot].collapseItem(self.trees[slot].topLevelItem(i))

            # If there's no text, just select None
            if txt == '':
                self.noneItems[slot].setSelected(True)
                return

            # Find the item matching the description, and select it
            item = self.itemDict[slot][txt]
            item.setSelected(True)

            # Expand all of its parents
            parent = item.parent()
            while parent is not None:
                parent.setExpanded(True)
                parent = parent.parent()

    def values(self):
        """
        Returns all 4 tileset choices
        """
        result = []
        for i in range(4):
            result.append(str(self.lineEdits[i].text()))
        return tuple(result)


def SimpleTilesetNames():
    """
    simple
    """

    # Category parser
    def ParseCategory(items):
        """
        Parses a list of strings and returns a tuple of strings
        """
        result = []
        for item in items:
            if isinstance(item[1], str):
                # It's a tileset
                name = item[1]
                file = item[0]
                result.append((file, name))
            else:
                # It's a category
                childStrings = ParseCategory(item[1])
                for child in childStrings:
                    result.append(child)
        return result

    return (
        sorted(ParseCategory(globals_.TilesetNames[i][0]), key=lambda e: e[1])
        for i in range(4)
    )
