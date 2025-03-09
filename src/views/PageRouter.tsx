import React from "react";
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
