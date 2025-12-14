import requests
import re
import subprocess
from pathlib import Path

# =========================
# CONFIGURATION
# =========================

GITHUB_REPO_PATH = Path(__file__).parent
HTML_FILE = GITHUB_REPO_PATH / "index.html"

PROTOCOL = "http"   # mets "https" quand ta box est bien configurée en HTTPS
IP_SERVICE = "https://api.ipify.org"

# =========================
# FONCTIONS
# =========================

def get_public_ip():
    """Récupère l'IP publique de la box"""
    response = requests.get(IP_SERVICE, timeout=5)
    response.raise_for_status()
    return response.text.strip()


def read_current_url(html_content):
    """Extrait l'URL actuelle définie dans TARGET_URL"""
    match = re.search(r'const\s+TARGET_URL\s*=\s*"([^"]+)"', html_content)
    if not match:
        raise ValueError("TARGET_URL non trouvé dans index.html")
    return match.group(1)


def update_html_url(html_content, new_url):
    """Met à jour TARGET_URL dans le HTML"""
    return re.sub(
        r'const\s+TARGET_URL\s*=\s*"[^"]+"',
        f'const TARGET_URL = "{new_url}"',
        html_content
    )


def git_commit_and_push():
    """Commit + push sans exposer l’IP"""
    subprocess.run(["git", "add", "index.html"], check=True)
    subprocess.run(
        ["git", "commit", "-m", "🔁 Mise à jour du transfert"],
        check=True
    )
    subprocess.run(["git", "push"], check=True)


# =========================
# MAIN
# =========================

def main():
    print("🔍 Vérification de l'IP publique…")

    public_ip = get_public_ip()
    new_url = f"{PROTOCOL}://{public_ip}"

    html = HTML_FILE.read_text(encoding="utf-8")
    current_url = read_current_url(html)

    if current_url == new_url:
        print("✅ Aucun changement détecté")
        return

    print("⚠️ Changement détecté, mise à jour en cours…")

    updated_html = update_html_url(html, new_url)
    HTML_FILE.write_text(updated_html, encoding="utf-8")

    git_commit_and_push()

    print("🚀 Transfert mis à jour et publié sur GitHub Pages")


if __name__ == "__main__":
    main()