# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-09-12 15:02:02
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-09-12 19:23:55
import re
import os
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path

import httpx

from translate import Translator

translator = Translator()
t = translator.t

with open("./config.json", "r") as f:
    config = json.load(f)


def get_proxy():
    http_proxy_host_re = re.compile(r"http.*://(.*?)$")
    system_proxies = urllib.request.getproxies()
    proxies = {}
    for protocol, proxy in system_proxies.items():
        http_proxy_host = http_proxy_host_re.findall(proxy)
        if not http_proxy_host:
            continue
        proxy_url = f"http://{http_proxy_host[0]}"
        proxies[f"{protocol}://"] = proxy_url
    return proxies


class Downloader:
    steam_downloader_v2_path = Path("./SteamDownloaderV2")
    proxies = get_proxy()

    @staticmethod
    async def download_file(url, output_file):
        try:
            async with httpx.AsyncClient(follow_redirects=True, proxies=Downloader.proxies) as client:
                response = await client.get(url)
                response.raise_for_status()
                with open(output_file, "wb") as f:
                    f.write(response.content)
        except Exception as e:
            print(t("Error while downloading"), url, str(e))

    @staticmethod
    async def read_online_string(url):
        async with httpx.AsyncClient(follow_redirects=True, proxies=Downloader.proxies) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    @staticmethod
    async def needs_update():
        version_string = await Downloader.read_online_string(f"{config['resources_base_url']}version.txt")
        latest_version = re.search(r"current_version = \"(.*)\"", version_string).group(1)
        return config["current_version"] != latest_version

    @staticmethod
    async def update_installer():
        current_app_path = Path(os.getcwd())
        await Downloader.download_file(
            f"{config['resources_base_url']}cs2-downloader-py.zip",
            current_app_path / "cs2-downloader-py.zip",
        )

    @staticmethod
    async def prepare_download():
        download_link = f"{config['resources_base_url']}depot_keys.json"
        download_path = Downloader.steam_downloader_v2_path / "depot_keys.json"
        await Downloader.download_file(download_link, download_path)

        with open(download_path, "r") as f:
            depot_keys = json.load(f)

        manifest_names = [f"730_{depot_id}" for depot_id in depot_keys]
        manifest_folder = Downloader.steam_downloader_v2_path / "manifests"
        for name in manifest_names:
            download_link = f"{config['resources_base_url']}{name}"
            download_path = manifest_folder / name
            await Downloader.download_file(download_link, download_path)

    @staticmethod
    async def download_cs2():
        manifest_folder = Downloader.steam_downloader_v2_path / "manifests"
        depot_keys = Downloader.steam_downloader_v2_path / "depot_keys.json"
        exe_path = Downloader.steam_downloader_v2_path / "SteamDownloader.exe"
        cmd = f"{exe_path.absolute()} --target {config['cs2_target_path']} --manifests {manifest_folder.absolute()} --depot_keys {depot_keys.absolute()}"
        subprocess.run(cmd, shell=True)

    @staticmethod
    async def download_mods():
        cs2_target_path = Path(config["cs2_target_path"])
        github_paths = [
            "https://github.com/CS2-OOF-LV/CS2-Client-Files/raw/main/Mod%20Loading%20Files/game/csgo_mods/pak01_000.vpk",
            "https://github.com/CS2-OOF-LV/CS2-Client-Files/raw/main/Mod%20Loading%20Files/game/csgo_mods/pak01_dir.vpk",
            "https://raw.githubusercontent.com/CS2-OOF-LV/CS2-Client-Files/main/Mod%20Loading%20Files/game/csgo/gameinfo.gi",
            "https://raw.githubusercontent.com/CS2-OOF-LV/CS2-Client-Files/main/Mod%20Loading%20Files/game/csgo/scripts/vscripts/banList.lua",
            "https://github.com/CS2-OOF-LV/CS2-Client-Files/raw/main/Mod%20Loading%20Files/Start%20Game%20(English)%20-%20DEBUG.bat",
            "https://github.com/CS2-OOF-LV/CS2-Client-Files/raw/main/Mod%20Loading%20Files/Start%20Game%20(English).bat",
            "https://github.com/CS2-OOF-LV/CS2-Client-Files/raw/main/Mod%20Loading%20Files/Start%20Server.bat",
            "https://github.com/CS2-OOF-LV/CS2-Client-Files/raw/main/Mod%20Loading%20Files/Workshop%20Tools%20-%20RAYTRACING.bat",
            "https://github.com/CS2-OOF-LV/CS2-Client-Files/raw/main/Mod%20Loading%20Files/Workshop%20Tools.bat",
            f"{config['resources_base_url']}启动CS2.bat",
        ]

        file_paths = [
            cs2_target_path / "game" / "csgo_mods" / "pak01_000.vpk",
            cs2_target_path / "game" / "csgo_mods" / "pak01_dir.vpk",
            cs2_target_path / "game" / "csgo" / "gameinfo.gi",
            cs2_target_path / "game" / "csgo" / "scripts" / "vscripts" / "banList.lua",
            cs2_target_path / "Start Game (English) - DEBUG.bat",
            cs2_target_path / "Start Game (English).bat",
            cs2_target_path / "Start Server.bat",
            cs2_target_path / "Workshop Tools - RAYTRACING.bat",
            cs2_target_path / "Workshop Tools.bat",
            cs2_target_path / "启动CS2.bat",
        ]

        replace_exception_list = ["banList.lua"]

        # delete the mods folder so that all older modifications get deleted
        shutil.rmtree(cs2_target_path / "game" / "csgo_mods", ignore_errors=True)

        # Create needed folders
        os.makedirs(cs2_target_path / "game" / "csgo_mods", exist_ok=True)
        os.makedirs(cs2_target_path / "game" / "csgo" / "scripts", exist_ok=True)
        os.makedirs(cs2_target_path / "game" / "csgo" / "scripts" / "vscripts", exist_ok=True)
        os.makedirs(cs2_target_path / "game" / "bin" / "win64", exist_ok=True)

        # download files to specific directories
        for github_path, file_path in zip(github_paths, file_paths):
            if file_path not in replace_exception_list and os.path.exists(file_path):
                os.remove(file_path)
            await Downloader.download_file(github_path, file_path)
