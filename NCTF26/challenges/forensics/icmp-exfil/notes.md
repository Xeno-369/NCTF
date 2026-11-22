# icmp-exfil (icmp.pcap — canal caché ICMP)

- Catégorie : forensics réseau
- Résolu : sam. 07 nov.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/icmp.pcap | 249e14fe4fdb53b5e63d057905f6f6ba376099ffc3d286748d15011550d97d44 |

## Résolution
- 2 destinations : .10 (pings normaux, leurre) et .200 (33 paquets, canal caché).
- Payload ICMP normal = 08090a0b0c0d0e0f **10** 1112...37 ; les paquets .200 ont le **9e octet (index 8) modifié** = 1 caractère du message (leet).
- Capturés dans le désordre -> trier par **icmp.seq** (0..32).
- PIEGE : le champ tshark data.data ignore 8 paquets (octet caché = chiffre leet), d'où un message tronqué. Parser le pcap à la main et prendre payload[8] de TOUS les 33 paquets.
- Leet : 1=i, 4=a, 0=o, 3=e.

## Flag
`NCTF{1cmp_p4yl04d_c0v3rt_ch4nn3l}`
