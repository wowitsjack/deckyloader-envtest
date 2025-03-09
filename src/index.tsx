import { definePlugin, staticClasses } from "@decky/ui";
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
