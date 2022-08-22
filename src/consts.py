from pathlib import Path

ADDON_NAME = "Wiktionary"
ADDON_DIR = Path(__file__).resolve().parent
ICONS_DIR = ADDON_DIR / "icons"
USER_FILES = ADDON_DIR / "user_files"
VERSION = "0.2"
ANKIWEB_ID = "2087444887"
VER_CONF_KEY = f"wiktionary_{ANKIWEB_ID}_version"
