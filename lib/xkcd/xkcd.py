
from typing import Tuple, Optional

import requests
import json

from json_objects import json_obj

__all__ = [
    "XKCDComic"
]

XKCD_LATEST_URL = "https://xkcd.com/info.0.json"
XKCD_COMIC_NUM_URL = "https://xkcd.com/{}/info.0.json"

@json_obj
class XKCDComic:
    num: int
    img_url: str
    safe_title: str
    alt: str
    day: int
    month: int
    year: int
    title: str
    news: str
    link: str
    transcript: str
    extra_parts: dict

    def to_json(self):
        # "Override" to omit extra_parts if it is None
        json_dict = self.to_json_dict()
        
        if json_dict["extra_parts"] is None:
            del json_dict["extra_parts"]

        return json.dumps(json_dict)


def get_comic(num: Optional[int] = None) -> Tuple[Optional[XKCDComic], int]:
    comic = None
    response = None

    if num:
        response = requests.get(XKCD_COMIC_NUM_URL.format(num))
    else:
        response = requests.get(XKCD_LATEST_URL)
    

    if(response.status_code == 200):
        comic = XKCDComic.from_json_str(response.content)

    return (comic, response.status_code)