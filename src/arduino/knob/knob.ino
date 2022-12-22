#include <Servo.h>

Servo shoulder;  // create servo object to control a servo
Servo elbow;
Servo base;
Servo gripper;

const int spot = 0;  // analog pin used to connect the potentiometer
const int epot = 1;
const int leftButton = 3;
//const int rightButton = 4;
const int toggleButton = 4;
const int saveButton = 2;

int sval;    // variable to read the value from the analog pin
int eval;
int bval;
int toggleState = 1;

int basePos = 90;

void setup() {
  Serial.begin(9600);

  shoulder.attach(8);
  elbow.attach(9);
  base.attach(10);
  base.write(90);
  gripper.attach(11);
  gripper.write(60);

  Serial.println("init");
}

void loop() {

  sval = analogRead(spot);            // reads the value of the potentiometer (value between 0 and 1023)
  sval = map(sval, 0, 1023, 0, 270);     // scale it to use it with the servo (value between 0 and 180)
  shoulder.write(sval);                  // sets the servo position according to the scaled value

  if (toggleState == -1){
    eval = analogRead(epot);            // reads the value of the potentiometer (value between 0 and 1023)
    eval = map(eval, 0, 1023, 0, 270);     // scale it to use it with the servo (value between 0 and 180)
    elbow.write(eval);                  // sets the servo position according to the scaled value
  }
  else {
    bval = analogRead(epot);            // reads the value of the potentiometer (value between 0 and 1023)
    bval = map(bval, 0, 1023, 0, 180);     // scale it to use it with the servo (value between 0 and 180)
    base.write(bval);                  // sets the servo position according to the scaled value
  }


  // if (digitalRead(leftButton) == HIGH){
  //   basePos++;
  //   base.write(basePos);
  // }

  // if (digitalRead(rightButton) == HIGH){
  //   basePos--;
  //   base.write(basePos);
  // }

  if (digitalRead(toggleButton) == HIGH){
    toggleState = -toggleState;
    delay(200);
  }

  if (digitalRead(saveButton) == HIGH){
    Serial.println(bval+400);
    Serial.println(sval);
    Serial.println(eval+200);
    delay(200);
  }

  //delay(15);                           // waits for the servo to get there
}