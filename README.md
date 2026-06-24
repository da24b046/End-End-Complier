# End-to-End Compiler

A comprehensive project implementing the complete compilation pipeline from high-level Jack language to Hack assembly code. This repository contains all the essential components needed to build a working compiler, including lexical analysis, parsing, code generation, memory management, and arithmetic logic operations.

## Project Overview

This is a full-stack compiler implementation that transforms Jack language programs into executable Hack machine code. The project demonstrates fundamental compiler architecture and digital logic design principles.

## Directory Structure

```
End-End-Complier/
├── Jack_Compiler/           # High-level language compiler
│   ├── JackCompiler.py      # Main compilation pipeline
│   ├── JackTokenizer.py     # Lexical analysis (tokenization)
│   ├── CompilationEngine.py # Syntax analysis & code generation
│   ├── SymbolTable.py       # Symbol table management
│   ├── VMWriter.py          # VM code generation
│   ├── README.md            # Jack compiler documentation
│   └── examples/            # Example Jack programs
│
├── VM_Translator/           # Virtual machine to assembly translator
│   ├── vm_translator.py     # Main VM translator
│   ├── parser_codewriter.py # Parser and code writer
│   ├── add_bias.vm          # Example VM program
│   ├── matmul.vm            # Matrix multiplication example
│   ├── rowxcol.vm           # Row-column operation example
│   ├── sum.vm               # Summation example
│   └── examples/            # Additional examples
│
├── Memory Components/       # Digital logic components for memory
│   ├── Bit.hdl              # 1-bit storage element
│   ├── Register.hdl         # 16-bit register
│   ├── RAM8.hdl             # 8-word RAM
│   ├── RAM16K.hdl           # 16K-word RAM
│   └── Counter.hdl          # Counter logic
│
├── Wallace Tree Multiplier/ # High-performance arithmetic circuit
│   ├── Multiplier.hdl       # Main multiplier (using Wallace tree)
│   ├── PP32.hdl             # Partial product generation (32-bit)
│   ├── CSA32.hdl            # Carry-save adder (32-bit)
│   ├── Add32.hdl            # 32-bit adder
│   ├── ALU.hdl              # Arithmetic logic unit
│   ├── ShiftLeft32.hdl      # Left shifter (32-bit)
│   ├── And16.hdl            # Logical operations
│   ├── Or16way.hdl          # Multi-input OR gate
│   ├── NG.hdl               # Negate gate
│   ├── Multiplier.tst       # Test bench for multiplier
│   ├── ALU.tst              # Test bench for ALU
│   ├── Multiplier.cmp       # Expected output (multiplier)
│   └── ALU.cmp              # Expected output (ALU)
│
└── README.md               # This file
```

## Pipeline Overview

The compiler follows a traditional multi-stage architecture:

```
Jack Source Code (.jack)
    ↓
[Tokenizer] → Token Stream (.xml)
    ↓
[Parser] → Parse Tree (.xml)
    ↓
[Code Generator] → VM Code (.vm)
    ↓
[VM Translator] → Assembly Code (.asm)
    ↓
[Hack CPU Emulator] → Execution
```

## Components

### 1. **Jack Compiler** (`Jack_Compiler/`)
Compiles high-level Jack programs into VM intermediate code.

- **JackTokenizer.py**: Lexical analyzer that converts source text into tokens
- **CompilationEngine.py**: Recursive descent parser and semantic analyzer
- **SymbolTable.py**: Manages variable scopes and symbol attributes
- **VMWriter.py**: Generates VM commands from the parse tree
- **JackCompiler.py**: Main driver for the compilation pipeline

**Usage:**
```bash
cd Jack_Compiler
python JackCompiler.py <source.jack> [output_directory]
```

**Output:**
- `<ClassName>T.xml` - Tokenizer output
- `<ClassName>.xml` - Parse tree
- `<ClassName>.vm` - VM code

### 2. **VM Translator** (`VM_Translator/`)
Translates VM intermediate code into Hack assembly language.

- **parser_codewriter.py**: Parser and assembly code writer
- **vm_translator.py**: Main translation engine
- Example VM programs demonstrating various operations

**Supported VM Commands:**
- Arithmetic: `add`, `sub`, `neg`, `eq`, `lt`, `gt`, `and`, `or`, `not`
- Memory: `push`, `pop` (local, argument, this, that, constant, static, temp, pointer)
- Control flow: `label`, `goto`, `if-goto`
- Functions: `function`, `call`, `return`

