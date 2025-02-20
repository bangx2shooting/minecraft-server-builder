import os
import sys
import urllib.request
import json
import subprocess
import shutil
import textwrap

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
SERVER_DIR = os.path.join(BASE_DIR, "servers")
TMP_DIR = os.path.join(BASE_DIR, "tmp")

class ServerBuilder:
    VERSION_MANIFEST_JSON = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
    EULA_FILE = "eula.txt"
    START_SCRIPT = "start_server.bat"
    CONFIG_FILE = os.path.join(BASE_DIR, "config/config.json")

    def __init__(self):
        self.base_dir = BASE_DIR
        self.server_dir = SERVER_DIR
        self.config = self.load_config()

    def load_config(self):
        config_path = os.path.join(self.base_dir, self.CONFIG_FILE)
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"server": {"memory": {"min": "1024M", "max": "1024M"}}}

    def fetch_json(self, url):
        with urllib.request.urlopen(url) as res:
            return json.load(res)

    def get_latest_version_url(self):
        version_manifest = self.fetch_json(self.VERSION_MANIFEST_JSON)
        latest_version = version_manifest["latest"]["release"]

        for version in version_manifest["versions"]:
            if version["id"] == latest_version:
                return latest_version, version["url"]

        raise ValueError("Failed to get latest version.")

    def download_file(self, url, filepath, headers=None):
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req) as res, open(filepath, 'wb') as f:
            f.write(res.read())

    def setup_server(self, target_dir):
        os.chdir(target_dir)

        min_memory = self.config["server"]["memory"]["min"]
        max_memory = self.config["server"]["memory"]["max"]

        subprocess.run(["java", f"-Xmx{min_memory}", f"-Xms{max_memory}", "-jar", "server.jar", "nogui"])

        eula_path = os.path.join(target_dir, self.EULA_FILE)
        if os.path.exists(eula_path):
            with open(eula_path, "r", encoding="utf-8") as file:
                eula_content = file.read().replace("eula=false", "eula=true")
            with open(eula_path, "w", encoding="utf-8") as file:
                file.write(eula_content)

        os.chdir(self.base_dir)

    def create_start_script(self, target_dir):
        min_memory = self.config["server"]["memory"]["min"]
        max_memory = self.config["server"]["memory"]["max"]
        script_content = textwrap.dedent(f"""\
            @echo off

            cd /d %~dp0
            setlocal

            java -Xmx{max_memory} -Xms{min_memory} -jar server.jar nogui 

            endlocal

            pause
        """)
        script_path = os.path.join(target_dir, self.START_SCRIPT)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

class OfficialServerBuilder(ServerBuilder):

    def main(self):
        latest_version, version_url = self.get_latest_version_url()
        version_data = self.fetch_json(version_url)
        server_jar_url = version_data["downloads"]["server"]["url"]

        server_path = os.path.join(self.server_dir, latest_version)
        os.makedirs(server_path, exist_ok=True)

        server_jar = os.path.join(server_path, "server.jar")
        self.download_file(server_jar_url, server_jar)

        self.setup_server(server_path)
        self.create_start_script(server_path)


class ForgeServerBuilder(ServerBuilder):
    GIT_API_URL = "https://api.github.com/repos/MinecraftForge/MinecraftForge/tags"
    INSTALLER_URL_TEMPLATE = "https://maven.minecraftforge.net/net/minecraftforge/forge/{0}-{1}/forge-{2}-{3}-installer.jar"

    def format_tag_name(self, tag_name):
        tag_name = tag_name.lstrip("v")
        if len(tag_name.split(".")) == 2:
            tag_name += ".0"
        return tag_name

    def get_latest_forge_version(self):
        tags = self.fetch_json(self.GIT_API_URL)
        latest_tag = self.format_tag_name(tags[-1]["name"])
        return latest_tag

    def build_installer_url(self, mc_version, forge_version):
        return self.INSTALLER_URL_TEMPLATE.format(mc_version, forge_version, mc_version, forge_version)

    def launch_installer(self, installer_path, server_dir):
        os.chdir(server_dir)
        subprocess.run(["java", "-jar", installer_path, "--installServer"])
        shutil.move(installer_path, server_dir)
        os.chdir(self.base_dir)

    def main(self):
        latest_version, _ = self.get_latest_version_url()
        latest_forge_version = self.get_latest_forge_version()

        installer_url = self.build_installer_url(latest_version, latest_forge_version)
        server_path = os.path.join(self.server_dir, f"forge-{latest_version}")
        os.makedirs(server_path, exist_ok=True)
        os.makedirs(TMP_DIR, exist_ok=True)

        installer_path = os.path.join(TMP_DIR, "server-installer.jar")
        headers = {"User-Agent": "Mozilla/5.0"}
        self.download_file(installer_url, installer_path, headers)

        self.launch_installer(installer_path, server_path)

        forge_jar = os.path.join(server_path, f"forge-{latest_version}-{latest_forge_version}-shim.jar")
        if os.path.exists(forge_jar):
            os.rename(forge_jar, os.path.join(server_path, "server.jar"))

        shutil.rmtree(TMP_DIR)
        self.setup_server(server_path)
        self.create_start_script(server_path)


if __name__ == "__main__":
    os.chdir(os.path.join(BASE_DIR, ".."))

    message = """\
        Choose a server type:
        1) Vanilla (Official)
        2) Forge

        Type a number: """
    formatted_message = textwrap.dedent(message)

    server_type = input(formatted_message)
    if server_type == "1":
        OfficialServerBuilder().main()
    elif server_type == "2":
        ForgeServerBuilder().main()
    else:
        sys.exit("Unknown server type.")
