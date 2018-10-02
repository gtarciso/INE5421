class Automata():
	def __init__(self, states, alphabet, start_state, final_states, transitions):
		self.states = states
		self.alphabet = alphabet
		self.start_state = start_state
		self.final_states = final_states
		self.transitions = transitions

	def __str__(self):
		string = ' '.join(self.states) + '\n'
		string += ' '.join(self.alphabet) + '\n'
		string += self.start_state + '\n'
		string += ' '.join(self.final_states) + '\n'
		for source, symbol_dict in self.transitions.items():
			for symbol, destiny_list in symbol_dict.items():
				for destiny in destiny_list:
					string += source + ' -> ' + destiny + ' ' + symbol + '\n'

		return string

	def episulon_closure(self, state):
		state_closure = set()
		if '&' in self.transitions[state]:
			for to_state in self.transitions[state]['&']:
				if to_state != state:
					to_state_closure = self.episulon_closure(to_state)
					state_closure = state_closure.union(to_state_closure)
		state_closure.add(state)
		return state_closure

class Grammar():
	def __init__(self, non_terminal, terminal, s, p):
		self.non_terminal = non_terminal
		self.terminal = terminal
		self.s = s
		self.p = p

	def __str__(self):
		string = self.s + ' -> ' + ' | '.join(self.p[self.s]) + '\n'
		for head, production in self.p.items():
			if head == self.s:
				continue
			string += head + ' -> ' + ' | '.join(production) + '\n'
		return string

class Syntax_Tree():
	def __init__(self, expression):
		self.tree = {}
		expression = expression + '#'
		self.reserved_symbols = {'#', '(', ')', '|', '*'}
		self.create(1, expression)

#	def create(self, index, expression):
#		# stop condition
#		if len(expression) == 1:
#			self.tree[index] = symbol
#			return
#
#		symbol = expression[-1]
#		if symbol == '#' or symbol not in reserved_symbols:
#			if expression[-2] != '|':
#				self.create(2*index, expression[:-1])  # left subtree
#				self.create(2*index+1, symbol)  # right subtree
#				self.tree[index] = '.'
#			else:
#				self.tree[index] = '.'
#				self.separate_or(index*2+1, expression)
#
#		elif symbol == '*':
#			# the operation only applies to the closest symbol
#			if expression[-2] != ')':
#				# it means there's only the operator
#				if len(expression) == 2:
#					self.tree[index] = '*'
#					self.create(index*2+1, expression[-2])
#			# the operation is inside ()
#			else:
#				# find where () ends
#				parenthesis_end = self.parenthesis_end(expression[:-1])
#				self.tree[index] = '.'
#				self.create(index*2+1, expression[parenthesis_end:])
#				# not the hole expression is in (), put the remaining expression on left child
#				if parenthesis_end != 0:
#					self.create(index*2, expression[:parenthesis_end])
#
#		elif symbol == ')':
#			parenthesis_end = self.find_parenthesis_end(expression)
#			if expression[parenthesis_end-1] == '|':
#				if expression[parenthesis_end-2] == ')':
#					new_parenthesis_end = self.find_parenthesis_end(expression[:parenthesis_end-2])
#					self.tree[index] = '.'
#					self.create(index*2, expression[:new_parenthesis_end])
#					self.separate_or(index*2+1, expression[new_parenthesis_end:])
#				else:
#					self.tree[index] = '.'
#					self.create(2*index, expression[:parenthesis_end])
#					self.separate_or(index*2+1, expression[parenthesis_end:])
#			else:
#				expression = expression[:-1]
#				expression.pop(parenthesis_end)
#				self.create(index, expression)
#
#	def find_parenthesis_end(self, expression):
#		parenthesis_end = 0
#		new_parenthesis = 0
#		for i in reversed(range(0, len(expression)-1)):
#			if symbol[i] == ')':
#				new_parenthesis += 1
#			elif symbol[i] == '(':
#				if new_parenthesis == 0:
#					parenthesis_end = i
#					break
#				else:
#					new_parenthesis -= 1
#		return parenthesis_end
#
#	def separate_or(self, index, expression):
#		pass	

def determinize_automata(automata):
	episulon_closure = {}
	for state in automata.states:
		episulon_closure[state] = automata.episulon_closure(state)
	
	states = []
	transitions = {}
	start_state = ''.join(sorted(episulon_closure[automata.start_state]))
	final_states = []
	states_to_be_added = []
	states_to_be_added.append(start_state)

	while(states_to_be_added):
		new_state = states_to_be_added.pop(0)
		states.append(new_state)
		for final_state in automata.final_states:
			if final_state in new_state:
				final_states.append(new_state)

		transitions[new_state] = {}

		for symbol in automata.alphabet:
			destiny = set()
			for state in new_state:
				if symbol not in automata.transitions[state]:
					continue

				for transition in automata.transitions[state][symbol]:
					destiny.add(transition)
					for episulon_transition in automata.episulon_closure(transition):
						destiny.add(episulon_transition)

			if (destiny):
				string_destiny = ''.join(sorted(destiny))
				transitions[new_state][symbol] = [string_destiny]

				if (string_destiny not in states) and (string_destiny not in states_to_be_added):
					states_to_be_added.append(string_destiny)

	new_automata = Automata(states, automata.alphabet, start_state, final_states, transitions)
	return new_automata


def fsm_to_regular_grammar(automata):
	non_terminal = automata.states
	terminal = automata.alphabet
	s = automata.start_state
	p = {}

	for source, symbol_dict in automata.transitions.items():
		if source not in p:
			p[source] = []

		for symbol, destiny in symbol_dict.items():
			for state in destiny:
				p[source].append(symbol+state)
				if state in automata.final_states:
					p[source].append(symbol)

	if automata.start_state in automata.final_states:
		p[s+'\''] = p[s]
		p[s+'\''].append('&')

	grammar = Grammar(non_terminal, terminal, s, p)
	return grammar

def regular_grammar_to_fsm(grammar):
	states = grammar.non_terminal
	states.append('W')
	alphabet = grammar.terminal
	start_state = grammar.s
	final_states = ['W']
	if '&' in grammar.p[grammar.s]:
		final_states.append(grammar.s)

	transitions = {}
	for head, body in grammar.p.items():
		if head not in transitions:
			transitions[head] = {}

		for production in body:
			symbol = production[0]
			if symbol not in transitions[head]:
				transitions[head][symbol] = []

			if len(production) == 1:
				transitions[head][symbol].append('W')
			elif len(production) == 2:
				transitions[head][symbol].append(production[1])

	fsm = Automata(states, alphabet, start_state, final_states, transitions)
	return fsm