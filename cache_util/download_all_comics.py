#!/usr/bin/env python

import json
import io

import requests

XKCD_CACHE_PATH = "../xkcd_cache/"

def load_comics():
    xkcd_info = None
    with open(XKCD_CACHE_PATH + "xkcd.json", "r") as json_file:
        xkcd_info = json.loads("".join(json_file.readlines()))

    return xkcd_info


def main():
    xkcd_info = load_comics()

    for comic in xkcd_info[1606:]:
        if comic["img"][-4:-3] == ".":
            # "comic["img"][-4]" is the image file extension from the metadata
            with open("{}/comics/{}{}".format(XKCD_CACHE_PATH, comic["num"], comic["img"][-4:]), "w+b") as image_file:
                print("{}: ".format(comic["num"]), end="")
                image_data = requests.get(comic["img"]).content
                image_file.write(image_data)
                print("Done")


if __name__ == "__main__":
    main()