/*
 * Serial.c
 *
 * Created: 21.12.2020 14:38:48
 * Author : Tobias
 */ 
#define F_CPU 16000000UL
#include <avr/io.h>
#include <stdio.h>
#include <stdint.h>
#include <util/delay.h>
#include "usart.h"
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdbool.h>
#define ADC_PIN 1 //X
#define ADC_PIN 2 //Y
#define V_REF 5010 //Voltage Reference

//variables for ADC
unsigned int voltage; //relust in mV
unsigned int X; //relust in mV
unsigned int Y; //relust in mV




//function prototypes
uint16_t adc_read(uint8_t adc_channel);

int main(){
	uart_init();
	io_redirect();
	
	//Variables for Communication
	int *JS_X_Y[1];
	int *Pos_X_Y[1]={0,0};
	int *Int_speed_M1_M2[1]={0,0};
	int *Act_speed_M1_M2[1]={0,0};
	int *Temp_1_2[1]={0,0};
	bool *Coll_det[0]={0};
		
	int *X;
	int *Y;	

	DDRD = 0x00;  //set PIND as a input port for receiving PD0 signal
	DDRB = 0x00;  //set PINB as a input port for receiving PB0 signal

	DDRD &= ~(1 << DDD2);     // Clear the PD2 pin

	EICRA |= (1 << ISC00);    // set INT0 to trigger on ANY logic change
	EIMSK |= (1 << INT0);     // Turns on INT0

	sei();                    // turn on interrupts

	PORTC = 0xFF;			//bit 0-4 is an input
	PORTC = 0x0F;			//enable pull ups
	
	uint16_t adc_result;
	// Select Vref = AVcc
	ADMUX = (1<<REFS0);
	//set prescaler to 128 and turn on the ADC module
	ADCSRA = (1<<ADPS2)|(1<<ADPS1)|(1<<ADPS0)|(1<<ADEN);
	while(1){
		for (int channel = 1; channel < 3; channel++)
		{
			adc_result = adc_read(channel);
			voltage = (adc_result * (V_REF / 1024.0))-2505;
			if (channel==1)
			{
				*JS_X_Y[0] = voltage;

			}
			if (channel ==2)
			{
				*JS_X_Y[1] = voltage;
			}
			

		}
		printf("%d;", *JS_X_Y[0]);
		printf("%d;", *Pos_X_Y[0]);
		printf("%d;", *Int_speed_M1_M2[0]);
		printf("%d;", *Act_speed_M1_M2[0]);
		printf("%d;", *Temp_1_2[0]);
		printf("%d;", *Coll_det[0]);		
		printf("%d;", *JS_X_Y[1]);
		printf("%d;", *Pos_X_Y[1]);
		printf("%d;", *Int_speed_M1_M2[1]);	
		printf("%d;", *Act_speed_M1_M2[1]);			
		printf("%d;", *Temp_1_2[1]);						


		_delay_ms(200);
	}
}


ISR (INT0_vect)
{
	timer_1ms();
	function_button();
}


uint16_t adc_read(uint8_t adc_channel){
	ADMUX &= 0xf0; // clear any previously used channel, but keep internal reference
	ADMUX |= adc_channel; // set the desired channel
	//start a conversion
	ADCSRA |= (1<<ADSC);
	// now wait for the conversion to complete
	while ( (ADCSRA & (1<<ADSC)) );
	// now we have the result, so we return it to the calling function as a 16 bit unsigned int
	return ADC;
}

function_button(void)
{
	if(PINB & (1<<1)) //S1 switch is pressed
	{
		printf("B1 works\n");
	}
	if (PIND & (1<<4)) //B1 switch
	{
		printf("S1 works\n");
	}
	if (PINB & (1<<2))
	{
		printf("S2 works\n");
	}
}

timer_1ms(void)// this code sets up a timer0 for 1ms @ 16Mhz clock cycle
{
	// Set the Timer Mode to CTC
	TCCR0A |= (1 << WGM01);

	// Set the value that you want to count to
	OCR0A = 0xF9;

	// start the timer
	TCCR0B |= (1 << CS01) | (1 << CS00);
	// set prescaler to 64 and start the timer

	while ( (TIFR0 & (1 << TOV0) ) > 0)        // wait for the overflow event
	{
	}

	TIFR0 |= (1 << TOV0);
	// reset the overflow flag
}