#-*-coding: utf-8;-*-
"""novel_editor.editor
エディタGUIクラス、関数定義
"""

import re
from functools import wraps

BEGIN = "《"
END = "》"

def html(func):
    @wraps(func)
    def _wrap(text):
        ret = f"<html><body>{func(text)}</body></html>"
        #print(ret)
        return ret
    return _wrap

@html
def parse(text):
    return re.sub(fr"\|([^{BEGIN}]*?){BEGIN}([^{END}]*?){END}",
                  r"<ruby>\1<rt>\2</rt></ruby>",
                  text.replace("\r", "").replace("\n", "<br />"))
