from my_token import *
import string as _string

_ALPHA = frozenset(_string.ascii_letters)
_DIGITS = frozenset(_string.digits)
_WHITESPACES = frozenset(" \t\v\n\r")

class Lexer:
    def __init__(self, source: str):
        self.__source = source

    def scan(self) -> tuple[Token, ...]:
        source = self.__source
        source_len = len(source)
        cur_index = 0
        cur_line = 1

        tokens = []
        types_dict = TokenType._value2member_map_

        while cur_index < source_len:
            cur_char = source[cur_index]

            if cur_char.isspace():
                if cur_char == "\n": cur_line += 1
                cur_index += 1
                continue


            elif cur_char in ("\'", "\""):
                cur_index += 1
                starting_index = cur_index

                cur_index = source.find(cur_char, starting_index)
                if cur_index == -1:
                    raise RuntimeError(f"Expected: ({cur_char}) at the end of the string")

                cur_char = source[starting_index : cur_index]

                if "\n" in cur_char:
                    raise RuntimeError("String should be written in one line")

                cur_type = TokenType.STRING
                cur_index += 1


            elif cur_char in _DIGITS:
                starting_index = cur_index
                decimal_point_count = 0

                while cur_index < source_len and source[cur_index] in _DIGITS:
                    cur_index += 1

                    if cur_index < source_len and source[cur_index] == ".":
                        cur_index += 1
                        decimal_point_count += 1

                if decimal_point_count > 1:
                    raise RuntimeError(f"Expected 1 decimal point '.' in the Double Number, got ({decimal_point_count})")

                elif source[cur_index - 1] == ".":
                    raise RuntimeError(f"Expected a number after the decimal point '.', At: line ({cur_line}), index ({cur_index})")

                cur_char = source[starting_index: cur_index]
                cur_type = TokenType.INTEGER if decimal_point_count == 0 else TokenType.DOUBLE


            elif cur_char in _ALPHA:
                starting_index = cur_index
                while cur_index < source_len and source[cur_index] in _ALPHA:
                    cur_index += 1

                cur_char = source[starting_index: cur_index]
                cur_type = types_dict.get(cur_char)

                if cur_type is None:
                    if cur_char in ("True", "False"):
                        cur_type = TokenType.BOOLEAN
                    else:
                        cur_type = TokenType.IDENTIFIER


            else:
                cur_type = types_dict.get(cur_char)
                if cur_type is None:
                    raise RuntimeError(f"Unexpected Token: '{cur_char}', At: line ({cur_line}), index ({cur_index})")
                cur_char = None
                cur_index += 1


            tokens.append(Token(cur_type, cur_char))

        tokens.append(Token(TokenType.EOF))
        return tuple(tokens)
