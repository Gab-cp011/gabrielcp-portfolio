
from print_functions import * 
from new_roots import *

def corrigir_velocidade(i, V, R, D, slope, AxmaxL, Axmin, AymaxL, k, g,
                        pcurve, m, Pv, marcha, P, mu,
                        contagem_metodo, contagem_sucesso):
    """
    Realiza correção retroativa da velocidade caso Roots retorne False,
    respeitando os limites impostos pelo Círculo de Kamm e Equação de Torricelli.
    Atualiza separadamente:
        - o método de correção utilizado (direto ou via V1),
        - e a profundidade da correção (j == 0 ou j > 0).
    """

    j = 0
    #print(f'[INÍCIO CORREÇÃO]i={i}')
    print_else_entry(i, j, R, V, AymaxL, AxmaxL, slope, D)
    Vymax = ((R[i - j] * AymaxL[i - j]) ** 0.5) * 0.99

    Vi_corrigido = ((Vymax ** 2 + (2 * g * slope[i - j] * D[i - j]) / (1 + D[i - j] * k)) /
                    (1 - (2 * D[i - j] * k) / (1 + k * D[i - j]))) ** 0.5

    metodo_corrigido = "Correção por Torricelli Modificado"

    # Verifica se a correção direta é inválida
    if isinstance(Vi_corrigido, complex) or Vi_corrigido > Vymax:
        V1 = (-(AxmaxL[i - j] ** 2 * AymaxL[i - j] ** 2 * R[i - j] ** 2 *
                (AxmaxL[i - j] ** 2 + AymaxL[i - j] ** 2 * (k ** 2) * R[i - j] ** 2
                 - g ** 2 * slope[i - j] ** 2)) ** 0.5 +
              AymaxL[i - j] ** 2 * g * k * R[i - j] ** 2 * slope[i - j]) / \
             (AxmaxL[i - j] ** 2 + AymaxL[i - j] ** 2 * (k ** 2) * R[i - j] ** 2)

        Vi_corrigido = abs(V1) ** 0.5
        Vymax = Vi_corrigido
        metodo_corrigido = "Correção por fórmula V1"

    # Atualiza contador do método utilizado
    if contagem_metodo is not None and metodo_corrigido in contagem_metodo:
        contagem_metodo[metodo_corrigido] += 1

    V[i - j] = Vi_corrigido
    print_v_info(i, j, Vymax, V[i - j])
    V.append(Vymax)

    # Tenta retroagir, se necessário
    while (i - j) >= 2:
        Vi_ant = V[i - j - 1]

        print(f"Debug: i={i}, j={j}, R={R[i-j-1]:.5f}, D={D[i-j-1]:.5f}")

        intervalo = Roots(
            Vi_ant, D[i - j - 1], R[i - j - 1],
            AxmaxL[i - j - 1], Axmin, AymaxL[i - j - 1],
            slope[i - j - 1], g, k,
            pcurve, m, Pv, marcha, P, verbose=False
        )[1]

        Vcalc = (V[i - j - 1]**2 + 2 * intervalo[1] * D[i - j - 1]) ** 0.5
        print_root_short(i, j, intervalo, Vcalc)

        if intervalo[0] <= V[i - j] <= intervalo[1]:
            break
        else:
            print_debug_raiz_x1n(i, j, V, R, AymaxL)

            #teste, colocar o argumento fora da fórmula do x1N
            argumento = 1 - V[i - j] ** 4 / (R[i - j - 1] ** 2 * AymaxL[i - j - 1] ** 2)

            x1N = (
                -Axmin * (argumento) ** 0.5
                - g * slope[i - j - 1]
                - k * V[i - j - 1] ** 2
            ) / (1 + k * D[i - j - 1])

            x1N_bruto = x1N
            x1N_ajustado = x1N_bruto

            if x1N_ajustado > V[i - j] ** 2 / (2 * D[i - j - 1]):
                x1N_ajustado = V[i - j] ** 2 / (2 * D[i - j - 1]) * 0.99

            if x1N_ajustado < (-Axmin - g * slope[i - j - 1] - k * V[i - j - 1] ** 2):
                x1N_ajustado = -Axmin - g * slope[i - j - 1] - k * V[i - j - 1] ** 2

            print_debug_raiz_x1n(i, j, V, R, AymaxL, x1N_bruto, x1N_ajustado)

            V[i - j - 1] = (V[i - j] ** 2 - 2 * x1N_ajustado * D[i - j - 1]) ** 0.5
            print_adjust_info(i, j, V, x1N_ajustado, D)

            j += 1
            print_iterador(j)

    # Atualiza o contador de sucesso (profundidade da correção)
    if contagem_sucesso is not None:
        if j == 0:
            contagem_sucesso["Correção local (j=0) "] += 1
        else:
            contagem_sucesso["Correção retroativa (j>0) "] += 1

    print_caminho_correcao(i, j, metodo_corrigido, contagem_metodo, contagem_sucesso)

    return V
