# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-09-12 14:59:58
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-09-13 02:47:19
import asyncio

from translate import Translator

print("Please select your language:\nPress '1' for 'English' or '2' for 'Chinese' on your keyboard")
print("请选择您的语言：\n在您的键盘上按'1'选择'英语'或按'2'选择'中文'")
language = input("> ")
language = "en-US" if language == "1" else "zh-CN"
translator = Translator(language)
t = translator.t

from download import Downloader
from patcher import Patcher


async def main():
    needs_update = await Downloader.needs_update()

    if needs_update:
        print(t("update required, please press enter to download the update."))
        input("> ")
        await Downloader.update_installer()

    skip_download = input(t("Skip Download? (y/N)"))
    skip_download = skip_download.lower()
    if "n" in skip_download or len(skip_download) == 0:
        print(t("Preparing Download..."))
        await Downloader.prepare_download()
        print(t("Prepared Download!"))
        Patcher.clean_patch_files()
        print(t("Starting Download..."))
        await Downloader.download_cs2()

    print(t("Finished Download!. Starting Patches..."))
    print(t("Do you want to install client patch? (Y/n)"))
    need_patch = input("> ")
    if "y" in need_patch.lower() or len(need_patch) == 0:
        print(t("Starting Client Patch..."))
        Patcher.patch_client()

    print(
        t(
            "Do you want to install the Movement Patch?(This is recommended for bhop/surf servers for better movement) (y/N))"
        )
    )
    wants_movement_patch = input("> ").lower()
    if "y" in wants_movement_patch:
        print(t("Starting Movement Patch..."))
        Patcher.patch_server()

    print(t("Do you want to install Client-Mod Patches? (Y/n)"))
    need_patch = input("> ").lower()
    if "y" in need_patch or len(need_patch) == 0:
        print(t("Starting Client-Mod Patches..."))
        await Downloader.download_mods()
    print(t("Download complete! Press 'Enter' to close the installer!"))
    input("> ")


if __name__ == "__main__":
    asyncio.run(main())
