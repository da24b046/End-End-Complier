class VMWriter:

    def __init__(self, filepath):
        self.fh = open(filepath, 'w', encoding='utf-8')


    def write_push(self, segment, index):
        self.emit(f'push {segment} {index}')

    def write_pop(self, segment, index):
        self.emit(f'pop {segment} {index}')

    def write_arithmetic(self, command):

        self.emit(command)

    def write_label(self, label):
        self.emit(f'label {label}')

    def write_goto(self, label):
        self.emit(f'goto {label}')

    def write_if(self, label):
        self.emit(f'if-goto {label}')

    def write_function(self, name, n_locals):
        self.emit(f'function {name} {n_locals}')

    def write_call(self, name, n_args):
        self.emit(f'call {name} {n_args}')

    def write_return(self):
        self.emit('return')

    def close(self):
        self.fh.close()

    def emit(self, line):
        self.fh.write(line + '\n')
