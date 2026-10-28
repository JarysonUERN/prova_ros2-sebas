"""Questao 10 - Cliente da acao /deslocamento que espera ate o final.

Solicita o deslocamento do robo, exibe os feedbacks de posicao e, ao
termino da acao, apresenta a distancia total percorrida.
"""

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from robo_interfaces.action import Deslocamento


class RoboAcaoCliente(Node):
    def __init__(self):
        super().__init__('robo_acao_cliente')
        self._cliente = ActionClient(self, Deslocamento, 'deslocamento')

    def enviar_meta(self, latitude, longitude, vel_lat, vel_lon):
        meta = Deslocamento.Goal()
        meta.latitude = latitude
        meta.longitude = longitude
        meta.velocidade_latitudinal = vel_lat
        meta.velocidade_longitudinal = vel_lon

        self.get_logger().info('Aguardando o servidor de acao...')
        self._cliente.wait_for_server()

        self.get_logger().info(
            f'Enviando meta: destino ({latitude}, {longitude}) com '
            f'velocidades ({vel_lat}, {vel_lon}) u/s')
        futuro_meta = self._cliente.send_goal_async(
            meta, feedback_callback=self.feedback_callback)
        futuro_meta.add_done_callback(self.resposta_meta_callback)

    def resposta_meta_callback(self, futuro):
        goal_handle = futuro.result()
        if not goal_handle.accepted:
            self.get_logger().info('Meta rejeitada pelo robo!')
            rclpy.shutdown()
            return
        self.get_logger().info('Meta aceita. Robo em deslocamento...')
        futuro_resultado = goal_handle.get_result_async()
        futuro_resultado.add_done_callback(self.resultado_callback)

    def feedback_callback(self, mensagem):
        feedback = mensagem.feedback
        self.get_logger().info(
            f'Feedback -> posicao atual: ({feedback.latitude_atual:.2f}, '
            f'{feedback.longitude_atual:.2f})')

    def resultado_callback(self, futuro):
        resultado = futuro.result().result
        self.get_logger().info(
            f'Acao finalizada! Distancia percorrida: '
            f'{resultado.distancia_percorrida:.2f} unidades')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    no = RoboAcaoCliente()
    # Destino (10, 10) com velocidade 1 u/s em cada eixo
    no.enviar_meta(10.0, 10.0, 1.0, 1.0)
    rclpy.spin(no)


if __name__ == '__main__':
    main()
