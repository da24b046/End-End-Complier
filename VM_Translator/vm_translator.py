import os
from parser_codewriter import Parser, C_ARITHMETIC, C_PUSH, C_POP, C_LABEL, C_GOTO, C_IF, C_FUNCTION, C_CALL, C_RETURN , CodeWriter

class VMTranslator:
    
    def translate(self, path):
 
        if os.path.isdir(path):
            vm_files = [os.path.join(path, f)
                        for f in os.listdir(path) if f.endswith(".vm")]
            out_path = os.path.join(path, os.path.basename(path) + ".asm")
        else:
            vm_files = [path]
            out_path = path.replace(".vm", ".asm")

        writer = CodeWriter(out_path)

        for vm_file in vm_files:

            base = os.path.splitext(os.path.basename(vm_file))[0]
            writer.set_file_name(base)
            parser = Parser(vm_file)

            while parser.has_more_commands():
                parser.advance()
                ct = parser.command_type()
                if ct == C_ARITHMETIC:
                    writer.write_arithmetic(parser.arg1())
                elif ct in (C_PUSH, C_POP):
                    writer.write_push_pop(ct, parser.arg1(), parser.arg2())
                elif ct == C_LABEL:
                    writer.write_label(parser.arg1())
                elif ct == C_GOTO:
                    writer.write_goto(parser.arg1())
                elif ct == C_IF:
                    writer.write_if(parser.arg1())
                elif ct == C_FUNCTION:
                    writer.write_function(parser.arg1(), parser.arg2())
                elif ct == C_CALL:
                    writer.write_call(parser.arg1(), parser.arg2())
                elif ct == C_RETURN:
                    writer.write_return()

        writer.close()
