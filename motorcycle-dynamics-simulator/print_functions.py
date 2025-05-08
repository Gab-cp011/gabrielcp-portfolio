def print_iteration_info(i, V, D, R, slope, Axmax, Aymax, intervalo):
    print(f"{'-'*40}")
    print(f" Iteração {i}")
    print(f"{'-'*40}")
    print(f"Velocidade     : {V:.2f} m/s")
    print(f"Distância      : {D:.2f} m")
    print(f"Raio           : {R:.2f} m")
    print(f"Inclinação     : {slope:.5f} rad")
    print(f"Acel. Long. Max: {Axmax:.5f} m/s²")
    print(f"Acel. Lat. Max : {Aymax:.5f} m/s²")
    print(f"Intervalo      : {intervalo}")
    print(f"{'='*40}\n")

# Função detalhada de entrada no ELSE (mantida como está)
def print_else_entry(i, j, R, V, AymaxL, AxmaxL, slope, D):
    print(f"\n{'*'*70}")
    print(f" ENTRANDO NO ELSE → i={i}, j={j}")
    print(f"{'*'*70}")
    print(f"Raio Atual     R[i-j]   : {R[i-j]:.5f} m")
    if (i-j-1) >= 0:
        print(f"Raio Anterior  R[i-j-1] : {R[i-j-1]:.5f} m")
    else:
        print("Raio Anterior  R[i-j-1] : inexistente")

    print(f"Velocidade Atual V[i-j]   : {V[i-j]:.5f} m/s")
    if (i-j-1) >= 0:
        print(f"Velocidade Anterior V[i-j-1] : {V[i-j-1]:.5f} m/s")
    else:
        print("Velocidade Anterior V[i-j-1] : inexistente")

    print(f"Aceleração Lateral Máxima Aymax[i-j] : {AymaxL[i-j]:.5f} m/s²")
    print(f"Aceleração Longitudinal Máxima Axmax[i-j] : {AxmaxL[i-j]:.5f} m/s²")
    print(f"Slope (inclinação) [i-j] : {slope[i-j]:.5f} rad")
    print(f"Distância D[i-j] : {D[i-j]:.5f} m")
    print(f"{'*'*70}\n")

# Prints enxutos para ajustes de velocidades
def print_v_info(i, j, Vymax, Vij):
    print(f"[Backward Pass] i={i}, j={j}")
    print(f"Vymax calculado : {Vymax:.5f} m/s")
    print(f"V[i-j] corrigido: {Vij:.5f} m/s\n")

def print_adjust_info(i, j, V, x1N, D):
    print(f"[Ajustando Velocidade] i={i}, j={j}")
    print(f"V[i-j] atual    : {V[i-j]:.5f} m/s")
    print(f"x1N usado       : {x1N:.5f} m/s²")
    print(f"D[i-j-1]        : {D[i-j-1]:.5f} m")
    print(f"Novo V[i-j-1]   : {V[i-j-1]:.5f} m/s\n")

def print_root_short(i, j, intervalo, Vcalc):
    print(f"[Roots Encontrado] i={i}, j={j}")
    print(f"Intervalo permitido: [{intervalo[0]:.5f}, {intervalo[1]:.5f}]")
    print(f"Velocidade candidata: {Vcalc:.5f} m/s\n")

def print_iterador(j):
    print(f"[Iterador Atualizado] j = {j}\n")

def print_debug_raiz_x1n(i, j, V, R, AymaxL, x1N_bruto=None, x1N_ajustado=None):
    argumento = 1 - (V[i - j] ** 4) / (R[i - j - 1] ** 2 * AymaxL[i - j - 1] ** 2)

    print("\n" + "="*70)
    print(f"[DEBUG RAIZ E x1N] i={i}, j={j}")
    print("="*70)
    print(f"Argumento da raiz crítica         : {argumento:.8f} (deve ser >= 0)")

    if argumento < 0:
        print("⚠️ Atenção: argumento negativo! Pode gerar raiz complexa.")

    # Parte condicional: valores de x1N só são mostrados se forem fornecidos
    if x1N_bruto is None or x1N_ajustado is None:
        print("ℹ️ x1N ainda não calculado — pré-verificação da raiz.")
    else:
        print(f"x1N calculado (bruto)             : {x1N_bruto}")
        print(f"x1N final após ajuste             : {x1N_ajustado}")

        if isinstance(x1N_bruto, complex):
            print("⚠️ x1N bruto é número complexo!")
        if isinstance(x1N_ajustado, complex):
            print("⚠️ x1N ajustado é número complexo!")

        if abs(x1N_bruto - x1N_ajustado) < 1e-6:
            print(f"Motivo do ajuste                  : Sem ajuste necessário")
        elif x1N_ajustado < x1N_bruto:
            print(f"Motivo do ajuste                  : Limitado inferior")
        elif x1N_ajustado > x1N_bruto:
            print(f"Motivo do ajuste                  : Limitado superior")
        else:
            print(f"Motivo do ajuste                  : Valor modificado (outro critério)")
    print("="*70 + "\n")


def print_caminho_correcao(i, j, metodo, contagem_metodo=None, contagem_sucesso=None):
    print("\n" + "-" * 70)
    print(f"[RESUMO DA CORREÇÃO] i={i}, j={j}")
    print(f"Método de correção adotado       : {metodo}")

    if contagem_metodo:
        total_metodos = sum(contagem_metodo.values())
        print("\n------------------ Tipo de Correção ------------------")
        for nome, contagem in contagem_metodo.items():
            porcentagem = (contagem / total_metodos * 100) if total_metodos > 0 else 0
            print(f"  {nome:<30}: {contagem:>5}  ({porcentagem:5.1f}%)")

    if contagem_sucesso:
        total_sucesso = sum(contagem_sucesso.values())
        print("\n-------------- Profundidade da Correção --------------")
        for nome, contagem in contagem_sucesso.items():
            porcentagem = (contagem / total_sucesso * 100) if total_sucesso > 0 else 0
            print(f"  {nome:<30}: {contagem:>5}  ({porcentagem:5.1f}%)")

    print("-" * 70 + "\n")











