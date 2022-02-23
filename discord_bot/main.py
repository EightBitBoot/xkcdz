import requests
import json

unformatted_file = open("xkcd.json", "rt")
unformatted_content = "".join(unformatted_file.readlines())
unformatted_file.close()

unformatted_json = json.loads(unformatted_content)

formatted_file = open("xkcd_formatted.json", "wt+")
formatted_file.write(json.dumps(parsed_json, indent=4))
formatted_file.close()