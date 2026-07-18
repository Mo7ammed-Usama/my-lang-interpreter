from my_lexer import *

from my_parser import Parser

source = '''
var x = 1555.5;
var str = "hello";
var test = 55 > 0;
var testt = 55 <= 0;

func add(a, b) { 
return a + b;
}

var sum = add(x, 3);

x = 5;
x ++;
y --;
x **= 8;
y //= 9;



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
}
'''

print(source + "\n")

tokens = Lexer(source).scan()
for index, token in enumerate(tokens):
    end = "\n\n" if token.type in (TokenType.SEMI_COLON, TokenType.CLOSE_BRACE, TokenType.EOF) else "\n"
    print(f"[{index}] {token}", end=end)

ast = Parser(tokens, True).parse()
print(*ast, sep="\n")



def hello():
    return "hello"

def hehe(sound, time, duration):
    print(f"{sound}, {time}, {duration}")

hehe(hello(), "9", "0.5")