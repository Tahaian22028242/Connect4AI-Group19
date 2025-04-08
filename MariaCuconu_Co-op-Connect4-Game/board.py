class Board:

    def __init__(self,row_count,column_count):
        self.__ROW_COUNT=row_count
        self.__COLUMN_COUNT=column_count
        self.__board=[[0 for i in range(column_count)] for i in range(row_count)]

    @property
    def ROW_COUNT(self):
        return self.__ROW_COUNT

    # @ROW_COUNT.setter
    # def ROW_COUNT(self,value):
    #     self.__ROW_COUNT

    @property
    def COLUMN_COUNT(self):
        return self.__COLUMN_COUNT

    @property
    def board(self):
        return self.__board

    def __str__(self):
        result = ""
        result = result + "0 1 2 3 4 5 6" + '\n'
        for row in range(self.ROW_COUNT):
            for column in range(self.COLUMN_COUNT):
                result = result + str(self.board[row][column]) + ' '
            result = result + '\n'
        return result



# board=Board(6,7)
# print(board)