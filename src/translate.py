# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-09-12 17:33:29
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-09-12 17:47:27
import json


with open("translations.json", "r") as f:
    translation_data = json.load(f)


class Translator:
    def __init__(self, language=None):
        with open("./config.json", "r") as f:
            config = json.load(f)
        if language is not None:
            self.language = config["language"] = language
            with open("./config.json", "w") as f:
                json.dump(config, f, indent=4)
        else:
            self.language = config["language"]

    def t(self, key: str):
        return translation_data[self.language].get(key, key)
