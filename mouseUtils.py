from pynput.mouse import Controller, Button
import time

MOUSE = Controller()


def mouseDragVertical(goDown: bool, goBack: bool = True) -> None:
    DIST = 100 * (1 if goDown else -1)
    MOUSE.press(Button.left)
    MOUSE.move(0, DIST)
    time.sleep(0.05)
    MOUSE.release(Button.left)
    if goBack is True:
        MOUSE.move(0, -DIST)


def decompose(dx: int, N: int) -> list[int]:
    assert N > 0
    q, r = divmod(abs(dx), N)
    sign = (1 if dx >= 0 else -1)
    steps = [sign * (q + 1) for _ in range(r)]
    steps.extend(sign * q for _ in range(N - r))
    return steps


def mouseDragSides(dx: int, duration: float, nbSteps: int = 10, goBack: bool = True) -> None:
    MOUSE.press(Button.left)
    steps = decompose(dx, nbSteps)
    for i in range(nbSteps):
        MOUSE.move(steps[i], 0)
        time.sleep(duration / nbSteps)
    remSleep = 0.05 - (duration / nbSteps)
    if remSleep > 0.0:
        time.sleep(remSleep)
    MOUSE.release(Button.left)
    MOUSE.move(-dx, 0)

# tests de drag side:
# env: ipad pro 1400x810, dpr:3
# grid size: 327 x 629
# -> move de 1 case (non exactement afiné: 50 trop peu)
# non, mouseDragSides(54, duration=0.5, nbSteps=10)
# oui, mouseDragSides(55, duration=0.3, nbSteps=10)
# non, mouseDragSides(55, duration=0.15, nbSteps=10)
# oui, mouseDragSides(57, duration=0.15, nbSteps=10)
# non, mouseDragSides(57, duration=0.10, nbSteps=57)
# oui, mouseDragSides(65, duration=0.10, nbSteps=65)
