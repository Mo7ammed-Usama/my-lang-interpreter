import sys
from my_compiler import Compiler
from my_lexer import *
from time import perf_counter_ns
from my_parser import Parser
from my_virtual_machine import VirtualMachine


sys.set_int_max_str_digits(1000000)
# ================== Source Code ===================
source = '''
/*
var x = 1555.5;
var str = "hello";
var test = 55 > 0;
var testt = 55 <= 0;
var y = 66;

func add(a, b) {
    return a + b;
}

var sum = add(x, 3);

x = 5;
x ++;
y --;
x *= 8;
y ^= 5;

if (9 >= x) {
    if (x != 4) {
        y += 7; 
        x --;
    }

    if (y == 7) {
        y --;
    }
}

while (x >= 8) {
    x --;
    if (x == 6) {
        continue;
    }
    
    while (x > 50) {
        x++;
        break;
    }
    
    if (y != x^2) {
        break;
    }
    y ++;
}

func mul(a, b) {
    var result = 0;
    
    func myAdd(a, b) {
        var myAddResult = a + b;
        result ++;
        result --;
        x++;
        return myAddResult;
    }
    
    while (b > 0) {
        result = myAdd(result, a);
        b --;
    }
    
    if (b < 0) {
        return "Unexpected error";
    }
    
    return result;
}

//A comment
var long = """
hello, how are you""";

var opp = -(-add(2, 3));

func tetration(a, b) {
    var result = 1;
    
    while (b > 0) {
        result = a^result;
        b--;
    }
    
    return result;
}

func recursiveMul(a, b) {
    if (b <= 0) {
        return 0;
    }
    
    return a + recursiveMul(a, b - 1);
}

var tetra = tetration(7, 2);
tetra;

var multi = mul(3, 4);
multi;

var reMulti = recursiveMul(12, 12);
reMulti;

log(3 + 4);
log(reMulti + tetra);
*/

func calculator(firstNum, secondNum, operator) {  
    var result = 0;
    
    if (operator == "+") {
        result = firstNum + secondNum;
    }
    
    if (operator == "-") {
        result = firstNum - secondNum;
    }
    
    if (operator == "*") {
        result = firstNum * secondNum;
    }
    
    if (operator == "/") {
        if (Integer(secondNum) == 0) {
            log("Cannot divide by 0, enter another number");
            return Null;
        }
        result = firstNum / secondNum;
    }
    
    return result;
}

func main() {
    while (True) {
        var firstNum = Integer(input("Enter 1st number: "));
        var operator = input("Enter the operator: ");
        var secondNum = Integer(input("Enter 2nd number: "));
        
        var result = calculator(firstNum, secondNum, operator);
        
        if (result != Null) {
            break;
        }
    }
    
    log(result);
}

main();
'''
start = perf_counter_ns()
# print(" Source Code ".center(100, "="))
# print(source)
# ==================================================


# ===================== Lexer ======================
tokens = Lexer(source).scan()

# print("\n" + " Tokens ".center(100, "="))
# for index, token in enumerate(tokens):
#     end = "\n\n\n" if token.type in (TokenType.CLOSE_BRACE, TokenType.EOF) else "\n\n" if token.type == TokenType.SEMI_COLON else "\n"
#     print(f"[{index}] {token}", end=end)
# ==================================================


# ===================== Parser =====================
ast = Parser(tokens, True).parse()

# print("\n" + " Abstract Syntax Tree (Parse Tree) ".center(100, "="))
# print(*ast, sep="\n\n", end="\n\n")
# ==================================================


# ==================== Compiler ====================
compiler = Compiler(ast)

instructions = compiler.compile()

constants = compiler.constants
global_slots_count = compiler.global_slots_count
function_signatures = compiler.function_signatures

# print("\n" + " Instructions ".center(100, "="))
# print(compiler.get_info())
# ==================================================


# ================ Virtual Machine =================
virtual_machine = VirtualMachine(instructions, constants, global_slots_count, function_signatures, False)
final_stack = virtual_machine.run()
# print("\n" + " Final Stack ".center(100, "="))
# print(final_stack)
# ==================================================



# print("\n" + " Process Time ".center(100, "="))

end = perf_counter_ns()
duration = end - start

# print(f"Processed in: {duration / 1_000_000} ms ({duration / 1_000_000_000} s)")


