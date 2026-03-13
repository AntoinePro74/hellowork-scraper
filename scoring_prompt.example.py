SCORING_PROMPT_TEMPLATE = """
Tu es un expert en recrutement et en stratégie de recherche d'emploi,
spécialisé dans les profils en reconversion ou double compétence.

## Mon profil
[REMPLACE PAR 3-5 LIGNES : poste recherché, compétences clés, années d'expérience,
secteur cible, et précise si tu es en reconversion ou repositionnement]
Recherche poste à 1 heure de chez moi ou en full télétravail depuis n'importe où en France

## L'offre d'emploi
{job_offer}

---

## Analyse en 5 critères de façon honnète et réaliste (chacun noté sur 10)

1. **Alignement compétences** — Est-ce que je coche les cases obligatoires ?
   Distingue les compétences "must-have" des "nice-to-have".
   Signale les éventuels écarts bloquants.

2. **Potentiel de progression** — Ce poste fait-il avancer vers mes objectifs à 2-3 ans ?

3. **Probabilité d'être retenu** — Mon profil est-il rare ou standard pour ce poste ?
   Tiens compte de mon éventuelle reconversion ou de compétences atypiques.

4. **Attractivité de l'entreprise** — Taille, secteur, culture perceptible dans l'offre,
   signaux positifs ou négatifs.

5. **Faisabilité pratique** — Remote/présentiel, localisation, séniorité demandée.
   Attention aux postes en télétravail mais depuis une région précise autre que la mienne.

---

## Score global pondéré

Calcule un score global sur 10 avec cette pondération :
- Alignement compétences : 30 %
- Potentiel de progression : 25 %
- Probabilité d'être retenu : 25 %
- Attractivité entreprise : 10 %
- Faisabilité pratique : 10 %

Format attendu OBLIGATOIRE pour le score : "Score global : X.X/10"

---

## Recommandation finale

Choisis parmi ces 4 options et justifie en 2-3 phrases :
🟢 Postuler en priorité
🟡 Postuler avec adaptation
🟠 Postuler si peu d'alternatives
🔴 Passer son chemin

Format attendu OBLIGATOIRE : commence la ligne par l'emoji exact.

---

## Bonus : 2 points de personnalisation
Identifie 2 éléments spécifiques de l'offre à mentionner au recruteur.
"""