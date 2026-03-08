import time
import rclpy
from rclpy.action import ActionServer, CancelResponse
from rclpy.node import Node
from interfaz.action import Battery

class BatteryCharger(Node):
    def __init__(self):
        super().__init__('battery_charger')
        self._action_server = ActionServer(
        self,
        Battery,
        'battery_status',
        execute_callback=self.execute_callback,
        cancel_callback=self.cancel_callback)
        self.get_logger().info('Servidor de Batería iniciado...')

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Recibida petición de cancelación')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        self.get_logger().info('Iniciando descarga de batería...')
        
        feedback_msg = Battery.Feedback()
        current_bat = 100   # Se usa directamente el porcentaje
        target = goal_handle.request.target_percentage

        while current_bat > target:
            
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Acción CANCELADA')
                return Battery.Result(warning="Proceso interrumpido por el usuario")

            current_bat -= 5
            feedback_msg.current_percentage = current_bat
            self.get_logger().info(f'Batería: {current_bat}%')
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(1.0)

        goal_handle.succeed()
        result = Battery.Result()
        result.warning = "Batería Baja, por favor cargue el robot!"
        return result

def main(args=None):
    rclpy.init(args=args)
    node = BatteryCharger()
    rclpy.spin(node)

if __name__ == '__main__':
    main()