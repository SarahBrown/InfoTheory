#include <WiFi.h>

// motor controller pins
#define MOTOR_L_IA  14
#define MOTOR_L_IB  27
#define MOTOR_R_IA  26
#define MOTOR_R_IB  25

#define MOTOR_L_IA_PWM 0
#define MOTOR_L_IB_PWM 1
#define MOTOR_R_IA_PWM 2
#define MOTOR_R_IB_PWM 3

// sensor pins
#define ULTRASONIC  16
#define ENCODER_L   18
#define ENCODER_R   19

#define SPEED_SLOW 200
#define SPEED_FAST 255
#define DIR_DELAY  1000

#define SERVER_PORT 23

WiFiServer server(SERVER_PORT);
WiFiClient wifi_client;

const char* ssid = "WIFI NAME";
const char* password =  "WIFI PASS";

volatile unsigned int counter_l; // left side is motor a
volatile unsigned int counter_r; // right side is motor b
volatile unsigned int limit_l = 1; 
volatile unsigned int limit_r = 1; 

void configPWM(int GPIO_pin, int PWM_Ch, int PWM_Freq, int PWM_Res) {
  // pwm channel 0-15, pwm res 1bit-16bits, pwm frequency
  ledcAttachPin(GPIO_pin, PWM_Ch);  
  ledcSetup(PWM_Ch, PWM_Freq, PWM_Res);
}

void setup()
{
    Serial.begin(115200);

    configPWM(MOTOR_L_IA, MOTOR_L_IA_PWM, 30000, 8);
    configPWM(MOTOR_L_IB, MOTOR_L_IB_PWM, 30000, 8);
    configPWM(MOTOR_R_IA, MOTOR_R_IA_PWM, 30000, 8);
    configPWM(MOTOR_R_IB, MOTOR_R_IB_PWM, 30000, 8);
  
    pinMode(ENCODER_L,  INPUT);
    pinMode(ENCODER_R,  INPUT);

    attachInterrupt(ENCODER_L, pulsecount_l, CHANGE);
    attachInterrupt(ENCODER_R, pulsecount_r, CHANGE);
    
    Serial.println();
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected.");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    
    server.begin();
    
}

void pulsecount_l() {
  counter_l++;

  if (counter_l > limit_l) {
    left_stop();
  }
}

void pulsecount_r() {
    counter_r++;

    if (counter_r > limit_r) {
      right_stop();
    }
}

void checkForConnections() {
  if (server.hasClient()) {
    if (wifi_client.connected()) {
      Serial.println("Connection rejected");
      server.available().stop();
    }

    else {
      Serial.println("Connection accepted");
      wifi_client = server.available();
    }
  }
}

// function to test wifi
void echoReceivedData() {
  uint8_t buff[30];
  while (wifi_client.connected() && wifi_client.available()) {
    int count = wifi_client.read(buff, sizeof(buff));

    Serial.print(count);
    Serial.print(" characters received -- '");

    for (int i = 0; i < count; i++) {
      Serial.print((char)(buff[i]));
    }
    Serial.println("'");

    wifi_client.write(buff, count);
  }
}

int ultrasonicDistance() {
  // trigger ultrasonic sensor with a 2 usec high pulse
  pinMode(ULTRASONIC, OUTPUT);
  digitalWrite(ULTRASONIC, HIGH);
  delayMicroseconds(2);
  digitalWrite(ULTRASONIC, LOW);
  
  // reads distance in usec and converts to cm
  // speed of sound at (0.034 cm/usec). divide for 2 for just there distance not there and back
   pinMode(ULTRASONIC, INPUT);
   long duration = pulseIn(ULTRASONIC, HIGH, 10000);
   int distance_cm = (int)(((float)duration)*0.017);

   return distance_cm;
}

void right_stop() {
  ledcWrite(MOTOR_R_IA_PWM, 0);
  ledcWrite(MOTOR_R_IB_PWM, 0);
}

void right_forward() {
  ledcWrite(MOTOR_R_IA_PWM, 0);
  ledcWrite(MOTOR_R_IB_PWM, SPEED_SLOW);
}

void right_back() {
  ledcWrite(MOTOR_R_IA_PWM, SPEED_SLOW);
  ledcWrite(MOTOR_R_IB_PWM, 0);
}

void left_stop() {
  ledcWrite(MOTOR_L_IA_PWM, 0);
  ledcWrite(MOTOR_L_IB_PWM, 0);
}

void left_forward() {
  ledcWrite(MOTOR_L_IA_PWM, 0);
  ledcWrite(MOTOR_L_IB_PWM, SPEED_SLOW);
}

void left_back() {
  ledcWrite(MOTOR_L_IA_PWM, SPEED_SLOW);
  ledcWrite(MOTOR_L_IB_PWM, 0);
}

void turn_left() {
  left_back();
  right_forward();
}

void turn_right() {
  left_forward();
  right_back();
}

void forwards() {
  left_forward();
  right_forward();
}

void backwards() {
  left_back();
  right_back();
}

void botCommands() {
  uint8_t buff[30];
  while (wifi_client.connected() && wifi_client.available()) {
    int count = wifi_client.read(buff, sizeof(buff));

     // prints ultrasonic distance 
     if ((count == 1) && (buff[0] == 'p')) {
      int ultra_dist = ultrasonicDistance();
      wifi_client.println(ultra_dist);
     }

     // prints ultrasonic for left encoder
     if ((count == 1) && (buff[0] == 'l')) { 
       wifi_client.println(counter_l);
     }
          
     // prints ultrasonic for right encoder
     if ((count == 1) && (buff[0] == 'r')) {
       wifi_client.println(counter_r);
     }

     // turns to the right 1 tick
     if ((count == 1) && (buff[0] == 'd')) {
        limit_r = counter_r+1;
        turn_right();
     }

     // turns to the left 1 tick
     if ((count == 1) && (buff[0] == 'a')) {
        limit_l = counter_l+1;
        turn_left();
     }

     // forwards 1 tick
     if ((count == 1) && (buff[0] == 'w')) {
       limit_r = counter_r+1;
       limit_l = counter_l+1;
       forwards();
     }

      // backs one tick
     if ((count == 1) && (buff[0] == 's')) {
        limit_r = counter_r+1;
        limit_l = counter_l+1;
        backwards();
     }

     wifi_client.write(buff, count);
  }
}

void loop() {
  checkForConnections();
  botCommands();
}
