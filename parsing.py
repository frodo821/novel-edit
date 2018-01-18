#-*-coding: utf-8;-*-
"""novel_editor.editor
エディタGUIクラス、関数定義
"""

import re
from functools import wraps
from os.path import join, dirname

from .config import default_wd

BEGIN = "《"
END = "》"

assets = join(dirname(__file__), "assets")

def html(func):
    @wraps(func)
    def _wrap(text):
        ret = f"""<!doctype html>
<html>
    <head>
        <title>Preview</title>
        <link rel="stylesheet" href="{join(assets, "default.css")}" type="text/css"/>
    </head>
    <body>
        {func(text)}
    </body>
</html>"""
        #print(ret)
        return ret
    return _wrap

@html
def parse(text):
    return re.sub(fr"\|([^{BEGIN}]*?){BEGIN}([^{END}]*?){END}",
                  r"<ruby>\1<rt>\2</rt></ruby>",
                  text.replace("\r", "").replace("\n", "<br />"))
