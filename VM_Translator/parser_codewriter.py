C_ARITHMETIC = "C_ARITHMETIC"
C_PUSH       = "C_PUSH"
C_POP        = "C_POP"
C_LABEL      = "C_LABEL"
C_GOTO       = "C_GOTO"
C_IF         = "C_IF"
C_FUNCTION   = "C_FUNCTION"
C_CALL       = "C_CALL"
C_RETURN     = "C_RETURN"

ARITHMETIC_CMDS = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}

class Parser:

    def __init__(self, filepath):

        with open(filepath, "r") as f:
            raw = f.readlines()
        self.commands = []
        for line in raw:
            line = line.split("//")[0].strip()
            if line:
                self.commands.append(line)
        self.current_index = -1
        self.current_command = None

    def has_more_commands(self):

        return self.current_index + 1  < len(self.commands) 

    def advance(self):

        self.current_index += 1
        self.current_command = self.commands[self.current_index]

    def command_type(self):

        first = self.current_command.split()[0]
        if first in ARITHMETIC_CMDS:
            return C_ARITHMETIC
        mapping = {"push": C_PUSH, "pop": C_POP,"label": C_LABEL, "goto": C_GOTO, "if-goto": C_IF,"function": C_FUNCTION, 
                   "call": C_CALL, "return": C_RETURN,}
        
        return mapping[first]

    def arg1(self):

        parts = self.current_command.split()
        if self.command_type() == C_ARITHMETIC:
            return parts[0]
        elif self.command_type() == C_RETURN:
            return None
        return parts[1]

    def arg2(self):

        if self.command_type() in {C_PUSH, C_POP, C_FUNCTION, C_CALL}:
            return int(self.current_command.split()[2])
        else:
            raise ValueError('given command type has no 2nd argument')
        

class CodeWriter:

    def __init__(self, output_path):

        self.output = open(output_path, "w")
        self.label_counter = 0   
        self.call_counter  = 0   
        self.current_file  = ""  
        self.write_bootstrap()

    def write_bootstrap(self):

        asm = ["// Bootstrap","@256", "D=A", "@SP", "M=D" ]
        self.output.write("\n".join(asm) + "\n")
        self.write_call("Sys.init", 0)

    def set_file_name(self, filename):

        self.current_file = filename

    def write_arithmetic(self, command):
 
        asm = [f"// {command}"]
        if command == "add":
            asm += self.binary_operation("D+M")
        elif command == "sub":
            asm += self.binary_operation("M-D")
        elif command == "and":
            asm += self.binary_operation("D&M")
        elif command == "or":
            asm += self.binary_operation("D|M")
        elif command == "neg":
            asm += self.unary_operation("-M")
        elif command == "not":
            asm += self.unary_operation("!M")
        elif command in ("eq", "gt", "lt"):
            asm += self.comparison_operation(command.upper())
        self.write(asm)

    def binary_operation(self, computation):
        
        return ["@SP", "AM=M-1", "D=M", "A=A-1", f"M={computation}"]

    def unary_operation(self, computation):

        return [ "@SP", "A=M-1",f"M={computation}"]

    def comparison_operation(self, jump_type):
 
        idx = self.label_counter
        self.label_counter += 1
        true_label = f"TRUE_{idx}"
        end_label  = f"END_{idx}"
        return ["@SP", "AM=M-1", "D=M", "A=A-1", "D=M-D", f"@{true_label}", f"D;J{jump_type}", "@SP", "A=M-1", "M=0", f"@{end_label}", "0;JMP",
            f"({true_label})", "@SP", "A=M-1", "M=-1", f"({end_label})"]


    def write_push_pop(self, command_type, segment, index):
 
        asm = [f"// {command_type.lower()} {segment} {index}"]
        if command_type == "C_PUSH":
            asm += self.push(segment, index)
        else:
            asm += self.pop(segment, index)
        self.write(asm)

    def resolve_segmentbase(self, segment, index):
       
        segment_mapping = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}

        if segment in segment_mapping:
            sym = segment_mapping[segment]
            return [f"@{index}", "D=A", f"@{sym}", "A=D+M"]
        elif segment == "temp":
            return [f"@{5 + index}"]           
        elif segment == "pointer":
            return [f"@{3 + index}"]
        elif segment == "static":
            return [f"@{self.current_file}.{index}"]

    def push(self, segment, index):

        if segment == "constant":
            return [f"@{index}", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1"]
        
        addr_asm = self.resolve_segmentbase(segment, index)

        return addr_asm + ["D=M", "@SP", "A=M", "M=D","@SP", "M=M+1"]

    def pop(self, segment, index):

        addr_asm = self.resolve_segmentbase(segment, index)

        return addr_asm + ["D=A","@R13", "M=D","@SP", "AM=M-1", "D=M", "@R13", "A=M", "M=D"]

    def write_label(self, label):

        self.write([f"// label {label}", f"({label})"])

    def write_goto(self, label):

        self.write([f"// goto {label}", f"@{label}", "0;JMP"])

    def write_if(self, label):

        self.write([f"// if-goto {label}", "@SP", "AM=M-1", "D=M", f"@{label}", "D;JNE"])

    def write_function(self, name, n_locals):

        asm = [f"// function {name} {n_locals}", f"({name})"]

        for _ in range(n_locals):
            asm += ["@SP", "A=M", "M=0", "@SP", "M=M+1"]

        self.write(asm)

    def write_call(self, name, n_args):

        ret_label = f"{name}$ret.{self.call_counter}"
        self.call_counter += 1
        asm = [f"// call {name} {n_args}", f"@{ret_label}", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1"]
        
        for seg in ("LCL", "ARG", "THIS", "THAT"):
            asm += [f"@{seg}", "D=M",
                    "@SP", "A=M", "M=D", "@SP", "M=M+1"]
        asm += ["@SP", "D=M", f"@{n_args + 5}", "D=D-A", "@ARG", "M=D", "@SP", "D=M", "@LCL", "M=D", f"@{name}", "0;JMP",
                 f"({ret_label})"]
        
        self.write(asm)

    def write_return(self):

        asm = ["// return", "@LCL", "D=M", "@R14", "M=D", "@5", "A=D-A", "D=M", "@R15", "M=D", "@SP", "AM=M-1", "D=M",
               "@ARG", "A=M", "M=D", "@ARG", "D=M+1", "@SP", "M=D"]
        
        for i, seg in enumerate(("THAT", "THIS", "ARG", "LCL"), start=1):
            asm += ["@R14", "D=M",
                    f"@{i}", "A=D-A", "D=M",
                    f"@{seg}", "M=D"]
        asm += ["@R15", "A=M", "0;JMP"]

        self.write(asm)

    def write(self, lines):

        self.output.write("\n".join(lines) + "\n")

    def close(self):
        
        self.output.close()