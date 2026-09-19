import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# CHARGEGRID INTELLIGENCE
# ANÁLISE DOS DADOS DAS SESSÕES
# ==========================================

# Dados coletados no Wokwi
dados = {
    "Sessao": [1, 2, 3, 4],
    "Duracao_s": [12.8, 18.3, 14.6, 24.6],
    "Temperatura_C": [24.0, 24.0, 24.0, 24.0],
    "Energia_solar_kW": [5.0, 4.0, 2.5, 5.5],
    "Energia_utilizada_kWh": [0.0064, 0.0092, 0.0000, 0.0124],
    "Resultado": [
        "RECARGA NORMAL",
        "RECARGA NORMAL",
        "ENERGIA BAIXA",
        "RECARGA NORMAL"
    ]
}

# Criar DataFrame
df = pd.DataFrame(dados)

# Mostrar tabela
print("===== DADOS DAS SESSÕES =====")
display(df)

# ==========================================
# ESTATÍSTICAS
# ==========================================

print("\n===== ESTATÍSTICAS =====")

print(f"Duração média: {df['Duracao_s'].mean():.2f} segundos")
print(f"Temperatura média: {df['Temperatura_C'].mean():.2f} °C")
print(f"Energia solar média: {df['Energia_solar_kW'].mean():.2f} kW")
print(f"Energia utilizada total: {df['Energia_utilizada_kWh'].sum():.4f} kWh")

# ==========================================
# MAIOR DURAÇÃO
# ==========================================

maior_duracao = df.loc[df["Duracao_s"].idxmax()]

print("\n===== MAIOR DURAÇÃO =====")
print(f"Sessão: {int(maior_duracao['Sessao'])}")
print(f"Duração: {maior_duracao['Duracao_s']:.1f} segundos")

# ==========================================
# MAIOR ENERGIA UTILIZADA
# ==========================================

maior_energia = df.loc[df["Energia_utilizada_kWh"].idxmax()]

print("\n===== MAIOR ENERGIA UTILIZADA =====")
print(f"Sessão: {int(maior_energia['Sessao'])}")
print(f"Energia: {maior_energia['Energia_utilizada_kWh']:.4f} kWh")

# ==========================================
# RESULTADOS
# ==========================================

print("\n===== RESULTADOS DAS SESSÕES =====")
print(df["Resultado"].value_counts())

# ==========================================
# GRÁFICO 1 - ENERGIA SOLAR
# ==========================================

plt.figure(figsize=(8, 5))

plt.bar(df["Sessao"], df["Energia_solar_kW"])

plt.xlabel("Sessão")
plt.ylabel("Energia solar (kW)")
plt.title("Energia solar disponível por sessão")
plt.xticks(df["Sessao"])

plt.show()

# ==========================================
# GRÁFICO 2 - ENERGIA UTILIZADA
# ==========================================

plt.figure(figsize=(8, 5))

plt.bar(df["Sessao"], df["Energia_utilizada_kWh"])

plt.xlabel("Sessão")
plt.ylabel("Energia utilizada (kWh)")
plt.title("Energia utilizada nas sessões")
plt.xticks(df["Sessao"])

plt.show()

# ==========================================
# GRÁFICO 3 - DURAÇÃO
# ==========================================

plt.figure(figsize=(8, 5))

plt.bar(df["Sessao"], df["Duracao_s"])

plt.xlabel("Sessão")
plt.ylabel("Duração (segundos)")
plt.title("Duração das sessões de recarga")
plt.xticks(df["Sessao"])

plt.show()
