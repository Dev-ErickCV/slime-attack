import pygame
import sys
import math
import random 

pygame.init()
pygame.font.init()
fuente = pygame.font.SysFont("Arial", 20, bold=True)
fuente_grande = pygame.font.SysFont("Arial", 40, bold=True)

ancho_pantalla = 620
alto_pantalla = 440
modo_fullscreen = False
pantalla_real = pygame.display.set_mode((ancho_pantalla, alto_pantalla), pygame.RESIZABLE)

pantalla = pygame.Surface((ancho_pantalla, alto_pantalla))
reloj = pygame.time.Clock()

def mostrar_pantalla():
    ancho_real, alto_real = pantalla_real.get_size()
    escala = min(ancho_real / ancho_pantalla, alto_real / alto_pantalla)

    ancho_escalado = int(ancho_pantalla * escala)
    alto_escalado = int(alto_pantalla * escala)

    offset_x = (ancho_real - ancho_escalado) // 2
    offset_y = (alto_real - alto_escalado) // 2

    pantalla_escalada = pygame.transform.scale(
        pantalla,
        (ancho_escalado, alto_escalado)
    )

    pantalla_real.fill((0, 0, 0))
    pantalla_real.blit(pantalla_escalada, (offset_x, offset_y))
    pygame.display.flip()

#texturas
sprite_piso = pygame.image.load("Sprites/pisox16.png").convert_alpha()
sprite_jugador = pygame.image.load("Sprites/smokix16.png").convert_alpha()
sprite_arma = pygame.image.load("Sprites/gunx16.png").convert_alpha()
sprite_ballet = pygame.image.load("Sprites/balletx16.png").convert_alpha()
sprite_slime = pygame.image.load("Sprites/slimex16.png").convert_alpha()
sprite_xp = pygame.image.load("Sprites/xpx16.png").convert_alpha()

tamaño_bloque = 16
limite_suelo = alto_pantalla - (tamaño_bloque * 3) - 16

jugador_x = 100
jugador_y = 376

arma_x = jugador_x + 8.5
arma_y = jugador_y

velocidad_x = 2
velocidad_y = 0
gravedad = 0.6
f_salto = -10
en_suelo = True
look_right = True

balas = []
velocidad_bala = 6

# slime y particulas
enemigos = []
particulas_polvo = [] 
fuerza_salto_slime = -11
tiempo_ultimo_spawn = pygame.time.get_ticks()
frecuencia_spawn = 3500

# vidas y daño
vidas_jugador = 3
inmune = False
tiempo_inmunidad = 1500
tiempo_ultimo_golpe = 0

# puntajes, experiencia, nivel de arma y estado de juego
puntaje = 0
nivel_arma = 1
xp_actual = 0
cristales_xp = []
corazones = []
pantalla_game_over = False

