import rclpy
import sys
from datetime import datetime
from rclpy.node import Node

from interfaz.msg import P2pkgmensaje
from random import random

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('nodopub_ejercicio2')
        self.publisher_ = self.create_publisher(P2pkgmensaje, '/topic_ejercicio2', 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.declare_parameter('numero', 5)

    def timer_callback(self):
        
        msg = P2pkgmensaje()
        
        # Número
        msg.numero = self.get_parameter('numero').get_parameter_value().integer_value

        # Point position
        msg.posicion.position.x = random()
        msg.posicion.position.y = random()
        msg.posicion.position.z = random()

        # Quaternion orientation
        msg.posicion.orientation.x = random()
        msg.posicion.orientation.y = random()
        msg.posicion.orientation.z = random()
        msg.posicion.orientation.w = random()

        # Fecha y hora
        msg.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.publisher_.publish(msg)
        self.get_logger().info(f"Enviando P2pkgmensaje: numero={msg.numero},\nposicion.position=({msg.posicion.position.x}, {msg.posicion.position.y}, {msg.posicion.position.z}),\nposicion.orientation=({msg.posicion.orientation.x}, {msg.posicion.orientation.y}, {msg.posicion.orientation.z}, {msg.posicion.orientation.w}),\nfecha={msg.fecha}\n\n")


def main(args=None):
    rclpy.init(args=args)
    nodopub_ejercicio2 = MinimalPublisher()
    rclpy.spin(nodopub_ejercicio2)
    nodopub_ejercicio2.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()