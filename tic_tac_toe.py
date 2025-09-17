import pygame
import sys
import random

# Inicializar pygame
pygame.init()

# Constantes
WINDOW_SIZE = 600
BOARD_SIZE = 3
# Padding para un tablero centrado al estilo Apple
BOARD_PADDING = 24
CELL_SIZE = (WINDOW_SIZE - BOARD_PADDING * 2) // BOARD_SIZE
LINE_WIDTH = 6
CROSS_WIDTH = 10

# Colores estilo Apple (modo claro)
WHITE = (255, 255, 255)
BG = (248, 249, 251)          # Fondo sutil
TEXT = (28, 28, 30)           # Label color
SUBTEXT = (142, 142, 147)     # Secondary label
LINE = (200, 200, 204)        # Separadores
ACCENT_BLUE = (10, 132, 255)  # iOS blue
ACCENT_RED = (255, 55, 95)    # iOS system red
SUCCESS = (52, 199, 89)

# Utilidad para alpha (sombra)
def make_alpha_surface(size, alpha):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.set_alpha(alpha)
    return surf

class TicTacToe:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 120))
        pygame.display.set_caption("Tic Tac Toe")
        self.clock = pygame.time.Clock()
        self.font = self._get_system_font(36)
        self.small_font = self._get_system_font(22)
        self.title_font = self._get_system_font(40, bold=True)
        
        # Estado del juego
        self.board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 'X'
        self.game_mode = None  # 'pvp' o 'pvc'
        self.game_over = False
        self.winner = None
        self.show_menu = True
        # Animación de aparición por celda (0 a 1)
        self.appear = [[1.0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        # Delay para la computadora
        self.computer_delay = 0.0
        self.computer_thinking = False
        self.computer_move_pending = None

    def _get_system_font(self, size, bold=False):
        candidates = [
            "SF Pro Display",
            "SF Pro Text",
            "SF Pro",
            "Helvetica Neue",
            "Helvetica",
            "Arial",
        ]
        for name in candidates:
            try:
                return pygame.font.SysFont(name, size, bold=bold)
            except Exception:
                continue
        return pygame.font.Font(None, size)
        
    def draw_menu(self):
        """Dibuja el menú de selección de modo de juego"""
        self._draw_background()
        
        # Título
        title = self.title_font.render("TIC TAC TOE", True, TEXT)
        title_rect = title.get_rect(center=(WINDOW_SIZE//2, 90))
        self.screen.blit(title, title_rect)
        
        # Botones de modo
        mouse_pos = pygame.mouse.get_pos()

        # Botón PvP
        pvp_rect = pygame.Rect(WINDOW_SIZE//2 - 160, 190, 320, 56)
        self._draw_button(pvp_rect, ACCENT_BLUE, hover=pvp_rect.collidepoint(mouse_pos))
        pvp_text = self.font.render("Jugador vs Jugador", True, WHITE)
        pvp_text_rect = pvp_text.get_rect(center=pvp_rect.center)
        self.screen.blit(pvp_text, pvp_text_rect)
        
        # Botón PvC
        pvc_rect = pygame.Rect(WINDOW_SIZE//2 - 160, 260, 320, 56)
        self._draw_button(pvc_rect, ACCENT_RED, hover=pvc_rect.collidepoint(mouse_pos))
        pvc_text = self.font.render("Jugador vs Computadora", True, WHITE)
        pvc_text_rect = pvc_text.get_rect(center=pvc_rect.center)
        self.screen.blit(pvc_text, pvc_text_rect)
        
        # Instrucciones
        instructions = [
            "Haz clic en una casilla para jugar",
            "X siempre empieza",
            "Presiona R para reiniciar",
            "Presiona ESC para volver al menú"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, SUBTEXT)
            text_rect = text.get_rect(center=(WINDOW_SIZE//2, 360 + i * 24))
            self.screen.blit(text, text_rect)
    
    def draw_board(self):
        """Dibuja el tablero de juego"""
        self._draw_background()
        
        # Tarjeta con sombra detrás del tablero
        outer_rect = pygame.Rect(BOARD_PADDING - 6, BOARD_PADDING - 6, CELL_SIZE * BOARD_SIZE + 12, CELL_SIZE * BOARD_SIZE + 12)
        self._draw_card_shadow(outer_rect)
        board_rect = pygame.Rect(BOARD_PADDING, BOARD_PADDING, CELL_SIZE * BOARD_SIZE, CELL_SIZE * BOARD_SIZE)
        pygame.draw.rect(self.screen, WHITE, board_rect, border_radius=16)
        
        # Dibujar líneas del tablero
        for i in range(1, BOARD_SIZE):
            # Líneas verticales
            x = BOARD_PADDING + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE, 
                           (x, BOARD_PADDING), 
                           (x, BOARD_PADDING + CELL_SIZE * BOARD_SIZE), 
                           LINE_WIDTH)
            # Líneas horizontales
            y = BOARD_PADDING + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE, 
                           (BOARD_PADDING, y), 
                           (BOARD_PADDING + CELL_SIZE * BOARD_SIZE, y), 
                           LINE_WIDTH)
        
        # Dibujar X y O
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == 'X':
                    self.draw_x(row, col)
                elif self.board[row][col] == 'O':
                    self.draw_o(row, col)
    
    def draw_x(self, row, col):
        """Dibuja una X en la casilla especificada"""
        center_x = BOARD_PADDING + col * CELL_SIZE + CELL_SIZE // 2
        center_y = BOARD_PADDING + row * CELL_SIZE + CELL_SIZE // 2
        p = self.appear[row][col]
        max_offset = int(CELL_SIZE * 0.33)
        offset = int(max_offset * p)
        color = ACCENT_RED
        
        # Dibujar las dos líneas de la X
        pygame.draw.line(self.screen, color, 
                        (center_x - offset, center_y - offset),
                        (center_x + offset, center_y + offset), int(CROSS_WIDTH * max(p, 0.6)))
        pygame.draw.line(self.screen, color, 
                        (center_x + offset, center_y - offset),
                        (center_x - offset, center_y + offset), int(CROSS_WIDTH * max(p, 0.6)))
    
    def draw_o(self, row, col):
        """Dibuja una O en la casilla especificada"""
        center_x = BOARD_PADDING + col * CELL_SIZE + CELL_SIZE // 2
        center_y = BOARD_PADDING + row * CELL_SIZE + CELL_SIZE // 2
        p = self.appear[row][col]
        radius = int((CELL_SIZE * 0.38) * p)
        pygame.draw.circle(self.screen, ACCENT_BLUE, (center_x, center_y), radius, int(CROSS_WIDTH * max(p, 0.6)))
    
    def draw_status(self):
        """Dibuja el estado del juego debajo del tablero"""
        y_offset = WINDOW_SIZE + 16
        
        if self.game_over:
            if self.winner:
                if self.winner == 'tie':
                    label = "¡Empate!"
                    color = TEXT
                else:
                    label = f"¡{self.winner} gana!"
                    color = SUCCESS
            else:
                label = "Juego terminado"
                color = TEXT
        else:
            if self.game_mode == 'pvc' and self.current_player == 'O':
                if self.computer_thinking:
                    label = "La computadora está pensando..."
                    color = SUBTEXT
                else:
                    label = "Turno de la computadora..."
                    color = TEXT
            else:
                label = f"Turno de {self.current_player}"
                color = TEXT
        
        text = self.small_font.render(label, True, color)
        text_rect = text.get_rect()
        pill_padding_x = 14
        pill_padding_y = 8
        pill_rect = pygame.Rect(0, 0, text_rect.width + pill_padding_x * 2, text_rect.height + pill_padding_y * 2)
        pill_rect.center = (WINDOW_SIZE//2, y_offset + 22)
        # Sombra de la pastilla
        shadow_rect = pill_rect.copy()
        shadow_rect.y += 4
        self._draw_soft_shadow(shadow_rect, radius=20, alpha=60)
        # Pastilla
        pygame.draw.rect(self.screen, WHITE, pill_rect, border_radius=20)
        pygame.draw.rect(self.screen, (235, 235, 240), pill_rect, width=1, border_radius=20)
        # Texto
        text_rect.center = pill_rect.center
        self.screen.blit(text, text_rect)
        
        # Instrucciones
        restart_text = self.small_font.render("Presiona R para reiniciar | ESC para menú", True, SUBTEXT)
        restart_rect = restart_text.get_rect(center=(WINDOW_SIZE//2, y_offset + 52))
        self.screen.blit(restart_text, restart_rect)
    
    def get_cell_from_pos(self, pos):
        """Convierte posición del mouse a coordenadas del tablero"""
        x, y = pos
        board_rect = pygame.Rect(BOARD_PADDING, BOARD_PADDING, CELL_SIZE * BOARD_SIZE, CELL_SIZE * BOARD_SIZE)
        if board_rect.collidepoint(x, y):
            col = (x - BOARD_PADDING) // CELL_SIZE
            row = (y - BOARD_PADDING) // CELL_SIZE
            return row, col
        return None, None
    
    def is_valid_move(self, row, col):
        """Verifica si un movimiento es válido"""
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and self.board[row][col] == ''
    
    def make_move(self, row, col):
        """Realiza un movimiento en el tablero"""
        if self.is_valid_move(row, col) and not self.game_over:
            self.board[row][col] = self.current_player
            self.appear[row][col] = 0.0
            return True
        return False
    
    def check_winner(self):
        """Verifica si hay un ganador o empate"""
        # Verificar filas
        for row in self.board:
            if row[0] == row[1] == row[2] != '':
                return row[0]
        
        # Verificar columnas
        for col in range(BOARD_SIZE):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != '':
                return self.board[0][col]
        
        # Verificar diagonales
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return self.board[0][2]
        
        # Verificar empate
        if all(self.board[row][col] != '' for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)):
            return 'tie'
        
        return None
    
    def get_computer_move(self):
        """Obtiene el movimiento de la computadora usando minimax"""
        # Primero verificar si puede ganar
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.is_valid_move(row, col):
                    self.board[row][col] = 'O'
                    if self.check_winner() == 'O':
                        self.board[row][col] = ''
                        return row, col
                    self.board[row][col] = ''
        
        # Luego verificar si debe bloquear al jugador
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.is_valid_move(row, col):
                    self.board[row][col] = 'X'
                    if self.check_winner() == 'X':
                        self.board[row][col] = ''
                        return row, col
                    self.board[row][col] = ''
        
        # Si no puede ganar ni bloquear, elegir una casilla aleatoria
        available_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.is_valid_move(row, col):
                    available_moves.append((row, col))
        
        if available_moves:
            return random.choice(available_moves)
        
        return None, None
    
    def reset_game(self):
        """Reinicia el juego"""
        self.board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.appear = [[1.0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.computer_delay = 0.0
        self.computer_thinking = False
        self.computer_move_pending = None
    
    def handle_click(self, pos):
        """Maneja el clic del mouse"""
        if self.show_menu:
            x, y = pos
            # Verificar clic en botón PvP
            if WINDOW_SIZE//2 - 160 <= x <= WINDOW_SIZE//2 + 160 and 190 <= y <= 246:
                self.game_mode = 'pvp'
                self.show_menu = False
                self.reset_game()
            # Verificar clic en botón PvC
            elif WINDOW_SIZE//2 - 160 <= x <= WINDOW_SIZE//2 + 160 and 260 <= y <= 316:
                self.game_mode = 'pvc'
                self.show_menu = False
                self.reset_game()
        else:
            if not self.game_over:
                row, col = self.get_cell_from_pos(pos)
                if row is not None and col is not None:
                    if self.make_move(row, col):
                        winner = self.check_winner()
                        if winner:
                            self.game_over = True
                            self.winner = winner
                        else:
                            self.current_player = 'O' if self.current_player == 'X' else 'X'
                            
                            # Si es modo PvC y es turno de la computadora
                            if self.game_mode == 'pvc' and self.current_player == 'O' and not self.game_over:
                                self.computer_thinking = True
                                self.computer_delay = 0.7  # 1.7 segundos de delay
                                self.computer_move_pending = self.get_computer_move()

    def _draw_background(self):
        # Fondo sólido
        self.screen.fill(BG)
        # Sutil gradiente superior
        gradient_height = 120
        grad_surface = make_alpha_surface((WINDOW_SIZE, gradient_height), 100)
        for i in range(gradient_height):
            alpha = max(0, 80 - int(i * 0.6))
            line = pygame.Surface((WINDOW_SIZE, 1), pygame.SRCALPHA)
            line.fill((255, 255, 255, alpha))
            grad_surface.blit(line, (0, i))
        self.screen.blit(grad_surface, (0, 0))

    def _draw_card_shadow(self, rect):
        shadow_rect = rect.copy()
        shadow_rect.x += 0
        shadow_rect.y += 6
        self._draw_soft_shadow(shadow_rect, radius=16, alpha=70)

    def _draw_soft_shadow(self, rect, radius=16, alpha=80):
        # Aproximar sombra dibujando varias capas con alpha decreciente
        for i in range(6):
            expand = i * 2
            a = max(0, alpha - i * 12)
            shadow_surf = pygame.Surface((rect.width + expand * 2, rect.height + expand * 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, a), shadow_surf.get_rect(), border_radius=radius + i)
            self.screen.blit(shadow_surf, (rect.x - expand, rect.y - expand))

    def _draw_button(self, rect, color, hover=False):
        # Sombra
        shadow = rect.copy()
        shadow.y += 6
        self._draw_soft_shadow(shadow, radius=20, alpha=70)
        # Botón
        btn_color = (
            min(255, int(color[0] * (1.06 if hover else 1.0))),
            min(255, int(color[1] * (1.06 if hover else 1.0))),
            min(255, int(color[2] * (1.06 if hover else 1.0)))
        )
        pygame.draw.rect(self.screen, btn_color, rect, border_radius=20)
    
    def run(self):
        """Bucle principal del juego"""
        running = True
        
        while running:
            dt = self.clock.get_time() / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic izquierdo
                        self.handle_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Reiniciar
                        if not self.show_menu:
                            self.reset_game()
                    elif event.key == pygame.K_ESCAPE:  # Volver al menú
                        if not self.show_menu:
                            self.show_menu = True
                            self.reset_game()
            
            # Actualizar animaciones
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if self.appear[r][c] < 1.0:
                        self.appear[r][c] = min(1.0, self.appear[r][c] + dt * 6.0)
            
            # Actualizar delay de la computadora
            if self.computer_thinking and self.computer_delay > 0:
                self.computer_delay -= dt
                if self.computer_delay <= 0:
                    # Ejecutar el movimiento pendiente de la computadora
                    if self.computer_move_pending and not self.game_over:
                        row, col = self.computer_move_pending
                        if self.make_move(row, col):
                            winner = self.check_winner()
                            if winner:
                                self.game_over = True
                                self.winner = winner
                            else:
                                self.current_player = 'X'
                    self.computer_thinking = False
                    self.computer_move_pending = None
            
            # Dibujar
            if self.show_menu:
                self.draw_menu()
            else:
                self.draw_board()
                self.draw_status()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TicTacToe()
    game.run()
