# docx-leak (communiqués CERT.tg)

- Catégorie : forensics (métadonnées OOXML)
- Résolu : sam. 07 nov.

## Énoncé
6 communiqués .docx fuités, signés 'Cellule Comms CERT.tg'. Qqn a bâclé le nettoyage. Recomposer ce qui a filé = flag.

## Résolution
docProps/core.xml de chaque .docx :
- dc:creator = 'Cellule Comms CERT.tg' (public) partout.
- cp:lastModifiedBy révèle le vrai éditeur : afanou.k (01,02,05,06) ; leurres stagiaire.doc (03), presse.externe (04).
- cp:keywords des 4 fichiers afanou.k = fragments du flag.
- Ordre = dcterms:created : 01(2025-01-14) 02(2025-02-01) 06(2025-03-25) 05(2025-05-10).
  NCTF{ooxml_ + core_xml_ + lastmodifiedby + _leak}

## Commande
```bash
for f in *.docx; do unzip -p $f docProps/core.xml; done  # lire keywords + lastModifiedBy + created
```

## Flag
`NCTF{ooxml_core_xml_lastmodifiedby_leak}`
