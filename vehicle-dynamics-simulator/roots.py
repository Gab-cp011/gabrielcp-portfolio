from tools import *

def print_roots_info(x1, x12, x2, sol, inter=None, Vint=None):
    print(f"\n{'='*50}")
    print(" RESULTADO - Roots()")
    print(f"{'='*50}")
    print(f"x1   : {x1:.5f} m/s²")
    print(f"x12  : {x12:.5f} m/s²")
    print(f"x2   : {x2:.5f} m/s²")
    print(f"Válidos (soluções) : {sol}")
    if inter and Vint:
        print(f"\nIntervalo de aceleração permitido: {inter}")
        print(f"Velocidades correspondentes: {Vint}")
    print(f"{'='*50}\n")


def Roots(Vo, D, R, Axmax, Axmin, Aymax, slope, g, k,pcurve,m,Pv,marcha,P, verbose=False):
    def arealP(v,marcha):
        if marcha == True:
            if v < pcurve[1][0]:
                return Axmax
            else:
                return Pv(v)/m/v
        else:
            return P/m/v

    x1 = -((Axmin**2*Aymax**2*R**2*(4*Axmin**2*D**2 + \
    Aymax**2*(2*D*k*R + R)**2 - (Vo**2 - 2*D*g*slope)**2))**0.5 + \
    2*Axmin**2*D*Vo**2 + Aymax**2*R**2*(2*D*k + 1)*(g*slope +
    k*Vo**2))/(4*Axmin**2*D**2 + \
    Aymax**2*R**2*(2*D*k + 1)**2)

    x12 = ((Axmin**2*Aymax**2*R**2*(4*Axmin**2*D**2 + Aymax**2*(2*D*k*R +
    R)**2\
    - (Vo**2 - 2*D*g*slope)**2))**0.5 - 2*Axmin**2*D*Vo**2 - \
    Aymax**2*R**2*(2*D*k + 1)*(g*slope + k*Vo**2))/(4*Axmin**2*D**2\
    + Aymax**2*R**2*(2*D*k + 1)**2)

    x2 = ((Axmax**2*Aymax**2*R**2*(4*Axmax**2*D**2\
    + Aymax**2*(2*D*k*R + R)**2 - (Vo**2 - 2*D*g*slope)**2))**0.5\
    - 2*Axmax**2*D*Vo**2 - Aymax**2*R**2*(2*D*k + 1)*(g*slope + k*Vo**2))\
    /(4*Axmax**2*D**2 + Aymax**2*R**2*(2*D*k + 1)**2)

    sol = [x1,x12, x2]
    
    if verbose:
        print_roots_info(x1, x12, x2, sol)


    if type(x1) == float and x1 > -g * slope - k * (Vo ** 2 + x1 * D): # alteracao possível aqui, multiplicar por 2
        sol.remove(x1)

    if type(x2) == float and x2 < -g * slope - k * (Vo ** 2 + x2 * D): # alteracao possível aqui, multiplicar por 2
        sol.remove(x2)

    if type(x12) == float and x12 > -g * slope - k * (Vo ** 2 + x1 * D): # alteracao possível aqui, multiplicar por 2
        sol.remove(x12)

    sol = [i for i in sol if type(i) == float]
    
    sol = [i for i in sol if -Axmin - g * slope - k * (Vo ** 2 + 2*i * D)- 0.00001 <= i <= Axmax - g * slope - k * (Vo ** 2 + 2*i * D) + 0.00001] # alteracao possivel, multiplicar por 2 

    sol = [i for i in sol if type((Vo ** 2 + 2 * i * D) ** 0.5) == float]
    sol.sort()

    if len(sol) == 0:

        return False
    else:
        if len(sol) == 2:
            inter = sol
            Vint = [(Vo ** 2 + 2 * sol[0] * D) ** 0.5, (Vo ** 2 + 2 * sol[1] * D) ** 0.5]

        else:
            inter = [-Vo ** 2 / (2 * D), sol[0]]
            Vint = [0, (Vo ** 2 + 2 * sol[0] * D) ** 0.5]
            
    axreal = arealP(Vint[1],marcha) - k*Vint[1]**2 - g*slope
    if axreal >= inter[1]:
        pass
    else:# #corrigir para que a aceleracao maxima seja guiada pela potencia:
        if inter[1] <= 0:
            pass
        else:
            inter[1] = axreal
            Vint[1] = float((Vo ** 2 + 2 * inter[1] * D) ** 0.5)
    return inter, Vint