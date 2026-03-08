import rclpy
from rclpy.node import Node

from interfaz.msg import P2pkgmensaje

class MinimalSubscriber(Node):
    
    def __init__(self):
        super().__init__('nodosub_ejercicio2')
        self.subscription = self.create_subscription(
            P2pkgmensaje,
            '/topic_ejercicio2',
            self.listener_callback,
            10)
        self.subscription

    def listener_callback(self, msg):
        self.get_logger().info(f"Recibido P2pkgmensaje: numero={msg.numero},\nposicion.position=({msg.posicion.position.x}, {msg.posicion.position.y}, {msg.posicion.position.z}),\nposicion.orientation=({msg.posicion.orientation.x}, {msg.posicion.orientation.y}, {msg.posicion.orientation.z}, {msg.posicion.orientation.w}),\nfecha={msg.fecha}\n\n")

def main(args=None):
    rclpy.init(args=args)
    nodosub_ejercicio2 = MinimalSubscriber()
    rclpy.spin(nodosub_ejercicio2)
    nodosub_ejercicio2.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()