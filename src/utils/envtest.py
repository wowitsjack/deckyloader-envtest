# coding: utf-8
"""
Decky EnvTest
A Decky plugin yoinks game-specifics from Decky's SteamClient.Apps and pulls Heroic configuration data.
It displays the results in a human-friendly, field-by-field layout can bounce it all out.
Repository: https://github.com/wowitsjack/deckyloader-envtest
"""

import os

folder = "envtest"

files = {
  # -------------------------
  # Backend stuff
  # -------------------------
  f"{folder}/main.py": r'''#!/usr/bin/env python
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
''',

  # -------------------------
  # Minimal decky.pyi thing.
  # -------------------------
  f"{folder}/decky.pyi": r'''"""
Decky Plugin Interface
Defines constants and helper functions for Decky plugins.
"""

version = "1.0.0"

import logging
from typing import Any

HOME: str
USER: str
DECKY_VERSION: str
DECKY_USER: str
DECKY_USER_HOME: str
DECKY_HOME: str
DECKY_PLUGIN_SETTINGS_DIR: str
DECKY_PLUGIN_RUNTIME_DIR: str
DECKY_PLUGIN_LOG_DIR: str
DECKY_PLUGIN_DIR: str
DECKY_PLUGIN_NAME: str
DECKY_PLUGIN_VERSION: str
DECKY_PLUGIN_AUTHOR: str
DECKY_PLUGIN_LOG: str

def migrate_any(target_dir: str, *files_or_directories: str) -> dict[str, str]:
    return {}

def migrate_settings(*files_or_directories: str) -> dict[str, str]:
    return {}

def migrate_runtime(*files_or_directories: str) -> dict[str, str]:
    return {}

def migrate_logs(*files_or_directories: str) -> dict[str, str]:
    return {}

logger: logging.Logger

async def emit(event: str, *args: Any) -> None:
    pass
''',

  # -------------------------
  # ESLint config files.
  # -------------------------
  f"{folder}/eslint.config.js": r'''import pluginJs from "@eslint/js";
import tseslint from "typescript-eslint";
import pluginReact from "eslint-plugin-react";
import stylistic from "@stylistic/eslint-plugin";

export default [
  { ignores: ["dist/"] },
  { settings: { react: { version: "18.3" } } },
  stylistic.configs.customize({ indent: 2, quotes: "double", semi: true, jsx: true }),
  pluginJs.configs.recommended,
  ...tseslint.configs.recommended,
  pluginReact.configs.flat.recommended,
  {
    files: ["src/**/.{js,mjs,cjs,ts,jsx,tsx}"],
    rules: { "react/react-in-jsx-scope": "off" }
  }
];
''',

  # -------------------------
  # Frontend/Backend caller thinger
  # -------------------------
  f"{folder}/src/utils/backend.ts": r'''import { callable } from "@decky/api";

const debugLog = callable<[ { appid: number, additional?: any } ], { status: string, log?: string }>("debug_log");
const pullHeroicData = callable<[ { appname: string } ], { status: string, data?: any, message?: string }>("pull_heroic_data");

export class Backend {
  static async debugLog(appid: number, additional?: any): Promise<{ status: string, log?: string }> {
    return await debugLog({ appid, additional });
  }
  static async pullHeroicData(appname: string): Promise<{ status: string, data?: any, message?: string }> {
    return await pullHeroicData({ appname });
  }
}

export {};
''',

  # -------------------------
  # Button Badger thinger
  # -------------------------
  f"{folder}/src/components/ChooChooModeBadge.tsx": r'''import React, { useState } from "react";
import { Navigation } from "@decky/ui";
import { Backend } from "../utils/backend";

// We only declare SteamClient here. Decky UI already defines 'appStore'.
declare global {
  interface Window {
    SteamClient?: {
      Apps?: {
        GetAppDetails?: (appid: number) => any;
        GetInstalledApps?: () => any[];
        GetGameVersion?: (appid: number) => string;
        GetGameActionStatus?: (appid: number) => any;
      };
    };
  }
}
export {};

const PrettyJSON: React.FC<{ data: any }> = ({ data }) => {
  if (typeof data !== "object" || data === null) return <div>{String(data)}</div>;
  return (
    <div>
      {Object.entries(data).map(([key, value]) => (
        <div key={key} style={{ marginBottom: "10px", borderBottom: "1px solid #444", paddingBottom: "4px" }}>
          <div style={{ fontWeight: "bold", color: "#ffcc00", marginBottom: "4px" }}>{key}</div>
          <div style={{ marginLeft: "10px" }}>
            {typeof value === "object" ? <PrettyJSON data={value} /> : String(value)}
          </div>
        </div>
      ))}
    </div>
  );
};

async function getGameInfo(appid: number): Promise<any> {
  let info: any = {};
  try {
    if (window.SteamClient && window.SteamClient.Apps) {
      if (typeof window.SteamClient.Apps.GetAppDetails === "function") {
        info.GetAppDetails = window.SteamClient.Apps.GetAppDetails(appid) || {};
      }
      if (typeof window.SteamClient.Apps.GetInstalledApps === "function") {
        info.InstalledApps = window.SteamClient.Apps.GetInstalledApps() || [];
      }
      if (typeof window.SteamClient.Apps.GetGameVersion === "function") {
        info.GameVersion = window.SteamClient.Apps.GetGameVersion(appid) || "Not available";
      }
      if (typeof window.SteamClient.Apps.GetGameActionStatus === "function") {
        info.GameActionStatus = window.SteamClient.Apps.GetGameActionStatus(appid) || "Not available";
      }
    }
    // Now we can directly reference window.appStore from the Decky UI definitions (no re-declaration needed).
    if (window.appStore && typeof window.appStore.GetAppOverviewByAppID === "function") {
      info.AppOverview = window.appStore.GetAppOverviewByAppID(appid) || {};
    }
  } catch (e: any) {
    info.error = e.toString();
  }
  return info;
}

const ChooChooModeBadge: React.FC<{ appid: number; appName: string }> = ({ appid, appName }) => {
  const [flashing, setFlashing] = useState(false);
  const [logData, setLogData] = useState("");
  const [cleanData, setCleanData] = useState<any>(null);
  const [heroicData, setHeroicData] = useState<any>(null);

  const handleDebugClick = async () => {
    setFlashing(true);
    setTimeout(() => setFlashing(false), 500);
    try {
      const gameInfo = await getGameInfo(appid);
      const result = await Backend.debugLog(appid, gameInfo);
      setLogData(result.log || "No log data returned");
      try {
        const parsed = JSON.parse(result.log || "{}");
        const unwantedKeys = [
          "review_score_with_bombs",
          "review_percentage_with_bombs",
          "review_score_without_bombs",
          "review_percentage_without_bombs"
        ];
        const filtered = Object.fromEntries(
          Object.entries(parsed.game_info || {}).filter(([k, v]) => !unwantedKeys.includes(k) && v !== 0 && v !== "0")
        );
        setCleanData(filtered);
      } catch (err) {
        setCleanData({ error: "Could not parse log data" });
      }
    } catch (error) {
      console.error("Error logging game data:", error);
    }
  };

  const handleHeroicClick = async () => {
    let displayName = appName;
    try {
      const gameInfo = await getGameInfo(appid);
      if (gameInfo && gameInfo.AppOverview && gameInfo.AppOverview.display_name) {
        displayName = gameInfo.AppOverview.display_name;
      }
    } catch (e) {
      console.error("Error fetching game info for heroic data:", e);
    }
    try {
      const result = await Backend.pullHeroicData(displayName);
      if (result.status === "success") {
        setHeroicData(result.data);
      } else {
        setHeroicData({ error: result.message || "Error pulling heroic data" });
      }
    } catch (error) {
      console.error("Error pulling heroic data:", error);
      setHeroicData({ error: String(error) });
    }
  };

  const handleExport = () => {
    if (!logData) return;
    const blob = new Blob([logData], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `game_info_${appid}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div
        onClick={handleDebugClick}
        style={{
          padding: "6px 12px",
          borderRadius: "4px",
          cursor: "pointer",
          backgroundColor: flashing ? "green" : "gold",
          color: "black",
          fontWeight: "bold",
          textAlign: "center",
          display: "inline-block",
          transition: "background-color 0.3s",
          marginBottom: "0.5em"
        }}
      >
        DEBUG: Log Game Data
      </div>
      <div
        onClick={handleHeroicClick}
        style={{
          padding: "6px 12px",
          borderRadius: "4px",
          cursor: "pointer",
          backgroundColor: "#007acc",
          color: "white",
          fontWeight: "bold",
          textAlign: "center",
          display: "inline-block",
          transition: "opacity 0.3s",
          marginBottom: "0.5em"
        }}
      >
        Pull Heroic Data
      </div>
      {cleanData && (
        <>
          <div style={{ marginBottom: "0.5em", fontSize: "1em", fontWeight: "bold" }}>
            Cleaned Game Info
          </div>
          <div
            style={{
              textAlign: "left",
              backgroundColor: "#222",
              color: "#fff",
              padding: "1em",
              borderRadius: "4px",
              maxHeight: "250px",
              overflowY: "auto",
              fontFamily: "monospace"
            }}
          >
            <PrettyJSON data={cleanData} />
          </div>
        </>
      )}
      {heroicData && (
        <>
          <div style={{ marginBottom: "0.5em", fontSize: "1em", fontWeight: "bold", marginTop: "1em" }}>
            Heroic Data
          </div>
          <div
            style={{
              textAlign: "left",
              backgroundColor: "#222",
              color: "#fff",
              padding: "1em",
              borderRadius: "4px",
              maxHeight: "250px",
              overflowY: "auto",
              fontFamily: "monospace"
            }}
          >
            <PrettyJSON data={heroicData} />
          </div>
        </>
      )}
      {logData && (
        <>
          <div style={{ marginBottom: "0.5em", fontSize: "0.9em", fontWeight: "bold", marginTop: "1em" }}>
            Raw Log JSON
          </div>
          <div
            style={{
              textAlign: "left",
              backgroundColor: "#333",
              color: "#fff",
              padding: "1em",
              borderRadius: "4px",
              maxHeight: "300px",
              overflowY: "auto",
              fontFamily: "monospace"
            }}
          >
            <pre style={{ margin: 0 }}>{logData}</pre>
          </div>
          <div style={{ marginTop: "0.5em" }}>
            <button
              onClick={handleExport}
              style={{
                padding: "4px 8px",
                borderRadius: "4px",
                cursor: "pointer",
                backgroundColor: "#007acc",
                color: "#fff",
                border: "none"
              }}
            >
              Export JSON
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ChooChooModeBadge;
''',

  # -------------------------
  # PageRouter.tsx
  # -------------------------
  f"{folder}/src/views/PageRouter.tsx": r'''import React from "react";
import ChooChooModeBadge from "../components/ChooChooModeBadge";

const PageRouter: React.FC = () => {
  const parts = window.location.pathname.split("/");
  const appid = parseInt(parts[parts.length - 1], 10) || 0;
  
  return (
    <div style={{ padding: "1em", textAlign: "center" }}>
      <h2 style={{ marginBottom: "0.5em" }}>Decky EnvTest</h2>
      <p style={{ marginBottom: "1em" }}>AppID: {appid}</p>
      <ChooChooModeBadge appid={appid} appName={appid.toString()} />
    </div>
  );
};

export default PageRouter;
''',

  # -------------------------
  # main reg index.tsx
  # -------------------------
  f"{folder}/src/index.tsx": r'''import { definePlugin, staticClasses } from "@decky/ui";
import { FaBug } from "react-icons/fa";
import { routerHook } from "@decky/api";
import PageRouter from "./views/PageRouter";

export default definePlugin(() => {
  routerHook.addRoute("/debug/:appid", PageRouter, { exact: true });
  return {
    title: <div className={staticClasses.Title}>Decky EnvTest</div>,
    content: <PageRouter />,
    icon: <FaBug />,
    onDismount() {
      routerHook.removeRoute("/debug/:appid");
    }
  };
});
''',

  # -------------------------
  # working tsconfig.json
  # -------------------------
  f"{folder}/tsconfig.json": r'''{
  "compilerOptions": {
    "outDir": "dist",
    "module": "ESNext",
    "target": "ES2020",
    "jsx": "react",
    "jsxFactory": "window.SP_REACT.createElement",
    "jsxFragmentFactory": "window.SP_REACT.Fragment",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "resolveJsonModule": true,
    "types": ["react", "react-dom"]
  },
  "include": ["src"],
  "exclude": ["node_modules"]
}
''',

  # -------------------------
  # Rollup configs
  # -------------------------
  f"{folder}/rollup.config.js": r'''import deckyPlugin from "@decky/rollup";
export default deckyPlugin({});
''',

  # -------------------------
  # package.json
  # -------------------------
  f"{folder}/package.json": r'''{
  "name": "decky-envtest",
  "type": "module",
  "version": "0.1.0",
  "main": "main.py",
  "description": "Decky EnvTest is a debugging tool by wowitsjack that logs game-specific details from Decky's SteamClient.Apps and pulls Heroic configuration data. It displays the cleaned data in a clear, field-by-field layout with export options.",
  "scripts": {
    "build": "rollup -c",
    "watch": "rollup -c -w"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/wowitsjack/deckyloader-envtest"
  },
  "keywords": [
    "decky",
    "plugin",
    "envtest",
    "debug",
    "logging",
    "steam"
  ],
  "author": "wowitsjack",
  "license": "GPL-3.0-or-later",
  "devDependencies": {
    "@decky/rollup": "^1.0.1",
    "@decky/ui": "^4.9.1",
    "rollup": "^4.34.9",
    "typescript": "^5.8.2",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0"
  },
  "dependencies": {
    "@decky/api": "^1.1.2",
    "react-icons": "^5.5.0"
  }
}
''',

  # -------------------------
  # plugin.json
  # -------------------------
  f"{folder}/plugin.json": r'''{
  "name": "Decky EnvTest",
  "author": "wowitsjack",
  "flags": [],
  "api_version": 1,
  "publish": {
    "tags": ["envtest", "debug", "logging", "steam"],
    "description": "Decky EnvTest is a debugging tool by wowitsjack that pulls game-specific details via Decky's SteamClient.Apps and Heroic configuration files, then displays the cleaned data in a user-friendly layout with export options.",
    "image": "https://github.com/wowitsjack/deckyloader-envtest/raw/main/icon.png"
  }
}
''',

  # -------------------------
  # pnpm-lock.yaml
  # -------------------------
  f"{folder}/pnpm-lock.yaml": r'''lockfileVersion: '9.0'
settings:
  autoInstallPeers: true
  excludeLinksFromLockfile: false
importers:
  .:
    dependencies:
      "@decky/api": { specifier: "^1.1.2", version: "1.1.2" },
      "react-icons": { specifier: "^5.5.0", version: "5.5.0" }
    devDependencies:
      "@decky/rollup": { specifier: "^1.0.1", version: "1.0.1" },
      "@decky/ui": { specifier: "^4.9.1", version: "4.9.1" }
'''
}

def create_files(file_dict):
    for filepath, content in file_dict.items():
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"Created directory: {directory}")
            except Exception as e:
                print(f"Failed to create directory {directory}: {e}")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"File {filepath} written successfully.")
        except Exception as e:
            print(f"Could not write file {filepath}: {e}")

if __name__ == "__main__":
    create_files(files)
    print(f"Decky EnvTest plugin structure generated in the '{folder}' directory. Enjoy debugging!")
