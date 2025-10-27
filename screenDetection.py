from PIL import ImageGrab, Image
import attrs
import numpy
from screeninfo import get_monitors as getAvailableMonitors, Monitor

import matplotlib.pyplot as plt

# --------------
# screen
# --------------


@attrs.frozen
class ScreenRect():
    """oa rectangle on the monitor pixels space
    -> always relative to a monitor"""
    x: int
    y: int
    w: int
    h: int

    def getBbox(self, onMonitor: None | Monitor) -> tuple[int, int, int, int]:
        x = self.x
        y = self.y
        if onMonitor is not None:
            x += onMonitor.x
            y += onMonitor.y
        return (x, y, x + self.w, y + self.h)

    @staticmethod
    def fullScreen(monitor: Monitor | None = None) -> "ScreenRect":
        if monitor is None:
            monitor = SELECTED_MONITOR
        return ScreenRect(
            monitor.x, monitor.y, monitor.width, monitor.height)


def screeshot(rect: ScreenRect | None, rgbMode: bool,
              monitor: Monitor | None = None) -> Image.Image:
    monitor = getMonitor(monitor)
    if rect is None:
        bbox = ScreenRect.fullScreen(monitor).getBbox(None)
    else:
        bbox = rect.getBbox(monitor)
    screen = ImageGrab.grab(bbox=bbox)
    if rgbMode is False:
        screen = screen.convert("L")
    return screen

# --------------
# monitors
# --------------


AVAILABLE_MONITORS = getAvailableMonitors()
SELECTED_MONITOR = AVAILABLE_MONITORS[0]


def getMonitor(monitor: Monitor | None) -> Monitor:
    return monitor or SELECTED_MONITOR


def setMonitor(monitor: Monitor) -> None:
    global SELECTED_MONITOR
    SELECTED_MONITOR = monitor

# --------------
# interface
# --------------


@attrs.frozen
class InterfaceElements():
    monitor: Monitor
    board: ScreenRect
    nextPiece: ScreenRect

    @staticmethod
    def findElements(monitor: "Monitor|None" = None) -> "InterfaceElements":
        ...
