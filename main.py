from my_compiler import Compiler
from my_instruction import OpCode
from my_lexer import *

from my_parser import Parser

source = '''
var x = 1555.5;
var str = "hello";
var test = 55 > 0;
var testt = 55 <= 0;
var y = 66;

func add(a, b) {
a + b;
}

var sum = add(x, 3);

x = 5;
x ++;
y --;
x *= 8;
y ^= 5;


if (9 >= x) {
    if (x != 4) {
        y += 7; /* A comment */
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
    x ++;
    //x -= 1;
    while (+-(-+(-b)) >= 0) {
        result += a;
        b --;
    }
    if (b != 0) {
        return "Unexpected error";
    }
    return result;
}
// A comment
var long = """
hello, how are you""";

var opp = -(-add(2, 3));
'''

print(source + "\n")


tokens = Lexer(source).scan()
for index, token in enumerate(tokens):
    end = "\n\n" if token.type in (TokenType.SEMI_COLON, TokenType.CLOSE_BRACE, TokenType.EOF) else "\n"
    print(f"[{index}] {token}", end=end)

ast = Parser(tokens, True).parse()
print(*ast, sep="\n", end="\n\n")


compiler = Compiler(ast)
instructions = compiler.compile()

for index, instruction in enumerate(instructions):
    end = "\n\n" if instruction.op_code == OpCode.RETURN or index == 0 else "\n"
    print(f"[{index}] {instruction}", end=end)

print("\n" + compiler.get_info())



def hehe(sound, time, duration):
    def hello():
        return sound

    print(f"{hello()}, {time}, {duration}")



x = 55


