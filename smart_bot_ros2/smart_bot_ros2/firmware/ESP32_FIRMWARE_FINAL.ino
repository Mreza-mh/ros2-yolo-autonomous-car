#include <WiFi.h>
#include <WiFiUdp.h>

// ================= WIFI =================
const char* WIFI_SSID = "Kk";
const char* WIFI_PASS = "11111111";
WiFiUDP udp;
unsigned int UDP_PORT = 8889;

// ================= STEERING MOTOR =================
#define STEER_IN1 19
#define STEER_IN2 20
#define STEER_PWM 47

// ================= DRIVE MOTOR =================
#define DRIVE_IN1 21
#define DRIVE_IN2 48
#define DRIVE_PWM 14

// ================= LED =================
#define LED_PIN 2

// ================= TUNING =================
int SPEED_FORWARD_DEFAULT = 75;
int SPEED_TURN = 180;
int TURN_SAFE_SPEED = 60;
int TURN_DURATION_MS = 1400;
int SPEED_FADE_STEP = 3;
int SPEED_STOP_DECAY = 6;
int MIN_SPEED = 20;
int COMMAND_TIMEOUT_MS = 4000;

// ================= LED MODES =================
enum LedMode { LED_FORWARD, LED_TURNING, LED_STOPPED, LED_TIMEOUT, LED_DATA_RECEIVED };
LedMode currentLedMode = LED_STOPPED;
unsigned long ledTimer = 0;
bool ledState = false;
unsigned long dataReceivedFlashTime = 0;
bool dataReceivedFlashActive = false;

// ================= STATE =================
int driveSpeedCurrent = 0;
int driveSpeedTarget = 0;

enum TurnState { TURN_NONE, TURN_SLOWING, TURN_ACTIVE };
TurnState turnState = TURN_NONE;

bool turnLeft = false;
int speedBeforeTurn = 0;
unsigned long turnStartTime = 0;

unsigned long lastCommandTime = 0;
String lastCommand = "STOP";
bool stopLocked = false;

// ================= LED LOGIC =================
void updateLed() {
  unsigned long now = millis();

  // Handle data received flash (overrides other modes for 400ms)
  // This provides clear visual feedback that data was received
  if (dataReceivedFlashActive) {
    unsigned long elapsed = now - dataReceivedFlashTime;
    // Double flash: ON-OFF-ON-OFF pattern (more visible)
    if (elapsed < 80) {
      digitalWrite(LED_PIN, HIGH);   // Flash ON (0-80ms)
    } else if (elapsed < 160) {
      digitalWrite(LED_PIN, LOW);    // Flash OFF (80-160ms)
    } else if (elapsed < 240) {
      digitalWrite(LED_PIN, HIGH);   // Flash ON again (160-240ms)
    } else if (elapsed < 320) {
      digitalWrite(LED_PIN, LOW);    // Flash OFF (240-320ms)
    } else {
      dataReceivedFlashActive = false;  // Flash complete
    }
    
    // Stay in flash mode while active
    if (dataReceivedFlashActive) {
      return;
    }
  }

  // Normal LED modes (when not flashing)
  switch (currentLedMode) {
    case LED_FORWARD:
      digitalWrite(LED_PIN, HIGH);
      break;

    case LED_TURNING:
      if (now - ledTimer > 150) {
        ledTimer = now;
        ledState = !ledState;
        digitalWrite(LED_PIN, ledState);
      }
      break;

    case LED_STOPPED:
      if (now - ledTimer > 1000) {
        ledTimer = now;
        ledState = !ledState;
        digitalWrite(LED_PIN, ledState);
      }
      break;

    case LED_TIMEOUT:
      if ((now / 200) % 2 == 0)
        digitalWrite(LED_PIN, HIGH);
      else
        digitalWrite(LED_PIN, LOW);
      break;

    default:
      digitalWrite(LED_PIN, LOW);
      break;
  }
}

void flashLedOnDataReceived() {
  dataReceivedFlashTime = millis();
  dataReceivedFlashActive = true;
}

// ================= MOTOR =================
void steerCenter() {
  digitalWrite(STEER_IN1, LOW);
  digitalWrite(STEER_IN2, LOW);
  analogWrite(STEER_PWM, 0);
}

void steerLeft() {
  digitalWrite(STEER_IN1, LOW);
  digitalWrite(STEER_IN2, HIGH);
  analogWrite(STEER_PWM, SPEED_TURN);
}

void steerRight() {
  digitalWrite(STEER_IN1, HIGH);
  digitalWrite(STEER_IN2, LOW);
  analogWrite(STEER_PWM, SPEED_TURN);
}

void driveMotor(int speed) {
  if (speed > 0) {
    digitalWrite(DRIVE_IN1, HIGH);
    digitalWrite(DRIVE_IN2, LOW);
    analogWrite(DRIVE_PWM, speed);
  } else {
    digitalWrite(DRIVE_IN1, LOW);
    digitalWrite(DRIVE_IN2, LOW);
    analogWrite(DRIVE_PWM, 0);
  }
}

// ================= SPEED RAMP =================
void updateDriveSpeed() {
  if (driveSpeedCurrent < driveSpeedTarget)
    driveSpeedCurrent += SPEED_FADE_STEP;
  else if (driveSpeedCurrent > driveSpeedTarget)
    driveSpeedCurrent -= SPEED_STOP_DECAY;

  driveSpeedCurrent = constrain(driveSpeedCurrent, MIN_SPEED, 255);

  driveMotor(driveSpeedCurrent);
}

