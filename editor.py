#-*-coding: utf-8;-*-
"""novel_editor.editor
エディタGUIクラス、関数定義
"""

from os.path import basename, expanduser
from threading import Timer

from wx import (EVT_MENU, EVT_TEXT, ID_CANCEL, ID_OK, OK, TE_MULTILINE, App,
                BoxSizer, FileSelector, Font, Frame, Menu, MenuBar, MessageBox,
                MessageDialog, StatusBar, TextCtrl, TextEntryDialog, ToolBar)
from wx.html2 import WebView

from .config import Canceled, load_config
from .mail import send
from .parsing import parse

BASETITLE = "小説エディタ(β)"

NoNewPara = [
    "　", "\t",
    "\v", " ",
    "「", "」",
    "（", "）",
    "【", "】",
    "〔", "〕",
    "『", "』",
    "◇", "◆",
    "□", "■",
    "○", "◎",
    "●", "◯"
    ]

class NovelEditor(Frame):
    def __init__(self, app: App):
        super(Frame, self).__init__(None)
        self.editor = TextCtrl(self, 101, style=TE_MULTILINE)
        self.SetTitle(f"{BASETITLE} - *Untitled*")
        self.SetSize(720, 540)
        self.File: str = None
        self.changed = False

        menubar: MenuBar = MenuBar()
        edit_menu: Menu = Menu()
        file_menu: Menu = Menu()

        edit_menu.Append(1, "&Preview\tCtrl+P")
        edit_menu.Append(2, "Post")
        edit_menu.AppendSeparator()
        edit_menu.Append(7, "&Ruby\tCtrl+R")
        edit_menu.Append(8, "&Paragraph\tCtrl+Space")

        file_menu.Append(3, "&New\tCtrl+N")
        file_menu.Append(4, "&Open\tCtrl+Shift+O")
        file_menu.AppendSeparator()
        file_menu.Append(5, "&Save as\tCtrl+Shift+S")
        file_menu.Append(6, "&Save\tCtrl+S")

        menubar.Append(file_menu, "&File")
        menubar.Append(edit_menu, "&Edit")

        self.SetMenuBar(menubar)
        self.Bind(EVT_MENU, self.Preview, id=1)
        self.Bind(EVT_MENU, self.Post, id=2)
        self.Bind(EVT_MENU, self.New, id=3)
        self.Bind(EVT_MENU, self.Open, id=4)
        self.Bind(EVT_MENU, self.SaveAs, id=5)
        self.Bind(EVT_MENU, self.Save, id=6)
        self.Bind(EVT_MENU, self.SetRuby, id=7)
        self.Bind(EVT_MENU, self.SetParagraphSpaces, id=8)

        self.pvframe = HideFrame(None, -1, "プレビュー")
        self.pvctrl: WebView = WebView.New(self.pvframe)
        self.Bind(EVT_TEXT, self.Reload, id=101)
        app.SetTopWindow(self)
        self.application = app
        self.Show()

    def SetRuby(self, e=None):
        slc = self.editor.GetSelection()
        if slc[0] == slc[1]:
            MessageBox("選択されたテキストがありません", "エラー", style=OK)
            return
        dialog = TextEntryDialog(None, "振り仮名を入力してください", "振り仮名を設定")
        if dialog.ShowModal() == ID_CANCEL:
            return
        dialog.Destroy()
        res = dialog.GetValue()
        if not res:
            MessageBox("空欄にはできません", "エラー", style=OK)
            return
        tmp = self.editor.GetValue()
        newlines = tmp[:slc[0]].count("\n")
        slc = slc[0] - newlines, slc[1] - newlines
        tmp = tmp[:slc[0]], tmp[slc[0]:slc[1]], tmp[slc[1]:]
        self.editor.SetValue(tmp[0] + f"|{tmp[1]}《{res}》" + tmp[2])

    def SetParagraphSpaces(self, e=None):
        self.editor.SetValue(
            "\n".join(
                [(l if l[0] in NoNewPara
                  else f"　{l}")
                 for l in self.editor.GetValue().splitlines()]))

    def Open(self, e=None):
        if self.changed:
            dlg = MessageDialog(
                self, "編集中の内容を保存して新規ファイルを作成しますか？",
                "新規ファイル")
            if dlg.ShowModal() == ID_OK:
                self.Save()
            dlg.Destroy()
        file = FileSelector("開くファイルを選択", expanduser('~'), "", "*.wnf")
        if not file:
            return
        self.File = file
        self.changed = False
        with open(self.File, encoding='utf-8') as f:
            self.editor.SetValue(f.read())
        self.SetTitle(f"{BASETITLE} - {basename(self.File)}")

    def New(self, e=None):
        if self.changed:
            dlg = MessageDialog(
                self, "編集中の内容を保存して新規ファイルを作成しますか？",
                "新規ファイル")
            if dlg.ShowModal() == ID_OK:
                self.Save()
            dlg.Destroy()
        self.changed = False
        self.File = None

    def Save(self, e=None):
        self.changed = False
        self.SetTitle(f"{BASETITLE} - {basename(self.File)}")
        if self.File:
            with open(self.File, 'w', encoding='utf-8') as f:
                f.write(self.editor.GetValue())
            return
        self.SaveAs()

    def SaveAs(self, e=None):
        file = FileSelector("保存します", expanduser('~'), "untitled.wnf", "wnf", "*.wnf")
        if not file:
            return
        self.File = file
        with open(self.File, 'w', encoding='utf-8') as f:
            f.write(self.editor.GetValue())
        self.changed = False
        self.SetTitle(f"{BASETITLE} - {basename(self.File)}")

    def Preview(self, e):
        self.pvctrl.SetPage(parse(self.editor.GetValue()), "")
        self.pvframe.Show()
        self.editor.SetFocus()

    def Reload(self, e):
        self.changed = True
        if self.File:
            self.SetTitle(f"{BASETITLE} - (変更){basename(self.File)}")
        self.pvctrl.SetPage(parse(self.editor.GetValue()), "")
        self.pvframe.Refresh()
        self.editor.SetFocus()

    def Post(self, e):
        try:
            load_config()
        except Canceled:
            return
        except ValueError as err:
            MessageBox(str(err), "エラー", style=OK)
            return
        dialog = TextEntryDialog(None, "小説のタイトルを設定してください", "小説タイトルを設定")
        dialog.ShowModal()
        dialog.Destroy()
        try:
            stat: StatusBar = self.CreateStatusBar()
            stat.SetStatusText("投稿中...")
            send(dialog.GetValue(), self.editor.GetValue(), lambda: _sent(stat))
        except ValueError as err:
            MessageBox(str(err), "エラー", style=OK)
            return

    def Destroy(self):
        self.application.ExitMainLoop()
        return True


def _sent(sbar: StatusBar):
    sbar.SetStatusText("投稿完了しました！")
    disposer = Timer(2, sbar.Destroy)
    disposer.start()

class HideFrame(Frame):
    def Destroy(self):
        self.Hide()
        return True
