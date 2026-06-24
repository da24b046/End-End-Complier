# DA2304 Assignment 3 

## Directory layout

```
DA2304_Assignment3_DA24B046/
├── jack/          
│   ├── Conv.jack
│   └── Main.jack
├── src/          
│   ├── JackCompiler.py      
│   ├── JackTokenizer.py     
│   ├── CompilationEngine.py 
│   ├── SymbolTable.py       
│   ├── VMWriter.py          
│   └── README.md          
├── out/           
│    ├── ConvT.xml  MainT.xml   
│    ├── Conv.xml   Main.xml    
│    └── Conv.vm    Main.vm    
├── 5x5_9x9_convolution.png
└──Navadeep_da24b046.pdf
```

## Running the pipeline


```bash
cd src/
python JackCompiler.py ../jack/ ../out/
```

Each run produces three files per `.jack` source:
| File | Description |
|------|-------------|
| `<Class>T.xml` | Token stream |
| `<Class>.xml`  | Parse-tree XML |
| `<Class>.vm`   | VM code |

## Execution on the Hack emulator

1. Feed `Conv.vm` and `Main.vm` into the Assignment-2 VM Translator

   This produces  `Conv.asm` + `Main.asm`.

2. Load the generated `.asm` files into the Hack CPU Emulator

3. Run the emulator — the convolution output will appear in the
   Hack terminal window.
