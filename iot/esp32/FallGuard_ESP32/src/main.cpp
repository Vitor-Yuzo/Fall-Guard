
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

// Wi-Fi
const char* ssid = "Yuzo";
const char* password = "12345678";

// MQTT
const char* mqtt_server = "10.212.237.57";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

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

void conectarMQTT() {
    while (!client.connected()) {
        Serial.print("Conectando ao MQTT...");

        if (client.connect("FallGuard_ESP32")) {
            Serial.println(" conectado!");

            client.subscribe("fallguard/alertas");
        } else {
            Serial.print(" falhou. Estado: ");
            Serial.println(client.state());
            delay(3000);
        }
    }
}

void receberMensagem(char* topic, byte* payload, unsigned int length) {
    Serial.print("Mensagem recebida: ");

    for (unsigned int i = 0; i < length; i++) {
        Serial.print((char)payload[i]);
    }

    Serial.println();
}

void setup() {
    Serial.begin(115200);
    conectarWiFi();

    Serial.println("Testando conexao TCP com Mosquitto...");

    WiFiClient teste;
    if (teste.connect(mqtt_server, mqtt_port)) {
        Serial.println("TCP CONECTADO!");
        teste.stop();
    } else {
        Serial.println("FALHA NA CONEXAO TCP!");
    }

    client.setServer(mqtt_server, mqtt_port);
    client.setCallback(receberMensagem);
}
void loop() {
    if (!client.connected()) {
        conectarMQTT();
    }

    client.loop();
}
