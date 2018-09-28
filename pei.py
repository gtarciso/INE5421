#coding: utf-8
import sys
from view import *
import algorithms

class Control():
    def __init__(self):
        app = Qt.QApplication([])
        self.create_interface()
        self.view.show() 
        self.view.raise_()
        sys.exit(app.exec_())

    def create_interface(self):
        self.view = View() 
        self.bind_buttons()
        
    def bind_buttons(self):
        open_act = Qt.QAction('Abrir', self.view)
        open_act.triggered.connect(self.load_file)
        self.view.file_menu.addAction(open_act)

        save_act = Qt.QAction('Salvar', self.view)
        save_act.triggered.connect(self.save_file)
        self.view.file_menu.addAction(save_act)

        self.view.convert_button.clicked.connect(self.call_convertion)

    def call_convertion(self):
        if self.view.determinize.isChecked():
            self.determinize_automata()

    def determinize_automata(self):
        content = self.view.editor.toPlainText()
        content = content.split('\n')
        states = content[0].split()
        alphabet = content[1].split()
        initial_state = content[2]
        final_states = content[3].split()

        transitions = {}
        for transition in content[4:]:
            t = transition.split()
            source = t[0]
            destiny = t[2]
            symbol = t[3]

            if source not in transitions:
                transitions[source] = {}
            if symbol not in transitions[source]:
                transitions[source][symbol] = []
            transitions[source][symbol].append(destiny)

        automata = algorithms.Automata(states, alphabet, initial_state, final_states, transitions)
        determinized_automata = algorithms.determinize_automata(automata)
        self.view.editor.setText(str(determinized_automata))

    def load_file(self):
        file_path = Qt.QFileDialog.getOpenFileName(self.view,'','','')[0]
        file = open(file_path, 'r')
        file_content = file.read()
        file.close()
        self.view.editor.setText(file_content)

    def save_file(self):
        file_path = Qt.QFileDialog.getSaveFileName(self.view,'','','')[0]
        file = open(file_path, 'w')
        content = self.view.editor.toPlainText()
        file_content = file.write(content)
        file.close()

def main():
    c = Control()
    
if __name__ == '__main__': 
    main()