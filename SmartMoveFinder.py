import random

from pygame.examples.midi import NullKey


def findRandomMove(validMoves):
   return validMoves[random.randint(0,len(validMoves)-1)]


def findBestMove():
    pass

#pieceScore: gán điểm cho từng quân cờ
pieceScore = {
    "K": 1000, "Q": 9, "R": 5, "B": 3, "N": 2, "p": 1
}

#scoreMaterial tính tổng điểm trên bàn cờ
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w': # quân trắng
                score += pieceScore[square[1]]
            elif square[0] == 'b': #quân đen
                score -= pieceScore[square[1]]
    return score



'''thử từng nước đi, gọi makeMove() để thực hiện giả lập, tính điểm, 
chọn nước tốt nhất rồi undoMove() để quay lại.
Nếu không tìm được nước ăn (tức mọi score bằng nhau) thì fallback sang random.'''


def findGreedyMove(gs, validMoves):

    '''
    Greedy: chon nước ăn quân cờ có giá trị cao nhất
    Nếu không có nước nào ăn thì chọn reandom
    '''

    bestMove = None
    maxScore = -9999

# dành cho quân trắng
    for move in validMoves:
        gs.makeMove(move)       #thử đi
        score = scoreMaterial(gs.board)# đánh giá sau khi thực hiện
        if score > maxScore:
            maxScore = score
            bestMove = move
        gs.undoMove()   #quay lại

    else: # nhánh dành cho quân đen
        minScore = 9999
        for move in validMoves:
            gs.makeMove(move)
            score = scoreMaterial(gs.board)
            if score < minScore:
                minScore = score
                bestMove = move
            gs.undoMove()
    return bestMove

def checkStateGame(gs):
    #Tra về trạng thái bàn cờ
    if gs.checkMate: # true nếu hết nước đi và đang bị chiếu. Ai tới lượt mà không có nước đi thì thua.
        if gs.whiteToMove:
            return "Black wins"
        else:
            return "White wins"
#true nếu hết nước đi nhưng KHÔNG bị chiếu → hòa. Nếu cả 2 cái trên đều không xảy ra → ván cờ vẫn tiếp tục
    elif gs.staleMate:
        return "Draw" #Hòa nhưng hết đường
    else:
        return "Next" #Game tiếp tục



# Hàm minmax
def minmax(gs,depth, isMaximizingPlayer) :
    if depth == 0 or gs.checkMate or gs.staleMate:
        return scoreMaterial(gs.board)

    validMoves = gs.getValidMoves()

    if isMaximizingPlayer: # lượt quân trắng
        maxEval = -9999
        for move in validMoves:
            gs.makeMove(move)
            eval = minmax(gs, depth - 1, False)
            gs.undoMove()
            maxEval = max(maxEval, eval)
        return maxEval
    else:  # lượt quân đen
        minEval = 9999
        for move in validMoves:
            gs.makeMove(move)
            eval = minmax(gs, depth - 1, True)
            gs.undoMove()
            minEval = min(minEval, eval)
        return minEval


# Tìm nước đi tốt nhất bằng minimax
def findBestMoveMinmax(gs, validMoves, depth):
    bestMove = None
    if gs.whiteToMove:  # lượt trắng -> maximizing
        maxEval = -9999
        for move in validMoves:
            gs.makeMove(move)
            eval = minmax(gs, depth - 1, False)
            gs.undoMove()
            if eval > maxEval:
                maxEval = eval
                bestMove = move
    else:  # lượt đen -> minimizing
        minEval = 9999
        for move in validMoves:
            gs.makeMove(move)
            eval = minmax(gs, depth - 1, True)
            gs.undoMove()
            if eval < minEval:
                minEval = eval
                bestMove = move
    return bestMove
'''
Cấu trúc hoạt động: 
- findBestMoveMinmax(...) duyệt qua tất cả các nước đi hợp lệ, thử và gọi minmax.
- minmax(...) đệ quy:
+ Nếu hết độ sâu (depth = 0) hoặc ván đã kết thúc → trả về scoreMaterial.
+ Nếu là lượt Maximizing player (trắng) → chọn giá trị lớn nhất.
+ Nếu là lượt Minimizing player (đen) → chọn giá trị nhỏ nhất.
'''



