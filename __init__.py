#-*-coding: utf-8;-*-
"""novel_editor
小説執筆用プログラム
"""

from wx import App

from .config import load_config
from .editor import NovelEditor

app: App = None
editor: NovelEditor = None

def init():
    global app
    app = App()

def main():
    global editor
    editor = NovelEditor(app)
    app.MainLoop()
