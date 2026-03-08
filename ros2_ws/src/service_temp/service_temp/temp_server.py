import rclpy
from rclpy.node import Node
from interfaz.srv import TempConvert

class TempServer(Node):
    def __init__(self):
        super().__init__('temp_convert_server')
        self.srv = self.create_service(TempConvert, 'convert_temp', self.convert_callback)
        self.get_logger().info('Servidor de Temperatura listo.')

    def convert_callback(self, request, response):
        if request.conversion_type == 'Cel_to_Far':
            response.converted_temp = (request.input_temp * 1.8) + 32
            self.get_logger().info(f'Convirtiendo {request.input_temp}C a Fahrenheit')
        elif request.conversion_type == 'Far_to_Cel':
            response.converted_temp = (request.input_temp - 32) / 1.8
            self.get_logger().info(f'Convirtiendo {request.input_temp}F a Celsius')
        
        return response

def main():
    rclpy.init()
    node = TempServer()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()