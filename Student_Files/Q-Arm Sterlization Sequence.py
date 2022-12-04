ip_address = 'localhost' # Enter your IP Address here
project_identifier = 'P2B' # Enter the project identifier i.e. P2A or P2B
#--------------------------------------------------------------------------------
import sys
import time
import random
sys.path.append('../')
from Common.simulation_project_library import *

hardware = False
QLabs = configure_environment(project_identifier, ip_address, hardware).QLabs
arm = qarm(project_identifier,ip_address,QLabs,hardware)
potentiometer = potentiometer_interface()
#--------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------

'''
-----------------------------
1P13 Project 2, "Get a Grip!" 
-----------------------------
Enviroment 4
Team Fri-16
-----------------------------
Matthew Jarzynowski
Rayan Nasrallah
-----------------------------
'''

#Coordinates for the locations of the home, pickup and autoclave drawer positions
home_c = [0.406, 0.0, 0.483] #Home coordinates
pickup_c = [0.600, 0.050, 0.05] #Pickup coordinates
actop_c = [[0.0, 0.62, 0.32], [-0.62, 0.22, 0.32], [0.0, -0.62, 0.32]] #Top autoclave coordinates
acbottom_c = [[0.0, 0.42, 0.18], [-0.46, 0.18, 0.18], [0.0, -0.42, 0.18]] #Bottom autoclave coordinates

#Unique container identifiers,(color and size)
container_color = ['red','green','blue'] #List of container colors
container_ID = [1,2,3,4,5,6] #List of container IDs


#The pickup function. Moves the end effector (gripper) to the pickup position, grips the container, then returns home.
def pickup():
    time.sleep(0.5) #Delay of 0.5 seconds
    print("Moving to the pickup position...") #Informs the user that the pickup sequence has started
    time.sleep(0.5) #Delay of 0.5 seconds
    arm.move_arm(pickup_c[0],pickup_c[1],pickup_c[2]) #Moves the Q-Arm's end effector to the pickup coordinates, stored in the pickup_c list
    time.sleep(1) #Delay of 1 second
    arm.control_gripper(45) #Closes the end effector by 45 degrees
    time.sleep(1) #Delay of 1 second
    print("Moving home...") #Informs the user that the Q-Arm is moving home
    time.sleep(0.5) #Delay of 0.5 seconds
    arm.move_arm(home_c[0],home_c[1],home_c[2]) #Returns the Q-Arm to the home coordinates, stored in the home_c list
    time.sleep(0.5) #Delay of 0.5 seconds
    print("In home position") #Informs the user that the Q-Arm is in the home position
    
#The rotate function. Using the right potentiometer, the user controls the rotation of the Q-Arm.
#Once the Q-Arm is in the range of the chosen autoclave, the rotation is halted.
def rotate(ID):
    #Checks if the right potentiometer is set at 50% before continuing
    old_potentiometer = potentiometer.right() #Sets the current potentiometer value to the variable "old_potentiometer"
    if (old_potentiometer != 0.5): #If the right potentiometer is not equal to 0.5 (50%)
        print("Please reset the right potentiometer by setting its value to 50%") #Guides the user on how to reset the right potentiometer
        while (old_potentiometer != 0.5): #Waits for the right potentiometer to be set to 50%
            old_potentiometer = potentiometer.right() #Sets the current potentiometer value to the variable "old_potentiometer". When the right potentiometer is at 50%, the while loop will terminate.

    time.sleep(0.5) #Delay of 0.5 seconds
    print("Please move the right potentiometer until the Q-Arm is in range of the chosen autoclave") #Guides the user on how to control the rotation of the Q-Arm
    time.sleep(0.5) #Delay of 0.5 seconds
    potentiometer_old = potentiometer.right() #Sets the current potentiometer value to the variable "potentiometer_old"
    while arm.check_autoclave(container_color[(ID % 3) - 1]) == False: #While the Q-Arm is not in range of the autoclave allow for the rotation of the base.
                                                                       #Also, when the Q-Arm will be in range of the autoclave, arm.check_autoclave will return True, thus terminating the while loop.  
        potentiometer_new = potentiometer.right() #Sets the current potentiometer value to the variable "potentiometer_new"
        arm.rotate_base(348 * (potentiometer_new - potentiometer_old)) #Rotates the base of the Q-Arm based on the difference from the new potentiometer value minus the old potentiometer value 
        potentiometer_old = potentiometer_new #Sets the old potentiometer value to the new potentiometer value

