from my_lexer import *
import cProfile

source = '''
var x = 1555.5;
var str = "hello";
var test = 55 > 0;
var test2 = 55 <= 0;

func add(a, b) {
return a + b;
}
add(x, 3);'''

print(source + "\n")

tokens = Lexer(source).scan()
print(*tokens, sep="\n")

