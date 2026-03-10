"""
Paramètres de configuration pour le scraper HelloWork.
"""

# Configuration du scraping
SCRAPE_DELAY = 2  # Secondes entre chaque requête
MAX_RETRIES = 3   # Nombre maximum de tentatives en cas d'erreur
TIMEOUT = 30      # Timeout pour les requêtes HTTP

# Configuration de Selenium
SELENIUM_CONFIG = {
    "headless": True,
    "window_size": "1920,1080",
    "implicit_wait": 10,
    "page_load_timeout": 30
}

# User-Agent pour les requêtes
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Fichiers de sortie
OUTPUT_FILES = {
    "csv": "job_offers.csv",
    "json": "job_offers.json",
    "excel": "job_offers.xlsx"
}

# Logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "scraper.log"
}