import time
import math # Necesario para sqrt

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from interfaz.action import EjFibonacci


class FibonacciActionServer(Node):

    def __init__(self):
        super().__init__('fibonacci_action_server_ejercicio')
        self._action_server = ActionServer(
            self,
            EjFibonacci,
            'fibonacci',
            self.execute_callback)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        feedback_msg = EjFibonacci.Feedback()
        secuencia_interna = [0, 1]

        for i in range(1, goal_handle.request.orden):
            secuencia_interna.append(secuencia_interna[i] + secuencia_interna[i-1])
            
            media = sum(secuencia_interna) / len(secuencia_interna)
            feedback_msg.secuencia_actual = math.sqrt(media)

            self.get_logger().info('Feedback: {0}'.format(feedback_msg.secuencia_actual))
            
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(1)

        goal_handle.succeed()

        result = EjFibonacci.Result()
        result.secuencia_final = secuencia_interna
        return result


def main(args=None):
    rclpy.init(args=args)

    fibonacci_action_server = FibonacciActionServer()

    rclpy.spin(fibonacci_action_server)


if __name__ == '__main__':
    main()