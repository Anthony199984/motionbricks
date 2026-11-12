# ROPA 3D para un personaje masculino de 1,87 m · Antonydfilms (12 nov 2026)

18 prendas sueltas (cada una es SOLO ropa, sin cuerpo) + 1 maniquí neutro + la hoja con 4 conjuntos.
**No están puestas en Max**: eso lo hace el otro chat cuando el cuerpo de Max esté listo.

## Cómo vienen los .glb
- Metros, Y arriba, frente hacia +Z (lo normal en glTF). Al cargarlos en el motor (Z arriba) el frente queda hacia -Y.
- Cada prenda ya está **a la altura de un hombre de 1,87 m**: la camiseta en el torso, el pantalón con la pretina a
  1,07 m, los zapatos en el piso con los pies a x = ±0,185 m. Si cargas una camiseta, un pantalón y unos zapatos
  sin moverlos, quedan armados como en la hoja.
- Normales y orden de triángulos ya corregidos (varios modelos venían con la tela gris o con manchas por eso).
- Texturas dentro de cada .glb. Los zapatos vienen en par (izquierdo en espejo del derecho).
- **Son mallas fijas, sin esqueleto ni pesos**: para que se muevan con un personaje hay que ajustarlas a su cuerpo y
  ligarlas a sus huesos (trabajo del otro chat).

## Conjuntos de la hoja (hoja_conjuntos_ropa.png)
1. Casual: camiseta_blanca + jeans_clasico + tenis_lona
2. Deportivo: sudadera_capucha + pantalon_deportivo + tenis_correr
3. Elegante: camisa_blanca + pantalon_vestir + zapato_oxford
4. Fin de semana: polo_azul + jeans_azul + tenis_blancos
Extras para combinar: camiseta_gris, camiseta_rayas, polo_blanco, camisa_cuadros, zapato_cuero_viejo, zapato_casual.

## Trucos que se usaron en la hoja (el código está en herramientas/)
- La parte del pantalón que queda bajo la camiseta se mete 22 % hacia el cuerpo (`conjunto.meter_bajo`): si no, la
  pretina atraviesa la tela de arriba.
- El maniquí se adelgaza dentro de la ropa y sus brazos se giran/corren para ir por el centro de cada manga
  (`conjunto.brazo_auto`). Con un personaje real pasa lo mismo: hay que ajustar la ropa a SU cuerpo.

## Pesos (triángulos)
Los más pesados: pantalon_vestir (2 millones, pespuntes en 3D), jeans_azul (1 millón, hilos en 3D),
camiseta_gris (373 mil), pantalon_deportivo (368 mil). Si pesan mucho en una toma, se pueden aligerar.
