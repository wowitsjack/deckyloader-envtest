import { callable } from "@decky/api";

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
