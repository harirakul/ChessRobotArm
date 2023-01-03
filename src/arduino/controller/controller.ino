#include <Servo.h>

Servo shoulder; //270-degree Sunfounder Servo
Servo elbow; // 270-degree Sunfounder Servo
Servo base; // 180-degree MicroServo
Servo gripper; //180-degree MicroServo

// For potentiometer control
const int buttonPin = 2;
int buttonState = 0;
int spot = 0;
int epot = 1;
int sval;
int eval;

void setup() {
  Serial.begin(9600);
  
  //Attach and initialize servos.
  shoulder.attach(8); 
  elbow.attach(9);
  base.attach(10);
  gripper.attach(11);
  gripper.write(70);
  base.write(100);
  //shoulder.write(33);
  //elbow.write(33);
  delay(500);
  
  rest();

  Serial.println("init");
  //comboMove(50, 94);
}

void loop(){
// Keep reading from Arduino Serial Monitor and send to HC-06
  if (Serial.available() > 0){
    float x = Serial.readString().toFloat();

    if (x == 190){
      rest();
    }
    
    if (x == 191){
      grasp();
    }

    if (x == 192){
      drop();
    }

    if (x == 193){
      graspKnight();
    }
    
    if (x >= 0 && x <= 180){
      shoulderTo(x);
    }

    if (x >= 200 && x <= 380){
      Serial.println("done");
      while(Serial.available() == 0) { }
      //Serial.println("received shoulder");
      float y = Serial.readString().toFloat();
      if (y >= 0 && y <= 180){
        comboMove(y, x-200);
      }
      //elbowTo(x - 200);
    }

    if (x >= 400 && x <= 580){
      baseTo(x - 400);
      // while (true){
      //   sval = analogRead(spot);            // reads the value of the potentiometer (value between 0 and 1023)
      //   sval = map(sval, 0, 1023, 0, 180);     // scale it to use it with the servo (value between 0 and 180)
      //   shoulder.write(sval);                  // sets the servo position according to the scaled value

      //   eval = analogRead(epot);            // reads the value of the potentiometer (value between 0 and 1023)
      //   eval = map(eval, 0, 1023, 0, 180);     // scale it to use it with the servo (value between 0 and 180)
      //   elbow.write(eval);                  // sets the servo position according to the scaled value

      //   delay(15);                           // waits for the servo to get there

      //   buttonState = digitalRead(buttonPin);
      //   if (buttonState == HIGH){
      //     Serial.println(sval);
      //     Serial.println(eval+200);
      //     break;
      //   }
      // }

    }

    Serial.println("done");
  }
}

void shoulderTo(float target) {
  target += 12; // Adjusting for mechanical imperfections
  target = 180 * target / 270; // Adjusting for 270-degree servo
  float pos = shoulder.read();
  if (pos <= target){
    for (pos = pos; pos <= target; pos += 1){
      shoulder.write(pos);
      delay(30);
    }
  }
  else {
    for (pos = pos; pos >= target; pos -= 1){
      shoulder.write(pos);
      delay(30);
    }
  }
}

void elbowTo(float target) {
  target += 3; // Adjusting for mechanical imperfections
  target = 180 * target / 270; // Adjusting for 270-degree servo
  float pos = elbow.read();
  if (pos <= target){
    for (pos = pos; pos <= target; pos += 1){
      elbow.write(pos);
      delay(20);
    }
  }
  else {
    for (pos = pos; pos >= target; pos -= 1){
      elbow.write(pos);
      delay(20);
    }
  }
}

void baseTo(float target){
  target += 12; // Adjusting for mechanical imperfections
  float pos = base.read();
  if (pos <= target){
    for (pos = pos; pos <= target; pos += 1){
      base.write(pos);
      delay(20);
    }
  }
  else {
    for (pos = pos; pos >= target; pos -= 1){
      base.write(pos);
      delay(20);
    }
  }
}

void gripperTo(float target){
  float pos = gripper.read();
  if (pos <= target){
    for (pos = pos; pos <= target; pos += 1){
      gripper.write(pos);
      delay(10);
    }
  }
  else {
    for (pos = pos; pos >= target; pos -= 1){
      gripper.write(pos);
      delay(10);
    }
  }
}

void comboMove(float starget, float etarget){
  starget += 12; // Adjusting for mechanical imperfections
  starget = 180 * starget / 270; // Adjusting for 270-degree servo

  etarget += 3; // Adjusting for mechanical imperfections
  etarget = 180 * etarget / 270; // Adjusting for 270-degree servo

  int sdir = 1;
  int edir = 1;
  float spos = shoulder.read();
  float epos = elbow.read();

  if (spos <= starget){
    sdir = 1;
  }
  else {
    sdir = -1;
  }

  if (epos <= etarget){
    edir = 1;
  }
  else {
    edir = -1;
  }
  int sdelay = 24;

  float epsilon = 1;
  while (abs(starget - spos) > epsilon || abs(etarget - epos) > epsilon){


    if (abs(etarget - epos) > epsilon){
      epos += edir;
      elbow.write(epos);
      delay(24);
    }
    else {
      sdelay = 50;
    }
    if (abs(starget - spos) > epsilon){
            //Serial.println("starting");

      spos += sdir;
      //Serial.println(spos);
      shoulder.write(spos);
      delay(sdelay);
    }
  }

}

void rest() {
  //comboMove(120, 40);
  shoulderTo(120);
  elbowTo(40);
}

void grasp(){
  //gripper.write(95);
  gripperTo(75);
}

void graspKnight(){
  gripperTo(50);
}

void drop(){
  //gripper.write(120);
  gripperTo(145);
}

