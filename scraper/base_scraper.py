#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper de base abstrait pour les sites d'emploi.

Définit le squelette commun à tous les scrapers avec :
- Gestion du driver Selenium
- Pipeline de scraping avec pagination
- Intégration avec la base de données pour déduplication
- Méthodes abstraites à implémenter par chaque scraper spécifique
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from scraper.models.job_offer import JobOffer


class BaseScraper(ABC):
    """
    Classe de base abstraite pour tous les scrapers d'offres d'emploi.

    Fournit une structure commune pour le scraping avec Selenium,
    la gestion de la pagination et l'intégration avec la base de données.

    Attributes:
        source_name (str): Nom de la source (ex: "hellowork", "welcometothejungle")
        base_url (str): URL de base du site
        headless (bool): Exécute Chrome en mode headless si True
        driver: Instance du driver Selenium (initialisé en lazy)
        logger: Logger spécifique à la source
    """

    def __init__(self, source_name: str, base_url: str, headless: bool = True):
        """
        Initialise le scraper avec une configuration de base.

        Args:
            source_name: Nom identifiant la source (pour logging)
            base_url: URL de base du site à scraper
            headless: Si True, Chrome s'exécute sans interface graphique
        """
        self.source_name = source_name
        self.base_url = base_url
        self.headless = headless
        self.driver = None
        self.logger = logging.getLogger(f"{__name__}.{source_name}")

    def _setup_driver(self):
        """
        Configure le driver Selenium avec Chrome.

        Utilise webdriver-manager pour gérer automatiquement la version de ChromeDriver.
        L'initialisation est lazy : ne crée le driver que si self.driver est None.

        Configuration Chrome :
        - headless (selon self.headless)
        - --no-sandbox
        - --disable-dev-shm-usage
        - --disable-gpu
        - --window-size=1920,1080
        - User-Agent Chrome 120
        """
        if self.driver is None:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            self.logger.info("Driver Selenium initialisé")

    def close(self):
        """
        Ferme proprement le driver Selenium et libère les ressources.

        Doit être appelé à la fin de l'utilisation du scraper.
        """
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("Driver Selenium fermé")

    def scrape_search_with_details(
        self,
        search_url: str,
        max_pages: Optional[int] = None,
        db_manager=None,
        rescrape_existing: bool = False
    ) -> List[JobOffer]:
        """
        Pipeline complet de scraping : recherche + détails avec déduplication DB.

        Args:
            search_url: URL de recherche du site
            max_pages: Nombre maximum de pages à scraper (None = toutes)
            db_manager: Instance de DatabaseManager pour vérifier les URLs existantes
            rescrape_existing: Si True, force le re-scraping des détails pour toutes les offres

        Returns:
            Liste des JobOffer avec détails complets pour les nouvelles,
            et JobOffer minimaux (sans détails) pour les connues
        """
        # Étape 1 : Scraping des résultats de recherche (titre + URL)
        basic_offers = self.scrape_search_results(search_url, max_pages=max_pages)

        # Si pas de DB, scraper toutes les offres normalement
        if db_manager is None:
            self.logger.info("Aucun gestionnaire de base de données fourni, scraping complet")
            return self.scrape_job_details(basic_offers)

        # Avec DB : optimisation de la déduplication
        if rescrape_existing:
            # Force le re-scraping de toutes les offres
            self.logger.info("Mode rescrape : re-scraping de toutes les offres")
            return self.scrape_job_details(basic_offers)
        else:
            # Comportement par défaut :skip les détails des offres déjà en base
            all_urls = [j['url'] for j in basic_offers]
            existing_urls = db_manager.get_existing_urls(all_urls)

            new_offers_dicts = [j for j in basic_offers if j['url'] not in existing_urls]
            known_offers_dicts = [j for j in basic_offers if j['url'] in existing_urls]

            self.logger.info(
                f"{len(new_offers_dicts)} nouvelles offres à scraper, "
                f"{len(known_offers_dicts)} déjà en base (détails non scrapés)"
            )

            # Scraper les détails uniquement pour les nouvelles offres
            detailed_new = self.scrape_job_details(new_offers_dicts)

            # Créer des JobOffer minimaux pour les offres connues (sans scraper détails)
            known_job_offers = [
                JobOffer(title=j['title'], url=j['url'], new_offer=False)
                for j in known_offers_dicts
            ]

            return detailed_new + known_job_offers

    @abstractmethod
    def _get_total_pages(self, search_url: str) -> int:
        """
        Détermine le nombre total de pages de résultats.

        Args:
            search_url: URL de recherche

        Returns:
            Nombre total de pages disponibles
        """
        pass

    @abstractmethod
    def _build_page_url(self, base_url: str, page: int) -> str:
        """
        Construit l'URL d'une page spécifique.

        Args:
            base_url: URL de base de recherche
            page: Numéro de page (1-indexé)

        Returns:
            URL complète de la page
        """
        pass

    @abstractmethod
    def scrape_search_results(self, search_url: str, max_pages: Optional[int] = None) -> List[Dict]:
        """
        Scrape les résultats de recherche (liste des offres).

        Doit implémenter :
        - Détection du nombre total de pages (ou utiliser _get_total_pages)
        - Pagination via _build_page_url
        - Extraction des titre + URL pour chaque offre
        - Retourne une liste de dict avec au moins 'title' et 'url'

        Args:
            search_url: URL de recherche
            max_pages: Limite optionnelle du nombre de pages

        Returns:
            Liste de dictionnaires representing les offres de base
        """
        pass

    @abstractmethod
    def scrape_job_details(self, job_offers: List[Dict]) -> List[JobOffer]:
        """
        Scrape les détails complets d'une liste d'offres.

        Doit implémenter :
        - Navigation vers chaque URL d'offre
        - Extraction des champs : company, location, employment_type, remote_work,
          salary, description, date_posted
        - Création d'objets JobOffer avec tous les champs renseignés

        Args:
            job_offers: Liste des offres avec au moins 'title' et 'url'

        Returns:
            Liste d'objets JobOffer avec détails complets
        """
        pass
