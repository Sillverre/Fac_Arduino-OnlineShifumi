#include <LiquidCrystal.h>
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

#define PINX A0
#define PINY A1
#define THRESHOLD_CISSORS 90    //rock and cissors are on axe Y
#define THRESHOLD_ROCK -90
#define THRESHOLD_PAPER 90


enum State : char {
  WAIT_PY_CLIENT = '1',
  WAIT_SERVER = '2',
  WAIT_READY = '3',  
  RUNNING = '4',  
  SEND_ACK = '5'
};


enum {  PAPER, CISSORS, ROCK, EMPTY };

const int MAX_PLAYERS = 4;
int NB_PLAYERS = 1;
int CURRENT_ID = 0;

int score_players[MAX_PLAYERS];


const byte numChars = 32;
char receivedChars[numChars];   // an array to store the received data

volatile boolean newData = false;

int waitInt() {
  while(Serial.available() == 0){}
  return Serial.read();
}

bool waitCommand(State state) {    
  while(Serial.available() > 0){
    if (Serial.read() == state) {
      return true;  
    };
  }
  return false;    
}

bool checkCommand(State state) {    
  while(Serial.available() == 0){}
  return Serial.read() == state;
}


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);  
    
  // Setup joytick
  pinMode(PINX, INPUT);
  pinMode(PINY, INPUT);

  // Setup LCD
  lcd.begin(16,2);
  lcd.setCursor(0,0);
  lcd.clear();

  lcd.print("Wait py-client...");
  lcd.setCursor(0,1);

  Serial.write(0);
   
  // wait python client
  while(!waitCommand(WAIT_PY_CLIENT)){}
  lcd.clear();
  lcd.print("Wait server...");
      
  // wait data from server
  while(!waitCommand(WAIT_SERVER)){}

  lcd.clear();
  lcd.print("Wait server info...");

  NB_PLAYERS = waitInt(); // receive NB_PLAYERS
  CURRENT_ID = waitInt(); // receive CURRENT_ID


  lcd.clear();
  lcd.print("NB JOUEURS: ");
  lcd.print(NB_PLAYERS);
  lcd.setCursor(0,1);
  lcd.print("YOUR ID: ");
  lcd.print(CURRENT_ID);

  delay(3000);
  
  Serial.write(SEND_ACK);
  
  lcd.clear();
  lcd.print("Wait other");
  lcd.setCursor(0,1);
  lcd.print("players...");
  while(!waitCommand(WAIT_READY)){}
  lcd.clear();
}

const unsigned long TIME_TO_PLAY_MS = 2000;
int makeChoice()
{
  lcd.clear();
  int current_choice = EMPTY;
  char buf[16];
  int joyValX = 0;
  int joyValY = 0;
  unsigned long last_time = millis();
  char choice_display = '?';
  
  unsigned long delta = (millis() - last_time);
  while(delta <= TIME_TO_PLAY_MS) {
    delta = (millis() - last_time);    
    joyValX = map(analogRead(PINX), 0, 1023, -100, 100);
    joyValY = map(analogRead(PINY), 0, 1023, -100, 100);
    if(abs(joyValY) > abs(joyValX))
    {
      if(joyValY < THRESHOLD_ROCK) {
        current_choice = ROCK;
        choice_display = 'R';
      }
      if(joyValY > THRESHOLD_CISSORS) {
        current_choice = CISSORS;
        choice_display = 'C';        
      }
    }
    else if(joyValX > THRESHOLD_PAPER) {
      current_choice = PAPER;
      choice_display = 'P';      
    }

    lcd.setCursor(0,0);
    sprintf(buf, "choice: %c", choice_display);
    lcd.print(buf);
    delay(200);
  }
  
  return current_choice;
}

void waitResultAndUpdate() {  
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Wait result...");
  delay(1000);
  while(Serial.available() == 0){}
  int winner_id = Serial.read();

  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Round win by");
  lcd.setCursor(0,1);
  lcd.print(winner_id);

  delay(1500);
}

void loop() {
  if (checkCommand(RUNNING)) { // new round
    int current_choice = makeChoice();
    Serial.write(current_choice); // send choice    
    waitResultAndUpdate();
    //display info
  } else { // game finished
    while(Serial.available() == 0){}
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("wait winner...");
    delay(1000);
    int winner_id = Serial.read();
    if ( winner_id == CURRENT_ID) {
      lcd.clear();
      lcd.setCursor(0,0);
      lcd.print("YOU WIN !!!");
    } else {
      lcd.clear();
      lcd.setCursor(0,0);
      lcd.print("YOU LOST !!!");
      lcd.setCursor(0,1);
      lcd.print(winner_id);
      // afficher ID player WINNER
    }
  }
}
