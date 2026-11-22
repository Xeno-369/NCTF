# mirage (mirage-1.pcapng — RTP/vidéo cachée)

- Catégorie : forensics réseau
- Résolu : sam. 07 nov.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/mirage-1.pcapng | 444e3d83217fd42ce8a65fcfbc42146b1148eec82e285fad2f44464a46e14965 |

## Résolution
- 7550 paquets ; bruit DNS/HTTP/TLS en camouflage.
- "Fantôme" = gros flux UDP 192.168.98.7 -> 192.168.8.93:5000 (3758 paquets, 5 Mo).
- En-têtes 0x80 21 ... = RTP version 2, payload type 33 (MP2T = MPEG-TS). Charges = paquets TS (sync 0x47).
- Décodage RTP + reassemblage .ts (H.264 360x640, 29s), extraction frames ffmpeg -> flag incrusté à l'écran.

## Commandes
```bash
tshark -r mirage-1.pcapng -d udp.port==5000,rtp -Y 'rtp && ip.src==192.168.98.7' -T fields -e rtp.payload | tr -d '\n:' | xxd -r -p > mirage.ts
ffmpeg -i mirage.ts -vf fps=2 frames/f_%04d.png
montage frames/f_*.png -tile 10x6 contact.png   # flag visible à l'écran
```

## Flag
`NCTF{oohhh_a_ghost_gg}`
