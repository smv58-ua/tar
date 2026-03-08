import sys
import rclpy
from rclpy.node import Node
from interfaz.srv import TempConvert

class TempClient(Node):
    def __init__(self):
        super().__init__('temp_convert_client')
        self.client = self.create_client(TempConvert, 'convert_temp')
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Servidor no disponible, esperando...')
        self.req = TempConvert.Request()

    def send_request(self, temp, conv_type):
        self.req.input_temp = float(temp)
        self.req.conversion_type = conv_type
        return self.client.call_async(self.req)

def main():
    rclpy.init()
    if len(sys.argv) < 3:
        print("Se debe usar: ros2 run service_temp client <temperatura> <tipo>")
        return

    temp_val = sys.argv[1]
    type_val = sys.argv[2]

    tipos_validos = ['Cel_to_Far', 'Far_to_Cel']
    if type_val not in tipos_validos:
        print(f"[ERROR CLIENTE]: '{type_val}' no es válido.")
        print("Opciones permitidas: Cel_to_Far, Far_to_Cel")
        return

    client_node = TempClient()
    future = client_node.send_request(temp_val, type_val)
    
    rclpy.spin_until_future_complete(client_node, future)

    if future.result() is not None:
        print(f'Resultado de la conversión: {future.result().converted_temp:.2f}')
    else:
        print('Error en la llamada al servicio')

    client_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()