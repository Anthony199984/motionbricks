# cielos_hdri — 12 cielos HDRI 4K EXR (CC0, Poly Haven)

Subido el 18 de noviembre de 2026 a la rama `recursos`, carpeta `recursos/out/cielos_hdri/`.
No toca `main` ni el modelo.

## Qué es

Un ZIP (`cielos_hdri_antonydfilms.zip`, 593.686.622 bytes, unos 566 MiB) con 12 HDRI
equirectangulares 4K (4096 × 2048) en OpenEXR, bajados de Poly Haven. Todos son CC0:
no hace falta dar crédito (es opcional). El ZIP va partido en **25 partes** de 23 MiB
(24.117.248 bytes cada una; la última, `.024`, pesa 14.872.670 bytes), así que todas
quedan por debajo del límite de 90 MB.

| # | Archivo dentro del ZIP | Uso |
|---|---|---|
| 1 | `campo_sol_01_noon_grass_4k.exr` | Campo de día, sol y cielo azul |
| 2 | `campo_sol_02_sunflowers_4k.exr` | Campo de día, sol y cielo azul |
| 3 | `campo_sol_03_hay_bales_4k.exr` | Campo de día, sol y cielo azul |
| 4 | `campo_nublado_01_farmland_overcast_4k.exr` | Campo nublado, luz suave |
| 5 | `campo_nublado_02_belfast_open_field_4k.exr` | Campo nublado, luz suave |
| 6 | `amanecer_campo_01_spruit_sunrise_4k.exr` | Amanecer en el campo |
| 7 | `amanecer_campo_02_bloem_field_sunrise_4k.exr` | Amanecer en el campo |
| 8 | `atardecer_campo_01_farm_sunset_4k.exr` | Atardecer en el campo |
| 9 | `atardecer_campo_02_straw_rolls_field_01_4k.exr` | Atardecer en el campo |
| 10 | `ciudad_dia_01_wide_street_01_4k.exr` | Ciudad o calle de día |
| 11 | `granero_interior_01_hayloft_4k.exr` | Interior de granero |
| 12 | `noche_luna_01_moonlit_golf_4k.exr` | Noche con luna |

Los detalles de cada uno (autor, enlace, descripción, tamaño) están en `LEEME.txt`.

Nota: `hay_bales` y `farm_sunset` ya estaban en `recursos/out/hdri/` en 4K `.hdr`.
Estos son la versión EXR.

## Archivos de esta carpeta

- `cielos_hdri_antonydfilms.zip.000` … `.024`: las partes, tal cual llegaron.
- `SHA256SUMS.txt`: la suma SHA-256 de cada parte y del ZIP unido.
- `COMO_UNIR.txt`: cómo unir y verificar. Se corrigió para que diga 25 partes de 23 MiB,
  porque la versión original hablaba de 7 partes de 90 MiB y no coincidía con estas partes.
- `LEEME.txt`: la lista original de los 12 HDRI.

## Estado de la subida

COMPLETO: están las 25 partes (000 a 024), todas verificadas con SHA-256.

- El 18 nov 2026 se unieron las 25 partes. El ZIP resultante pesa 593.686.622 bytes y da SHA-256
  `ece22a3db12a09f2276792c847a45bf748625a04453451b37065c9c7403b966b`, que coincide con `SHA256SUMS.txt`.
  `unzip -t` no da errores.
- Historia de la 004: la primera copia llegó dañada (42.904.388 bytes, convertida como texto)
  y no se subió. La buena llegó comprimida con gzip (`.bin.gz`), y tras descomprimirla pesa
  24.117.248 bytes con el SHA-256 correcto. Para pasar binarios por el chat funciona mandarlos
  como `.bin` o `.bin.gz`.

### Revisión de los EXR (18 nov 2026)

Se descomprimió el ZIP en una carpeta vacía y se abrieron los 12 EXR con OpenEXR. Los 12 miden
4096 × 2048, usan compresión PIZ, tienen valores HDR reales y ningún píxel roto. Sus tamaños
coinciden con `LEEME.txt`. Todos están bien.

Ojo: `atardecer_campo_01_farm_sunset_4k.exr` pesa 96.947.614 bytes, más de 90 MB. Si algún día
se sube suelto (fuera del ZIP), tiene que ir partido en la rama `pesados`.

## Unir (resumen)

```
cat cielos_hdri_antonydfilms.zip.[0-9][0-9][0-9] > cielos_hdri_antonydfilms.zip
sha256sum cielos_hdri_antonydfilms.zip
# debe dar ece22a3db12a09f2276792c847a45bf748625a04453451b37065c9c7403b966b
```
