"""Questao 9 - Servidor da acao /deslocamento (simula o robo).

Recebe como meta a localizacao de destino (latitude, longitude) e as
velocidades latitudinal e longitudinal (unidades por segundo).
- So aceita a meta se a localizacao for diferente da atual;
- Desloca o robo e envia feedback com a localizacao atual a cada 1 s;
- Ao final, responde com a distancia total percorrida.
"""

import math
import time

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from robo_interfaces.action import Deslocamento


class RoboAcaoServidor(Node):
    def __init__(self):
        super().__init__('robo_acao_servidor')
        # Posicao inicial do robo
        self._latitude = 0.0
        self._longitude = 0.0
        self._server = ActionServer(
            self,
            Deslocamento,
            'deslocamento',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=ReentrantCallbackGroup())
        self.get_logger().info('Servidor da acao deslocamento disponivel')

    def goal_callback(self, goal_request):
        # Sucesso so faz sentido se o destino for diferente da posicao atual
        if (goal_request.latitude == self._latitude
                and goal_request.longitude == self._longitude):
            self.get_logger().info(
                'Meta rejeitada: destino igual a posicao atual')
            return GoalResponse.REJECT
        self.get_logger().info(
            f'Meta aceita: ({goal_request.latitude}, '
            f'{goal_request.longitude})')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Pedido de cancelamento recebido')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        meta = goal_handle.request
        distancia_percorrida = 0.0
        feedback = Deslocamento.Feedback()

        while True:
            # Cancelamento: devolve a distancia percorrida ate aqui
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                resultado = Deslocamento.Result()
                resultado.distancia_percorrida = distancia_percorrida
                self.get_logger().info(
                    f'Acao cancelada. Distancia percorrida: '
                    f'{distancia_percorrida:.2f}')
                return resultado

            # Passo de 1 segundo em cada eixo (sem ultrapassar a meta)
            passo_lat = self._passo(meta.latitude - self._latitude,
                                    meta.velocidade_latitudinal)
            passo_lon = self._passo(meta.longitude - self._longitude,
                                    meta.velocidade_longitudinal)

            if passo_lat == 0.0 and passo_lon == 0.0:
                if (self._latitude == meta.latitude
                        and self._longitude == meta.longitude):
                    break  # chegou ao destino
                # Velocidade nula: impossivel sair do lugar
                goal_handle.abort()
                resultado = Deslocamento.Result()
                resultado.distancia_percorrida = distancia_percorrida
                self.get_logger().info(
                    'Meta abortada: velocidade nula impede o deslocamento')
                return resultado

            self._latitude += passo_lat
            self._longitude += passo_lon
            distancia_percorrida += math.hypot(passo_lat, passo_lon)

            # Feedback com a localizacao atual (a cada 1 segundo)
            feedback.latitude_atual = self._latitude
            feedback.longitude_atual = self._longitude
            goal_handle.publish_feedback(feedback)
            self.get_logger().info(
                f'Feedback -> posicao atual: ({self._latitude:.2f}, '
                f'{self._longitude:.2f})')

            time.sleep(1.0)

        goal_handle.succeed()
        resultado = Deslocamento.Result()
        resultado.distancia_percorrida = distancia_percorrida
        self.get_logger().info(
            f'Destino alcancado! Distancia percorrida: '
            f'{distancia_percorrida:.2f}')
        return resultado

    @staticmethod
    def _passo(delta, velocidade):
        """Tamanho do passo em um eixo, limitado pela velocidade."""
        if delta == 0.0:
            return 0.0
        passo = min(abs(delta), velocidade)
        return passo if delta > 0 else -passo


def main(args=None):
    rclpy.init(args=args)
    no = RoboAcaoServidor()
    # MultiThreadedExecutor permite atender cancelamento e feedback juntos
    rclpy.spin(no, executor=MultiThreadedExecutor())
    no.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
