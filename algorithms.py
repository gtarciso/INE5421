#coding: utf-8
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
		self.roots = {}
		self.nullable = {}
		self.firstpos = {}
		self.lastpos = {}
		self.followpos = {}
		expression = expression + '#'
		self.create_tree(1, expression)
		self.calculate_nullable(1)
		self.calculate_firstpos(1)
		self.calculate_lastpos(1)
		# initialize followpos
		for x,i in self.roots.items():
			self.followpos[i] = set()
		self.calculate_followpos(1)

	def create_tree(self, index, expression):
		#stop conditions
		if len(expression) == 0:
			return
		elif len(expression) == 1:
			self.tree[index] = expression
			self.roots[index] = len(self.roots)+1
			return

		symbol = expression[len(expression)-1]
		operation = expression[len(expression)-2]

		# Treats the case were the rightmost symbol is an alphabet symbol
		if symbol != ')' and symbol != '*':
			if operation != '|':
				self.tree[index] = '.'
				self.create_tree(index*2, expression[:-1])
				self.create_tree(index*2+1, symbol)
			else:
				operand_index = self.left_operand_index(expression[:-2])

				# there are more on the left side besides this operation. put
				# a concatenation symbol here and move the or operation to the
				# left branch
				if operand_index != 0:
					self.tree[index] = '.'
					self.create_tree(index*2, expression[:operand_index])
					self.create_or_branch(index*2+1, expression[operand_index:])

				# there's only the or operation to do, so do it here
				else:
					self.create_or_branch(index, expression)

		# Treats the case where the rightmost symbol is a closure operation
		elif symbol == '*':
			operand_index = self.left_operand_index(expression[:-1])
			if operand_index != 0:
				self.tree[index] = '.'
				self.create_tree(index*2, expression[:operand_index])
				self.create_closure_branch(index*2+1, expression[operand_index:])
			else:
				self.create_closure_branch(index, expression)

		# Treats the case where 
		elif symbol == ')':
			opening_index = self.parenthesis_opening_index(expression[:-1])
			predecessor_symbol = expression[opening_index-1]

			# The parenthesis where useless. Remove them and try again
			if opening_index == 0 or predecessor_symbol != '|':
				expression = expression[:-1]
				expression = list(expression)
				expression.pop(opening_index)
				expression = ''.join(expression)
				self.create_tree(index, expression)

			# It was an or operand. get the other one and start an or branch
			else:
				operand_index = self.left_operand_index(expression[:opening_index])

				# there are more on the left side besides this operation. put
				# a concatenation symbol here and move the or operation to the
				# left branch
				if operand_index != 0:
					self.tree[index] = '.'
					self.create_tree(index*2, expression[:operand_index])
					self.create_or_branch(index*2+1, expression[operand_index:])

				# there's only the or operation to do, so do it here
				else:
					self.create_or_branch(index, expression)

	# get the index where the left side of a operations stars
	def left_operand_index(self, expression):
		symbol = expression[len(expression)-1]

		if symbol == '*':
			return self.left_operand_index(expression[:-1])
		elif symbol != ')':
			return len(expression) - 1
		else:
			opens = self.parenthesis_opening_index(expression[:-1])
			return opens

	# returns where, from right to left, the most recente closed parenthesis
	# was open
	def parenthesis_opening_index(self, expression):
		new_closed_parenthesis = 0

		for i in reversed(range(len(expression)-1)):
			if expression[i] == ')':
				new_closed_parenthesis += 1

			elif expression[i] == '(':
				if new_closed_parenthesis == 0:
					return i
				else:
					new_closed_parenthesis -= 1

	def create_or_branch(self, index, expression):
		if expression[len(expression)-1] != ')':
			operator_index = len(expression)-2
		else:
			start_index = self.parenthesis_opening_index(expression[:-1])
			operator_index = start_index - 1	

		self.tree[index] = '|'
		self.create_tree(2*index, expression[:operator_index])
		self.create_tree(2*index+1, expression[operator_index+1:])

	def create_closure_branch(self, index, expression):
		self.tree[index] = '*'
		self.create_tree(2*index+1, expression[:-1])

	def calculate_nullable(self, index):
		if index*2 in self.tree:
			self.calculate_nullable(index*2)
		if index*2+1 in self.tree:
			self.calculate_nullable(index*2+1)

		if self.tree[index] == '|':
			self.nullable[index] = self.nullable[index*2] or self.nullable[index*2+1]
		elif self.tree[index] == '.':
			self.nullable[index] = self.nullable[index*2] and self.nullable[index*2+1]
		elif self.tree[index] == '*':
			self.nullable[index] = True
		else:
			self.nullable[index] = False

	def calculate_firstpos(self, index):
		if index*2 in self.tree:
			self.calculate_firstpos(index*2)
		if index*2+1 in self.tree:
			self.calculate_firstpos(index*2+1)

		if self.tree[index] == '|':
			self.firstpos[index] = self.firstpos[index*2] | self.firstpos[index*2+1]
		elif self.tree[index] == '.':
			if self.nullable[index*2]:
				self.firstpos[index] = self.firstpos[index*2] | self.firstpos[index*2+1]
			else:
				self.firstpos[index] = self.firstpos[index*2]
		elif self.tree[index] == '*':
			self.firstpos[index] = self.firstpos[index*2+1]
		else:
			self.firstpos[index] = {self.roots[index]}

	def calculate_lastpos(self, index):
		if index*2 in self.tree:
			self.calculate_lastpos(index*2)
		if index*2+1 in self.tree:
			self.calculate_lastpos(index*2+1)

		if self.tree[index] == '|':
			self.lastpos[index] = self.lastpos[index*2] | self.lastpos[index*2+1]
		elif self.tree[index] == '.':
			if self.nullable[index*2+1]:
				self.lastpos[index] = self.lastpos[index*2] | self.lastpos[index*2+1]
			else:
				self.lastpos[index] = self.lastpos[index*2+1]
		elif self.tree[index] == '*':
			self.lastpos[index] = self.lastpos[index*2+1]
		else:
			self.lastpos[index] = {self.roots[index]}

	def calculate_followpos(self, index):
		if index*2 in self.tree:
			self.calculate_followpos(index*2)
		if index*2+1 in self.tree:
			self.calculate_followpos(index*2+1)

		if self.tree[index] == '.':
			for i in self.lastpos[index*2]:
				self.followpos[i] = self.followpos[i] | self.firstpos[index*2+1]
		elif self.tree[index] == '*':
			for i in self.lastpos[index]:
				self.followpos[i] = self.followpos[i] | self.firstpos[index]

