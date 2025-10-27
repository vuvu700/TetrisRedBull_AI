import enum, attrs
from abc import ABC, abstractmethod
from typing import Generator, Literal, Self
from copy import deepcopy


# ! NOTE ! -> grids will be using [row][col] style indexing


# --------------
# pieces
# --------------

class PieceKind(enum.StrEnum):
    magenta = "magenta"
    cyan = "cyan"
    orange = "orange"
    blue = "blue"
    green = "green"
    red = "red"
    yellow = "yellow"

_LitPieceBlock = Literal[0, 1, 2]
class PieceBlock(enum.IntEnum):
    empty = 0
    block = 1
    canSpot = 2

_Blocks = list[list[_LitPieceBlock]]


BASE_ROTATIONS_CONFIGS: dict[PieceKind, dict[int, _Blocks]] = {
    # 1) the ones that are commented are the config 
    #   that will result in another one after a translation
    #   (they can be de-commented later if needed)
    # 2) they all start at the same relative possition based 
    #   on the given masks
    PieceKind.magenta: {
        0: [[0,1,0],[1,2,1],[0,0,0]],
        1: [[0,1,0],[0,2,1],[0,1,0]],
        2: [[0,0,0],[2,1,1],[0,1,0]],
        3: [[0,1,0],[2,1,0],[0,1,0]],
    }, PieceKind.cyan: {
        0: [[0,0,0,0],[1,2,1,1],[0,0,0,0],[0,0,0,0]],
        1: [[0,0,1,0],[0,0,1,0],[0,0,2,0],[0,0,1,0]],
        #2:[[0,0,0,0],[0,0,0,0],[1,2,1,1],[0,0,0,0]],
        #3:[[0,1,0,0],[0,1,0,0],[0,2,0,0],[0,1,0,0]],
    }, PieceKind.orange: {
        0: [[0,0,1],[1,2,1],[0,0,0]],
        1: [[0,1,0],[0,1,0],[0,1,2]],
        2: [[0,0,0],[2,1,1],[1,0,0]],
        3: [[1,1,0],[0,2,0],[0,2,0]],
    }, PieceKind.blue: {
        0: [[1,0,0],[1,2,1],[0,0,0]],
        1: [[0,1,1],[0,2,0],[0,1,0]],
        2: [[0,0,0],[2,1,1],[0,0,1]],
        3: [[0,1,0],[0,1,0],[1,2,0]],
    }, PieceKind.green: {
        0: [[0,1,1],[1,2,0],[0,0,0]],
        1: [[0,1,0],[0,2,1],[0,0,1]],
        #2:[[0,0,0],[0,1,1],[1,2,0]],
        #3:[[1,0,0],[2,1,0],[0,1,0]],
    }, PieceKind.red: {
        0: [[1,1,0],[0,2,1],[0,0,0]],
        1: [[0,0,1],[0,1,1],[0,2,0]],
        #2:[[0,0,0],[1,1,0],[0,2,1]],
        #3:[[0,1,0],[1,1,0],[2,0,0]],
    }, PieceKind.yellow: {
        0: [[0,1,1],[0,1,1]],
        #1:[[0,1,1],[0,1,1]],
        #2:[[0,1,1],[0,1,1]],
        #3:[[0,1,1],[0,1,1]],
    },
}


class Piece():
    kind: PieceKind
    rotation: int = 0
    
    def getBlocks(self)->_Blocks|None:
        return BASE_ROTATIONS_CONFIGS[self.kind].get(self.rotation)


@attrs.frozen
class KnownPieces():
    memory: PieceKind
    currentPiece: PieceKind
    nextPiece: PieceKind
    
    def swapMem(self)->"KnownPieces":
        return KnownPieces(
            memory=self.currentPiece,
            currentPiece=self.memory,
            nextPiece=self.nextPiece)
    
    def placeCurrent(self, newNext:PieceKind)->"KnownPieces":
        return KnownPieces(
            memory=self.memory,
            currentPiece=self.nextPiece,
            nextPiece=newNext)


# --------------
# moves
# --------------

class Move():
    useMemory: bool
    """to use the block from the memory"""
    rotate: int
    """nb of rigth rotation, must be mod 4"""
    blockToSlide: int
    """nb of block to slide to the rigth (negative for left)"""



# --------------
# base board
# --------------

class BaseBoard(ABC):
    
    @abstractmethod
    def copy(self)->Self:
        raise NotImplementedError
    
    @abstractmethod
    def swapWithMemory(self)->PieceKind:
        raise NotImplementedError
    
    @abstractmethod
    def play(self, move:Move):
        raise NotImplementedError
    
    @abstractmethod
    def generateMoves(self)->list[Move]:
        raise NotImplementedError

    @abstractmethod
    def iterMoves(self, moves:list[Move]|None)->Generator[Self]:
        # maybe not abstract
        raise NotImplementedError

# --------------
# all boards
# --------------

class SimpleBoard(BaseBoard):
    """this board will be a basic tetris board,
    this will not consider the special things of the redbull challenge"""
    
    def __init__(self, nbLines:int, nbCols:int, 
                 gameStart:KnownPieces) -> None:
        self.board: list[list[bool]] = [
            [False for _ in range(nbCols)] for _ in range(nbLines)]
        self.gameState: KnownPieces = gameStart
    
    def swapWithMemory(self) -> PieceKind:
        self.gameState = self.gameState.swapMem()
        return self.gameState.currentPiece

    def copy(self) -> "SimpleBoard":
        return deepcopy(self)
    
    def play(self, move: Move)->None:
        if move.useMemory is True:
            self.swapWithMemory()
        ... 
    

if __name__ == "__main__":
    board = SimpleBoard(
        nbLines=20, nbCols=10, 
        gameStart=KnownPieces(
            memory=PieceKind.red,
            currentPiece=PieceKind.green,
            nextPiece=PieceKind.yellow))
    