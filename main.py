from my_lexer import Lexer

source = '''
var x = 1555.5;
var str = "hello";func add(a, b) {return a + b;}add(x, 3);
'''

print(source + "\n")

tokens = Lexer(source).scan()
print(*tokens, sep="\n")

s = ""

print(s)

