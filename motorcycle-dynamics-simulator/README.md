Simulador de Dinâmica Veicular em Python

✨ Sobre o Projeto


Este é meu projeto final de graduação em Engenharia Mecânica no CEFET/RJ com foco em simulação física de veículos terrestres. Ele nasceu do Trabalho de Conclusão de Curso do João Marcos Cavalcante da Silva na UFRJ (2023), que desenvolveu uma versão funcional para carros com base em dinâmica longitudinal e lateral. A partir desse núcleo original, **estou dando continuidade ao projeto com o desenvolvimento de uma versão dedicada a motocicletas.

O objetivo principal continua o mesmo: criar um simulador automotivo, didático e acessível — usando apenas Python puro, equações analíticas e fundamentos da engenharia mecânica.

🧩 Estrutura Modular


O simulador está organizado em alguns arquivos principais:

Arquivo	Função
loop.py	    Coração da simulação. Realiza os cálculos ponto a ponto com base na física do movimento.

roots.py	Resolve a equação de Torricelli adaptada com restrições físicas (potência, aderência, geometria).

tools.py	Conjunto de funções auxiliares: interpolação de trajetos, cálculo de raios, inclinação, curvas de potência,         filtragens e processamentos de dados de telemetria.

velocity_correction.py    executa a lógica de correção de velocidades em uma dada iteração para um trajeto que está sendo simulado, quando os limites de aderência do veículo não são respeitados no trecho correspondente 

print_functions.py     Funções auxiliares para o monitoramento de simulações e debug do código 


🎯 Meu Objetivo (Motocicletas)


A missão atual é adaptar e validar o simulador para veículos de duas rodas, respeitando as diferenças dinâmicas fundamentais entre carros e motos, utilizando também uma modelagem didática e simplificada, baseada na literatura acadêmica do tema. Além de realizar algumas melhorias e otimizações no algoritmo computacional 

🔍 O que o simulador já faz (versão carro)


Simula a evolução de velocidade ao longo de uma trajetória 3D usando apenas equações analíticas

Considera forças reais: peso, arrasto, rolamento, tração e sustentação

Respeita os limites de aderência combinada (Elipse de Tração)

Aplica a equação de Torricelli ponto a ponto, com validação física de cada solução

Permite simulação com ou sem marchas, incluindo cálculo de RPM e curvas de potência realistas

Gera DataFrame completo com: distância, velocidade, acelerações, força longitudinal, tempo, marcha, etc.

🛠 Como Usar


1. Instale as dependências:

bash
Copiar
Editar
pip install numpy pandas matplotlib shapely scipy

2. Prepare os dados:

Você precisará de listas com as coordenadas x, y, z da pista, além de parâmetros físicos e geométricos do veículo.

3. Rode a simulação:

python
Copiar
Editar
from loop_original import loop

resultado = loop(
    fx=1, fy=1, x=x, y=y, z=z, P=90, m=210, Cl=0.2, Cd=0.35, Af=0.9,
    Crr=0.015, ld=1, lt=1, h=0.3, Tracao='D', Vo=0, Frenagem=1,
    Vmax=180, mu=1.2, nu=1,
    marcha=True, Ps=[...], ns=[...],
    finaldrive=4.2, gearslist=[3.2, 2.1, 1.3, 1.0, 0.8], rw=0.3
)

4. Visualize os resultados:

python
Copiar
Editar
from tools_original import graph
graph(resultado)

📘 Documentação Teórica


Toda a fundamentação física e computacional está documentada no TCC original do João Marcos Cavalcante (UFRJ, 2023), que cobre:

Forças atuantes (arrasto, peso, tração, rolamento, sustentação)

Cinemática lateral e longitudinal

Acoplamento dinâmico via Círculo de Kamm

Adaptação da equação de Torricelli para restrições de aceleração

Estou estendendo esse conteúdo agora para cobrir aspectos específicos da dinâmica de motocicletas.

🧪 Saídas da Simulação


O programa retorna um pandas.DataFrame com as seguintes colunas:

Distance (m)

Speed (m/s)

Ax (m/s²) — aceleração longitudinal

Ay (m/s²) — aceleração lateral

Force (N) — força resultante longitudinal

Time (s)

Gears, GRatios, RPM — se simulação com marchas estiver ativada

👤 Créditos


João Marcos Cavalcante da Silva — autor original da versão para carro

Gabriel Cândido Passos — responsável pela nova versão para motos e manutenção atual do projeto

📜 Licença


Uso livre para fins educacionais e acadêmicos. Para outros usos, entre em contato.
