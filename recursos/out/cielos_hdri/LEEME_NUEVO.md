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

PARCIAL: hay 22 de 25 partes subidas, todas verificadas con SHA-256.

- Subidas: 000, 001, 002, 003, 005, 006, 007, 008, 009, 010, 011, 012, 013, 014, 015,
  016, 017, 018, 019, 020, 021, 022.
- **Faltan: 004, 023, 024.**
- La 004 llegó el 18 nov 2026 pero DAÑADA: pesaba 42.904.388 bytes en vez de 24.117.248,
  porque algún paso la trató como texto y cambió unos 9,6 millones de bytes por el carácter
  de reemplazo "�". No se puede reparar: hay que volver a pedirla tal cual (archivo binario,
  sin convertir). No se subió. La buena debe pesar 24.117.248 bytes y dar SHA-256
  `6a384ee9a9f6ec802c2dd3de77d654cdb6ba8fd8c59eeecd93f63c5f58a877c4`. Truco que funcionó con la 022:
  mandarla con extensión `.bin` y renombrarla al subir.

Hasta que estén las 25, el ZIP completo no se puede unir ni dar el SHA-256
`ece22a3db12a09f2276792c847a45bf748625a04453451b37065c9c7403b966b`.

### Revisión de los EXR (18 nov 2026)

Las entradas que caen enteras dentro de las partes presentes se sacaron sin unir el ZIP,
y se comprobó su CRC32 del ZIP. Se abrieron con OpenEXR: 4096 × 2048, compresión PIZ y
valores HDR reales. Ninguna da problemas.

- OK (9 de 12): `campo_sol_01_noon_grass`, `campo_sol_02_sunflowers`,
  `campo_nublado_01_farmland_overcast`, `campo_nublado_02_belfast_open_field`,
  `amanecer_campo_01_spruit_sunrise`, `amanecer_campo_02_bloem_field_sunrise`,
  `atardecer_campo_01_farm_sunset`, `atardecer_campo_02_straw_rolls_field_01`, `ciudad_dia_01_wide_street_01`. También `LEEME.txt`.
- Sin revisar: `campo_sol_03_hay_bales` (necesita la 004), `granero_interior_01_hayloft`
  (022-023) y `noche_luna_01_moonlit_golf` (023-024).

Ojo: `atardecer_campo_01_farm_sunset_4k.exr` pesa 96.947.614 bytes, más de 90 MB. Si algún día
se sube suelto (fuera del ZIP), tiene que ir partido en la rama `pesados`.

## Unir (resumen)

```
cat cielos_hdri_antonydfilms.zip.[0-9][0-9][0-9] > cielos_hdri_antonydfilms.zip
sha256sum cielos_hdri_antonydfilms.zip
# debe dar ece22a3db12a09f2276792c847a45bf748625a04453451b37065c9c7403b966b
```
