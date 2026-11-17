
#include <Arduino.h>
#include <MD_MAX72xx.h>

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

void setup() {
    Serial.begin(115200);

    matriz.begin();
    matriz.control(MD_MAX72XX::INTENSITY, 3);
    matriz.clear();
}

void loop() {
    matriz.clear();

    byte coracao[8] = {
        B00000000,
        B01100110,
        B11111111,
        B11111111,
        B01111110,
        B00111100,
        B00011000,
        B00000000
    };

    for (int linha = 0; linha < 8; linha++) {
        matriz.setRow(0, linha, coracao[linha]);
    }

    delay(3000);
}
