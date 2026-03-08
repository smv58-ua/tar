import time

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from interfaz.action import Fibonacci


class FibonacciActionServer(Node):

    def __init__(self):
        super().__init__('fibonacci_action_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.secuencia_actual = [0, 1]

        for i in range(1, goal_handle.request.orden):
            feedback_msg.secuencia_actual.append(
                feedback_msg.secuencia_actual[i] + feedback_msg.secuencia_actual[i-1])
            self.get_logger().info('Feedback: {0}'.format(feedback_msg.secuencia_actual))
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(1)

        goal_handle.succeed()

        result = Fibonacci.Result()
        result.secuencia_final = feedback_msg.secuencia_actual
        return result


def main(args=None):
    rclpy.init(args=args)

    fibonacci_action_server = FibonacciActionServer()

    rclpy.spin(fibonacci_action_server)


if __name__ == '__main__':
    main()