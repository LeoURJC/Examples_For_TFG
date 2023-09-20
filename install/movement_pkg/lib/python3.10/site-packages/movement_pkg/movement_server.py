
# import the ROS2 Python client libraries
import rclpy
from rclpy.node import Node
import time
import numpy as np

# interface del topic /scan
from sensor_msgs.msg import LaserScan
from rclpy.qos import ReliabilityPolicy, QoSProfile

# interface del topic /odom
from nav_msgs.msg import Odometry

# interface del topic /cmd_vel
from geometry_msgs.msg import Twist

# interfaces custom
from custom_interfaces.srv import MyCustomServiceMessage

# Import the libraries to use executors and callback groups
from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor, SingleThreadedExecutor



class Service(Node):

    def __init__(self, seconds_sleeping= 4):
        # Here you have the class constructor

        # call the class constructor to initialize the node as service_stop
        super().__init__('movement_server')
        # create the Service Server object
        # create the Publisher object
        # in this case, the Publisher will publish on /cmd_vel topic with a queue size of 10 messages.
        # use the Twist module
        self.vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        #Creamos un command cmd
        self.cmd = Twist()

        # Create 3 MutuallyExclusiveCallbackGroup
        self.group1 = MutuallyExclusiveCallbackGroup()
        self.group2 = MutuallyExclusiveCallbackGroup()
        self.group3 = MutuallyExclusiveCallbackGroup()


        # Define a Subscriber for the /odom topic and add it to the callback group
        self.odom_sub = self.create_subscription(
            Odometry, 'odom', self.odom_callback, 10,  callback_group=self.group1)
        
        # Define a Subscriber for the /scan topic and add it to the callback group
        self.scan_sub = self.create_subscription(LaserScan, 'scan', self.scan_callback, QoSProfile(
            depth=10, reliability=ReliabilityPolicy.BEST_EFFORT), callback_group=self.group2)
       
        # defines the type, name, and callback function
        self.srv = self.create_service(MyCustomServiceMessage, 'movement', self.custom_service_callback, callback_group=self.group3)




        self.laser_msg = LaserScan()
        self._seconds_sleeping = seconds_sleeping
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.giro = 0.0
        #Variable de estado para que el robot no se quede pillado tras completar figura
        self.figure_completed = False  
        # Atributo para almacenar el nuevo comando
        self.new_command = None
        #Bucle while del square forma
        self.contador = True

    # Callback function for the /odom Subscriber
    def odom_callback(self, msg):
        #self.get_logger().info("Odom CallBack")

        orientation_q = msg.pose.pose.orientation
        orientation_list = [orientation_q.x,
                            orientation_q.y, orientation_q.z, orientation_q.w]
        (self.roll, self.pitch, self.yaw) = self.euler_from_quaternion(orientation_list)
        
        #self.get_logger().info("YAW value:" + str(self.yaw))

        return self.yaw

    # Get the value of the front laser
    def get_front_laser(self):
        return self.laser_msg.ranges[360]

    # Callback function for the /scan Subscriber
    def scan_callback(self, msg):
        #self.get_logger().info("Scan CallBack")
        self.laser_msg = msg
        #self.get_logger().info("LASER Value=" + str(self.laser_msg.ranges[360]))


    # Get the yaw value
    def get_yaw(self):
        return self.yaw

    # Convert a quaternion to Euler angles
    def euler_from_quaternion(self, quaternion):
        """
        Converts quaternion (w in last place) to Euler roll, pitch, yaw
        quaternion = [x, y, z, w]
        Below should be replaced when porting for ROS2 Python tf_conversions is done.
        """
        
        x = quaternion[0]
        y = quaternion[1]
        z = quaternion[2]
        w = quaternion[3]

        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (w * y - z * x)
        pitch = np.arcsin(sinp)

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        if yaw < 0:
            yaw += 2 * np.pi

        if yaw > 6.10:
            yaw = 0

        return roll, pitch, yaw

    # Send velocities to stop the robot
    def stop_robot(self):
        self.cmd.linear.x = 0.0
        self.cmd.angular.z = 0.0

        self.vel_pub.publish(self.cmd)

    # Send velocities to move the robot forward
    def move_straight(self):
        self.cmd.linear.x = 0.5
        self.cmd.angular.z = 0.0
        self.vel_pub.publish(self.cmd)

    # Send velocities to rotate the robot
    def rotate(self,degree):

        self.cmd.angular.z = 0.3
        self.cmd.linear.x = 0.0
        #BEBUG
        #self.get_logger().info("YAW value:" + str(self.yaw))
        #self.get_logger().info("GIRO value:" + str(self.giro))

        self.vel_pub.publish(self.cmd)
        
        self.giro = self.giro + degree
        
        # Keep rotating the robot 90º
        while self.yaw < self.giro:
            self.get_logger().info("YAW value:" + str(self.yaw))
            self.get_logger().info("GIRO value:" + str(self.giro))
            rclpy.spin_once(self, timeout_sec=1)

        
        

    def custom_service_callback(self, request, response):
        # The callback function receives the self-class parameter, 
        # received along with two parameters called request and response
        # - receive the data by request
        # - return a result as a response

        # create a Twist message
        
