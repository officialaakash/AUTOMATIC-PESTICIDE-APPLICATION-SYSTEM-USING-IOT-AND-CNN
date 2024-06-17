#define BLYNK_PRINT Serial

#define BLYNK_TEMPLATE_ID "TMPL3oaotcwxp"
#define BLYNK_TEMPLATE_NAME "Pesticide robot"
#define BLYNK_AUTH_TOKEN "Ci5CGTZwutcRMRbqfO7sKtk3RWfRbK-V"

#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
  
char auth[] = BLYNK_AUTH_TOKEN;

char ssid[] = "Aakash's S22";  // type your wifi name
char pass[] = "12345678";  // type your wifi password
 
int M1PWM = D5;
int M1F = D1; //GPIO5
int M1R = D2; //GPIO4


int pinValue1;
int pinValue2;

BLYNK_WRITE(V1)
{
  int pinValue1 = param.asInt();
  analogWrite(M1PWM,pinValue1);
  Blynk.virtualWrite(V1,pinValue1);
  Serial.print("V1 Slider Value is ");
  Serial.println(pinValue1);
}


 

void setup(){
  pinMode(M1PWM, OUTPUT);
  
  pinMode(M1F, OUTPUT);
  pinMode(M1R, OUTPUT);
  Serial.begin(9600);
  Blynk.begin(auth,ssid,pass);
  
}

void loop(){
  Blynk.run();
 
}