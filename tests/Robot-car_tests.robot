*** Settings ***
Documentation    This test suite tests robot car that works on Raspperry Pi.
Metadata    Version        1.0
Metadata    More Info      For more information about *Robot Framework* see http://robotframework.org
Library       SSHLibrary
Library       BuiltIn
Suite Setup    Suite Set
Suite Teardown    Suite Tear

*** Variables ***
${ADDRESS}     192.168.1.219
${PORT}        8270
${USER}        raspi
${PASSWORD}    malmlunD1@
${PATH}        /home/raspi/Robotcar_test/
${COMMAND}     python /home/raspi/Robotcar_test/RobotCarLibrary.py
${picNameBase}     Pic
${expectedDistanceToObstacle}    15
${roundingDistanceToObstacle}    3
@{MOTOR_SPEEDS}    1011    2022    4044
@{SERVO_HORIZONTAL_VALUES}    45    20    45    90    135    160    135    90
@{SERVO_VERTICAL_VALUES}    50    80    130    170    130    80

*** Keywords ***
Suite Set
    SSHLibrary.Open Connection    ${ADDRESS}    alias=None    port=22    timeout=2    newline=None    prompt=None    term_type=None    width=None    height=None    path_separator=None    encoding=None    escape_ansi=None
    ##SSHLibrary.Open Connection    ${ADDRESS}    RemoteServer    22
    SSHLibrary.Login    ${USER}    ${PASSWORD}    allow_agent=False    look_for_keys=False    delay=1 seconds
    SSHLibrary.Write    sudo python /home/raspi/Robotcar_test/RobotCarLibrary.py  
    Sleep    2    reason=None
    Import Library    Remote    http://${ADDRESS}:${PORT}

Suite Tear
    SSHLibrary.Write    ^C
    SSHLibrary.Close All Connections

Take Screenshot From Remote
    ${scrShotName}=    Remote Screenshot
    SSHLibrary.Get File    ${PATH}${scrShotName}    destination=/screenShots

*** Test Cases ***
SmokeTest
    [Documentation]    Tests that battery is on place and it has enough power on it.
    [Tags]    smoke    complete
    ${batteryVoltage}=    Get Battery Voltage
    ${isBatteryAlive}=    Evaluate    ${batteryVoltage} > 6     modules=None    namespace=None
    Run Keyword If    not ${isBatteryAlive}    Fatal Error    Batterys should be placed and charged. Battery voltage was ${batteryVoltage} V.
    Log    Battery voltage was ${batteryVoltage} V.

Servos
    [Documentation]    Tests that servos are working on given angles on horizontal and vertical axis.
    [Tags]    testcase2    complete
    Reset Servos

    FOR   ${x}    IN    @{SERVO_HORIZONTAL_VALUES}
        ${isServoWorking}=    Test Servo    0    ${x}
        Should Be True    ${isServoWorking}    msg=Servo horizontal value was not angle ${x}
    END

    FOR   ${y}    IN    @{SERVO_VERTICAL_VALUES}
        ${isServoWorking}=    Test Servo    1    ${y}
        Should Be True    ${isServoWorking}    msg=Servo vertical value was not angle ${y}
    END

LedWhite
    [Documentation]    Tests that all leds light on white color.
    [Tags]    testcase3    complete
    ${areWhite}=    All Leds Are White
    Should Be True    ${areWhite}    msg=None

LedColors
    [Documentation]    Tests that all leds light on every color on given color palette.
    [Tags]    testcase4    complete
    ${allHaveAllColors}=    All Leds Have All Colors
    Should Be True    ${allHaveAllColors}    msg=None

InfraredSensor
    [Documentation]    Tests that infrared sensor detects black line under robot.
    ...                For this test to work there has to be black line directly under robotcar.
    [Tags]    testcase5    complete
    ${isLineDirectlyUnderCar}=    Test Infrared Sensor
    Should Be True    ${isLineDirectlyUnderCar}    msg=Black line was NOT directly under robotcar
    Log    Black line was directly under robotcar

Camera
    [Documentation]    Tests that camera takes picture. Saves picture for manual inspection.
    [Tags]    testcase6    WIP
    ${stdout}    ${stderr}    ${rc}=    SSHLibrary.Execute Command    sudo python /home/raspi/Robotcar_test/camera.py    return_stdout=True    return_stderr=True    return_rc=True    sudo=False    sudo_password=None    timeout=15    invoke_subsystem=False    forward_agent=False
    
    Log    ${stdout}    level=INFO    html=False    console=False    formatter=repr
    Log    ${rc}    level=INFO    html=False    console=False    formatter=repr
    Should Be Empty    ${stderr}    msg=${stderr}
    SSHLibrary.Get File    /home/raspi/Robotcar_test/test.jpg    destination=.    scp=OFF

