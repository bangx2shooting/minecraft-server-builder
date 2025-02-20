# Minecraft Server Builder

A Python-based tool for setting up Minecraft servers, both **Vanilla** (official) and **Forge** modded servers, with automatic downloading and setup. This tool is designed to only support the **latest** Minecraft version.

## Features
- **Vanilla (Official) Server**:
  - Automatically fetches the latest official Minecraft server version.
  - Sets up the server, accepts the EULA, and creates a start script (`start_server.bat`).
  
- **Forge Modded Server**:
  - Automatically fetches the latest Minecraft version and corresponding Forge version.
  - Downloads and runs the Forge installer to set up the server.
  - Creates a start script (`start_server.bat`).

### Note
- **Only the latest version of Minecraft is supported**. The tool fetches the latest official release version and the latest corresponding Forge version, making it easy to set up Minecraft servers without manually checking for updates.
- All servers are set up with default memory settings, which can be configured in the `config/config.json` file.

## Requirements
- Java 8 or higher installed
- Internet access for downloading server files

## Usage

### Step 1: Prepare the Environment
1. Clone or download the repository.
2. Ensure that you have Java installed on your system.
3. Make sure the `config/config.json` file exists. If it does not, the script will use the default memory settings (`1024M` min and `1024M` max).
   
### Step 2: Run the Setup Script
To set up a Minecraft server, follow these steps:

1. Navigate to the `bin` directory where `build_server.bat` is located.
2. Double-click the `build_server.bat` file to run the setup script.
3. You will be prompted to choose the server type.
4. After selecting the server type, the script will download the necessary files and set up the server. A new directory for the server will be created inside the servers folder, and the server files will be placed there.
5. To start the server, navigate to the newly created server directory inside the servers folder. There, you will find a start_server.bat file. Double-click start_server.bat to launch the server.