### 3. **Memory Components** (`Memory Components/`)
Hardware description language (HDL) implementations of memory elements:

- **Bit.hdl**: Basic 1-bit flip-flop storage
- **Register.hdl**: 16-bit register
- **RAM8.hdl**: 8 words of RAM
- **RAM16K.hdl**: 16K words of RAM
- **Counter.hdl**: Program counter logic

### 4. **Wallace Tree Multiplier** (`Wallace Tree Multiplier/`)
High-performance 32-bit multiplier using Wallace tree reduction:

- **Multiplier.hdl**: Main multiplier implementation
- **PP32.hdl**: Partial product generation
- **CSA32.hdl**: Carry-save adder for Wallace tree
- **Add32.hdl**: Final sum computation
- **ALU.hdl**: Full arithmetic logic unit
- Test files for verification

**Features:**
- 32-bit multiplication using carry-save addition
- Reduced latency through parallel computation
- Arithmetic operations: add, subtract, multiply
- Logical operations: AND, OR, NOT
- Special functions: negate, zero test

## Usage Examples

### Compile a Jack Program

```bash
cd Jack_Compiler
python JackCompiler.py ../examples/Main.jack ../output/
```

This produces:
- `MainT.xml` - Tokens
- `Main.xml` - Parse tree  
- `Main.vm` - VM code

### Translate VM Code to Assembly

```bash
cd VM_Translator
python vm_translator.py program.vm
```

This produces `program.asm` ready for the Hack emulator.

### Full Pipeline

```bash
# Step 1: Compile Jack to VM
cd Jack_Compiler
python JackCompiler.py ../examples/ ../build/

# Step 2: Translate VM to Assembly
cd ../VM_Translator
python vm_translator.py ../build/*.vm

# Step 3: Load and run in Hack emulator
# (Use the provided Hack CPU Emulator with the .asm files)
```

## Language Support

### Jack Language Features
- Classes with constructors, methods, and functions
- Variables: local, field (instance), static, parameter
- Primitive types: int, boolean, String, void
- Arrays and objects
- Expressions with operator precedence
- Control flow: if/else, while, do statements

### VM Language Features
- Stack-based operations
- Segment-based memory access
- Function calls with local scopes
- Conditional and unconditional jumps
- Arithmetic and logical operations

## Technical Details

### Compilation Stages

1. **Lexical Analysis (Tokenizer)**
   - Pattern matching for keywords, symbols, identifiers
   - Number and string literal parsing
   - Comment removal

2. **Syntax Analysis (Parser)**
   - Recursive descent parsing
   - Grammar compliance checking
   - Parse tree generation

3. **Semantic Analysis**
   - Symbol table construction
   - Type checking (future enhancement)
   - Scope management

4. **Code Generation**
   - VM command emission
   - Temporary variable allocation
   - Label and function management

5. **VM Translation**
   - Stack machine semantics
   - Memory segment mapping
   - Bootstrap code generation

### Architecture Support

The Hack Architecture provides:
- 16-bit words
- 32KB memory address space
- Built-in I/O and screen memory
- Two 16-bit registers: A (address), D (data)
- 16-bit ALU for arithmetic/logic

## Testing

Test files are included in the Wallace Tree Multiplier directory:
- `Multiplier.tst` - Multiplier test script
- `Multiplier.cmp` - Expected outputs
- `ALU.tst` - ALU test script
- `ALU.cmp` - ALU expected outputs

Run tests with the Hack Hardware Simulator.

## Project Features

✅ Complete compilation pipeline from source to assembly
✅ Recursive descent parser with full grammar support
✅ Symbol table with multi-level scoping
✅ VM-based intermediate code generation
✅ Wallace tree multiplier for efficient arithmetic
✅ Comprehensive memory hierarchy
✅ ALU with 18 operations
✅ Example programs and test cases

## Future Enhancements

- Optimization passes (constant folding, dead code elimination)
- Peephole optimization
- Extended type system with type inference
- Standard library implementation
- Debugger integration
- Performance profiling

## References

This implementation is based on the Nand2Tetris course, a comprehensive introduction to computer systems from logic gates to operating systems.


---

**Project Language**: Python (Compiler), Hardware Description Language (HDL for circuits)

**Last Updated**: June 2026
