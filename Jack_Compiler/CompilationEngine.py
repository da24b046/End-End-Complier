import os
from SymbolTable import SymbolTable
from VMWriter    import VMWriter

ESCAPE = {'<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;'}

def xe(s):
    for ch, esc in ESCAPE.items():
        s = s.replace(ch, esc)
    return s

OP_MAP = { '+': 'add', '-': 'sub','*': None,  '/': None,'&': 'and', '|': 'or','<': 'lt',  '>': 'gt', '=': 'eq'}
UNARY_MAP = {'-': 'neg', '~': 'not'}

class CompilationEngine:

    def __init__(self, tokens, out_dir, class_name):
        self.tokens   = tokens
        self.pos      = 0
        self.classname    = class_name
        self.label_counter = 0

        xml_path = os.path.join(out_dir, class_name + '.xml')
        self.xml = open(xml_path, 'w', encoding='utf-8')
        self.indent = 0

        vm_path = os.path.join(out_dir, class_name + '.vm')
        self.vm = VMWriter(vm_path)
        self.st = SymbolTable()

    def compileclassname(self):

        self.open_tag('class')
        self.eat('keyword', 'class')
        self.classname = self.eat_type('identifier') 
        self.eat('symbol', '{')
        while self.peek_val() in ('static', 'field'):
            self.compileclassname_var_dec()
        while self.peek_val() in ('constructor', 'function', 'method'):
            self.compile_subroutine_dec()
        self.eat('symbol', '}')
        self.close_tag('class')
        self.xml.close()
        self.vm.close()

    def compileclassname_var_dec(self):

        self.open_tag('classVarDec')
        kind_word = self.eat_type('keyword')   
        kind = SymbolTable.KIND_STATIC if kind_word == 'static' else SymbolTable.KIND_FIELD
        typ  = self.compile_type()
        name = self.eat_type('identifier')
        self.st.define(name, typ, kind)
        while self.peek_val() == ',':
            self.eat('symbol', ',')
            name = self.eat_type('identifier')
            self.st.define(name, typ, kind)
        self.eat('symbol', ';')
        self.close_tag('classVarDec')

    def compile_subroutine_dec(self):
        self.open_tag('subroutineDec')
        self.st.start_subroutine()
        sub_kind = self.eat_type('keyword')     
        self.compile_type(allow_void=True)      
        sub_name = self.eat_type('identifier')  
       
        if sub_kind == 'method':
            self.st.define('this', self.classname, SymbolTable.KIND_ARG)   # For methods, 'this' is argument 0

        self.eat('symbol', '(')
        self.compile_parameter_list()
        self.eat('symbol', ')')
        self.compile_subroutine_body(sub_kind, sub_name)
        self.close_tag('subroutineDec')

    def compile_parameter_list(self):
        self.open_tag('parameterList')
        if self.peek_val() != ')':
            typ  = self.compile_type()
            name = self.eat_type('identifier')
            self.st.define(name, typ, SymbolTable.KIND_ARG)
            while self.peek_val() == ',':
                self.eat('symbol', ',')
                typ  = self.compile_type()
                name = self.eat_type('identifier')
                self.st.define(name, typ, SymbolTable.KIND_ARG)
        self.close_tag('parameterList')

    def compile_subroutine_body(self, sub_kind, sub_name):

        self.open_tag('subroutineBody')
        self.eat('symbol', '{')

        while self.peek_val() == 'var':
            self.compile_var_dec()

        n_locals = self.st.var_count(SymbolTable.KIND_VAR)
        self.vm.write_function(f'{self.classname}.{sub_name}', n_locals)

        if sub_kind == 'constructor':
            n_fields = self.st.var_count(SymbolTable.KIND_FIELD)
            self.vm.write_push('constant', n_fields)
            self.vm.write_call('Memory.alloc', 1)
            self.vm.write_pop('pointer', 0)
        elif sub_kind == 'method':
            self.vm.write_push('argument', 0)
            self.vm.write_pop('pointer', 0)

        self.compile_statements()
        self.eat('symbol', '}')
        self.close_tag('subroutineBody')

    def compile_var_dec(self):

        self.open_tag('varDec')
        self.eat('keyword', 'var')
        typ  = self.compile_type()
        name = self.eat_type('identifier')
        self.st.define(name, typ, SymbolTable.KIND_VAR)
        while self.peek_val() == ',':
            self.eat('symbol', ',')
            name = self.eat_type('identifier')
            self.st.define(name, typ, SymbolTable.KIND_VAR)
        self.eat('symbol', ';')
        self.close_tag('varDec')

    def compile_statements(self):
        self.open_tag('statements')
        while self.peek_val() in ('let', 'if', 'while', 'do', 'return'):
            v = self.peek_val()

            if   v == 'let':
                self.compile_let()
            elif v == 'if':   
                self.compile_if()
            elif v == 'while': 
                self.compile_while()
            elif v == 'do':   
                self.compile_do()
            elif v == 'return': 
                self.compile_return()

        self.close_tag('statements')

    def compile_let(self):
        self.open_tag('letStatement')
        self.eat('keyword', 'let')
        name = self.eat_type('identifier')
        is_array = self.peek_val() == '['

        if is_array:
            self.push_var(name)
            self.eat('symbol', '[')
            self.compile_expression()    
            self.eat('symbol', ']')
            self.vm.write_arithmetic('add')   

        self.eat('symbol', '=')
        self.compile_expression()        
        self.eat('symbol', ';')

        if is_array:
            self.vm.write_pop('temp', 0)      
            self.vm.write_pop('pointer', 1) 
            self.vm.write_push('temp', 0)
            self.vm.write_pop('that', 0)
        else:
            self.pop_var(name)

        self.close_tag('letStatement')

    def compile_if(self):

        self.open_tag('ifStatement')
        label_false = self.new_label('IF_FALSE')
        label_end   = self.new_label('IF_END')

        self.eat('keyword', 'if')
        self.eat('symbol', '(')
        self.compile_expression()
        self.eat('symbol', ')')
        self.vm.write_arithmetic('not')
        self.vm.write_if(label_false)

        self.eat('symbol', '{')
        self.compile_statements()
        self.eat('symbol', '}')
        self.vm.write_goto(label_end)
        self.vm.write_label(label_false)

        if self.peek_val() == 'else':
            self.eat('keyword', 'else')
            self.eat('symbol', '{')
            self.compile_statements()
            self.eat('symbol', '}')

        self.vm.write_label(label_end)
        self.close_tag('ifStatement')

    def compile_while(self):

        self.open_tag('whileStatement')
        label_top  = self.new_label('WHILE_EXP')
        label_end  = self.new_label('WHILE_END')

        self.eat('keyword', 'while')
        self.vm.write_label(label_top)
        self.eat('symbol', '(')
        self.compile_expression()
        self.eat('symbol', ')')
        self.vm.write_arithmetic('not')
        self.vm.write_if(label_end)

        self.eat('symbol', '{')
        self.compile_statements()
        self.eat('symbol', '}')
        self.vm.write_goto(label_top)
        self.vm.write_label(label_end)
        self.close_tag('whileStatement')

    def compile_do(self):

        self.open_tag('doStatement')
        self.eat('keyword', 'do')
        self.compile_subroutine_call()
        self.eat('symbol', ';')
        self.vm.write_pop('temp', 0) 
        self.close_tag('doStatement')

    def compile_return(self):

        self.open_tag('returnStatement')
        self.eat('keyword', 'return')
        if self.peek_val() != ';':
            self.compile_expression()
        else:
            self.vm.write_push('constant', 0) 

        self.eat('symbol', ';')
        self.vm.write_return()
        self.close_tag('returnStatement')

    def compile_expression(self):

        self.open_tag('expression')
        self.compile_term()
        while self.peek_val() in OP_MAP:
            op = self.eat_type('symbol')
            self.compile_term()

            if op == '*':
                self.vm.write_call('Math.multiply', 2)
            elif op == '/':
                self.vm.write_call('Math.divide', 2)
            else:
                self.vm.write_arithmetic(OP_MAP[op])
        self.close_tag('expression')

    def compile_term(self):

        self.open_tag('term')
        tok_type, val = self.peek()

        if tok_type == 'integerConstant':

            self.advance()
            self.vm.write_push('constant', int(val))

        elif tok_type == 'stringConstant':

            self.advance()
            self.vm.write_push('constant', len(val))
            self.vm.write_call('String.new', 1)
            for ch in val:
                self.vm.write_push('constant', ord(ch))
                self.vm.write_call('String.appendChar', 2)

        elif tok_type == 'keyword' and val in ('true', 'false', 'null', 'this'):
            self.advance()
            if val == 'true':
                self.vm.write_push('constant', 0)
                self.vm.write_arithmetic('not')
            elif val in ('false', 'null'):
                self.vm.write_push('constant', 0)
            else: 
                self.vm.write_push('pointer', 0)

        elif tok_type == 'symbol' and val == '(':
            self.eat('symbol', '(')
            self.compile_expression()
            self.eat('symbol', ')')

        elif tok_type == 'symbol' and val in ('-', '~'):
            op = self.eat_type('symbol')
            self.compile_term()
            self.vm.write_arithmetic(UNARY_MAP[op])

        elif tok_type == 'identifier':
            next_tok_type, next_val = self.peek_ahead(1)

            if next_val == '[':
                name = self.eat_type('identifier')
                self.push_var(name)
                self.eat('symbol', '[')
                self.compile_expression()
                self.eat('symbol', ']')
                self.vm.write_arithmetic('add')
                self.vm.write_pop('pointer', 1)
                self.vm.write_push('that', 0)
            elif next_val in ('(', '.'):
                self.compile_subroutine_call()
            else:
                name = self.eat_type('identifier')
                self.push_var(name)
        self.close_tag('term')

    def compile_subroutine_call(self):

        name = self.eat_type('identifier')
        n_args = 0

        if self.peek_val() == '.':
            self.eat('symbol', '.')
            method_name = self.eat_type('identifier')

            if self.st.contains(name):
     
                self.push_var(name)     
                callee = f'{self.st.type_of(name)}.{method_name}'
                n_args = 1
            else:
         
                callee = f'{name}.{method_name}'
        else:
          
            self.vm.write_push('pointer', 0)
            callee = f'{self.classname}.{name}'
            n_args = 1

        self.eat('symbol', '(')
        n_args += self.compile_expression_list()
        self.eat('symbol', ')')
        self.vm.write_call(callee, n_args)

    def compile_expression_list(self):

        self.open_tag('expressionList')
        n = 0
        if self.peek_val() != ')':
            self.compile_expression()
            n += 1
            while self.peek_val() == ',':
                self.eat('symbol', ',')
                self.compile_expression()
                n += 1
        self.close_tag('expressionList')
        return n


    def compile_type(self, allow_void = False):
    
        tok_type, val = self.peek()

        allowed = ['int', 'char', 'boolean']

        if allow_void:
            allowed.append('void')

        if tok_type == 'keyword' and val in allowed:
            return self.eat_type('keyword')
        else:
            return self.eat_type('identifier')

 
    def push_var(self, name):

        seg = self.st.kind_of(name)
        idx = self.st.index_of(name)
        if seg is None:
            raise RuntimeError(f'Undefined variable: {name}')
        self.vm.write_push(seg, idx)

    def pop_var(self, name):

        seg = self.st.kind_of(name)
        idx = self.st.index_of(name)
        if seg is None:
            raise RuntimeError(f'Undefined variable: {name}')
        self.vm.write_pop(seg, idx)


    def peek(self, offset = 0):

        idx = self.pos + offset
        if idx >= len(self.tokens):
            return ('', '')
        return self.tokens[idx]

    def peek_ahead(self, offset):
        return self.peek(offset)

    def peek_val(self, offset = 0):
        return self.peek(offset)[1]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        tok_type, val = tok
        self.write_terminal(tok_type, val)
        return tok

    def eat(self, expected_type, expected_val):

        tok_type, val = self.peek()
        if tok_type != expected_type or val != expected_val:
            raise SyntaxError(
                f'Expected ({expected_type}, {expected_val!r}) '
                f'but got ({tok_type}, {val!r}) at token {self.pos}'
            )
        self.advance()
        return val

    def eat_type(self, expected_type):

        tok_type, val = self.peek()
        if tok_type != expected_type:
            raise SyntaxError(
                f'Expected token type {expected_type!r} '
                f'but got ({tok_type}, {val!r}) at token {self.pos}'
            )
        self.advance()
        return val

    def new_label(self, prefix):

        lbl = f'{prefix}_{self.label_counter}'
        self.label_counter += 1
        return lbl

    def open_tag(self, tag):
        self.xml.write('  ' * self.indent + f'<{tag}>\n')
        self.indent += 1

    def close_tag(self, tag):
        self.indent -= 1
        self.xml.write('  ' * self.indent + f'</{tag}>\n')

    def write_terminal(self, tok_type, val):
        safe = xe(val)
        self.xml.write('  ' * self.indent + f'<{tok_type}> {safe} </{tok_type}>\n')
