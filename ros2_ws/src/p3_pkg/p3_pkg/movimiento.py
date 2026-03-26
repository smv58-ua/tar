import sys
import math

from collections import deque

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

SPEED = 0.15    # m/s - Velocidad lineal
ANGLE_SPEED = 0.3   # rad/s - Velocidad angular

LINEAR_TOLERANCE = 0.01     # m - Tolerancia para el movimiento lineal
ANGULAR_TOLERANCE = 0.008   # rad - Tolerancia para el movimiento angular

SEQUENCES = {0, 1, 2, 3}

def quaternion_to_euler(x, y, z, w):
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))

class MovementNode(Node):

    def __init__(self):

        super().__init__('movement_node')

        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.subscription = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)

        self.x = None
        self.y = None
        self.theta = None

        self.origin_x = None
        self.origin_y = None
        self.origin_theta = None


        self.angular_vel = 0.0

        self.type = None
        self.value = None

        self.steps = deque()

    # ------------ Callback ------------

    def odom_callback(self, msg):
        
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        self.theta = quaternion_to_euler(
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w
        )
        self.angular_vel = msg.twist.twist.angular.z
                
        if self.type == 'forward':
            self.forward_movement_controller()
        
        elif self.type == 'rotate':
            self.rotate_movement_controller()

    # ------------ Movement controllers ------------

    def forward_movement_controller(self):
        
        if self.x is None or self.y is None:
            return

        # Distancia recorrida como módulo del desplazamiento (independiente de la dirección)
        distance_traveled = math.hypot(self.x - self.origin_x, self.y - self.origin_y)
        remaining = self.value - distance_traveled

        if remaining < LINEAR_TOLERANCE:
            self.stop_robot()
            self.next_step()
            return
        else:
            speed = min(SPEED, max(0.05, remaining * 1.5))
            msg = Twist()
            msg.linear.x = speed
            self.publisher.publish(msg)

    def rotate_movement_controller(self):

        if self.theta is None:
            return

        # Ángulo recorrido desde el origen, normalizado a (-π, π]
        angle_traveled = math.atan2(
            math.sin(self.theta - self.origin_theta),
            math.cos(self.theta - self.origin_theta)
        )
        remaining = self.value - angle_traveled

        if abs(remaining) < ANGULAR_TOLERANCE and abs(self.angular_vel) < 0.01:
            self.stop_robot()
            self.next_step()
            return

        else:
            angular_speed = min(ANGLE_SPEED, max(0.05, abs(remaining) * 1.5))
            msg = Twist()
            msg.angular.z = angular_speed if remaining > 0 else -angular_speed
            self.publisher.publish(msg)

    def stop_robot(self):
        self.publisher.publish(Twist())

    # ----------- Movement sequence management ------------

    def next_step(self):

        if self.x is not None and self.y is not None and self.theta is not None:
            self.get_logger().info(f'Initial/Final step position: x={self.x:.2f}, y={self.y:.2f}, theta={math.degrees(self.theta):.2f} degrees')
        
        if len(self.steps) > 0:
            self.steps.popleft()

            if len(self.steps) > 0:
                
                tuple = self.steps[0]
                
                if len(tuple) == 2:
                    self.type, self.value = tuple

            else:
                self.get_logger().info('All steps completed.')
                exit(0)

        if self.type == 'forward':
            
            self.origin_x = self.x
            self.origin_y = self.y

            msg = Twist()
            msg.linear.x = SPEED
            self.publisher.publish(msg)

        elif self.type == 'rotate':
            
            self.origin_theta = self.theta
            self.value = math.radians(self.value)

            msg = Twist()
            msg.angular.z = ANGLE_SPEED if self.value > 0 else -ANGLE_SPEED
            self.publisher.publish(msg)

    def init(self):

        if len(self.steps) > 0:
                
            tuple = self.steps[0]
            
            if len(tuple) == 2:
                self.type, self.value = tuple

        else:
            self.get_logger().info('No steps to execute.')
            exit(0)

        if self.type == 'forward':
            
            self.origin_x = self.x
            self.origin_y = self.y

        elif self.type == 'rotate':
            
            self.origin_theta = self.theta
            self.value = math.radians(self.value)

    def run(self, movement_type):

        if movement_type == 0:

            self.steps.append(('forward', 2.0))

        elif movement_type == 1:

            self.steps.append(('forward', 3))
            self.steps.append(('rotate', -120))
            self.steps.append(('forward', 3))
            self.steps.append(('rotate', -120))
            self.steps.append(('forward', 3))

        self.get_logger().info('Esperando primer mensaje de odometría...')
        while self.x is None or self.y is None or self.theta is None:
            rclpy.spin_once(self, timeout_sec=0.1)

        # Alinear el robot con el eje X positivo (yaw = 0) antes de empezar
        initial_correction = -math.degrees(self.theta)
        if abs(initial_correction) > math.degrees(ANGULAR_TOLERANCE):
            self.steps.appendleft(("rotate", initial_correction))

        self.init()

def main(args=None):
    
    rclpy.init(args=args)

    if len(sys.argv) < 2:
        print('Uso: ros2 run p3_pkg movimiento <modo>')
        rclpy.shutdown()
        return

    try:
        mode = int(sys.argv[1])
    except ValueError:
        print(f'Error: "{sys.argv[1]}" no es un entero válido.')
        rclpy.shutdown()
        return

    if mode not in SEQUENCES:
        print(f'Error: Modo "{mode}" no reconocido.')
        rclpy.shutdown()
        return

    node = MovementNode()
    node.run(mode)
    
    rclpy.spin(node)

if __name__ == '__main__':
    main()