// ================= TURN =================
void beginTurn(bool left) {
  if (turnState != TURN_NONE) return;

  turnLeft = left;
  speedBeforeTurn = driveSpeedTarget;
  driveSpeedTarget = TURN_SAFE_SPEED;
  turnState = TURN_SLOWING;
  currentLedMode = LED_TURNING;
}

void updateTurn() {
  if (turnState == TURN_NONE) return;

  if (turnState == TURN_SLOWING &&
      driveSpeedCurrent <= TURN_SAFE_SPEED + 15) {

    if (turnLeft) steerLeft();
    else steerRight();

    turnState = TURN_ACTIVE;
    turnStartTime = millis();
  }

  if (turnState == TURN_ACTIVE &&
      millis() - turnStartTime > TURN_DURATION_MS) {

    steerCenter();
    driveSpeedTarget = speedBeforeTurn;
    turnState = TURN_NONE;

    currentLedMode = (driveSpeedTarget > 0) ? LED_FORWARD : LED_STOPPED;
  }
}

// ================= COMMAND PARSE =================
bool isLeftCmd(String c) {
  return c == "LEFT" || c == "LLEFT" || c == "TURNLEFT";
}

bool isRightCmd(String c) {
  return c == "RIGHT" || c == "RRIGHT" || c == "TURNRIGHT";
}

void handleCommand(String cmd) {
  // Clean and normalize command
  cmd.trim();
  cmd.toUpperCase();  // Arduino String: toUpperCase() modifies in place, returns void

  lastCommand = cmd;
  lastCommandTime = millis();
  
  // Flash LED to show data received - THIS SHOULD ALWAYS HAPPEN
  flashLedOnDataReceived();
  
  // Serial logging - ASCII only to avoid encoding issues
  Serial.print("[RX] CMD: ");
  Serial.println(cmd);

  if (cmd == "STOP") {
    stopLocked = true;
    driveSpeedTarget = 0;
    steerCenter();
    turnState = TURN_NONE;
    currentLedMode = LED_STOPPED;
    Serial.println("[OK] STOP executed");
    return;
  }

  // بعد از stop، فقط دستورات LEFT/RIGHT/GO اجازه حرکت دارن
  if (stopLocked) {
    if (cmd == "LEFT" || cmd == "RIGHT" || cmd == "GO" || cmd == "FORWARD") {
      stopLocked = false;
    } else {
      Serial.println("[IGNORED] Command blocked (stop locked)");
      return;
    }
  }

  if (cmd == "LEFT") {
    Serial.println("[OK] LEFT turn initiated");
    beginTurn(true);
    return;
  }

  if (cmd == "RIGHT") {
    Serial.println("[OK] RIGHT turn initiated");
    beginTurn(false);
    return;
  }

  if (cmd == "FORWARD" || cmd == "UP" || cmd == "W" || cmd == "GO") {
    driveSpeedTarget = SPEED_FORWARD_DEFAULT;
    if (turnState == TURN_NONE) steerCenter();  // اگر در حال چرخش نیست، مرکز کن
    currentLedMode = LED_FORWARD;
    Serial.println("[OK] GO (forward) executed");
    return;
  }

  // هر دستور دیگه → برو جلو
  driveSpeedTarget = SPEED_FORWARD_DEFAULT;
  if (turnState == TURN_NONE) steerCenter();
  currentLedMode = LED_FORWARD;
}

// ================= SAFETY =================
void autoSafety() {
  if (millis() - lastCommandTime > COMMAND_TIMEOUT_MS && lastCommand != "STOP" && !stopLocked) {
    driveSpeedTarget = 0;
    steerCenter();
    currentLedMode = LED_TIMEOUT;
    ledTimer = millis();
  }
}

// ================= SETUP / LOOP =================
void setup() {
  Serial.begin(115200);

  pinMode(STEER_IN1, OUTPUT);
  pinMode(STEER_IN2, OUTPUT);
  pinMode(STEER_PWM, OUTPUT);

  pinMode(DRIVE_IN1, OUTPUT);
  pinMode(DRIVE_IN2, OUTPUT);
  pinMode(DRIVE_PWM, OUTPUT);

  pinMode(LED_PIN, OUTPUT);

  steerCenter();
  driveMotor(0);

  // Test LED at startup
  Serial.println("=== ESP32 Smart Bot ===");
  Serial.println("Testing LED...");
  for (int i = 0; i < 5; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }
  Serial.println("LED test complete");
  
  Serial.println("Starting WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  int wifiAttempts = 0;
  while (WiFi.status() != WL_CONNECTED && wifiAttempts < 50) {
    delay(200);
    Serial.print(".");
    wifiAttempts++;
  }
  Serial.println("");
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi OK! IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi FAILED!");
  }

  udp.begin(UDP_PORT);
  Serial.print("UDP listening on port: ");
  Serial.println(UDP_PORT);
  Serial.println("=== READY ===");
  Serial.println("Send commands: LEFT, RIGHT, GO, STOP");
}

void loop() {
  // Check for UDP packets
  int packetSize = udp.parsePacket();
  if (packetSize > 0) {
    // Read packet
    char buf[32];
    int len = udp.read(buf, min(31, packetSize));  // Read up to buffer size
    buf[len] = 0;  // Null terminate
    
    // Log received packet info
    Serial.print("[UDP] Packet received (");
    Serial.print(len);
    Serial.print(" bytes) from ");
    Serial.print(udp.remoteIP());
    Serial.print(":");
    Serial.println(udp.remotePort());
    
    // Process command
    handleCommand(String(buf));
  }

  // Update motors and LED
  updateTurn();
  updateDriveSpeed();
  autoSafety();
  updateLed();

  delay(10);
}