ejecutando = True
while ejecutando:
    pantalla.fill(pygame.Color("#5C9DAB"))
    tiempo_actual = pygame.time.get_ticks()

    if inmune and (tiempo_actual - tiempo_ultimo_golpe > tiempo_inmunidad):
        inmune = False

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
            
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_F11:
                modo_fullscreen = not modo_fullscreen

                if modo_fullscreen:
                    pantalla_real = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    pantalla_real = pygame.display.set_mode((ancho_pantalla, alto_pantalla), pygame.RESIZABLE)

            if evento.key == pygame.K_ESCAPE and modo_fullscreen:
                modo_fullscreen = False
                pantalla_real = pygame.display.set_mode((ancho_pantalla, alto_pantalla), pygame.RESIZABLE)

            if pantalla_game_over:
                vidas_jugador = 3
                puntaje = 0
                nivel_arma = 1
                xp_actual = 0
                enemigos.clear()
                balas.clear()
                cristales_xp.clear()
                corazones.clear()
                particulas_polvo.clear()
                jugador_x = 100
                jugador_y = 376
                frecuencia_spawn = 3500
                pantalla_game_over = False
            else:
                if evento.key == pygame.K_o:
                    bx = arma_x + (7 if look_right else -4)
                    by = arma_y - 3
                    direccion = 1 if look_right else -1
                    
                    rango_bala = (2.0 + min(nivel_arma - 1, 2) * 2.0) * 16

                    if nivel_arma == 1:
                        balas.append([bx, by, direccion, 0, rango_bala])
                    elif nivel_arma == 2:
                        balas.append([bx, by, direccion, 0, rango_bala])       
                        balas.append([bx, by + 3, direccion, 0, rango_bala])   
                    elif nivel_arma >= 3:
                        balas.append([bx, by, direccion, 0, rango_bala])       
                        balas.append([bx, by + 3, direccion, 0, rango_bala])   
                        balas.append([bx, by - 3, direccion, 0, rango_bala])   

    if pantalla_game_over:
        texto_puntaje = fuente.render(f"SCORE: {puntaje}", True, pygame.Color("white"))
        texto_go = fuente_grande.render("GAME OVER", True, pygame.Color("red"))
        texto_restart = fuente.render("Press any key to reload", True, pygame.Color("white"))
        pantalla.blit(texto_go, (ancho_pantalla // 2 - 100, alto_pantalla // 2 - 40))
        pantalla.blit(texto_puntaje, (ancho_pantalla // 2 - 100, alto_pantalla // 2 - 80))
        pantalla.blit(texto_restart, (ancho_pantalla // 2 - 100, alto_pantalla // 2 + 20))
        mostrar_pantalla()
        reloj.tick(60)
        continue

#taclas wtf
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_a]:
        jugador_x -= velocidad_x
        look_right = False
    if teclas[pygame.K_d]:
        jugador_x += velocidad_x
        look_right = True

    if teclas[pygame.K_p] and en_suelo:
        velocidad_y = f_salto
        en_suelo = False

    velocidad_y += gravedad
    jugador_y += velocidad_y

    if jugador_y >= limite_suelo:
        jugador_y = limite_suelo
        velocidad_y = 0
        en_suelo = True
        
    if look_right:
        jugador_final = sprite_jugador
        arma_final = sprite_arma
        arma_x = jugador_x + 8.5
        arma_y = jugador_y
    else:
        jugador_final = pygame.transform.flip(sprite_jugador, True, False)
        arma_final = pygame.transform.flip(sprite_arma, True, False)
        arma_x = jugador_x - 8.5
        arma_y = jugador_y

    rect_jugador = pygame.Rect(jugador_x, jugador_y, 16, 16)

    if not inmune or (tiempo_actual // 100 % 2 == 0):
        pantalla.blit(jugador_final, (jugador_x, jugador_y))
        pantalla.blit(arma_final, (arma_x, arma_y))
    
    # --- SPAWN DINÁMICO DE SLIMES SEGÚN NIVEL DE ARMA ---
    if tiempo_actual - tiempo_ultimo_spawn > frecuencia_spawn:
        lado_spawn = random.choice(["izquierda", "derecha"])

        if lado_spawn == "izquierda":
            spawn_x = -32
            direccion_slime = 1
        else:
            spawn_x = ancho_pantalla + 32
            direccion_slime = -1

        spawn_y = limite_suelo
        tipo_slime = "normal"

        if nivel_arma == 1:
            frecuencia_spawn = random.randint(2800, 4200)
            vel_x_slime = random.uniform(1.0, 3.0)
            hp_slime = 8

        elif nivel_arma == 2:
            frecuencia_spawn = random.randint(1200, 2200)

            prob = random.random()

            if prob < 0.20:
                hp_slime = 8
                vel_x_slime = random.uniform(2.0, 3.2)
            elif prob < 0.80:
                hp_slime = 12
                vel_x_slime = random.uniform(2.6, 4.0)
            else:
                hp_slime = 16
                vel_x_slime = random.uniform(2.3, 3.5)

        elif nivel_arma == 3:
            frecuencia_spawn = random.randint(900, 1700)

            prob = random.random()

            if prob < 0.45:
                lado_cielo = random.choice(["izquierda", "derecha"])

                if lado_cielo == "izquierda":
                    spawn_x = random.randint(0, 140)
                    direccion_slime = 1
                else:
                    spawn_x = random.randint(ancho_pantalla - 140, ancho_pantalla)
                    direccion_slime = -1

                spawn_y = -32
                hp_slime = 3
                vel_x_slime = random.uniform(1.2, 2.4)
                tipo_slime = "cielo"

            elif prob < 0.60:
                hp_slime = 8
                vel_x_slime = random.uniform(2.0, 3.4)

            elif prob < 0.80:
                hp_slime = 12
                vel_x_slime = random.uniform(2.4, 3.8)

            elif prob < 0.95:
                hp_slime = 16
                vel_x_slime = random.uniform(2.8, 4.4)

            else:
                hp_slime = 18
                vel_x_slime = random.uniform(2.2, 3.6)

                
        elif nivel_arma >= 4:
            frecuencia_spawn = random.randint(600, 1200)

            prob = random.random()

            if prob < 0.45:
                lado_cielo = random.choice(["izquierda", "derecha"])

                if lado_cielo == "izquierda":
                    spawn_x = random.randint(0, 140)
                    direccion_slime = 1
                else:
                    spawn_x = random.randint(ancho_pantalla - 140, ancho_pantalla - 16)
                    direccion_slime = -1

                spawn_y = -32
                hp_slime = 3
                vel_x_slime = random.uniform(1.2, 2.4)
                tipo_slime = "cielo"

            elif prob < 0.60:
                hp_slime = 8
                vel_x_slime = random.uniform(2.0, 3.4)

            elif prob < 0.80:
                hp_slime = 12
                vel_x_slime = random.uniform(2.4, 3.8)

            elif prob < 0.95:
                hp_slime = 16
                vel_x_slime = random.uniform(2.8, 4.4)

            else:
                hp_slime = 18
                vel_x_slime = random.uniform(2.2, 3.6)


        
        vel_y_slime = 0
        en_suelo_slime = True if spawn_y == limite_suelo else False
        proximo_salto = tiempo_actual + random.randint(400, 1200) 
        
        enemigos.append([
            spawn_x,
            spawn_y,
            direccion_slime,
            hp_slime,
            vel_y_slime,
            en_suelo_slime,
            proximo_salto,
            vel_x_slime,
            tipo_slime
        ])

        tiempo_ultimo_spawn = tiempo_actual

    # --- SLIME ACTUALIZAR Y FISICAS ---
    for enemigo in enemigos[:]:
        enemigo[4] += gravedad 
        enemigo[1] += enemigo[4] 
        
        if enemigo[1] >= limite_suelo:
            enemigo[1] = limite_suelo
            enemigo[4] = 0
            
            if not enemigo[5]: 
                for _ in range(4):
                    color = random.choice([(100, 100, 100), (50, 50, 50), (20, 20, 20)])
                    particulas_polvo.append([enemigo[0] + 8, enemigo[1] + 16, random.randint(2, 4), color, 20, random.uniform(-1, -0.2), random.uniform(-1, 1)])
            
            enemigo[5] = True 

        if enemigo[5] and tiempo_actual > enemigo[6]:
            enemigo[4] = fuerza_salto_slime 
            enemigo[5] = False
            enemigo[6] = tiempo_actual + random.randint(800, 2000) 

        if not enemigo[5]:
            enemigo[0] += enemigo[7] * enemigo[2]
            
            if random.random() < 0.4:
                color = random.choice([(120, 120, 120), (60, 60, 60)])
                particulas_polvo.append([enemigo[0] + 8 + random.uniform(-4, 4), enemigo[1] + 14, random.randint(1, 3), color, 15, random.uniform(-0.5, 0), random.uniform(-0.2, 0.2)])

        pantalla.blit(sprite_slime, (enemigo[0], enemigo[1]))
        
        color_hp = pygame.Color("red") if enemigo[3] > 8 else pygame.Color("white")
        texto_hp_slime = fuente.render(str(enemigo[3]), True, color_hp)
        pantalla.blit(texto_hp_slime, (enemigo[0] + 2, enemigo[1] - 18))

        rect_slime = pygame.Rect(enemigo[0], enemigo[1], 16, 16)

        if rect_jugador.colliderect(rect_slime):
            if not inmune and vidas_jugador > 0:
                vidas_jugador -= 1
                inmune = True
                tiempo_ultimo_golpe = tiempo_actual
                
                if nivel_arma == 4:
                    nivel_arma = 3
                    xp_actual = 0
                elif nivel_arma == 3:
                    nivel_arma = 2
                    xp_actual = 0
                elif nivel_arma == 2:
                    nivel_arma = 1
                    xp_actual = 0
                elif nivel_arma == 1:
                    xp_actual = 0

                if vidas_jugador <= 0:
                    pantalla_game_over = True
                    
        if enemigo[0] < -80 or enemigo[0] > ancho_pantalla + 80 or enemigo[1] > alto_pantalla + 80:
            enemigos.remove(enemigo)

    # --- DIBUJAR Y ACTUALIZAR POLVO ---
    for particula in particulas_polvo[:]:
        particula[4] -= 1 
        particula[0] += particula[6] 
        particula[1] += particula[5] 
        
        radio_actual = max(0, particula[2] * (particula[4] / 20.0))
        
        if particula[4] <= 0:
            particulas_polvo.remove(particula)
        else:
            pygame.draw.circle(pantalla, particula[3], (int(particula[0]), int(particula[1])), int(radio_actual))

    # balas actualizar, dibujar y colisiones
    for bala in balas[:]:
        desplazamiento = velocidad_bala * bala[2]
        bala[0] += desplazamiento
        bala[3] += abs(desplazamiento)

        rect_bala = pygame.Rect(bala[0], bala[1], 8, 8) 
        bala_destruida = False

        if bala[3] <= bala[4]:
            for enemigo in enemigos[:]:
                rect_enemigo = pygame.Rect(enemigo[0], enemigo[1], 16, 16)

                if rect_bala.colliderect(rect_enemigo):
                    enemigo[3] -= 1  
                    bala_destruida = True
                    
                    if enemigo[3] <= 0:
                        xp_soltada = 2 if enemigo[3] == -1 else 1

                        for _ in range(xp_soltada):
                            cristales_xp.append([
                                enemigo[0] + random.randint(-5, 5),
                                enemigo[1],
                                random.randint(0, 360)
                            ])

                        if random.random() < 0.35:
                            corazones.append([
                                enemigo[0] + random.randint(-5, 5),
                                enemigo[1]
                            ])

                        enemigos.remove(enemigo)
                        puntaje += 8

                    break

            if bala_destruida:
                balas.remove(bala)
            else:
                if bala[2] == 1:
                    pantalla.blit(sprite_ballet, (bala[0], bala[1]))
                else:
                    pantalla.blit(pygame.transform.flip(sprite_ballet, True, False), (bala[0], bala[1]))
        else:
            balas.remove(bala)

    # corazones curativos
    for corazon in corazones[:]:
        desfase_y = math.sin(tiempo_actual * 0.005) * 4
        y_flotando = corazon[1] + desfase_y

        pygame.draw.circle(
            pantalla,
            pygame.Color("red"),
            (int(corazon[0] + 8), int(y_flotando + 8)),
            5
        )

        pygame.draw.circle(
            pantalla,
            pygame.Color("#FF7777"),
            (int(corazon[0] + 6), int(y_flotando + 6)),
            2
        )

        rect_corazon = pygame.Rect(corazon[0], corazon[1], 16, 16)

        if rect_jugador.colliderect(rect_corazon):
            corazones.remove(corazon)

            if vidas_jugador < 5:
                vidas_jugador += 1

    # cristales XP
    for xp in cristales_xp[:]:
        xp[2] = (xp[2] + 5) % 360
        sprite_rotado = pygame.transform.rotate(sprite_xp, xp[2])
        nuevo_rect = sprite_rotado.get_rect()
        
        desfase_y = math.sin(tiempo_actual * 0.005) * 4
        y_flotando = xp[1] + desfase_y
        nuevo_rect.center = (xp[0] + 8, y_flotando + 8)
        pantalla.blit(sprite_rotado, nuevo_rect.topleft)

        rect_xp_colision = pygame.Rect(xp[0], xp[1], 16, 16)

        if rect_jugador.colliderect(rect_xp_colision):
            cristales_xp.remove(xp)
            
            if nivel_arma == 1:
                xp_actual += 1
                if xp_actual >= 3:
                    nivel_arma = 2
                    xp_actual = 0

            elif nivel_arma == 2:
                xp_actual += 1
                if xp_actual >= 5:
                    nivel_arma = 3
                    xp_actual = 0

            elif nivel_arma == 3:
                xp_actual += 1
                if xp_actual >= 5:
                    nivel_arma = 4
                    xp_actual = 0

    # piso:
    y_inicio = alto_pantalla - (tamaño_bloque * 3)
    y_fin = alto_pantalla

    for y in range(y_inicio, y_fin, tamaño_bloque):
        for x in range(0, ancho_pantalla, tamaño_bloque):
            pantalla.blit(sprite_piso, (x, y))

    # textos de interfaz en pantalla
    texto_vidas = fuente.render(f"HP: {vidas_jugador}", True, pygame.Color("white"))
    texto_puntos = fuente.render(f"SCORE: {puntaje}", True, pygame.Color("white"))
    
    if nivel_arma == 4:
        texto_nivel = fuente.render("ARMA: LVL 3 (MAX)", True, pygame.Color("orange"))
        texto_xp = fuente.render("XP: MAX", True, pygame.Color("yellow"))
    else:
        texto_nivel = fuente.render(f"ARMA: LVL {nivel_arma}", True, pygame.Color("orange"))
        meta_xp = 3 if nivel_arma == 1 else 5
        texto_xp = fuente.render(f"XP: {xp_actual} / {meta_xp}", True, pygame.Color("yellow"))
    
    pantalla.blit(texto_vidas, (20, 20))
    pantalla.blit(texto_puntos, (20, 45))
    pantalla.blit(texto_nivel, (20, 70))  
    pantalla.blit(texto_xp, (20, 95))     

    mostrar_pantalla()
    reloj.tick(60)

pygame.quit()
sys.exit()
