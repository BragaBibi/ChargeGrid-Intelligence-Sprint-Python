from machine import Pin, I2C
import dht
import time
from i2c_lcd import I2cLcd

# ==========================================
# CHARGEGRID INTELLIGENCE
# Sistema inteligente de gerenciamento de recarga
# ==========================================

# Componentes
sensor_temp = dht.DHT22(Pin(16))

botao_veiculo = Pin(14, Pin.IN, Pin.PULL_UP)
botao_mais = Pin(17, Pin.IN, Pin.PULL_UP)
botao_menos = Pin(18, Pin.IN, Pin.PULL_UP)

led_recarga = Pin(15, Pin.OUT)

# Configurações
ENERGIA_MINIMA = 3.0
TEMPERATURA_MAXIMA = 40.0
POTENCIA_RECARGA = 3.3
energia_solar = 5.0

# LCD I2C
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

def mostrar_lcd(linha1, linha2):
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(str(linha1)[:16])
    lcd.move_to(0, 1)
    lcd.putstr(str(linha2)[:16])

def ler_temperatura():
    try:
        sensor_temp.measure()
        return sensor_temp.temperature()
    except Exception:
        return 25.0

def atualizar_tempo_recarga(recarga_ativa):
    global tempo_recarga, inicio_trecho_recarga
    agora = time.ticks_ms()

    if recarga_ativa:
        if inicio_trecho_recarga is None:
            inicio_trecho_recarga = agora
    else:
        if inicio_trecho_recarga is not None:
            decorrido = time.ticks_diff(agora, inicio_trecho_recarga)
            tempo_recarga += decorrido / 1000
            inicio_trecho_recarga = None

# Estados
ultimo_veiculo = 1
ultimo_mais = 1
ultimo_menos = 1
veiculo_conectado = False

numero_sessao = 0
sessao_ativa = False
inicio_sessao = 0
tempo_recarga = 0.0
inicio_trecho_recarga = None
historico_sessoes = []
motivo_sessao = "RECARGA NORMAL"

print("========================================")
print("       CHARGEGRID INTELLIGENCE")
print("          SISTEMA INICIADO")
print("========================================")

mostrar_lcd("CHARGEGRID", "SISTEMA ONLINE")
time.sleep(2)

# Loop principal
while True:
    estado_veiculo = botao_veiculo.value()

    # Detecta pressionamento do botão do veículo
    if estado_veiculo == 0 and ultimo_veiculo == 1:
        estava_conectado = veiculo_conectado
        veiculo_conectado = not veiculo_conectado

        # Inicia uma nova sessão
        if not estava_conectado and veiculo_conectado:
            numero_sessao += 1
            sessao_ativa = True
            inicio_sessao = time.ticks_ms()
            tempo_recarga = 0.0
            inicio_trecho_recarga = None
            motivo_sessao = "RECARGA NORMAL"

            print()
            print("========================================")
            print("       NOVA SESSAO DE RECARGA")
            print("       SESSAO:", numero_sessao)
            print("========================================")

        # Finaliza a sessão quando o veículo é desconectado
        elif estava_conectado and not veiculo_conectado:
            atualizar_tempo_recarga(False)

            if sessao_ativa:
                duracao = time.ticks_diff(
                    time.ticks_ms(), inicio_sessao
                ) / 1000

                energia_utilizada = (
                    POTENCIA_RECARGA * tempo_recarga / 3600
                )
                temperatura_final = ler_temperatura()

                sessao = {
                    "numero": numero_sessao,
                    "duracao": duracao,
                    "temperatura": temperatura_final,
                    "energia_solar": energia_solar,
                    "tempo_recarga": tempo_recarga,
                    "energia_utilizada": energia_utilizada,
                    "resultado": motivo_sessao
                }
                historico_sessoes.append(sessao)
                sessao_ativa = False

                print()
                print("========================================")
                print("          SESSAO FINALIZADA")
                print("========================================")
                print("Sessao:", numero_sessao)
                print("Duracao: %.1f segundos" % duracao)
                print("Temperatura: %.1f C" % temperatura_final)
                print("Energia solar: %.1f kW" % energia_solar)
                print("Tempo de recarga: %.1f segundos" % tempo_recarga)
                print("Energia utilizada: %.4f kWh" % energia_utilizada)
                print("Resultado:", motivo_sessao)
                print("========================================")
                print("CSV:")
                print("%d;%.1f;%.1f;%.1f;%.4f;%s" % (
                    numero_sessao,
                    duracao,
                    temperatura_final,
                    energia_solar,
                    energia_utilizada,
                    motivo_sessao
                ))
                print()
                motivo_sessao = "RECARGA NORMAL"

    ultimo_veiculo = estado_veiculo

    # Botão +: aumenta a energia solar em 0,5 kW
    estado_mais = botao_mais.value()
    if estado_mais == 0 and ultimo_mais == 1:
        energia_solar += 0.5
        if energia_solar > 6.0:
            energia_solar = 6.0
        print("ENERGIA SOLAR AUMENTADA:", energia_solar, "kW")
        time.sleep(0.2)
    ultimo_mais = estado_mais

    # Botão -: reduz a energia solar em 0,5 kW
    estado_menos = botao_menos.value()
    if estado_menos == 0 and ultimo_menos == 1:
        energia_solar -= 0.5
        if energia_solar < 0.0:
            energia_solar = 0.0
        print("ENERGIA SOLAR REDUZIDA:", energia_solar, "kW")
        time.sleep(0.2)
    ultimo_menos = estado_menos

    # Monitoramento e decisão automática
    temperatura = ler_temperatura()

    if not veiculo_conectado:
        status = "VEICULO OFF"
        motivo_sessao = "RECARGA NORMAL"
        led_recarga.value(0)
        mostrar_lcd("VEICULO OFF", "AGUARDANDO...")

    elif temperatura > TEMPERATURA_MAXIMA:
        status = "TEMP. ALTA"
        motivo_sessao = "TEMPERATURA ALTA"
        led_recarga.value(0)
        mostrar_lcd("TEMP. ALTA!", "RECARGA OFF")

    elif energia_solar < ENERGIA_MINIMA:
        status = "ENERGIA BAIXA"
        motivo_sessao = "ENERGIA BAIXA"
        led_recarga.value(0)
        mostrar_lcd("ENERGIA BAIXA", "RECARGA OFF")

    else:
        status = "RECARGA ATIVA"
        motivo_sessao = "RECARGA NORMAL"
        led_recarga.value(1)
        mostrar_lcd("SOL: %.1f kW" % energia_solar, "RECARGA: ATIVA")

    recarga_ativa = (
        sessao_ativa
        and veiculo_conectado
        and temperatura <= TEMPERATURA_MAXIMA
        and energia_solar >= ENERGIA_MINIMA
    )
    atualizar_tempo_recarga(recarga_ativa)

    print("----------------------------------------")
    print("       CHARGEGRID INTELLIGENCE")
    print("----------------------------------------")
    print("Temperatura: %.1f C" % temperatura)
    print("Energia solar: %.1f kW" % energia_solar)
    print("Veiculo:", "CONECTADO" if veiculo_conectado else "DESCONECTADO")

    if sessao_ativa:
        print("Sessao:", numero_sessao)
        print("Tempo recarga: %.1f s" % tempo_recarga)

    print("STATUS:", status)
    print("----------------------------------------")

    time.sleep(0.5)
