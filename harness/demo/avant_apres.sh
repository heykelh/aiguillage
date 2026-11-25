#!/usr/bin/env bash
# Démonstration en 1 minute : même demande, sans puis avec le harnais.
set -u
cd "$(dirname "$0")/../.."

echo "=================================================================="
echo " AVANT : ce qu'un agent de code produit sans harnais"
echo "=================================================================="
python3 harness/checks/conformite.py harness/demo/sans_harnais

read -r -p "Entrée pour voir le même besoin construit avec le harnais... " _

echo "=================================================================="
echo " APRÈS : le même besoin, construit avec AGENTS.md et les skills"
echo "=================================================================="
python3 -m pytest -q
echo
python3 eval/run_eval.py
python3 harness/checks/conformite.py
