import React, { useState } from "react";
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
