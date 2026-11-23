
"""
AI BUSINESS ANALYST
Agent autonome d'analyse de données commerciales.

Qwen choisit les outils Python nécessaires.
Les outils effectuent les calculs.
Qwen rédige le rapport à partir des résultats obtenus.
"""

import json
import re
from datetime import datetime
from pathlib import Path

import ollama

from tools import TOOLS


# ============================================================
# 1. CONFIGURATION
# ============================================================

MODEL = "qwen3:4b"

BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"

MAX_STEPS = 10
MAX_REPEATS = 2
MAX_ERRORS = 3

REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. INSTRUCTIONS DE L'AGENT
# ============================================================

SYSTEM_PROMPT = """
Tu es AI Business Analyst, un agent IA autonome.

Tu analyses des données commerciales fictives à l'aide
d'outils Python.

Tu dois comprendre la demande de l'utilisateur et choisir
les outils nécessaires.

OUTILS DISPONIBLES :

explore_data
Arguments : {}

analyze_sales
Arguments : {"year": 2025, "group_by": "region"}
group_by peut être region, product ou year.
year peut être null.

compare_years
Arguments : {"year1": 2025, "year2": 2026}

check_data_quality
Arguments : {}

create_chart
Arguments : {"group_by": "year", "year": null}

RÈGLES :

1. Choisis uniquement les outils nécessaires à la mission.
2. Ne répète pas une action déjà exécutée.
3. Si la mission est simple, un seul outil peut suffire.
4. Si la mission comporte plusieurs demandes,
   utilise les outils correspondants.
5. Dès que les résultats sont suffisants, termine.
6. N'invente jamais de chiffres.
7. N'affirme jamais qu'un résultat est statistiquement
   significatif sans test statistique.
8. Ne suppose pas de devise si elle n'est pas indiquée.
9. Les données sont fictives.

FORMAT DE RÉPONSE :

Pour appeler un outil :
{"tool": "analyze_sales", "args": {"year": 2025, "group_by": "region"}}

Pour indiquer que l'analyse est terminée :
{"final": true}

IMPORTANT :

La clé final sert uniquement à signaler
que tu as terminé les analyses.

Tu ne dois PAS rédiger le rapport dans cette étape.
Un autre appel à Qwen sera consacré à la rédaction.

Réponds uniquement avec un objet JSON valide.
"""


# ============================================================
# 3. COMMUNIQUER AVEC QWEN
# ============================================================

def ask_qwen(messages, json_mode=True):
    """
    Envoyer une conversation au modèle local.

    json_mode=True :
        Utilisé pour choisir les outils.

    json_mode=False :
        Utilisé pour rédiger un véritable rapport.
    """

    options = {
        "temperature": 0
    }

    parameters = {
        "model": MODEL,
        "messages": messages,
        "think": False,
        "options": options
    }

    if json_mode:
        parameters["format"] = "json"

    response = ollama.chat(**parameters)

    return response.message.content.strip()


# ============================================================
# 4. VÉRIFIER LES DÉCISIONS
# ============================================================

def parse_action(content):
    """
    Transformer la réponse JSON en dictionnaire Python.
    """

    try:
        action = json.loads(content)

        if isinstance(action, dict):
            return action

    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    return None


# ============================================================
# 5. CONVERTIR LES RÉSULTATS EN TEXTE
# ============================================================

def result_to_text(result):
    """
    Convertir un résultat Python en texte lisible.

    Les outils peuvent retourner :
    - un dictionnaire ;
    - une liste ;
    - une chaîne JSON ;
    - un autre type Python.
    """

    if isinstance(result, str):
        return result

    return json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
        default=str
    )


# ============================================================
# 6. VALIDER UN RAPPORT
# ============================================================

