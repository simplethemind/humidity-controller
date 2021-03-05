const int INPUT_PINS[3] = {A0, A2, A4};
const int currentSensors = 3;
int sensors[3][5] = {0, 0, 0};
int sensorsMin[3] = {260, 260, 260};
int sensorsMax[3] = {615, 640, 620};
int sensorsStart[3] = {0, 0, 0};
int sensorsEnd[3] = {1000, 1000, 1000};
long sensorsRelayDuration[3] = {1000, 1000, 1000};

char b[12];
int readIndex = 0;

const int RELAY_PINS[4] = {6, 5, 4, 3};
long relayTimers[4] = {0, 0, 0, 0};

long deltaTime;
unsigned long oldMillis;

long logDelay = 3 * 1000L; // read every sixty seconds
long nextLogStep = 0L;

void CheckForValueSetter(char b[12])
{
  if (b[0] == 'v')
  {
    char sensorNo[2] = {b[1], '\0'};
    int sensorIndex = atoi(sensorNo);
    char valueNo[5] = {b[3], b[4], b[5], b[6], 0};
    long newValue = atol(valueNo);

    Serial.print("Setting ");

    if (b[2] == 'm')
    {
      sensorsMin[sensorIndex] = newValue;
      Serial.print("minimum value for sensor ");
    }
    else if (b[2] == 'M')
    {
      sensorsMax[sensorIndex] = newValue;
      Serial.print("maximum value for sensor ");
    }
    else if (b[2] == 's')
    {
      sensorsStart[sensorIndex] = newValue;
      Serial.print("pump start value for sensor ");
    }
    else if (b[2] == 'e')
    {
      sensorsEnd[sensorIndex] = newValue;
      Serial.print("pump stop value for sensor ");
    }
    else if (b[2] == 'r')
    {
      sensorsRelayDuration[sensorIndex] = newValue;
      Serial.print("pumping duration for sensor ");
    }
    Serial.print(sensorIndex);
    Serial.print(" to ");
    Serial.println(newValue);
    Serial.flush();
  }
}

void CheckForMockSensorValue(char b[12])
{
  if (b[0] == 's' && b[2] == 'v')
  {
    char sensorNo[2] = {b[1], 0};
    int sensorIndex = atoi(sensorNo);
    char valueNo[5] = {b[3], b[4], b[5], b[6], 0};
    int newValue = atoi(valueNo);

    SetSensorHistory(sensorIndex, newValue);

    Serial.print("Setting mock value for sensor ");
    Serial.print(sensorIndex);
    Serial.print(" to ");
    Serial.println(newValue);
    Serial.flush();
  }
}

void StartRelay(int relay, long onDuration)
{
  relayTimers[relay] = onDuration;
  digitalWrite(RELAY_PINS[relay], LOW);

  Serial.print("Opening relay ");
  Serial.print(relay);
  Serial.print(" for ");
  Serial.print(onDuration);
  Serial.println("ms");
  Serial.flush();
}

void StopRelay(int relay)
{
  digitalWrite(RELAY_PINS[relay], HIGH);

  Serial.print("Closing relay ");
  Serial.println(relay);
  Serial.flush();
}

void CheckForMockRelayStart(char b[12])
{
  if (b[0] == 'r' && b[2] == 'd')
  {
    char relayNo[2] = {b[1], 0};
    int relay = atoi(relayNo);
    char durationNo[6] = {b[3], b[4], b[5], b[6], b[7], 0};
    long onDuration = atol(durationNo);

    StartRelay(relay, onDuration);
  }
}

void SerialReadLoop()
{
  if (Serial.available())
  {
    b[readIndex] = Serial.read();
    readIndex++;
    if (readIndex == 12 || b[readIndex - 1] == '\n' || b[readIndex - 1] == '\r')
    {
      CheckForValueSetter(b);
      CheckForMockSensorValue(b);
      CheckForMockRelayStart(b);
      readIndex = 0;
    }
  }
}

void setup()
{
  // Initialize pins
  for (int i=0; i<3; i++)
  {
    pinMode(INPUT_PINS[i], INPUT);
  }
  for (int i=0; i<4; i++)
  {
    pinMode(RELAY_PINS[i], OUTPUT); 
    digitalWrite(RELAY_PINS[i], HIGH);
  }

  // Initialzie serial connection
  Serial.begin(115200);
  while (!Serial) 
  {
    ; // wait for serial port to connect. Needed for native USB
  }

  // Send ready signal to computer
  Serial.println("Ready");
  Serial.flush();

  // Initialize from stored values
  while (Serial.peek() != '^')
  {
    SerialReadLoop();
  }

  // Initialize global variables
  oldMillis = millis();
  nextLogStep = logDelay;
}

long getDeltaTime()
{
  long returnValue = millis() - oldMillis;
  oldMillis = millis();
  return returnValue;
}

float ConvertToPercent(int sensorValue, int sensorMin, int sensorMax)
{
  float x = (float)(sensorValue - sensorMin) / (float)(sensorMax - sensorMin);
  return (float)(1.0 - x) * 100.0;
}

float AverageValue(int index)
{
  int sum = 0;
  for (int i=0; i<5; i++)
  {
    sum += sensors[index][i];
  }
  return (float)sum / (float)5;
}

void SetSensorHistory(int i, int newValue)
{
      for(int j=4; j>0; j--)
      {
        sensors[i][j] = sensors[i][j-1];
      }
      sensors[i][0] = newValue;
}

void LogSensorValues()
{
  if (nextLogStep <= 0)
  {
    for(int i=0; i<currentSensors; i++)
    {
      SetSensorHistory(i, analogRead(INPUT_PINS[i]));
      if (i>0)
        Serial.print(",");
      // Serial.print(constrain(ConvertToPercent(sensors[i][0], sensorsMin[i], sensorsMax[i]), 0.00, 100.00));
      Serial.print(sensors[i][0]);
    }
    Serial.println("");
    Serial.flush();

    for(int i=0; i<currentSensors; i++)
    {
      if (AverageValue(i) > sensorsStart[i])
      {
        StartRelay(i, sensorsRelayDuration[i]);
      }
    }

    nextLogStep += logDelay;
  }
  nextLogStep -= deltaTime;
}

void RelayCommandLoop()
{
  for (int i = 0; i < 4; i++)
  {
    if (relayTimers[i] > 0)
    {
      relayTimers[i] -= deltaTime;
      if (relayTimers[i] <= 0)
      {
        StopRelay(i);
      }
    }
  }
}

void loop()
{
  deltaTime = getDeltaTime();
  LogSensorValues();
  SerialReadLoop();
  RelayCommandLoop();
}
