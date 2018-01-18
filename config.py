#-*-coding: utf-8;-*-
"""novel_editor.load_config
コンフィグのロード
"""

from json import dump, load
from os.path import exists, join, expanduser
from os import name, getenv, makedirs

from wx import TextEntryDialog, ID_CANCEL

default_wd = (join(getenv("APPDATA"), "frodo", "novedit")
              if name == 'nt' else expanduser("~/novedit"))

class Canceled(BaseException):
    pass

config = {
    "user": {
        "password": "",
        "mailaddr": ""
    },
    "post-to": ""
}

config_path = join(default_wd, ".neblob")

def load_config():
    global config
    if not exists(config_path):
        dialog = TextEntryDialog(None, "メールアドレスを入力してください。", "投稿元アドレスを設定")
        if dialog.ShowModal() == ID_CANCEL:
            raise Canceled()
        dialog.Destroy()
        res = dialog.GetValue()
        if not res:
            raise ValueError("空欄にはできません。")
        config["user"]["mailaddr"] = res

        dialog = TextEntryDialog(None, "パスワードを入力してください。", "投稿元アドレスのパスワードを設定")
        if dialog.ShowModal() == ID_CANCEL:
            raise Canceled()
        dialog.Destroy()
        res = dialog.GetValue()
        if not res:
            raise ValueError("空欄にはできません。")
        config["user"]["password"] = res

        dialog = TextEntryDialog(None, "投稿先メールアドレスを入力してください。", "投稿先アドレスを設定")
        if dialog.ShowModal() == ID_CANCEL:
            raise Canceled()
        dialog.Destroy()
        res = dialog.GetValue()
        if not res:
            raise ValueError("空欄にはできません。")
        config["post-to"] = res

        if not exists(default_wd):
            makedirs(default_wd)
        with open(config_path, 'w') as f:
            dump(config, f)
    else:
        with open(config_path) as f:
            config = load(f)
    return config
