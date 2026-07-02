from railui.core.ast import RawJS
from railui.all import *

user_store = createStore({
    "name": "Alice Developer",
    "role": "Admin",
    "is_logged_in": True
})

def persist():
    return RawJS(f"sessionStorage.setItem('user_store', JSON.stringify({user_store.toJSON()}))")
