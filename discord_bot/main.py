import requests
import json

current_comic_res = requests.get("https://xkcd.com/info.0.json")
current_comic_json = json.loads(current_comic_res.content.decode("ascii"))
current_comic_num = current_comic_json["num"]

data_file = open("data.json", "at+")
data_file.write("[\n")

for comic_num in range(0, current_comic_num + 1):
    url = "https://xkcd.com/{}/info.0.json".format(comic_num)
    comic_res = requests.get(url)

    if comic_res.status_code == 200:
        data_file.write(comic_res.content.decode("ascii") + ",\n")
    else:
        print("{}: {}".format(url, comic_res.status_code))

data_file.write("]")
data_file.close()