import json
import os

config_path = os.path.expanduser("~/AppData/Roaming/Claude/claude_desktop_config.json")

# Lire le fichier
with open(config_path, 'r') as f:
    config = json.load(f)

# Ajouter la configuration Grok
config['mcpServers']['grok'] = {
    "command": "node",
    "args": ["c:/analyse_immobiliere/grok-mcp/build/index.js"],
    "env": {
        "GROK_API_KEY": "xai-OFmpjg3Ic3fx7HH1qln8XVtmMygVI8emgX5nhyaGOps0eLTEQ0ZAPk3dKRHMpQrKo9kWeiGAWOHRYMVg"
    }
}

# Écrire le fichier
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("Grok MCP configure avec succes!")