def valid_report(report):
    """
    Refuser les réponses vides ou génériques.

    Cette validation ne garantit pas que toutes les
    conclusions sont exactes, mais évite d'enregistrer
    un simple titre comme rapport complet.
    """

    if not isinstance(report, str):
        return False

    report = report.strip()

    # Un rapport doit contenir une vraie explication.
    if len(report) < 180:
        return False

    # Rejeter les réponses génériques connues.
    generic_responses = [
        "rapport détaillé en français",
        "rapport final",
        "votre rapport ici",
        "analyse terminée",
        "conclusion de l'analyse"
    ]

    if report.lower() in generic_responses:
        return False

    # Éviter d'accepter un rapport composé uniquement
    # d'un titre ou d'une phrase répétée.
    words = re.findall(r"\w+", report.lower())

    if len(set(words)) < 25:
        return False

    return True


# ============================================================
# 7. GÉNÉRER LE RAPPORT FINAL
# ============================================================

def generate_report(question, results):
    """
    Demander à Qwen de rédiger le rapport final.

    IMPORTANT :

    Cette étape est séparée du choix des outils.

    Qwen reçoit :
    - la mission initiale ;
    - les résultats des outils réellement exécutés.

    Il ne doit plus choisir d'outil.

    Le rapport est rédigé par l'IA, pas par Python.
    """

    if not results:
        print(
            "\nImpossible de générer un rapport : "
            "aucune analyse réussie."
        )
        return None

    results_text = json.dumps(
        results,
        ensure_ascii=False,
        indent=2,
        default=str
    )

    report_system_prompt = """
Tu es un analyste de données commerciales professionnel.

Tu dois rédiger un véritable rapport d'analyse en français.

Tu disposes de résultats calculés par des outils Python.

RÈGLES ABSOLUES :

- Tu ne peux plus appeler d'outils.
- Tu dois interpréter les résultats fournis.
- Tu dois répondre à la mission initiale.
- Tu dois citer les chiffres importants.
- Tu dois identifier les tendances pertinentes.
- Tu dois donner des conclusions concrètes.
- Tu dois proposer des recommandations si pertinentes.
- Tu ne dois inventer aucun chiffre.
- Tu ne dois pas inventer de devise.
- Tu ne dois pas inventer d'analyse non effectuée.
- Si des résultats manquent, indique-le clairement.
- Les données sont fictives.
- Sans test statistique, la significativité
  n'a pas été évaluée.
- Une quantité négative peut représenter un retour :
  recommande de vérifier avant de supprimer.
- Évite les conclusions excessives.

STRUCTURE ATTENDUE :

# Rapport d'analyse

## Résultats

Présente les résultats obtenus avec les chiffres.

## Interprétation

Explique ce que signifient les résultats.

## Conclusions et recommandations

Réponds précisément à la question de l'utilisateur.

## Limites

Mentionne les limites pertinentes.

IMPORTANT :

Ne réponds pas avec du JSON.
Ne réponds pas avec un titre seul.
Rédige un véritable rapport Markdown.
"""

    user_prompt = f"""
MISSION DE L'UTILISATEUR :

{question}

RÉSULTATS RÉELS DES OUTILS PYTHON :

{results_text}

Rédige maintenant le rapport complet en français.

Utilise les résultats ci-dessus pour répondre
précisément à la mission.

Ne te contente pas de répéter les instructions.
Explique les chiffres et les conclusions.
"""

    messages = [
        {
            "role": "system",
            "content": report_system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    # Deux tentatives maximum.
    for attempt in range(2):

        print(
            f"\nGénération du rapport "
            f"(tentative {attempt + 1}/2)..."
        )

        try:
            report = ask_qwen(
                messages,
                json_mode=False
            )

        except Exception as error:
            print(
                f"Erreur lors de la rédaction : {error}"
            )
            continue

        # Vérifier que le rapport contient
        # une véritable analyse.
        if valid_report(report):
            return report

        print(
            "Rapport trop court ou générique : "
            "nouvelle tentative."
        )

        messages.append({
            "role": "assistant",
            "content": report
        })

        messages.append({
            "role": "user",
            "content": (
                "Ton rapport précédent est insuffisant. "
                "Rédige une analyse complète de plusieurs "
                "paragraphes. Cite les chiffres des outils, "
                "interprète-les et réponds précisément "
                "à la mission. Aucun JSON."
            )
        })

    return None


# ============================================================
# 8. ENREGISTRER LE RAPPORT
# ============================================================

def save_report(question, report, history):
    """
    Enregistrer le rapport final dans reports/.
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    path = REPORT_DIR / f"report_{timestamp}.md"

    history_text = "\n".join(
        f"- {item}"
        for item in history
    )

    content = (
        "# AI Business Analyst\n\n"
        "## Mission initiale\n\n"
        f"{question}\n\n"
        f"{report}\n\n"
        "## Outils exécutés\n\n"
        f"{history_text}\n"
    )

    path.write_text(
        content,
        encoding="utf-8"
    )

    return path


# ============================================================
# 9. TERMINER L'ANALYSE
# ============================================================

def finish_analysis(question, results, history):
    """
    Générer, vérifier et enregistrer le rapport.

    Cette fonction est appelée :
    - lorsque Qwen a terminé ;
    - lorsqu'il répète des actions ;
    - lorsqu'il rencontre trop d'erreurs ;
    - lorsqu'il atteint la limite de décisions.
    """

    print("\nPréparation du rapport final...")

    report = generate_report(
        question,
        results
    )

    if report is None:
        print(
            "\nImpossible de générer un rapport "
            "satisfaisant avec les résultats disponibles."
        )
        return

    path = save_report(
        question,
        report,
        history
    )

    print("\n========== RAPPORT ==========\n")

    print(report)

    print(f"\nRapport enregistré : {path}")

    print("\nAnalyse terminée !")


# ============================================================
# 10. AGENT AUTONOME
# ============================================================

def run_agent(question):
    """
    Boucle principale de l'agent.

    Qwen décide.
    Python exécute.
    Qwen analyse les résultats.
    """

    print("\n===================================")
    print("       AI BUSINESS ANALYST")
    print("===================================")

    print(f"\nQuestion : {question}")

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": question
        }
    ]

    # Résultats réellement obtenus.
    results = []

    # Historique des outils exécutés.
    history = []

    # Cache pour éviter de relancer les mêmes outils.
    executed_actions = {}

    repeated_actions = 0
    consecutive_errors = 0

    # --------------------------------------------------------
    # BOUCLE DE DÉCISION
    # --------------------------------------------------------

    for step in range(MAX_STEPS):

        print(
            f"\n--- Décision {step + 1}/{MAX_STEPS} ---"
        )

        # ----------------------------------------------------
        # DEMANDER UNE DÉCISION À QWEN
        # ----------------------------------------------------

        try:
            content = ask_qwen(messages)

        except Exception as error:

            print(
                f"Erreur Ollama : {error}"
            )

            consecutive_errors += 1

            if consecutive_errors >= MAX_ERRORS:
                break

            continue

        action = parse_action(content)

        # ----------------------------------------------------
        # RÉPONSE JSON INVALIDE
        # ----------------------------------------------------

        if action is None:

            print("Réponse JSON invalide.")

            consecutive_errors += 1

            messages.append({
                "role": "assistant",
                "content": content
            })

            messages.append({
                "role": "user",
                "content": (
                    "Réponds avec un objet JSON valide. "
                    "Choisis un outil ou utilise "
                    '{"final": true} si tu as terminé.'
                )
            })

            if consecutive_errors >= MAX_ERRORS:
                break

            continue

        # ----------------------------------------------------
        # QWEN A TERMINÉ
        # ----------------------------------------------------

        if "final" in action:

            print(
                "Qwen a terminé la sélection des outils."
            )

            break

        # ----------------------------------------------------
        # EXTRAIRE L'OUTIL CHOISI
        # ----------------------------------------------------

        tool_name = action.get("tool")
        arguments = action.get("args", {})

        # ----------------------------------------------------
        # VÉRIFIER L'ACTION
        # ----------------------------------------------------

        if (
            not isinstance(tool_name, str)
            or tool_name not in TOOLS
            or not isinstance(arguments, dict)
        ):

            print(
                "Outil inconnu ou arguments invalides."
            )

            consecutive_errors += 1

            messages.append({
                "role": "assistant",
                "content": content
            })

            messages.append({
                "role": "user",
                "content": (
                    "Action invalide. Choisis un outil "
                    "disponible ou termine avec "
                    '{"final": true}.'
                )
            })

            if consecutive_errors >= MAX_ERRORS:
                break

            continue

        print(f"Outil choisi : {tool_name}")
        print(f"Arguments : {arguments}")

        # ----------------------------------------------------
        # IDENTIFIER UNE ACTION UNIQUE
        # ----------------------------------------------------

        action_key = json.dumps(
            {
                "tool": tool_name,
                "args": arguments
            },
            sort_keys=True,
            ensure_ascii=False
        )

        # ----------------------------------------------------
        # ACTION DÉJÀ EXÉCUTÉE
        # ----------------------------------------------------

        if action_key in executed_actions:

            repeated_actions += 1

            previous_result = executed_actions[action_key]

            print(
                "Action déjà exécutée : "
                "aucune nouvelle exécution."
            )

            # Réutiliser le résultat sans appeler l'outil.
            result_text = result_to_text(previous_result)

            # Enregistrer la décision de Qwen.
            messages.append({
                "role": "assistant",
                "content": content
            })

            messages.append({
                "role": "user",
                "content": (
                    "ATTENTION : cet outil a déjà été "
                    "exécuté avec les mêmes arguments.\n\n"
                    f"Résultat disponible :\n{result_text}\n\n"
                    "Ne répète plus cet outil. "
                    "Si les résultats suffisent, réponds "
                    'maintenant avec {"final": true}. '
                    "Sinon, choisis uniquement un autre "
                    "outil nécessaire à la mission."
                )
            })

            # Après deux répétitions, terminer.
            # Le rapport sera rédigé séparément.
            if repeated_actions >= MAX_REPEATS:

                print(
                    "Répétitions détectées : "
                    "passage au rapport final."
                )

                break

            continue

        # ----------------------------------------------------
        # EXÉCUTER UNE NOUVELLE ACTION
        # ----------------------------------------------------

        try:

            tool_function = TOOLS[tool_name]

            result = tool_function(**arguments)

            # Enregistrer le résultat dans le cache.
            executed_actions[action_key] = result

            # Conserver le résultat pour Qwen.
            results.append({
                "tool": tool_name,
                "arguments": arguments,
                "result": result
            })

            history.append(
                f"{tool_name}({arguments})"
            )

            repeated_actions = 0
            consecutive_errors = 0

        except Exception as error:

            print(
                f"Erreur d'exécution : {error}"
            )

            consecutive_errors += 1

            messages.append({
                "role": "assistant",
                "content": content
            })

            messages.append({
                "role": "user",
                "content": (
                    f"L'outil {tool_name} a échoué : "
                    f"{error}. "
                    "Corrige les arguments ou choisis "
                    "une autre action pertinente. "
                    "N'invente aucun résultat."
                )
            })

            if consecutive_errors >= MAX_ERRORS:
                break

            continue

        # ----------------------------------------------------
        # AFFICHER LE RÉSULTAT
        # ----------------------------------------------------

        result_text = result_to_text(result)

        print("\nRésultat de l'outil :")

        print(result_text[:1500])

        # ----------------------------------------------------
        # TRANSMETTRE LE RÉSULTAT À QWEN
        # ----------------------------------------------------

        messages.append({
            "role": "assistant",
            "content": content
        })

        messages.append({
            "role": "user",
            "content": (
                f"L'outil {tool_name} a réussi.\n\n"
                f"Résultat :\n{result_text}\n\n"
                "Détermine si la mission nécessite "
                "une autre analyse.\n"
                "Si les résultats suffisent, réponds "
                'uniquement avec {"final": true}.\n'
                "Ne répète pas une action déjà exécutée."
            )
        })

    # --------------------------------------------------------
    # RÉDIGER LE RAPPORT FINAL
    # --------------------------------------------------------

    finish_analysis(
        question,
        results,
        history
    )


# ============================================================
# 11. DÉMARRAGE DU PROGRAMME
# ============================================================

if __name__ == "__main__":

    question = input(
        "\nQuelle analyse veux-tu effectuer ?\n> "
    ).strip()

    if not question:

        print(
            "Erreur : aucune mission saisie."
        )

    else:

        run_agent(question)
