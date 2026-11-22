# wifi-deauth (traffic-04.cap)

- **Catégorie :** forensics (WiFi / WPA2)
- **Résolu :** sam. 07 nov.

## Énoncé
SOC SecureCorp. WIDS alerte le 08/06/2026 ~13h : flood de beacons canal 10, déconnexions simultanées, MAC inconnue. Analyser traffic-04.cap. Flag: NCTF{1_2_3_4_5_6} = SSID_BSSID_attaque_heure1reHandshake_passWPA2_MITRE.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/traffic-04.cap | ad07ada999b274044e48a2ece316d1d634239882fbb470a2f762e66d0d842633 |

## Résolution
1. **SSID** : Wifi-Test — `aircrack-ng traffic-04.cap`.
2. **BSSID** : EA:2A:EA:1E:A0:5A.
3. **Attaque** : Déauthentification. 196 250 trames deauth (subtype 0x0c) du BSSID vers ff:ff:ff:ff:ff:ff.
   `tshark -Y 'wlan.fc.type_subtype==0x0c'`.
4. **1re trame handshake** : 13:24:51 (EAPOL frame 18608, 13:24:51.624999).
   `tshark -Y eapol -e frame.number -e frame.time | head`.
5. **Pass WPA2** : 30secondstomars — `aircrack-ng -w rockyou.txt -b EA:2A:EA:1E:A0:5A traffic-04.cap`.
6. **MITRE Initial Access** : T1078 (Valid Accounts) — la PSK crackée = credential valide pour accéder au réseau.

## Incertitudes de format
- #3 : "Déauthentification" / "Deauthentication" / "Deauth" selon la plateforme.
- #6 : T1078 (sinon T1078.001).

## Flag
`NCTF{Wifi-Test_EA:2A:EA:1E:A0:5A_Deauthentification_13:24:51_30secondstomars_T1078}`
