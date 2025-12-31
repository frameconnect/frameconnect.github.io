import requests
import re
import subprocess
from pathlib import Path

# =========================
# CONFIGURATION
# =========================

GITHUB_REPO_PATH = Path(__file__).parent
HTML_FILE = GITHUB_REPO_PATH / "index.html"
REDIRECT_REGEX = r'window\.location\.href\s*=\s*"([^"]+)"'

PROTOCOL = "http"   # mets "https" quand ta box sera bien configurée
PORT = 5000         # port de ton service (ex: Flask)
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
    """
    Extrait l'URL actuelle depuis le script de redirection JS.
    """
    match = re.search(REDIRECT_REGEX, html_content)
    if not match:
        raise ValueError(
            "❌ Redirection window.location.href non trouvée dans index.html"
        )
    return match.group(1)


def update_html_url(html_content, new_url):
    """
    Met à jour l'URL dans le script window.location.href
    """
    return re.sub(
        REDIRECT_REGEX,
        f'window.location.href = "{new_url}"',
        html_content
    )


def git_commit_and_push():
    """Commit + push forcé (-f)"""
    subprocess.run(["git", "add", "index.html"], check=True)
    subprocess.run(
        ["git", "commit", "-m", "🔁 Mise à jour automatique FrameConnect"],
        check=True
    )
    subprocess.run(["git", "push", "-f"], check=True)


# =========================
# MAIN
# =========================

def main():
    print("🔍 Vérification de l'IP publique…")

    public_ip = get_public_ip()
    new_url = f"{PROTOCOL}://{public_ip}:{PORT}"

    html = HTML_FILE.read_text(encoding="utf-8")
    if "window.location.href" not in html:
        raise RuntimeError("❌ Aucune redirection JS détectée dans index.html")
    current_url = read_current_url(html)

    if current_url == new_url:
        print("✅ Aucun changement détecté")
        return

    print(f"⚠️ Changement détecté :\n   {current_url}\n→  {new_url}")

    updated_html = update_html_url(html, new_url)
    HTML_FILE.write_text(updated_html, encoding="utf-8")

    git_commit_and_push()

    print("🚀 Transfert mis à jour et publié sur GitHub Pages")


if __name__ == "__main__":
    main()