###**********************************SQUARE************************************************************###
      
        if request.move == "Square" and self.figure_completed == False: #verificamos el estado de la figura

            self.bucle = 0.0    
            self.giro = 0.0

            while self.bucle < 4:
                
                # Instead of using time.sleep(1), use rclpy.spin_once() with a timer
                start_time = time.time()
                while time.time() - start_time < self._seconds_sleeping:
                    self.move_straight()  # Move forward
                    rclpy.spin_once(self, timeout_sec=0.1)  # Adjust the timeout as needed

                self.stop_robot()
                # Wait briefly to ensure the robot stops
                rclpy.spin_once(self, timeout_sec=0.5)  # Adjust the timeout as needed
               
                #Rotamos 1.50 --> 90 º
                self.rotate(1.50) #El robot va de 0-6 rad por lo que 90º son 1.50 rads
                self.bucle += 1
            

            self.get_logger().info('Maquing a Square!!')

            # response state
            response.success = True

            if response.success == True:
                self.stop_robot()
                self.figure_completed = True


###**********************************TRIANGLE************************************************************###
      
        if request.move == "Triangle" and self.figure_completed == False: #verificamos el estado de la figura

            self.bucle = 0.0    
            self.giro = 0.0

            while self.bucle < 3:
                
                # Instead of using time.sleep(1), use rclpy.spin_once() with a timer
                start_time = time.time()
                while time.time() - start_time < self._seconds_sleeping:
                    self.move_straight()  # Move forward
                    rclpy.spin_once(self, timeout_sec=0.1)  # Adjust the timeout as needed

                self.stop_robot()
                # Wait briefly to ensure the robot stops
                rclpy.spin_once(self, timeout_sec=0.5)  # Adjust the timeout as needed
               
                #Rotamos 2 --> 120
                self.rotate(2) #El robot va de 0-6 rad por lo que 120º son 2 rads
                self.bucle += 1
            

            self.get_logger().info('Maquing a Triangle!!')

            # response state
            response.success = True

            if response.success == True:
                self.stop_robot()
                self.figure_completed = True


###**********************************REINICIAR************************************************************###

        elif request.move == "Reiniciar":
            # Paramos el robot con su función
            self.stop_robot()
            #Reiniciamos el poder hacer figuras 
            self.figure_completed = False
            # print a pretty message
            self.get_logger().info('Reiniciando el robot!!')

            self.cmd.angular.z = 0.1
            self.cmd.linear.x = 0.0


            self.vel_pub.publish(self.cmd)
            
            
            # Con esta logica algo compleja hacemos que el robot vuelva a una posicion  de
            while self.yaw < 6.2 and self.contador == True:
                self.get_logger().info("YAW value:" + str(self.yaw))
                self.get_logger().info("GIRO value:" + str(self.giro))
                rclpy.spin_once(self, timeout_sec=1)

                if self.yaw < 0.1:
                    self.contador = False
             
            while self.yaw < 0.1 and self.contador == False:
                self.get_logger().info("YAW value:" + str(self.yaw))
                self.get_logger().info("GIRO value:" + str(self.giro))
                rclpy.spin_once(self, timeout_sec=1)
                
                if self.yaw > 0.1:
                    self.contador = True


            # Paramos el robot con su función
            self.stop_robot()
            self.giro = 0.0 
            self.contador = True

            # response state
            response.success = True


###**********************************STOP************************************************************###

        elif request.move == "Stop":
            # define the linear x-axis velocity of /cmd_vel topic parameter to 0
            self.cmd.linear.x = 0.0
            # define the angular z-axis velocity of /cmd_vel topic parameter to 0
            self.cmd.angular.z = 0.0
            # Publish the message to the topic
            self.vel_pub.publish(self.cmd)

            # print a pretty message
            self.get_logger().info('Stop there!!')
            # response state
            response.success = True
      

###**********************************ELSE OTRA COSA************************************************************###

        else:
            # response state
            response.success = False
        
        # return the response parameter
        return response


def main(args=None):
    rclpy.init(args=args)
    # declare the node constructor  
    service = Service()
    # initialize the ROS communication
    executor = MultiThreadedExecutor(num_threads=4)
    # Add the node to the executor
    executor.add_node(service)
    
    try:

        # Keep running the executor
        while rclpy.ok():
            rclpy.spin_once(service, timeout_sec=0.1)

            # Here you can add additional logic or commands
            # For example, you can check for new commands and respond to them
            # For simplicity, let's assume you have a variable "new_command" that contains the latest command
            # You can check it and take appropriate actions here
            if service.new_command == "NewCommand":
                # Execute the new command here
                pass  # Replace with your command execution logic
    
    except KeyboardInterrupt:
        pass
        
    # shutdown the ROS communication
    rclpy.shutdown()


if __name__ == '__main__':
    main()