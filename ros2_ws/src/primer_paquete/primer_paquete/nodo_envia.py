import rclpy
from rclpy.node import Node

from interfaz.msg import MiMensaje

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('nodo_envia')
        self.publisher_ = self.create_publisher(MiMensaje, '/mitopic', 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.x = 0
        self.y = 0

    def timer_callback(self):
        msg = MiMensaje()                                                
        msg.x = self.x 
        msg.y = self.y
        self.publisher_.publish(msg)
        self.get_logger().info(f"Enviando MiMensaje: Nombre={msg.NOMBRE} x={msg.x}, y={msg.y}")       
        self.x += 1
        self.y += 2


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()