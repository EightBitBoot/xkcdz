
__all__ = [
    "XKCDComic"
]

class XKCDComic:
    def __init__(self, num, img_url, safe_title, alt, day, month, year, title, news, link, transcript):
        self.num = num
        self.img_url = img_url
        self.safe_title = safe_title
        self.alt = alt
        self.day = day
        self.month = month
        self.year = year
        self.title = title
        self.news = news
        self.link = link
        self.transcript = transcript

    @classmethod
    def from_parsed_json(cls, parsed_json):
        num        = parsed_json["num"]        if "num"        in parsed_json else None   
        img_url    = parsed_json["img_url"]    if "img_url"    in parsed_json else None   
        safe_title = parsed_json["safe_title"] if "safe_title" in parsed_json else None   
        alt        = parsed_json["alt"]        if "alt"        in parsed_json else None   
        day        = parsed_json["day"]        if "day"        in parsed_json else None   
        month      = parsed_json["month"]      if "month"      in parsed_json else None   
        year       = parsed_json["year"]       if "year"       in parsed_json else None   
        title      = parsed_json["title"]      if "title"      in parsed_json else None   
        news       = parsed_json["news"]       if "news"       in parsed_json else None   
        link       = parsed_json["link"]       if "link"       in parsed_json else None   
        transcript = parsed_json["transcript"] if "transcript" in parsed_json else None   