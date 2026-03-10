#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script principal pour lancer le scraping HelloWork avec export CSV + JSON.
Gère plusieurs URLs de recherche simultanément.
"""

import logging
import json
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime
from scraper.hellowork_scraper import HelloWorkScraper
from scraper.models.job_offer import JobOffer
from config import SEARCH_URLS

# Dossier de sortie
OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)


def setup_logging():
    """Configure le logging pour l'application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )


def save_to_csv(job_offers: list, filename: str):
    """
    Sauvegarde les offres dans un fichier CSV.

    Args:
        job_offers (list): Liste des offres à sauvegarder
        filename (str): Nom du fichier de sortie
    """
    data = [offer.to_dict() for offer in job_offers]
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    logging.info(f"{len(job_offers)} offres sauvegardées dans {filename}")


def save_to_json(job_offers: list, filename: str):
    """
    Sauvegarde les offres dans un fichier JSON.

    Args:
        job_offers (list): Liste des offres à sauvegarder
        filename (str): Nom du fichier de sortie
    """
    data = [offer.to_dict() for offer in job_offers]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info(f"{len(job_offers)} offres sauvegardées dans {filename}")


def print_summary(job_offers: list):
    """Affiche un résumé des offres scrapées."""
    print("\n" + "=" * 70)
    print("RÉSUMÉ DES OFFRES COLLECTÉES")
    print("=" * 70)

    for i, offer in enumerate(job_offers, 1):
        print(f"\n[{i}/{len(job_offers)}] {offer.title}")
        print(f"      Entreprise : {offer.company or 'N/A'}")
        print(f"      Localisation : {offer.location or 'N/A'}")
        print(f"      Contrat : {offer.employment_type.value}")
        print(f"      Télétravail : {offer.remote_work.value}")
        print(f"      Salaire : {offer.salary or 'N/A'}")
        print(f"      URL : {offer.url}")

    print("\n" + "=" * 70)


def main():
    """Fonction principale du scraper."""
    # Parser les arguments en ligne de commande
    parser = argparse.ArgumentParser(description="Scraper HelloWork avec pagination et URLs multiples")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Nombre maximum de pages à scraper par URL (par défaut: toutes)"
    )
    parser.add_argument(
        "--urls",
        type=str,
        nargs="+",
        default=None,
        help="URLs de recherche HelloWork (par défaut: URLs prédéfinies)"
    )
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)

    # Déterminer les URLs à scraper
    urls_to_scrape = args.urls if args.urls else SEARCH_URLS

    logger.info("=" * 70)
    logger.info("SCRAPER HELLOWORK")
    logger.info("=" * 70)
    logger.info(f"Nombre d'URLs à scraper : {len(urls_to_scrape)}")
    if args.max_pages:
        logger.info(f"Limitation : {args.max_pages} pages maximum par URL")

    scraper = HelloWorkScraper(headless=True)
    all_job_offers = []

    try:
        # Scraping pour chaque URL
        for i, url in enumerate(urls_to_scrape, 1):
            logger.info(f"\n{'=' * 70}")
            logger.info(f"URL {i}/{len(urls_to_scrape)}")
            logger.info(f"{'=' * 70}")
            logger.info(f"URL de recherche : {url}")

            # Scraping complet : recherche + détails
            logger.info("Lancement du scraping...")
            job_offers = scraper.scrape_search_with_details(url, max_pages=args.max_pages)

            logger.info(f"{len(job_offers)} offres collectées avec leurs détails")
            all_job_offers.extend(job_offers)

            # Pause entre les URLs
            if i < len(urls_to_scrape):
                logger.info("Pause de 5 secondes avant la prochaine URL...")
                import time
                time.sleep(5)

        logger.info(f"\n{'=' * 70}")
        logger.info(f"TOTAL : {len(all_job_offers)} offres collectées")
        logger.info(f"{'=' * 70}")

        # Affichage du résumé
        print_summary(all_job_offers)

        # Génération des noms de fichiers avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = OUTPUT_DIR / f"job_offers_{timestamp}.csv"
        json_file = OUTPUT_DIR / f"job_offers_{timestamp}.json"

        # Export des données
        logger.info("\n" + "=" * 70)
        logger.info("EXPORT DES DONNÉES")
        logger.info("=" * 70)

        save_to_csv(all_job_offers, str(csv_file))
        save_to_json(all_job_offers, str(json_file))

        logger.info(f"\nFichiers générés :")
        logger.info(f"  - CSV : {csv_file.absolute()}")
        logger.info(f"  - JSON: {json_file.absolute()}")

        logger.info("\n" + "=" * 70)
        logger.info("SCRAPING TERMINÉ AVEC SUCCÈS")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"Erreur lors du scraping : {e}")
        import traceback
        traceback.print_exc()
        raise

    finally:
        scraper.close()
        logger.info("Scraper fermé proprement")


if __name__ == "__main__":
    main()
