/* 
 * PWS. Nodo de recogida de datos.
 */

#include <avr/power.h>
#include <avr/sleep.h>
#include <avr/wdt.h>
#include <DHT.h>

#define DHTTYPE DHT11

const byte DHTPIN = 4;
DHT dht(DHTPIN, DHTTYPE);

float temp, hum;
//const byte LIGHTPIN = A5;
//int light;

ISR(WDT_vect){
  wdt_disable();  // disable watchdog
}

void myWatchdogEnable(const byte interval){
  MCUSR = 0;                          // reset various flags
  WDTCSR |= 0b00011000;               // set WDCE, WDE
  WDTCSR =  0b01000000 | interval;    // set WDIE, and appropriate delay
  
  wdt_reset();
  noInterrupts ();

  byte old_ADCSRA = ADCSRA;
  // disable ADC
  ADCSRA = 0;
  // pin change interrupt (D0)
  PCMSK2 |= bit (PCINT16); // want pin 0
  PCIFR  |= bit (PCIF2);   // clear any outstanding interrupts
  PCICR  |= bit (PCIE2);   // enable pin change interrupts for D0 to D7

  set_sleep_mode (SLEEP_MODE_IDLE);
  power_adc_disable();
  power_spi_disable();
  power_timer0_disable();
  power_timer1_disable();
  power_timer2_disable();
  power_twi_disable();
  // UCSR0B &= ~bit (RXEN0);  // disable receiver
  // UCSR0B &= ~bit (TXEN0);  // disable transmitter

  sleep_enable();
  interrupts ();
  sleep_mode();
  
  sleep_disable();
  power_all_enable();
  ADCSRA = old_ADCSRA;
  PCICR  &= ~bit (PCIE2);   // disable pin change interrupts for D0 to D7
  //UCSR0B |= bit (RXEN0);  // enable receiver
  //UCSR0B |= bit (TXEN0);  // enable transmitter
} 

void setup() {
  Serial.begin(9600);
  
  dht.begin();
  pinMode(DHTPIN, INPUT);
  
  //Watchdog config
  wdt_enable(WDTO_8S);
}

void loop() {
  wdt_reset();
  temp = dht.readTemperature();
  hum = dht.readHumidity();
  Serial.print(":temp!");
  Serial.print(temp);
  Serial.print(":hum!");
  Serial.println(hum);
  delay(200);

  int i;
  for (i=0; i<1; i++){
    myWatchdogEnable (0b100001);  // 8 seconds
  }
}


