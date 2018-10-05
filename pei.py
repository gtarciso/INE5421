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

        elif self.view.convert.isChecked():
            if(self.view.from_finite_automata.isChecked() and self.view.to_regular_grammar.isChecked()):
                self.fsm_to_regular_grammar()
            elif (self.view.from_regular_grammar.isChecked()) and (self.view.to_finite_automata.isChecked()):
                self.regular_grammar_to_fsm()
            elif (self.view.from_regular_expression.isChecked()) and (self.view.to_finite_automata.isChecked()):
                self.regular_expression_to_fsm()

        elif self.view.minimize.isChecked():
            self.minimize_automata()

    def minimize_automata(self):
        automata = self.read_automata()
        algorithms.minimize_automata(automata)

    def regular_expression_to_fsm(self):
        expression = self.view.editor.toPlainText()
        fsm = algorithms.regular_expression_to_fsm(expression)
        self.view.editor.setText(str(fsm)[:-1])

    def read_automata(self):
        content = self.view.editor.toPlainText()
        content = content.split('\n')
        states = content[0].split()
        alphabet = content[1].split()
        initial_state = content[2]
        final_states = content[3].split()

        transitions = {}
        for state in states:
            transitions[state] = {}
            for symbol in alphabet:
                transitions[state][symbol] = []
        for transition in content[4:]:
            t = transition.split()
            source = t[0]
            destiny = t[2]
            symbol = t[3]
            transitions[source][symbol].append(destiny)

        automata = algorithms.Automata(states, alphabet, initial_state, final_states, transitions)
        return automata
        
    def regular_grammar_to_fsm(self):
        content = self.view.editor.toPlainText()
        content = content.split('\n')
        s = content[0][0]
        productions = {}

        # create productions
        for production in content:
            head = production[0]
            productions[head] = []
            p = production.split()
            for body in p[2:]:
                if body == '|':
                    continue
                else:
                    productions[head].append(body)

        non_terminal = list(productions.keys())
        terminal = []
        # analise  productions to find terminals
        for head, body in productions.items():
            for production in body:
                for symbol in production:
                    if symbol not in non_terminal and symbol not in terminal:
                        terminal.append(symbol)

        grammar = algorithms.Grammar(non_terminal, terminal, s, productions)
        fsm = algorithms.regular_grammar_to_fsm(grammar)
        self.view.editor.setText(str(fsm)[:-1])

    def fsm_to_regular_grammar(self):
        automata = self.read_automata()
        regular_grammar = algorithms.fsm_to_regular_grammar(automata)
        self.view.editor.setText(str(regular_grammar)[:-1])

    def determinize_automata(self):
        automata = self.read_automata()
        determinized_automata = algorithms.determinize_automata(automata)
        self.view.editor.setText(str(determinized_automata)[:-1])

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