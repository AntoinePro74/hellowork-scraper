#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HelloWork Scraper
=================

Un scraper pour récupérer les offres d'emploi depuis le site HelloWork.
"""

import logging
from scraper.hellowork_scraper import HelloWorkScraper


def setup_logging():
    """Configure le logging pour l'application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """Fonction principale du scraper."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Démarrage du scraper HelloWork")

    # Initialisation du scraper
    scraper = HelloWorkScraper()

    try:
        # Exécution du scraping
        scraper.scrape_jobs()
        logger.info("Scraping terminé avec succès")

    except Exception as e:
        logger.error(f"Erreur lors du scraping: {e}")
        raise

    finally:
        # Fermeture propre du scraper
        scraper.close()
        logger.info("Scraper fermé")


if __name__ == "__main__":
    main()