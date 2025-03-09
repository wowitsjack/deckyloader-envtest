# Decky EnvTest

Decky EnvTest is a debugging tool designed for the Decky platform. It logs game-specific details sourced from Decky's SteamClient.Apps and pulls configuration data from Heroic. 

The plugin then displays both raw and cleaned data in a user-friendly, field-by-field layout, with export options for further analysis.

## Features

- **Game Data Logging:** Captures detailed game information provided by the Decky frontend.
- **Heroic Data Retrieval:** Pulls and parses configuration data and the Heroic library, filtering for game-specific entries.
- **Clean Data Display:** Presents a cleaned version of the logged game information, removing unnecessary fields.
- **Export Capability:** Allows exporting of raw log data as a JSON file for offline inspection.
- **Seamless Integration:** Works within the Decky environment and leverages its plugin infrastructure.

## Building:

### Prerequisites

- **Python 3.7+** – Required to run the backend Python code.
- **Node.js & npm/pnpm** – Necessary for building the frontend components.
- **Decky Environment** – The plugin is intended to be deployed within a Decky-compatible setup.

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/wowitsjack/deckyloader-envtest.git
   cd deckyloader-envtest
   ```

2. **Install Node Dependencies**

   Use npm or pnpm to install required packages:

   ```bash
   npm install
   ```
   
   Or, if using pnpm:

   ```bash
   pnpm install
   ```

3. **Build the Plugin**

   Build the frontend assets using Rollup:

   ```bash
   npm run build
   ```
   
   Or with pnpm:

   ```bash
   pnpm run build
   ```

4. **Deploy the Plugin**

   Follow the Decky plugin deployment instructions to load the plugin into your Decky environment.

## Usage

- **Accessing the Plugin:**  
  Navigate to a game and open the plugin from the Decky Plugins UI.

- **Logging Game Data:**  
  Click the **DEBUG: Log Game Data** button to log game information. The plugin captures and displays both raw and cleaned game details.

- **Pulling Heroic Data:**  
  Use the **Pull Heroic Data** button to fetch Heroic configuration details and filter the data based on the game title.

- **Exporting Data:**  
  Use the **Export JSON** button to download the logged data for further analysis.

## Project Structure

- **envtest/main.py**  
  Main backend script that handles logging of game data and pulling of Heroic configuration files.

- **envtest/decky.pyi**  
  Type definitions and helper functions for Decky plugins.

- **envtest/src/**  
  Contains the frontend code written in TypeScript and React:
  - **src/utils/backend.ts**: Provides callable functions to communicate with the backend.
  - **src/components/ChooChooModeBadge.tsx**: Main UI component handling user interactions.
  - **src/views/PageRouter.tsx**: Manages routing based on the application ID.
  - **src/index.tsx**: Registers and initializes the plugin with Decky.

- **Configuration Files:**
  - **tsconfig.json:** TypeScript configuration.
  - **rollup.config.js:** Rollup configuration for bundling frontend assets.
  - **package.json & plugin.json:** Metadata and dependency information.
  - **pnpm-lock.yaml:** Lockfile for dependency management (if using pnpm).

## Contributing

Contributions to Decky EnvTest are welcome. If you have suggestions, feature requests, or bug fixes, please open an issue or submit a pull request.

## License

Decky EnvTest is released under the **GPL-3.0-or-later** license. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

- **Decky Team:** For providing the robust plugin platform.
- **Heroic Games Launcher Community:** For inspiring the integration of Heroic configuration data.
- **Contributors:** Thanks to all developers and users who helped test and improve Decky EnvTest.
