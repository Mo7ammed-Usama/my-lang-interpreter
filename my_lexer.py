from my_token import *


class Lexer:
    def __init__(self, source: str):
        self.__source = source

    def scan(self) -> tuple[Token, ...]:
        source = self.__source
        source_len = len(source)
        cur_index = 0
        cur_line = 1

        tokens = []

        while cur_index < source_len:
            cur_char = source[cur_index]
            cur_type = None

            if cur_char.isspace():
                if cur_char == "\n": cur_line += 1
                cur_index += 1
                continue

            if cur_char in ("\'", "\""):
                cur_index += 1
                starting_index = cur_index
                while cur_index <= source_len and source[cur_index] != cur_char:
                    cur_index += 1

                    if cur_index >= source_len:
                        raise RuntimeError(f"Expected {cur_char} at the end of the string")

                    if source[cur_index] == "\n":
                        raise RuntimeError("String should be written in one line")

                string = source[starting_index : cur_index]
                tokens.append(Token(TokenType.STRING, string))
                cur_index += 1
                continue

            if cur_char.isdecimal():
                starting_index = cur_index
                decimal_point_count = 0

                while cur_index < source_len and source[cur_index].isdecimal():
                    cur_index += 1
                    if source[cur_index] == "." and source[cur_index + 1].isdecimal():
                        cur_index += 1
                        decimal_point_count += 1

                if decimal_point_count > 1:
                    raise RuntimeError(f"Expected 1 decimal point '.' in the Double Number, got {decimal_point_count}")

                cur_type = TokenType.DOUBLE if decimal_point_count == 1 else TokenType.INTEGER
                number = source[starting_index: cur_index]

                tokens.append(Token(cur_type, number))
                continue

            if cur_char.isalpha():
                starting_index = cur_index
                while cur_index < source_len and source[cur_index].isalpha():
                    cur_index += 1

                string = source[starting_index: cur_index]
                cur_type = TokenType._value2member_map_.get(string)

                if cur_type is None:
                    if string in ("True", "False"):
                        cur_type = TokenType.BOOLEAN
                    else:
                        cur_type = TokenType.IDENTIFIER

                tokens.append(Token(cur_type, string))
                continue

            cur_type = TokenType._value2member_map_.get(cur_char)

            if cur_type is None:
                raise RuntimeError(f"Unexpected Token: ({cur_char}), At: line ({cur_line}), index ({cur_index})")

            tokens.append(Token(cur_type, cur_char))
            cur_index += 1


        tokens.append(Token(TokenType.EOF))
        return tuple(tokens)