def regular_expression_to_fsm(expression):
	tree = Syntax_Tree(expression)
	start_state = ''.join(map(str, sorted(list(tree.firstpos[1])))) 
	alphabet = []
	for i in tree.roots:
		if tree.tree[i] != '#' and tree.tree[i] not in alphabet:
			alphabet.append(tree.tree[i])

	transitions = {}
	states = []
	unmarked_states = [tree.firstpos[1]]
	while(unmarked_states):
		state = unmarked_states.pop()
		state_name = ''.join(map(str, sorted(list(state))))
		transitions[state_name] = {}
		states.append(state_name)
		for symbol in alphabet:
			b = set()
			for i in state:
				for index, value in tree.roots.items():
					if i == value and tree.tree[index] == symbol:
						b = b | tree.followpos[i]
			b_name = ''.join(map(str, sorted(list(b))))
			if b and b not in unmarked_states and b_name not in states:
				unmarked_states.append(b)
			transitions[state_name][symbol] = [b_name]

	final_states = []
	final_state_name = str(len(tree.roots))
	for state in states:
		if final_state_name in state:
			final_states.append(state)

	fsm = Automata(states, alphabet, start_state, final_states, transitions)
	return fsm		


def determinize_automata(automata):
	episulon_closure = {}
	for state in automata.states:
		episulon_closure[state] = automata.episulon_closure(state)
	
	states = []
	transitions = {}
	start_state = ''.join(sorted(episulon_closure[automata.start_state]))
	final_states = []
	states_to_be_added = []
	states_to_be_added.append(episulon_closure[automata.start_state])

	while(states_to_be_added):
		new_state = states_to_be_added.pop(0)
		new_state_name = ''.join(sorted(list(new_state)))
		states.append(new_state_name)
		for final_state in automata.final_states:
			for state in new_state:
				if final_state == state:
					final_states.append(new_state_name)

		transitions[new_state_name] = {}

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
				transitions[new_state_name][symbol] = [string_destiny]

				if (string_destiny not in states) and (string_destiny not in states_to_be_added):
					states_to_be_added.append(destiny)

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

def remove_dead_states(automata):
	states = []
	to_check = [x for x in automata.final_states]

	for state in to_check:
		states.append(state)
		for symbol in automata.transitions[state]:
			for destiny in automata.transitions[state][symbol]:
				if destiny not in states and destiny not in to_check:
					to_check.append(destiny)

	alphabet = automata.alphabet
	start_state = automata.start_state
	final_states = automata.final_states

	for origin, transition in automata.transitions.items():
		if origin not in states:
			del automata.transitions[origin]
		else:
			for symbol, destiny in transition.items():
				for destiny_state in destiny:
					if destiny_state not in states:
						automata.transitions[origin][symbol].pop(destiny_state)
						if not automata.transitions[origin][symbol]:
							del automata.transitions[origin][symbol]

	transitions = automata.transitions

	resulting_automata = Automata(states, alphabet, start_state, final_states, transitions)
	return resulting_automata

def minimize_automata(automata):
	automata = determinize_automata(automata)
	automata = remove_dead_states(automata)
	automata = remove_equivalent_states(automata)


def remove_equivalent_states(automata):
	p = [automata.final_states, [state for state in automata.states if state not in automata.final_states]]
	consistent = False
	while not consistent:
		consistent = True
		for sets in p:
			for symbol in automata.alphabet:
				for sett in p:
					temp = []
					for q in sett:
						if symbol in automata.transitions[q]:
							for destiny in automata.transitions[q][symbol]:
								if destiny in sets:
									if q not in temp:
										temp.append(q)
					if temp and temp != sett:
						consistent = False
						p.remove(sett)
						p.append(temp)
						temp_t = list(sett)
						for state in temp:
							temp_t.remove(state)

						p.append(temp_t)
