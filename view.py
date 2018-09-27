from PyQt5 import Qt

class View(Qt.QMainWindow):
    def __init__(self):
        super(View, self).__init__()
        self.widget = Qt.QWidget(self)
        self.editor = Qt.QTextEdit()
        self.layout = Qt.QGridLayout();
        self.layout.addWidget(self.editor, 0, 0, 1, -1)
        self.widget.setLayout(self.layout)

        self.create_buttons()
        self.create_menus()

        self.setCentralWidget(self.widget)

    def create_buttons(self):
        action_box = Qt.QGroupBox('Ação:')
        self.convert = Qt.QRadioButton('Converter')
        self.minimize = Qt.QRadioButton('Minimizar')
        self.union = Qt.QRadioButton('União')
        self.intersec = Qt.QRadioButton('Intersecção')
        self.determinize = Qt.QRadioButton('Determinizar')
        action_layout = Qt.QVBoxLayout()
        action_layout.addWidget(self.convert)
        action_layout.addWidget(self.minimize)
        action_layout.addWidget(self.union)
        action_layout.addWidget(self.intersec)
        action_layout.addWidget(self.determinize)
        action_box.setLayout(action_layout)
        self.layout.addWidget(action_box, 2, 0)

        from_box = Qt.QGroupBox('De:')
        self.from_regular_expression = Qt.QRadioButton('Expressão regular')
        self.from_regular_grammar = Qt.QRadioButton('Gramática regular')
        self.from_finite_automata = Qt.QRadioButton('Automato Finito')
        from_layout = Qt.QVBoxLayout()
        from_layout.addWidget(self.from_regular_expression)
        from_layout.addWidget(self.from_regular_grammar)
        from_layout.addWidget(self.from_finite_automata)
        from_box.setLayout(from_layout)
        self.layout.addWidget(from_box, 2, 1)

        to_box = Qt.QGroupBox('Para:')
        self.to_regular_expression = Qt.QRadioButton('Expressão regular')
        self.to_regular_grammar = Qt.QRadioButton('Gramática regular')
        self.to_finite_automata = Qt.QRadioButton('Automato Finito')
        to_layout = Qt.QVBoxLayout()
        to_layout.addWidget(self.to_regular_expression)
        to_layout.addWidget(self.to_regular_grammar)
        to_layout.addWidget(self.to_finite_automata)
        to_box.setLayout(to_layout)
        self.layout.addWidget(to_box, 2, 2)

        self.convert_button = Qt.QPushButton('Converter')
        self.layout.addWidget(self.convert_button, 2, 3)

    def create_menus(self):
        self.file_menu = self.menuBar().addMenu('Arquivo')

