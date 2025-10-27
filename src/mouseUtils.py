from pynput.mouse import Controller as Mouse, Button as MouseBtn
from pynput import keyboard
import time
import attrs

MOUSE = Mouse()
KEYBOARD = keyboard.Controller()

@attrs.frozen
class ActionSetup():
    dx: int
    dt: float

@attrs.frozen
class MouseSetup():
    # actions related
    slide: ActionSetup
    memory: ActionSetup
    drop: ActionSetup
    rotateDuration: float|None
    
    # env related
    deviceSize: tuple[int, int]
    isFullScreen: bool


TETRIS_FULLSCREEN = MouseSetup(
    slide=ActionSetup(65, 0.2),
    memory=ActionSetup(100, 0.05),
    drop=ActionSetup(100, 0.05),
    rotateDuration=None,
    deviceSize=(1000, 1000), isFullScreen=True)

CURRENT_SETUP = TETRIS_FULLSCREEN

def mouseDragVertical(
        dist:int, duration:float, goDown: bool, goBack: bool = True) -> None:
    dist = dist * (1 if goDown else -1)
    MOUSE.press(MouseBtn.left)
    MOUSE.move(0, dist)
    time.sleep(duration)
    MOUSE.release(MouseBtn.left)
    if goBack is True:
        MOUSE.move(0, -dist)


def decomposeMove(dPx: int, N: int) -> list[int]:
    assert N > 0
    q, r = divmod(abs(dPx), N)
    sign = (1 if dPx >= 0 else -1)
    steps = [sign * (q + 1) for _ in range(r)]
    steps.extend(sign * q for _ in range(N - r))
    return steps

def mouseDragSides(
        dx: int, duration: float, 
        nbSteps: int|None = None, goBack: bool = True) -> None:
    if nbSteps is None:
        # => move 1 px at each step
        nbSteps = abs(dx) 
    steps = decomposeMove(dx, nbSteps)
    MOUSE.press(MouseBtn.left)
    start = time.perf_counter()
    sleep_time = 0
    for i in range(nbSteps):
        MOUSE.move(steps[i], 0)
        target = start + (i + 1) * (duration / nbSteps)
        sleep_time = target - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)
    MOUSE.release(MouseBtn.left)
    if goBack is True:
        MOUSE.move(-dx, 0)


def slideBy(nbBlocks:int)->None:
    """slide the current block by `nbBlocks`
    `nbBlocks` < 0 => to the left | > 0 to the rigth | can't be 0"""
    assert nbBlocks != 0
    mouseDragSides(
        dx=nbBlocks*CURRENT_SETUP.slide.dx,
        duration=CURRENT_SETUP.slide.dt,
        nbSteps=None, goBack=True)

def dropBlock()->None:
    mouseDragVertical(
        dist=CURRENT_SETUP.drop.dx, 
        duration=CURRENT_SETUP.drop.dt,
        goDown=True, goBack=True)
    
def putInMemory()->None:
    mouseDragVertical(
        dist=CURRENT_SETUP.memory.dx, 
        duration=CURRENT_SETUP.memory.dt,
        goDown=False, goBack=True)

def rotateBy(nbRigthRotations:int)->None:
    for _ in range(nbRigthRotations):
        MOUSE.press(MouseBtn.left)
        if CURRENT_SETUP.rotateDuration is not None:
            time.sleep(CURRENT_SETUP.rotateDuration)
        MOUSE.release(MouseBtn.left)

