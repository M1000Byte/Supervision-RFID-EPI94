# Module de Contrôle d'Accès RFID
[cite_start]Ce module est développé pour l'entreprise EPI-94 dans le cadre du projet de supervision[cite: 42, 44].

## Matériel utilisé
- [cite_start]Raspberry Pi 4 Model B [cite: 124]
- [cite_start]Lecteur NFC ACR122U 

## État actuel
- Environnement Linux configuré.
- Pilotes PCSC installés.
- Test de détection : OK.
## Resolution d'incidents
### Probleme Accès refusé au lecteur via SSH (Polkit)
**Symptôme :** Impossible de communiquer avec l'ACR122U lors d'une session à distance, malgré le bon fonctionnement de `pcsc_scan`.
**Cause :** Les politiques de sécurité Debian (Polkit) restreignent l'accès au matériel PC/SC pour les sessions non locales.
**Solution :** Création d'une règle Polkit personnalisée dans ( `/usr/share/polkit-1/rules.d/`) pour autoriser explicitement mon utilisateur.