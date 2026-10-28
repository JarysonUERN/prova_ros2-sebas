"""Questao 7 - Servidor do servico coleta_material (simula o robo).

Recebe a profundidade da coleta e retorna sucesso (True) com
probabilidade de 70% (numero aleatorio entre 0 e 1 menor ou igual a 0.7).
"""

import random

import rclpy
from rclpy.node import Node

from robo_interfaces.srv import ColetaMaterial


class RoboColetaServidor(Node):
    def __init__(self):
        super().__init__('robo_coleta_servidor')
        self._service = self.create_service(
            ColetaMaterial, 'coleta_material', self.coleta_callback)
        self.get_logger().info('Servico coleta_material disponivel')

    def coleta_callback(self, request, response):
        response.sucesso = random.random() <= 0.7
        resultado = 'SUCESSO' if response.sucesso else 'FALHA'
        self.get_logger().info(
            f'Coleta na profundidade {request.profundidade:.2f} m -> '
            f'{resultado}')
        return response


def main(args=None):
    rclpy.init(args=args)
    no = RoboColetaServidor()
    rclpy.spin(no)
    no.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
