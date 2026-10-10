def make_board(size):
    return [[0] * size] * size

board = make_board(3)
board[0][0] = 1
print(board)

# [[0] * size] * size не создает три разные строки, а кладет в список три ссылки на один и тот же список.
# Поэтому когда меняем клетку в первой строке, она меняется во всех строках сразу.
# Нужно создавать каждую строку отдельно, например через генератор списка.

def make_board(size):
    return [[0] * size for _ in range(size)]

board = make_board(3)
board[0][0] = 1
print(board)
