# Registre RGPD : fiche de traitement

| Rubrique | Contenu |
|---|---|
| Traitement | Aide au tri des tickets d'incident informatique |
| Responsable | Direction des systèmes d'information (fictive pour la démonstration) |
| Finalité | Suggérer catégorie, priorité et procédure pour accélérer la prise en charge |
| Base légale | Intérêt légitime (bon fonctionnement du système d'information) |
| Personnes concernées | Collaborateurs et clients cités dans les tickets |
| Données | Texte libre des tickets, pouvant contenir nom, e-mail, téléphone, matricule, IP, IBAN |
| Minimisation | Masquage automatique avant LLM, journal et affichage ; le journal ne garde qu'une empreinte du texte |
| Destinataires | Agents de support ; fournisseur LLM pour le seul résumé, sur texte masqué |
| Transferts hors UE | Possible selon le fournisseur LLM choisi. Recommandation : socle IA interne ou fournisseur hébergé dans l'UE. En attendant, seul du texte masqué est envoyé, et l'outil fonctionne sans LLM |
| Conservation | Journal d'audit : 90 jours (`AUDIT_RETENTION_JOURS`) |
| Sécurité | Secrets en variables d'environnement, contrôle CI, détection d'injection, point d'entrée LLM unique |
| AIPD | Non requise à ce stade (pas de traitement à grande échelle de données sensibles ni de profilage) ; à réévaluer si le périmètre s'étend |
