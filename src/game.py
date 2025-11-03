import enum, attrs
from abc import ABC, abstractmethod
from typing import Generator, Literal, Self
from copy import deepcopy
import numpy
import random

from holo.prettyFormats import PrettyfyClass

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
_BlocksNP = numpy.ndarray[tuple[int, int], numpy.dtype[numpy.uint8]]
"""still ordered (lines, cols)"""
_BaseGridNP = numpy.ndarray[tuple[int, int], numpy.dtype[numpy.uint64]]

class _BlocksWithInfos(PrettyfyClass):
    def __init__(self, baseBlocks:_Blocks) -> None:
        self.baseBlocks: _Blocks = baseBlocks
        blocksArr: _BlocksNP = numpy.array(baseBlocks, dtype=numpy.uint8)
        self.baseShape: tuple[int, int] = blocksArr.shape # type:ignore
        nbLines, nbCols = self.baseShape
        self.dLines: int = 0
        self.dCols: int = 0
        self.nbLines: int = nbLines
        self.nbCols: int = nbCols
        for _ in range(nbLines):
            if (blocksArr[0, :] == 0).all():
                self.dLines += 1
                self.nbLines -= 1
                blocksArr = blocksArr[1:, :]
            if (blocksArr[-1, :] == 0).all():
                self.nbLines -= 1
                blocksArr = blocksArr[:-1, :]
        assert blocksArr.shape[0] != 0
        for _ in range(nbCols):
            if (blocksArr[:, 0] == 0).all():
                self.dCols += 1
                self.nbCols -= 1
                blocksArr = blocksArr[:, 1:]
            if (blocksArr[:, -1] == 0).all():
                self.nbCols -= 1
                blocksArr = blocksArr[:, :-1]
        assert blocksArr.shape[0] != 0
        self.simplifiedBlocks: _BlocksNP = blocksArr.copy("C")

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

COMPUTED_ROTATIONS_CONFIGS: dict[PieceKind, dict[int, _BlocksWithInfos]] = {
    kind: {nbRot: _BlocksWithInfos(baseBlocks) for nbRot, baseBlocks in rots.items()}
    for kind, rots in BASE_ROTATIONS_CONFIGS.items()}

@attrs.frozen
class Piece(PrettyfyClass):
    kind: PieceKind
    rotation: int = 0
    
    def getBlocks(self)->_BlocksWithInfos|None:
        return COMPUTED_ROTATIONS_CONFIGS[self.kind].get(self.rotation)


@attrs.frozen
class KnownPieces(PrettyfyClass):
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

@attrs.frozen
class Move(PrettyfyClass):
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
    def getNewNext(self)->PieceKind:
        raise NotImplementedError
    
    @abstractmethod
    def swapWithMemory(self)->PieceKind:
        raise NotImplementedError
    
    @abstractmethod
    def play(self, move:Move)->int:
        """play a move on the board and """
        raise NotImplementedError
    
    @abstractmethod
    def generateMoves(self)->list[Move]:
        raise NotImplementedError

    @abstractmethod
    def iterMoves(self, moves:list[Move]|None)->Generator[Self, None, None]:
        # maybe not abstract
        raise NotImplementedError

# --------------
# all boards
# --------------

