# Module de Contrôle d'Accès RFID
Ce module est développé pour l'entreprise EPI-94 dans le cadre du projet de supervision.

## Matériel utilisé
- **Raspberry Pi 4 Model B**: Unité centrale de traitement.
- **Lecteur NFC ACR122U** : Interface USB pour la lecture des badges RFID[cite: 51].
- **Carte Relais USB (FT245RL)** [cite: 122] : Interface de puissance pour la commande de la gâche électrique.
- **Gâche électrique** [cite: 123] : Actionneur de verrouillage de la porte.

## 🚀 État actuel & Fonctionnalités
- ✅ Environnement Linux configuré & Services `pcscd` opérationnels.
- ✅ Lecture d'UID et journalisation locale validées(`acces.csv`) : **OK**.
- 🔄 Intégration MFA (Multi-Facteurs) et Edge Computing en cours.
---

## Installation et Configuration (Bash)

### 1. Dépendances système
```bash
sudo apt update
sudo apt install -y pcscd libpcsclite-dev libftdi1-dev
```

## État actuel
- Environnement Linux configuré.
- Pilotes PCSC installés.
- Test de détection : OK.
## Resolution d'incidents
### Probleme Accès refusé au lecteur via SSH (Polkit)
**Symptôme :** Impossible de communiquer avec l'ACR122U lors d'une session à distance, malgré le bon fonctionnement de `pcsc_scan`.
**Cause :** Les politiques de sécurité Debian (Polkit) restreignent l'accès au matériel PC/SC pour les sessions non locales.
**Solution :** Création d'une règle Polkit personnalisée dans ( `/usr/share/polkit-1/rules.d/`) pour autoriser explicitement mon utilisateur :
```javascript
polkit.addRule(function(action, subject) {
    if (action.id == "org.debian.pcsc-lite.access_pcsc") {
        return polkit.Result.YES;
    }
});
```

## 2. Pilotage Physique : Relais et Gâche Électrique

Cette section détaille la conception de la chaîne d'actionnement, de l'étude documentaire à la mise en œuvre physique.

### 2.1 Validation Matérielle sous Windows
Avant l'intégration sur Raspberry Pi, une phase de test "Pre-flight" a été réalisée sous Windows pour écarter toute défaillance matérielle.

**Procédure de test :**
1. **Installation du Driver :** Utilisation de l'exécutable `CDM20802_Setup` (FTDI CDM Drivers). Ce pilote permet au système de reconnaître la puce FT245RL et d'établir la communication D2XX/VCP.[Documentation](https://docs.sainsmart.com/article/790hrr4nux-sain-smart-relay-module-sensors)
2. **Logiciel de Test :** Exécution de **USB 8 Relay Manager v.1.4** (issu de l'archive `USB 8-CH.zip` de SainSmart).
3. **Résultat :** Validation du basculement physique des relais (clic mécanique) et vérification de la correspondance entre les commandes logicielles et les sorties physiques.

> **Note :** Cette étape a permis de confirmer que le **Relais 8** répondait correctement, isolant ainsi les futurs problèmes de développement comme étant purement logiciels (drivers Linux/Permissions).

* **Puce FTDI FT245RL :** La consultation de la [Datasheet officielle FTDI](https://ftdichip.com/wp-content/uploads/2020/07/DS_FT245RL.pdf) a permis d'identifier le mode **Asynchronous Bit-Bang**. Ce mode permet de bypasser le protocole série pour piloter directement les 8 lignes de données ($D0$ à $D7$).
* **Librairie Pylibftdi :** L'étude de la [documentation Pylibftdi](https://pylibftdi.readthedocs.io/) a été cruciale pour implémenter la gestion du contexte (`with BitBangDevice() as dev`) afin de garantir la libération des ressources USB après chaque accès.

### 2.2 Configuration Logique (Mapping des Relais)
**Problématique rencontrée :** Lors des premiers tests, l'envoi de la valeur `1` n'activait pas le Relais 1 comme prévu. 
**Analyse :** Après lecture des schémas de la carte, il s'est avéré que l'indexation commence à 0. 

Pour activer le **Relais 8**, il faut donc cibler le **Bit 7** :
$$Valeur = 2^{7} = 128_{10} = \mathbf{0x80_{16}}$$


### 2.3 Problématiques & Solutions Techniques



### 2.4 Schéma de Raccordement (Fail-Secure)
Le montage utilise le contact **Normally Open (NO)**. En cas de panne logicielle, le circuit s'ouvre et la porte reste sécurisée.

```text
       [ ALIMENTATION 12V ]
          |            |
          |          (GND)-----------+
        (+12V)                       |
          |                    [ GÂCHE ÉLECTRIQUE ]
      [ RELAIS 8 ]                   |
     (Borne COM)                     |
     (Borne NO)----------------------+
```
     
 ```python

     from pylibftdi import BitBangDevice
import time

def piloter_gache():
    try:
        with BitBangDevice() as dev:
            dev.direction = 0xFF # Configure les 8 bits en sortie
            
            print("Déverrouillage (Relais 8)...")
            dev.port = 0x80      # Activation Bit 7 donc porte relai 8
            time.sleep(2)        # Temporisation d'ouverture
            
            dev.port = 0x00      # Reset (Verrouillage)
            print("Porte sécurisée.")
            
    except Exception as e:
        print(f"Erreur de communication USB : {e}")

if __name__ == "__main__":
    piloter_gache()
    ```