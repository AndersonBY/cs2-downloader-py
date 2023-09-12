# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-09-12 15:12:40
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-09-12 17:49:11
import os
import re
import json
from pathlib import Path

from translate import Translator

translator = Translator()
t = translator.t

with open("./config.json", "r") as f:
    config = json.load(f)

cs2_target_path = Path(config["cs2_target_path"])


class Patcher:
    @staticmethod
    def patch_client():
        steam_check_bytes = [b"\x75\x73\xFF\x15", b"\xEB\x73\xFF\x15"]
        version_check_bytes = [
            b"\x6C\x69\x6D\x69\x74\x65\x64\x62\x65\x74\x61",
            b"\x66\x75\x6C\x6C\x76\x65\x72\x73\x69\x6F\x6E",
            b"\x6C\x69\x6D\x69\x74\x65\x64\x62\x65\x74\x61",
            b"\x66\x75\x6C\x6C\x76\x65\x72\x73\x69\x6F\x6E",
        ]

        if not Patcher.replace_bytes(
            cs2_target_path / "game/csgo/bin/win64/client.dll", steam_check_bytes[0], steam_check_bytes[1]
        ):
            print(t("failed to patch steam check"))
            return False

        if not Patcher.replace_bytes(
            cs2_target_path / "game/csgo/bin/win64/client.dll",
            version_check_bytes[0],
            version_check_bytes[1],
        ) or not Patcher.replace_bytes(
            cs2_target_path / "game/csgo/bin/win64/client.dll",
            version_check_bytes[2],
            version_check_bytes[3],
        ):
            print(t("failed to patch version check"))
            return False

        return True

    @staticmethod
    def patch_server():
        clamp_check_bytes = [b"\x76\x59\xF2\x0F\x10\x4F\x3C", b"\xEB\x59\xF2\x0F\x10\x4F\x3C"]

        if not Patcher.replace_bytes(
            cs2_target_path / "game/csgo/bin/win64/server.dll",
            clamp_check_bytes[0],
            clamp_check_bytes[1],
        ):
            print(t("failed to patch movement clamp"))
            return False

        return True

    @staticmethod
    def clean_patch_files():
        for file in [
            cs2_target_path / "game/csgo/bin/win64/client.dll",
            cs2_target_path / "game/csgo/bin/win64/server.dll",
        ]:
            if os.path.exists(file):
                os.remove(file)

    @staticmethod
    def replace_bytes(filename, search_pattern, replace_bytes):
        with open(filename, "rb") as file:
            content = file.read()

        content = re.sub(search_pattern, replace_bytes, content)

        with open(filename, "wb") as file:
            file.write(content)

        return True
