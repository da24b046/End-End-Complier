class SymbolTable:
    
    KIND_STATIC   = 'static'
    KIND_FIELD    = 'this'      
    KIND_ARG      = 'argument'
    KIND_VAR      = 'local'

    def __init__(self):

        self.class_table = {}
        self.sub_table = {}
        self.counters = { self.KIND_STATIC:0, self.KIND_FIELD:0, self.KIND_ARG:0,self.KIND_VAR:0 }

    def start_subroutine(self):
    
        self.sub_table = {}
        self.counters[self.KIND_ARG] = 0
        self.counters[self.KIND_VAR] = 0

    def define(self, name, typ, kind) :

        idx = self.counters[kind]
        self.counters[kind] += 1

        if kind in (self.KIND_STATIC, self.KIND_FIELD):
            self.class_table[name] = (typ, kind, idx)
        else:
            self.sub_table[name] = (typ, kind, idx)


    def lookup(self, name):

        if name in self.sub_table:
            return self.sub_table[name]
        if name in self.class_table:
            return self.class_table[name]
        return None

    def type_of(self, name):

        entry = self.lookup(name)
        if entry :
            return entry[0] 
        

    def kind_of(self, name):
        entry = self.lookup(name)
        if entry:
            return entry[1] 

    def index_of(self, name):
        entry = self.lookup(name)
        if entry:
            return entry[2]

    def contains(self, name):
        return self.lookup(name) is not None

    def var_count(self, kind) :
        return self.counters.get(kind, 0)

    def dump(self):
        lines = ['--- class scope ---']
        for name, (typ, kind, idx) in sorted(self.class_table.items()):
            lines.append(f'  {name}: type={typ}, kind={kind}, index={idx}')
        lines.append('--- subroutine scope ---')
        for name, (typ, kind, idx) in sorted(self.sub_table.items()):
            lines.append(f'  {name}: type={typ}, kind={kind}, index={idx}')
        return '\n'.join(lines)
