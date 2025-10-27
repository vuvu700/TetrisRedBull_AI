from PIL import ImageGrab, Image
import attrs
import numpy
from screeninfo import get_monitors as getAvailableMonitors, Monitor
from typing import Literal

import matplotlib.pyplot as plt

# --------------
# screen
# --------------


@attrs.frozen
class Rect():
    """oa rectangle on the monitor pixels space
    -> always relative to a monitor"""
    x: int
    y: int
    w: int
    h: int

    def getBbox(self, onMonitor: Literal[False] | Monitor) -> tuple[int, int, int, int]:
        """-> (left, upper, right, lower)"""
        x = self.x
        y = self.y
        if onMonitor is not False:
            x += onMonitor.x
            y += onMonitor.y
        return (x, y, x + self.w, y + self.h)

    @staticmethod
    def fullScreen(monitor: Monitor | None = None) -> "Rect":
        if monitor is None:
            monitor = SELECTED_MONITOR
        return Rect(
            monitor.x, monitor.y, monitor.width, monitor.height)


def screeshotRaw(rect: Rect, rgbMode: bool) -> Image.Image:
    bbox = rect.getBbox(False)
    screen = ImageGrab.grab(bbox=bbox, all_screens=True)
    if rgbMode is False:
        screen = screen.convert("L")
    return screen

def screeshot(rect: Rect | None, rgbMode: bool,
              monitor: Monitor | None = None) -> Image.Image:
    monitor = getMonitor(monitor)
    if rect is None:
        bbox = Rect.fullScreen(monitor).getBbox(False)
    else:
        bbox = rect.getBbox(monitor)
    screen = ImageGrab.grab(bbox=bbox, all_screens=True)
    if rgbMode is False:
        screen = screen.convert("L")
    return screen

# --------------
# monitors
# --------------


AVAILABLE_MONITORS = getAvailableMonitors()

def getMonitor(monitor: Monitor | None) -> Monitor:
    return monitor or SELECTED_MONITOR


def setMonitor(monitor: Monitor) -> None:
    global SELECTED_MONITOR
    SELECTED_MONITOR = monitor

# --------------
# interface
# --------------


@attrs.frozen
class InterfaceImages():
    fullInterface: Image.Image
    board: Image.Image
    nextPiece: Image.Image
    score: Image.Image
    timer: Image.Image
    multText: Image.Image
    multBarre: Image.Image
    canBarre: Image.Image
    memory: Image.Image

@attrs.frozen
class InterfaceConfig():
    fullInterface: Rect
    """all rects of elements will be relative to it"""
    board: Rect
    nextPiece: Rect
    score: Rect
    timer: Rect
    multText: Rect
    multBarre: Rect
    canBarre: Rect
    memory: Rect
    comments: str
    
    def __extract(self, img:Image.Image, rect:Rect)->Image.Image:
        return img.crop(rect.getBbox(False))
    
    def cutScreen(self, screen:Image.Image)->"InterfaceImages":
        return InterfaceImages(
            fullInterface=screen,
            board=self.__extract(screen, self.board),
            nextPiece=self.__extract(screen, self.nextPiece),
            score=self.__extract(screen, self.score),
            timer=self.__extract(screen, self.timer),
            multText=self.__extract(screen, self.multText),
            multBarre=self.__extract(screen, self.multBarre),
            canBarre=self.__extract(screen, self.canBarre),
            memory=self.__extract(screen, self.memory))



ALL_INTERFACES = [
    InterfaceConfig(
        fullInterface=Rect(690, 130, 508, 910),
        board=Rect(92, 101, 357, 716),
        nextPiece=Rect(393, 9, 103, 59),
        score=Rect(364, 854, 144, 53),
        timer=Rect(217, 847, 108, 55),
        multText=Rect(4, 94, 66, 60),
        multBarre=Rect(42, 162, 22, 652),
        canBarre=Rect(476, 162, 22, 652),
        memory=Rect(51, 11, 99, 57),
        comments="""personal computer: done with 1000x1000 device in full screen"""),
]


# ----------------------------
# select the elements to use
# ----------------------------

SELECTED_INTERFACE = ALL_INTERFACES[0]
SELECTED_MONITOR = AVAILABLE_MONITORS[1]