#The drop-off function. Using the left potentiometer, the user choses a value that is greater than 50 or equal to 100 based on the size of the container.
#The logic inside of the function determines if a autoclave drawer needs to be opened, based on the containers unique identifier, its color and ID.
def dropoff(ID):
    print("Please move the left potentiometer to greater than 50 (>50) for a small container or 100 for a large container") #Guides the user on how to correctly use the left potentiometer
    time.sleep(0.5) #Delay of 0.5 seconds
    ID_Check = ID > 3 #If the container is large, its ID is greater than 3, set ID_Check to True. If the container is small, its ID is less than 3, set ID_Check to False
    potentiometer_value = not ID_Check #Set the variable potentiometer_value to NOT ID_Check, the opposite off ID_Check

    while ID_Check != potentiometer_value: #While ID_Check is not equal to potentiometer value, False =/ True or True =/ False
        if potentiometer.left() == 1.0: #Check if the left potentiometer value is equal to 1.0 (100%)
            potentiometer_value = True #If it is, set potentiometer_value to True, thus indicating a large container
        elif potentiometer.left() > 0.5 and potentiometer.left() < 1.0: #Check if the left potentiometer is between 0.5 (50%) and 1.0 (100%)
            potentiometer_value = False #if it is, set the potentiometer_value to False, thus indicating a small container
            
    if ID_Check == True: #If the container is large, ID_Check returns True, move the Q-Arm to the bottom autoclave coordinates
        arm.open_autoclave(container_color[(ID % 3) - 1], True) #Open the autoclave drawer depending on the container color
        time.sleep(1) #Delay of 1 second
        arm.move_arm(acbottom_c[(ID % 3) - 1][0],acbottom_c[(ID % 3) - 1][1],acbottom_c[(ID % 3) - 1][2]) #Based on the containers ID, return the remainder of the ID/3 then subtract 1. This gives the index value for the coordinates.
        time.sleep(1) #Delay of 1 second
        arm.control_gripper(-45) #Open the end effector by 45 degrees
        time.sleep(1) #Delay of 1 second
    else: #Else, if the container is small, ID_Check returns False, move the Q-Arm to the top autoclave coordinates
        arm.move_arm(actop_c[(ID % 3) - 1][0],actop_c[(ID % 3) - 1][1],actop_c[(ID % 3) - 1][2]) #Based on the containers ID, return the remainder of the ID/3 then subtract 1. This gives the index value for the coordinates.
        time.sleep(1) #Delay of 1 second
        arm.control_gripper(-45) #Open the end effector by 45 degrees
        time.sleep(1) #Delay of 1 second
    arm.home()

#The main function. Calls each function in sequence to complete the sterilization process for a single container.
#Then, it loops 6 times, the length of the container_ID list, until all containers have been serialized, thus terminating the program.
def main(ID):
    arm.home() #Moves the Q-Arm to its home coordinates
    arm.activate_autoclaves() #Activates the autoclaves
    arm.home() #Moves the Q-Arm to its home position, with its end effector open
    arm.spawn_cage(ID) #Spawns the container within the virtual environment based on a randomized ID chosen from the container_ID list
    print("Beginning the sterilization of container of ID:", ID) #Informs the user which container is being sterilized
    pickup() #Calls the pickup function to pickup the container
    rotate(ID) #Calls the rotate function, passing the containers ID into it, to determine which autoclave the Q-Arm should be in range of 
    dropoff(ID) #Calls the dropoff function, passing the containers ID into it, to determine which autoclave is it designated for
    arm.open_autoclave(container_color[(ID % 3) - 1], False) #Closes the autoclave drawer based on which random ID was chosen, only for large containers

#The randomization for loop. This loop iterates through the list container_ID, where it randomly choses an ID from the list, then removes it.
#This iteration continues until there are no items left in the list, ending at 6 containers sterilized.   
for i in range(len(container_ID)):
    ID = random.choice(container_ID) #Randomly picks an ID from the list container_ID
    container_ID.remove(ID) #Removes that ID from the list container _ID 
    main(ID) #Returns the chosen ID into the main function
arm.deactivate_autoclaves() #Once all containers have been sterilized, deactivate all the autoclaves 
print("Completed all cycles for all containers!") #Informs the user that all containers have been sterilized, the sequence is complete.

#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
