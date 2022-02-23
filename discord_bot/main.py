import requests
import json
import io

with open("xkcd.json", "r+") as unformatted_file:
    json_data = json.loads("".join(unformatted_file.readlines()))
    unformatted_file.truncate(0)
    unformatted_file.seek(0, io.SEEK_SET)
    unformatted_file.write(json.dumps(json_data))