Buzzer
    [Documentation]    Tests that buzzers rings for given time.
    [Tags]    testcase7    complete
    ${buzzerIsWorking}=    Test Buzzer    1
    Should Be True    ${buzzerIsWorking}    msg=Buzzer should have been ringing for 1 seconds
    Sleep    0.5    reason=None
    ${buzzerIsWorking}=    Test Buzzer    2
    Should Be True    ${buzzerIsWorking}    msg=Buzzer should have been ringing for 2 seconds
    Sleep    0.5    reason=None
    ${buzzerIsWorking}=    Test Buzzer    3
    Should Be True    ${buzzerIsWorking}    msg=Buzzer should have been ringing for 3 seconds

UltraSonicSensor
    [Documentation]    Tests that ultra sonic sensor detects obstacle on a given distance.
    ...                For this test to work there has to be solid obstacle in front of sensor.
    [Tags]    testcase8    complete
    ${distanceToObstacle}=    Get Distance With Ultrasonic Sensor
    ${status} =  Evaluate  (${expectedDistanceToObstacle} - ${roundingDistanceToObstacle}) <= ${distanceToObstacle} <= (${expectedDistanceToObstacle} + ${roundingDistanceToObstacle})
    Log    Distance to the obstacle was ${distanceToObstacle} cm
    Should Be True    ${status}    msg=Distance to the obstacle was ${distanceToObstacle}cm, which is not in range that was expected (${expectedDistanceToObstacle}+-${roundingDistanceToObstacle}).

InfraredSensorMultipleLines
    [Documentation]    Tests that infrared sensor detects black line under robot.
    ...                For this test to work there has to be black line directly under robotcar.
    [Tags]    testcase9    complete
    ${timeoutIndex}=    Set Variable    30
    ${sleepTime}=    Set Variable    0.05
    ${expectedNumberOfLines}=    Set Variable    5
    ${linesFound}=   Set Variable  0
    ${wasLineDirectlyUnderCar}=    Set Variable    False
    ${carSpeed}=    Set Variable    -500

    Set Motors    ${carSpeed}    ${carSpeed}    ${carSpeed}    ${carSpeed}

    FOR    ${index}    IN RANGE    ${timeoutIndex}
        
        ${isLineDirectlyUnderCar}=    Test Infrared Sensor

        IF    ${isLineDirectlyUnderCar} != ${wasLineDirectlyUnderCar}
            ${wasLineDirectlyUnderCar}=    Set Variable    ${isLineDirectlyUnderCar}
            IF    ${wasLineDirectlyUnderCar}
                ${linesFound}=    Evaluate    ${linesFound}+1
                # IF    ${index} > 0
                #     Set Motors    0    0    0    0
                # END     
            END
        END 

        Exit For Loop If    ${linesFound} == ${expectedNumberOfLines}  
        Sleep    ${sleepTime}
    END

    Set Motors    0    0    0    0

    Should Be Equal As Integers    ${expectedNumberOfLines}    ${linesFound}    msg=There should have been ${expectedNumberOfLines} lines found, but ${linesFound} was found!  
    Log    ${linesFound} black lines passed the bottom of robot car.

InfraredSensorMultipleLines2
    [Documentation]    Tests that infrared sensor detects black line under robot.
    ...                For this test to work there has to be black line directly under robotcar.
    [Tags]    testcase10    complete
    ${timeoutIndex}=    Set Variable    30
    ${sleepTime}=    Set Variable    0.05
    ${expectedNumberOfLines}=    Set Variable    5
    ${linesFound}=   Set Variable  0
    ${wasLineDirectlyUnderCar}=    Set Variable    None
    ${carSpeed}=    Set Variable    -500

    Set Motors    ${carSpeed}    ${carSpeed}    ${carSpeed}    ${carSpeed}

    FOR    ${index}    IN RANGE    ${timeoutIndex}
        
        ${isLineDirectlyUnderCar}=    Get Infrared Sensors Value

        IF    ${isLineDirectlyUnderCar} != ${wasLineDirectlyUnderCar}
            ${wasLineDirectlyUnderCar}=    Set Variable    ${isLineDirectlyUnderCar}
            IF    ${wasLineDirectlyUnderCar} == CENTER
                ${linesFound}=    Evaluate    ${linesFound}+1
                # IF    ${index} > 0
                #     Set Motors    0    0    0    0
                # END     
            END
        END 

        Exit For Loop If    ${linesFound} == ${expectedNumberOfLines}  
        Sleep    ${sleepTime}
    END

    Set Motors    0    0    0    0

    Should Be Equal As Integers    ${expectedNumberOfLines}    ${linesFound}    msg=There should have been ${expectedNumberOfLines} lines found, but ${linesFound} was found!  
    Log    ${linesFound} black lines passed the bottom of robot car.

Motors
    [Documentation]    Tests that motors are working on given speeds on both directions.
    [Tags]    testcase1    complete
    FOR    ${index}    IN RANGE    4
        FOR    ${motorSpeed}    IN    @{MOTOR_SPEEDS}
            ${isMotorWorking}=    Test Motor    ${index}    ${motorSpeed}
            Should Be True    ${isMotorWorking}    msg=Motor ${index} was not working as expected.

            ${isMotorWorking}=    Test Motor    ${index}    -${motorSpeed}
            Should Be True    ${isMotorWorking}    msg=Motor ${index} was not working as expected.
        END
    END

    
