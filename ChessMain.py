"""
this Class responsible for handling user input and displaying current game state object
"""
from difflib import SequenceMatcher

import pygame as p
import ChessEngine
import SmartMoveFinder
from Chess.SmartMoveFinder import checkStateGame

'''Code chỉnh màu điều chỉnh bàn cờ'''

COLORS = [p.Color("#FFFFCC"), p.Color("#CC9933")]
WIDTH = HEIGHT = 512
DIMENSION = 8  # 8*8 chess board
SQ_SIZE = HEIGHT // DIMENSION  # square size
MAX_FPS = 15  # for animation
IMAGES = {}
'''
 initialize a global dictionary of images.Call once in the main
'''

'''Gán hình anh cho các quân cờ'''
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ',
              'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


'''
main driver-> handle user input and updating graphics
'''


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.gameState()
    validMoves=gs.getAllPossibleMoves()
    moveMade=False #flag variable for when a move is made ->khi nào user play valid move và gameState thay đổi
                   # thì list validMoves mới tạo mới danh sách lại ,còn không thì giữ nguyên

    animate =False
    loadImages()
    running = True
    sqSelected = ()  # no square is selected,keep track of the last click of user(tuple:(row,col))
    playerClicks = [] #keep track of player clicks(two tuples)-> vị trí user click để di chuyển và vị trí mục tiêu của user
    gameOver=False
    playerOne=True#if a human play white, true.If AI playing :false
    playerTwo=False# same as above but for black
    while running:
        humanTurn=(gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):  # user click the same square twice
                        sqSelected = ()  # deselect
                        playerClicks = []  # clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(
                            sqSelected)  # append both 1st and 2nd clicks
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1],
                                                gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade=True
                                animate=True
                                sqSelected=() #reset user click
                                playerClicks=[]
                        if not moveMade:
                            playerClicks=[sqSelected]
                #key handlers
                elif e.type == p.KEYDOWN:
                    if e.key==p.K_z: #undo when 'z' is press
                        gs.undoMove()
                        moveMade=True
                        animate=False

                    if e.key==p.K_f: #restart the game when 'f' is press
                        gs=ChessEngine.gameState()
                        validMoves=gs.getValidMoves()
                        sqSelected=()
                        playerClicks=[]
                        moveMade=False
                        animate=False

                # AI move finder
        if not gameOver and not humanTurn:
            # Dùng cho quân random
            '''
            AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True
            '''

            # Dùng Greedy
            '''
            AIMove = SmartMoveFinder.findGreedyMove(gs, validMoves)
            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)  # backup
            '''

            # Dùng Minmax
            AIMove = SmartMoveFinder.findBestMoveMinmax(gs, validMoves, depth=2)
            if AIMove is None:
                AIMove = SmartMoveFinder.findGreedyMove(gs, validMoves)  # backup Greedy
            elif AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(gs, validMoves)

            gs.makeMove(AIMove)
            moveMade = True
            animate = True


        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1],screen,gs.board,clock)
            validMoves=gs.getValidMoves()
            moveMade=False
            animate=False


        drawGameState(screen, gs,validMoves,sqSelected)

        '''if gs.checkMate:
            gameOver=True
            if gs.whiteToMove:
                drawText(screen,'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.staleMate:
            gameOver=True
            drawText(screen,'StaleMate')'''
        # Thay thế đoạn trên
        state = checkStateGame(gs)
        if state != "Next":
            gameOver=True
            drawText(screen,state)
        clock.tick(MAX_FPS)
        p.display.flip()

'''
    Highlight square selected and moves for piece selected
'''
def highlightSquares(screen,gs,validMoves,sqSelected):
    if sqSelected!=():
        r,c=sqSelected
        if gs.board[r][c][0]==('w' if gs.whiteToMove else 'b'):
            s=p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100) #transparent value ->0:transparent
            s.fill(p.Color('green'))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('blue'))
            for move in validMoves:
                if move.startRow==r and move.startCol==c:
                    screen.blit(s,(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE))


'''
   Responsible for all the graphics within a current game state
'''


def drawGameState(screen, gs,validMoves,sqSelected):
    drawBoard(screen)
    highlightSquares(screen,gs,validMoves,sqSelected)
    drawPieces(screen, gs.board)




def drawBoard(screen):
    for r in range(DIMENSION):

        for c in range(DIMENSION):
            color = COLORS[(r + c) % 2]  # row+column==chẵn thì chọn color[0]->white,ngược lại gray
            p.draw.rect(screen, color,p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# draw pieces using the current game state board
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty square
                screen.blit(IMAGES[piece],
                            p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

#Animating
def animateMove(move,screen,board,clock):
    global colors
    dR=move.endRow-move.startRow
    dC=move.endCol-move.startCol
    framesPerSquare=10
    frameCount=(abs(dR)+abs(dC))*framesPerSquare
    for frame in range(frameCount+1):
        r,c=(move.startRow+dR*frame/frameCount,move.startCol+dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        color = COLORS[(move.endRow + move.endCol) % 2]
        endSquare=p.Rect(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,color,endSquare)

        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured],endSquare)

        screen.blit(IMAGES[move.pieceMoved],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(70)

def drawText(screen,text):
    font=p.font.SysFont("Arial",40,True,False)
    textObject=font.render(text,0,p.Color('Gray'))
    textLocation=p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2- textObject.get_width()/2,HEIGHT/2-textObject.get_height()/2)
    screen.blit(textObject,textLocation)
    textObject=font.render(text,0,p.Color("Black"))
    screen.blit(textObject,textLocation.move(2,2))
if __name__ == "__main__":
    main()