"""Questao 6 - Cliente do servico coleta_material (estacao base).

Envia uma requisicao com profundidade aleatoria entre 0.1 e 0.5 e
informa se a coleta foi ou nao bem sucedida, conforme a resposta.
"""

import random

import rclpy
from rclpy.node import Node

from robo_interfaces.srv import ColetaMaterial


class RoboColetaCliente(Node):
    def __init__(self):
        super().__init__('robo_coleta_cliente')
        self._client = self.create_client(ColetaMaterial, 'coleta_material')
        while not self._client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Aguardando o servico coleta_material...')
        self._request = ColetaMaterial.Request()

    def enviar_requisicao(self):
        self._request.profundidade = random.uniform(0.1, 0.5)
        self.get_logger().info(
            f'Requisitando coleta na profundidade '
            f'{self._request.profundidade:.2f} m')
        futuro = self._client.call_async(self._request)
        rclpy.spin_until_future_complete(self, futuro)
        return futuro.result()


def main(args=None):
    rclpy.init(args=args)
    no = RoboColetaCliente()
    resposta = no.enviar_requisicao()
    if resposta.sucesso:
        no.get_logger().info('A coleta foi BEM SUCEDIDA!')
    else:
        no.get_logger().info('A coleta NAO foi bem sucedida.')
    no.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
