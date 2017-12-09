class Automaton:
	def __init__(self,states,start,final,trans):
		(self.states, self.start, self.final, self.trans) = (states, start, final, trans)

	def epsilon_closure(self,set_of_states):
		E = set(set_of_states) | set([new_state for (state,read,new_state) in self.trans if read == '' and state in set_of_states])
		if list(E) == list(set_of_states):	return list(E)
		return self.epsilon_closure(E)

	def __repr__(self):
		s = "States: " + str(self.states)[1:-1] + "\n"
		s += "Initial: " + str([self.start])[1:-1] + "\n"
		s += "Final: " +str(self.final)[1:-1] + "\n"
		s += "Transitions: " +str(self.trans)[1:-1]
		return s

	def run(self,w,state=None):
		if not state: 
			state = self.start

		if len(w)==0:
			return [f for f in self.final if f in self.epsilon_closure([state])] != []

		T = [(w[1:],next_state) for (current_state,read,next_state) in self.trans if read==w[0] and current_state == state]
		T_ep = [(w,next_state) for  (current_state,read,next_state) in self.trans if read=='' and current_state == state]

		for (next_w,next_state) in T+T_ep:
			if self.run(next_w,state=next_state): return True
		return False

def join_or(A,B):
	states = [(a,0) for a in A.states] + [(b,1) for b in B.states] + ['q0']
	final = [(a,0) for a in A.final] + [(b,1) for b in B.final]
	trans = [((x,0),r,(y,0)) for (x,r,y) in A.trans] + [((x,1),r,(y,1)) for (x,r,y) in B.trans]+ [('q0','',(A.start,0)),('q0','',(B.start,1))]
	return Automaton(states,'q0',final,trans)

def join_concat(A,B):
	states = [(a,0) for a in A.states] + [(b,1) for b in B.states]
	trans = [((x,0),r,(y,0)) for (x,r,y) in A.trans] + [((x,1),r,(y,1)) for (x,r,y) in B.trans] + [((a,0),'',(B.start,1)) for a in A.final]
	return Automaton(states,(A.start,0),[(b,1) for b in B.final],trans)

def join_star(A):
	trans = A.trans + [(a,'',A.start) for a in A.final]
	return Automaton(A.states,A.start,[A.start],trans)


class Parser:
	reserved = ['(',')','[',']','*','+','|']
	def __init__(self,src):
		self.src = src
		self.pos = 0

	def parse_symbol(self,symbol):
		if self.pos < len(self.src) and self.src[self.pos]==symbol:
			self.pos += 1
			return True
		else:
			raise SyntaxError("Expecting pattern {0}. Got {1} '".format(symbol, self.src[self.pos:self.pos+15]) + "' instead.")


	def parse(self):
		p = self.pos
		try:
			return self.parse_union()
		except: self.pos = p
		
		return self.parse_simple()

	def parse_union(self):
		A = self.parse_simple()
		self.parse_symbol("|")
		B = self.parse()
		return join_or(A,B)

	def parse_simple(self):
		p = self.pos
		try:
			return self.parse_concat()
		except: self.pos = p
			
		return self.parse_basic()

	def parse_concat(self):
		A = self.parse_basic()
		B = self.parse_simple()
		return join_concat(A,B)
		
	def parse_basic(self):
		p = self.pos
		try:
			return self.parse_star()
		except: self.pos = p
		
		try:
			return self.parse_plus()
		except: self.pos = p
		
		return self.parse_elementary()

	def parse_star(self):
		A = self.parse_elementary()
		self.parse_symbol("*")
		return join_star(A)

	def parse_plus(self):
		A = self.parse_elementary()
		self.parse_symbol("+")
		return join_concat(A,join_star(A))
		

	def parse_elementary(self):
		p = self.pos
		try:
			return self.parse_group()
		except: self.pos = p
		
		return self.parse_char()

	def parse_char(self):
		s = self.src[self.pos]
		if s not in self.reserved:
			self.pos += 1
			return Automaton([0,1],0,[1],[(0,str(s),1)])
		else:
			raise SyntaxError('Expecting Character. Got {0}'.format(self.src[self.pos:self.pos+15]))

	def parse_group(self):
		self.parse_symbol("(")
		A = self.parse()
		self.parse_symbol(")")
		return A



pattern = "(a|b)+c"
string = "aabababbac"

print "Checking '{0}' for pattern '{1}' : {2}".format(string, pattern, Parser(pattern).parse().run(string))

