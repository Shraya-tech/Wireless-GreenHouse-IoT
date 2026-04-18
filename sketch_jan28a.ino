#include <WiFi.h>
#include <esp_now.h>

// Structure to receive data (must match sender)
typedef struct {
    int randomValue;
} receivedData;

receivedData myData;

// Callback function to handle received data
void OnDataRecv(const uint8_t *mac_addr, const uint8_t *incomingData, int len) {
    // Copy received data to myData structure
    memcpy(&myData, incomingData, sizeof(myData));

    // Display received integer on Serial Monitor
    Serial.print("Received: ");
    Serial.println(myData.randomValue);
}

void setup() {
    Serial.begin(115200);
    WiFi.mode(WIFI_STA);

    // Initialize ESP-NOW
    if (esp_now_init() != ESP_OK) {
        Serial.println("Error initializing ESP-NOW");
        return;
    }

    // Register receive callback
    esp_now_register_recv_cb((esp_now_recv_cb_t)OnDataRecv);
}

void loop() {
    // Nothing to do in loop; data is handled by callback
}   