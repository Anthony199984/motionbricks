"""Prendas elegidas: de dónde salen, cómo se giran (Z arriba, frente -Y), a qué medida van y qué tela llevan.
Medidas para un hombre de 1,87 m: cuello ~1,58 m, cintura del pantalón ~1,07 m, pies en z=0 con los centros en x=±0,185.
R = giros (rx, ry, rz) en grados después de pasar de Y arriba a Z arriba.
arriba: z_top = altura del borde más alto (cuello); alto = largo total; ancho = ancho del cuerpo de la prenda a 1,22 m
        (esc_xy lo fija a mano cuando las mangas estorban la medida); brazo = grados que el maniquí sube los brazos.
abajo: z_top = altura de la pretina; alto = largo hasta el ruedo; ancho = ancho a la altura de la cadera (0,96 m).
zapato: largo (m); un zapato suelto se gira solo (punta a -Y) y se copia en espejo para el otro pie.
tela: tejido de Poly Haven; solo_relieve = conserva el color de la prenda y agrega el tejido (relieve + tono)."""

PRENDAS = {
    # --------------------------------------------------------------- camisetas / polos / camisas / sudaderas
    'camiseta_blanca':   dict(src='c_tshirt_blanca46k', tipo='arriba', R=(0, 0, -90), z_top=1.635, alto=.76, ancho=.40,
                              tela=dict(id='cotton_jersey', solo_relieve=True, rep=.12)),
    'camiseta_gris':     dict(src='c_tshirt_oscura', tipo='arriba', z_top=1.635, alto=.76,
                              tela=dict(id='jersey_melange', solo_relieve=True, rep=.15)),
    'camiseta_rayas':    dict(src='c_tshirt_rayas', tipo='arriba', z_top=1.635, alto=.76),
    'polo_blanco':       dict(src='c_polo_blanco', tipo='arriba', z_top=1.66, alto=.78,
                              tela=dict(id='waffle_pique_cotton', solo_relieve=True, rep=.06)),
    'polo_azul':         dict(src='c_polo_azul', tipo='arriba', z_top=1.66, alto=.78,
                              tela=dict(id='waffle_pique_cotton', solo_relieve=True, rep=.06)),
    'camisa_blanca':     dict(src='c_camisa_md', tipo='arriba', z_top=1.69, alto=.84, esc_xy=1.0, brazo='auto', manga_larga=True,
                              colores=[], blanco=True,
                              tela=dict(id='stretch_poplin', solo_relieve=True, rep=.08)),
    'camisa_cuadros':    dict(src='c_camisa_cuadros', tipo='arriba', z_top=1.68, alto=.84, esc_xy=1.0),
    'sudadera_capucha':  dict(src='c_hoodie_amarillo', tipo='arriba', z_top=1.84, alto=1.0, esc_xy=1.16, brazo='auto', manga_larga=True,
                              tela=dict(id='knitted_fleece', solo_relieve=True, rep=.12)),
    # --------------------------------------------------------------- pantalones
    'jeans_azul':        dict(src='c_jeans_levis', tipo='abajo', z_top=1.07, alto=1.07),
    'jeans_clasico':     dict(src='c_jeans_male', tipo='abajo', z_top=1.07, alto=1.07),
    'pantalon_vestir':   dict(src='c_pant_costura', tipo='abajo', z_top=1.08, alto=1.08,
                              tela=dict(id='poly_wool_herringbone', tinte=(.40, .40, .44), rep=.10, cuales=[0], rough=.85),
                              colores=[((.78, .6, .04), (.10, .10, .11)), ((.91, .91, .91), (.12, .12, .13))]),
    'pantalon_deportivo': dict(src='c_sweatpants', tipo='abajo', z_top=1.07, alto=1.05,
                              tela=dict(id='jogging_melange', solo_relieve=True, rep=.15)),
    # --------------------------------------------------------------- zapatos
    'tenis_lona':        dict(src='c_converse_chuck', tipo='zapato', partes=[0, 1, 2, 3, 4], largo=.30, dy=-.045),
    'tenis_correr':      dict(src='c_asics', tipo='zapato', largo=.305, dy=-.045),
    'tenis_blancos':     dict(src='c_common_projects', tipo='zapato', largo=.30, dy=-.045),
    'zapato_oxford':     dict(src='c_oxford', tipo='zapato', largo=.305, dy=-.045),
    'zapato_cuero_viejo': dict(src='c_oxford_viejo', tipo='zapato', largo=.30, dy=-.045),
    'zapato_casual':     dict(src='c_ecco_cuero', tipo='zapato', largo=.30, dy=-.045),
}

CONJUNTOS = [
    ('Casual', ['camiseta_blanca', 'jeans_clasico', 'tenis_lona']),
    ('Deportivo', ['sudadera_capucha', 'pantalon_deportivo', 'tenis_correr']),
    ('Elegante', ['camisa_blanca', 'pantalon_vestir', 'zapato_oxford']),
    ('Fin de semana', ['polo_azul', 'jeans_azul', 'tenis_blancos']),
]
