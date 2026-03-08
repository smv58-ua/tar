import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from std_msgs.msg import String
from interfaz.action import EjFibonacci

class FibonacciActionClient(Node):

    def __init__(self):
        super().__init__('fibonacci_action_client')
        
        self.declare_parameter('orden', 10)
        self._action_client = ActionClient(self, EjFibonacci, 'fibonacci')
        
        self._publisher = self.create_publisher(String, '/estado_accion', 10)
        
        self.is_executing = False
        self.timer = self.create_timer(0.5, self.publish_status)

    def publish_status(self):
        
        if self.is_executing:
            msg = String()
            msg.data = 'en proceso'
            self._publisher.publish(msg)

    def send_goal(self):

        orden_val = self.get_parameter('orden').get_parameter_value().integer_value
        
        self.get_logger().info(f'Esperando al servidor... (Orden: {orden_val})')
        self._action_client.wait_for_server()

        goal_msg = EjFibonacci.Goal()
        goal_msg.orden = orden_val

        self.get_logger().info('Enviando goal...')
        self.is_executing = True

        self._send_goal_future = self._action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)

        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        
        result = future.result().result
        self.get_logger().info(f'Result: {result.secuencia_final}')
        self.is_executing = False
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):

        feedback = feedback_msg.feedback
        self.get_logger().info(f'Received feedback: {feedback.secuencia_actual:.4f}')

def main(args=None):
    rclpy.init(args=args)
    action_client = FibonacciActionClient()
    action_client.send_goal()
    rclpy.spin(action_client)

if __name__ == '__main__':
    main()