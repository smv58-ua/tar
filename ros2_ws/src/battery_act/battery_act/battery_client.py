import sys
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from interfaz.action import Battery

class BatteryClient(Node):
    def __init__(self):
        super().__init__('battery_client')
        self._action_client = ActionClient(self, Battery, 'battery_status')

    def send_goal(self, target):
        goal_msg = Battery.Goal()
        goal_msg.target_percentage = target

        self._action_client.wait_for_server()
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rechazado')
            return
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        print(f'[FEEDBACK] Batería actual: {feedback_msg.feedback.current_percentage}%')

    def get_result_callback(self, future):
        result = future.result().result
        print(f'[RESULTADO] Mensaje: {result.warning}')
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    
    if len(sys.argv) < 2:
        print("Uso: ros2 run battery_act client <porcentaje_objetivo>")
        return

    target = int(sys.argv[1])
    client = BatteryClient()
    client.send_goal(target)
    rclpy.spin(client)

if __name__ == '__main__':
    main()