from datetime import datetime,date
from functools import partial

try:
    import misaka
except ImportError:
    import markdown as __markdown
    _markdown = partial(__markdown.markdown,safe_mode=True)
else:
    _markdown = partial(misaka.html,render_flags=misaka.HTML_SKIP_HTML)

def markdown(text):
    return _markdown(text)

def nicedate(dt):
    """ a human readable date"""
    # TODO: expand on this to include timedeltas and other things.
    if dt.date() == date.today():
        return dt.strftime("Today %H:%M")
    elif dt.year != datetime.now().year:
        return dt.strftime("%a, %d. %b %Y %H:%M")
    else:
        return dt.strftime("%a, %d. %b %H:%M")

filters = [markdown,nicedate]
