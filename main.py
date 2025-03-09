#!/usr/bin/env python
# coding: utf-8
"""
Decky EnvTest (Backend)
Logs game-specific details (provided by the frontend) and pulls Heroic configuration data.
The debug_log function logs the game info passed from the frontend.
The pull_heroic_data function loads and parses the Heroic config and library files,
then filters the library JSON to only return the entry whose "title" matches the provided display name.
Both are appended to a log file named "log-YYYYMMDD.log" in DECKY_PLUGIN_LOG_DIR (or ~/choochoo).
"""

import os
import sys
import json
import datetime
import logging

import decky

logger = decky.logger
logger.setLevel(logging.DEBUG)

LOG_DIR = os.environ.get("DECKY_PLUGIN_LOG_DIR", os.path.join(os.path.expanduser("~"), "choochoo"))
try:
    os.makedirs(LOG_DIR, exist_ok=True)
    os.chmod(LOG_DIR, 0o700)
except Exception as e:
    logger.error(f"Error creating log directory {LOG_DIR}: {e}")

def get_log_file_path() -> str:
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    return os.path.join(LOG_DIR, f"log-{date_str}.log")

def collect_debug_data(appid: int, additional_data=None) -> dict:
    data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "appid": appid,
        "game_info": additional_data if additional_data is not None else "No game info provided"
    }
    return data

def debug_log(appid: int, extra_data=None) -> str:
    debug_info = collect_debug_data(appid, additional_data=extra_data)
    written_data = json.dumps(debug_info, indent=2)
    log_file = get_log_file_path()
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(written_data + "\n")
        logger.info(f"Logged game data to {log_file}")
    except Exception as e:
        logger.error(f"Error writing to log file {log_file}: {e}")
    return written_data

def pull_heroic_data(appname: str) -> dict:
    data = {"timestamp": datetime.datetime.now().isoformat(), "appname": appname}
    try:
        # Determine the path for the Heroic configuration file.
        if appname.isdigit():
            config_path = os.path.join(os.path.expanduser("~"), ".config", "Heroic", "GameConfig", f"{appname}.json")
        else:
            config_path = os.path.join(os.path.expanduser("~"), ".var", "app", "com.heroicgameslauncher.hgl",
                                       "config", "heroic", "GamesConfig", f"{appname}.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                heroic_config = json.load(f)
            data["heroic_config"] = heroic_config
        else:
            data["heroic_config"] = "Not found"

        # Read the Heroic library file.
        lib_path = os.path.join(os.path.expanduser("~"), ".var", "app", "com.heroicgameslauncher.hgl",
                                "config", "heroic", "sideload_apps", "library.json")
        if os.path.exists(lib_path):
            with open(lib_path, "r", encoding="utf-8") as f:
                library_data = json.load(f)
            # Filter the library JSON to only include the game whose title matches the provided display name
            # (case-insensitive).
            if isinstance(library_data, dict) and "games" in library_data:
                filtered_games = [
                    game for game in library_data["games"]
                    if game.get("title", "").strip().lower() == appname.strip().lower()
                ]
                data["heroic_library"] = {"games": filtered_games} if filtered_games else "Not found"
            else:
                data["heroic_library"] = library_data
        else:
            data["heroic_library"] = "Not found"

    except Exception as e:
        data["error"] = str(e)
    return data

class Plugin:
    @classmethod
    async def _main(cls):
        logger.info("[backend] Decky EnvTest loaded.")

    @classmethod
    async def _unload(cls):
        logger.info("[backend] Decky EnvTest unloaded.")

    @classmethod
    async def debug_log(cls, data):
        try:
            appid = data.get("appid", 0)
            extra = data.get("additional", {})
            log_output = debug_log(appid, extra)
            return {"status": "success", "log": log_output}
        except Exception as e:
            logger.error(f"Error in debug_log: {e}")
            return {"status": "error", "message": str(e)}

    @classmethod
    async def pull_heroic_data(cls, data):
        try:
            appname = data.get("appname", "")
            heroic = pull_heroic_data(appname)
            return {"status": "success", "data": heroic}
        except Exception as e:
            logger.error(f"Error in pull_heroic_data: {e}")
            return {"status": "error", "message": str(e)}
