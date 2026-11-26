
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <MD_MAX72xx.h>

// =====================================
// MATRIZ MAX7219
// =====================================

#define HARDWARE_TYPE MD_MAX72XX::FC16_HW
#define MAX_DEVICES 1

#define DATA_PIN 23
#define CLK_PIN 18
#define CS_PIN 5

MD_MAX72XX matriz(
    HARDWARE_TYPE,
    DATA_PIN,
    CLK_PIN,
    CS_PIN,
    MAX_DEVICES
);

// =====================================
// BUZZER
// =====================================

#define BUZZER_PIN 25

bool alertaAtivo = false;
bool buzzerLigado = false;

unsigned long ultimoBip = 0;

const unsigned long TEMPO_LIGADO = 200;
const unsigned long TEMPO_DESLIGADO = 800;

// =====================================
// WI-FI
// =====================================

//const char* ssid = "Yuzo";
//const char* password = "12345678";

const char* ssid = "CLARO_A830DC";
const char* password = "tYc9XTAYNx";

// =====================================
// MQTT
// =====================================

//const char* mqtt_server = "10.174.234.57";
const char* mqtt_server = "192.168.0.183";
const int mqtt_port = 1883;
const char* mqtt_topic = "fallguard/alertas";

WiFiClient espClient;
PubSubClient client(espClient);

// =====================================
// ALERTA VISUAL
// =====================================

void exibirAlerta() {

    byte alerta[8] = {
        B00011000,
        B00011000,
        B00011000,
        B00011000,
        B00011000,
        B00000000,
        B00011000,
        B00000000
    };

    matriz.clear();

    for (int linha = 0; linha < 8; linha++) {
        matriz.setRow(0, linha, alerta[linha]);
    }

    Serial.println("Alerta visual ativado!");
}

void limparAlerta() {

    matriz.clear();

    Serial.println("Alerta visual desativado.");
}

// =====================================
// CONTROLE SONORO
// =====================================

void atualizarBuzzer() {

    if (!alertaAtivo) {
        return;
    }

    unsigned long agora = millis();

    unsigned long intervalo = buzzerLigado
        ? TEMPO_LIGADO
        : TEMPO_DESLIGADO;

    if (agora - ultimoBip >= intervalo) {

        buzzerLigado = !buzzerLigado;

        digitalWrite(
            BUZZER_PIN,
            buzzerLigado ? LOW : HIGH
        );

        ultimoBip = agora;
    }
}

void iniciarAlerta() {

    alertaAtivo = true;

    exibirAlerta();

    buzzerLigado = true;
    digitalWrite(BUZZER_PIN, LOW);

    ultimoBip = millis();

    Serial.println("Alerta sonoro ativado!");
}

void encerrarAlerta() {

    alertaAtivo = false;
    buzzerLigado = false;

    digitalWrite(BUZZER_PIN, HIGH);

    limparAlerta();

    Serial.println("Alerta sonoro desativado!");
}

// =====================================
// CONEXAO WI-FI
// =====================================

void conectarWiFi() {

    Serial.print("Conectando ao Wi-Fi");

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nWi-Fi conectado!");
    Serial.println(WiFi.localIP());
}

// =====================================
// RECEBIMENTO MQTT
// =====================================

void receberMensagem(
    char* topic,
    byte* payload,
    unsigned int length
) {

    String mensagem = "";

    for (unsigned int i = 0; i < length; i++) {
        mensagem += (char)payload[i];
    }

    Serial.print("Mensagem recebida: ");
    Serial.println(mensagem);

    if (mensagem == "QUEDA_DETECTADA") {

        iniciarAlerta();

    } else if (mensagem == "NORMAL") {

        encerrarAlerta();

    }
}

// =====================================
// CONEXAO MQTT
// =====================================

void conectarMQTT() {

    while (!client.connected()) {

        Serial.print("Conectando ao MQTT...");

        if (client.connect("FallGuard_ESP32")) {

            Serial.println(" conectado!");

            client.subscribe(mqtt_topic);

        } else {

            Serial.print(" falhou. Estado: ");
            Serial.println(client.state());

            delay(3000);
        }
    }
}

// =====================================
// SETUP
// =====================================

void setup() {

    Serial.begin(115200);

    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, HIGH);

    matriz.begin();
    matriz.control(MD_MAX72XX::INTENSITY, 3);
    matriz.clear();

    conectarWiFi();

    client.setServer(mqtt_server, mqtt_port);
    client.setCallback(receberMensagem);

    conectarMQTT();

    Serial.println("FallGuard ativo!");
}

// =====================================
// LOOP PRINCIPAL
// =====================================

void loop() {

    if (!client.connected()) {
        conectarMQTT();
    }

    client.loop();

    atualizarBuzzer();
}
