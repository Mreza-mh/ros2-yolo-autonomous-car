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

int SPEED_FORWARD_DEFAULT = 80;
int SPEED_TURN = 205;
int TURN_SAFE_SPEED = 80;
int TURN_DURATION_MS = 2000;
int SPEED_FADE_STEP = 3;
int SPEED_STOP_DECAY = 6;
int MIN_SPEED = 20;
int COMMAND_TIMEOUT_MS = 4000;

// ================= LED MODES =================
enum LedMode { LED_FORWARD, LED_TURNING, LED_STOPPED };
LedMode currentLedMode = LED_STOPPED;
unsigned long ledTimer = 0;
bool ledState = false;

// ================= STATE =================
int driveSpeedCurrent = 0;
int driveSpeedTarget = 0;

enum TurnState { TURN_NONE, TURN_SLOWING, TURN_ACTIVE };
TurnState turnState = TURN_NONE;

bool turnLeft = false;
int speedBeforeTurn = 0;
unsigned long turnStartTime = 0;

unsigned long lastCommandTime = 0;
bool stopLocked = false;

// ================= LED LOGIC =================
void updateLed() {
  unsigned long now = millis();

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
  }
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

  driveSpeedCurrent = constrain(driveSpeedCurrent, 0, 255);

  if (driveSpeedTarget > 0 && driveSpeedCurrent < MIN_SPEED)
    driveSpeedCurrent = MIN_SPEED;

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
  if (turnState == TURN_SLOWING &&
      driveSpeedCurrent <= TURN_SAFE_SPEED + 10) {

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
    currentLedMode = LED_FORWARD;
  }
}

// ================= COMMAND PARSE =================
bool isLeftCmd(String c) {
  return c == "LEFT" || c == "TURNLEFT";
}

bool isRightCmd(String c) {
  return c == "RIGHT" || c == "TURNRIGHT";
}

void handleCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();

  lastCommandTime = millis();

  // ---------- STOP ----------
  if (cmd == "STOP") {
    stopLocked = true;
    driveSpeedTarget = 0;
    steerCenter();
    turnState = TURN_NONE;
    currentLedMode = LED_STOPPED;
    return;
  }

  // ---------- GO (only unlock STOP) ----------
  if (cmd == "GO") {
    stopLocked = false;
    driveSpeedTarget = SPEED_FORWARD_DEFAULT;
    steerCenter();
    currentLedMode = LED_FORWARD;
    return;
  }

  // ---------- If STOP is active, ignore others ----------
  if (stopLocked) return;

  // ---------- TURN ----------
  if (isLeftCmd(cmd)) {
    beginTurn(true);
    return;
  }

  if (isRightCmd(cmd)) {
    beginTurn(false);
    return;
  }
}

// ================= IDLE BEHAVIOR =================
void autoIdle() {
  if (stopLocked) return;
  if (turnState != TURN_NONE) return;

  if (millis() - lastCommandTime > COMMAND_TIMEOUT_MS) {
    driveSpeedTarget = SPEED_FORWARD_DEFAULT;
    steerCenter();
    currentLedMode = LED_FORWARD;
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

  // Default state: forward
  driveSpeedTarget = SPEED_FORWARD_DEFAULT;
  currentLedMode = LED_FORWARD;
  lastCommandTime = millis();

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) delay(200);

  udp.begin(UDP_PORT);
}

void loop() {
  int packet = udp.parsePacket();
  if (packet) {
    char buf[32];
    int len = udp.read(buf, 31);
    buf[len] = 0;
    handleCommand(String(buf));
  }

  updateTurn();
  updateDriveSpeed();
  autoIdle();
  updateLed();

  delay(10);
}