class SimpleBoard(BaseBoard, PrettyfyClass):
    """this board will be a basic tetris board,
    this will not consider the special things of the redbull challenge
    this is meant to train the AI in simulations mode"""
    
    def __init__(self, nbLines:int, nbCols:int, 
                 gameStart:KnownPieces|None) -> None:
        self.board: _BaseGridNP = numpy.zeros((nbLines, nbCols), dtype=numpy.uint64)
        if gameStart is None:
            gameStart = KnownPieces(
                memory=self.getNewNext(), 
                currentPiece=self.getNewNext(),
                nextPiece=self.getNewNext())
        self.gameState: KnownPieces = gameStart
        self.score: int = 0
        self.history: list[tuple[PieceKind, Move, int]] = []
        """[(Move, score of the move)]"""
        self.nbCols: int = nbCols
        self.nbLines: int = nbLines
    
    def getNewNext(self) -> PieceKind:
        return random.choice(list(PieceKind))
    
    def swapWithMemory(self) -> PieceKind:
        self.gameState = self.gameState.swapMem()
        return self.gameState.currentPiece

    def copy(self) -> "SimpleBoard":
        return deepcopy(self)
    
    def __getStartCol(self, blockToSlide:int, dCols:int):
        return (self.nbCols//2) -2 + blockToSlide + dCols
        
    def _findLastValidLine(self, move:Move, blocks:_BlocksWithInfos)->int|None:
        """int >= 0 found a valid position | -1 the top is filled | None out on the side"""
        # the -1 is to center the masks on the board
        startCol = self.__getStartCol(blockToSlide=move.blockToSlide, dCols=blocks.dCols)
        if (startCol < 0)  or (startCol+blocks.nbCols > self.nbCols):
            return None # too much on the side (no need to check later)
        maskBlocks: _BaseGridNP = (blocks.simplifiedBlocks != 0)
        lastValidLine = -1 # not checked
        canBePlaced = True
        while canBePlaced is True:
            # => try to place one line under the last valid line
            # check that next line is valid
            startLine = lastValidLine + 1 + blocks.dLines
            boardSlice = self.board[
                startLine: startLine+blocks.nbLines, startCol: startCol+blocks.nbCols]
            if boardSlice.shape[0] != maskBlocks.shape[0]:
                canBePlaced = False
                break # over fill on the top or bottom
            if boardSlice.shape[1] != maskBlocks.shape[1]:
                raise RuntimeError(f"[BUG] sould have been checked before: "
                                   f"{boardSlice.shape[1]=} != {maskBlocks.shape[1]=}")
            boardSlice = boardSlice > 0
            intersections = (boardSlice & maskBlocks)
            canBePlaced = not (intersections.any())
            if canBePlaced is True:
                lastValidLine += 1
        return lastValidLine
    
    def play(self, move: Move)->int:
        if move.useMemory is True:
            kind = self.gameState.memory
        else: kind = self.gameState.currentPiece
        currentPiece = Piece(kind, (move.rotate%4))
        blocks = currentPiece.getBlocks()
        assert blocks is not None, \
            f"illegal rotation: {currentPiece.rotation} for the piece: {currentPiece.kind}"
        lastValidLine = self._findLastValidLine(move=move, blocks=blocks)
        assert lastValidLine is not None, \
            f"the slide: {move.blockToSlide} " \
            f"put the piece: {currentPiece} is outside of the grid"
        if lastValidLine == -1:
            raise RuntimeError(f"NOT A BUG: reached the top, the board is filled")
        # => the move is considered valid => play it for real
        startLine = lastValidLine + blocks.dLines
        startCol = self.__getStartCol(blockToSlide=move.blockToSlide, dCols=blocks.dCols)
        blockValues = (blocks.simplifiedBlocks != 0) * numpy.uint64(1+len(self.history))
        self.board[startLine: startLine+blocks.nbLines, 
                   startCol: startCol+blocks.nbCols] += blockValues
        scoreDelta = 0
        # check for completed lines (from top to bottom)
        nbClears = 0
        for line in range(startLine, startLine+blocks.nbLines):
            if (self.board[line] == 0).any():
                continue
            # => full line
            self.board[1: line+1] = self.board[: line]
            self.board[0] = 0 # new empty line
            nbClears += 1
        scoreDelta += [0, 100, 300, 500, 800][nbClears]
        # apply the stats changes
        self.score += scoreDelta
        if move.useMemory is True: 
            self.swapWithMemory()
        self.gameState = self.gameState.placeCurrent(self.getNewNext())
        self.history.append((currentPiece.kind, move, scoreDelta))
        return scoreDelta
    
    def generateMoves(self) -> list[Move]:
        return super().generateMoves()
    
    def iterMoves(self, moves: list[Move] | None) -> Generator[Self, None, None]:
        return super().iterMoves(moves)
    

class LiveBoard(BaseBoard):
    """this board will be a basic tetris board,
    this will not consider the special things of the redbull challenge
    this is meant for the AI to play in the real world"""
    ...

if __name__ == "__main__":
    board = SimpleBoard(
        nbLines=20, nbCols=10, 
        gameStart=KnownPieces(
            memory=PieceKind.red,
            currentPiece=PieceKind.green,
            nextPiece=PieceKind.yellow))
    