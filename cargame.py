import pygame
import random
from sys import exit as sys_exit

# TODO: Add sound effect, trees graphics
# TODO: Make the movement of the dashed line smoothly transition when level up

pygame.init()

pygame.mixer.init()


class Game:
    FPS = 60  # set also game speed, the higher the value the faster the game

    def __init__(self):
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 800, 660
        self.road_w = self.SCREEN_WIDTH // 1.6
        self.roadmark_w = self.SCREEN_WIDTH // 80
        self.right_lane = self.SCREEN_WIDTH / 2 + self.road_w / 4
        self.left_lane = self.SCREEN_WIDTH / 2 - self.road_w / 4
        self.speed = 3
        self.speed_factor = self.SCREEN_HEIGHT / 660  # animate enemy vehicle
        self.car_lane = "R"
        self.car2_lane = "L"
        self.current_enemy = None

        self.GRASS_COLOR = (60, 220, 0)
        self.DARK_ROAD_COLOR = (50, 50, 50)
        self.YELLOW_LINE_COLOR = (255, 240, 60)
        self.WHITE_LINE_COLOR = (255, 255, 255)

        self.score = 0
        self.level = 0

        self.CLOCK = pygame.time.Clock()
        self.event_updater_counter = 0  # for moving dashed line on the road

        self.SCREEN = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE
        )

        pygame.display.set_caption("2D Car Game")

        self.game_over_font = pygame.font.SysFont("Arial", 60)
        self.score_font = pygame.font.Font("assets/fonts/joystix monospace.otf", 30)
        self.game_info_font = pygame.font.SysFont("Arial", 40)

        # load sound effects
        self.car_crash_sound = pygame.mixer.Sound("assets/carCrash.wav")

        # load player car
        self.original_car = pygame.image.load("assets/cars/car.png")
        self.car = pygame.transform.scale(
            self.original_car,
            (
                int(self.original_car.get_width() * (self.SCREEN_WIDTH / 800)),
                int(self.original_car.get_height() * (self.SCREEN_HEIGHT / 600)),
            ),
        )
        self.car_loc = self.car.get_rect()
        self.car_loc.center = (
            self.right_lane,
            self.SCREEN_HEIGHT - self.car_loc.height * 0.5,
        )

        # load enemy car
        self.original_car2 = pygame.image.load("assets/cars/otherCar.png")
        self.car2 = pygame.transform.scale(
            self.original_car2,
            (
                int(self.original_car2.get_width() * (self.SCREEN_WIDTH / 800)),
                int(self.original_car2.get_height() * (self.SCREEN_HEIGHT / 600)),
            ),
        )
        self.car2_loc = self.car2.get_rect()
        self.car2_loc.center = self.left_lane, self.SCREEN_HEIGHT * 0.2

        # load enemy truck
        self.original_truck = pygame.image.load("assets/cars/truck.png")
        self.truck = pygame.transform.scale(
            self.original_truck,
            (
                int(self.original_truck.get_width() * (self.SCREEN_WIDTH / 800)),
                int(self.original_truck.get_height() * (self.SCREEN_HEIGHT / 600)),
            ),
        )
        self.truck_loc = self.truck.get_rect()
        self.truck_loc.center = self.right_lane, -self.truck_loc.height

        self.scale = self.SCREEN_HEIGHT - self.car2_loc.height

        self.game_state = "MAIN GAME"
        self.game_paused = False

        self.has_update_scores = False
        self.scores = []

    def main_loop(self):
         while True:
            if self.game_paused:
                self.game_paused_draw()
                self.game_info_draw()
                self.CLOCK.tick(10)
                pygame.display.update()
                self.handle_critical_events()
                continue

            self.event_loop()
            self.event_updater_counter += 1

            if self.event_updater_counter > self.SCREEN_HEIGHT:
                self.event_updater_counter = 0

            if self.game_state == "GAME OVER":
                self.game_over_draw()
                self.CLOCK.tick(self.FPS)
                pygame.display.update()
                continue

            if self.score % 5000 == 0:
                self.speed += 0.16
                self.level += 1
                print("Level Up!")

            # Update enemy positions
            if self.current_enemy == 'car':
                self.car2_loc[1] += self.speed * self.speed_factor
            elif self.current_enemy == 'truck':
                self.truck_loc[1] += self.speed * self.speed_factor * 0.8

            # Check if we need to reset enemy positions
            if (self.current_enemy == 'car' and self.car2_loc[1] > self.SCREEN_HEIGHT) or \
               (self.current_enemy == 'truck' and self.truck_loc[1] > self.SCREEN_HEIGHT) or \
               self.current_enemy is None:
                self.spawn_new_enemy()

            # Check for collisions
            if (self.current_enemy == 'car' and self.car2_loc.colliderect(self.car_loc)) or \
               (self.current_enemy == 'truck' and self.truck_loc.colliderect(self.car_loc)):
                self.car_crash_sound.play()
                self.game_state = "GAME OVER"

            self.draw(self.event_updater_counter)
            self.display_score()

            self.score += 1

            self.CLOCK.tick(self.FPS)
            pygame.display.update()

    def spawn_new_enemy(self):
        # Randomly choose between car and truck
        self.current_enemy = random.choice(['car', 'truck'])
        
        # Choose lane randomly
        chosen_lane = random.choice([self.left_lane, self.right_lane])
        
        if self.current_enemy == 'car':
            self.car2_loc.center = chosen_lane, -200
            self.car2_lane = "L" if chosen_lane == self.left_lane else "R"
            # Reset truck position off-screen
            self.truck_loc.center = self.right_lane, -self.truck_loc.height - 1000
        else:  # truck
            self.truck_loc.center = chosen_lane, -self.truck_loc.height
            self.truck_lane = "L" if chosen_lane == self.left_lane else "R"
            # Reset car position off-screen
            self.car2_loc.center = self.right_lane, -1000

    def handle_critical_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game_paused = False

    def event_loop(self):
        for event in pygame.event.get():  # Event Loop
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_a, pygame.K_LEFT] and self.car_lane == "R":
                    # Use this line to add game over
                    # if car_lane == 'L': game_over()
                    self.car_loc = self.car_loc.move([-int(self.road_w / 2), 0])
                    self.car_lane = "L"
                if event.key in [pygame.K_d, pygame.K_RIGHT] and self.car_lane == "L":
                    self.car_loc = self.car_loc.move([int(self.road_w / 2), 0])
                    self.car_lane = "R"
                if event.key in [pygame.K_w, pygame.K_UP]:
                    self.speed = self.speed + 5
                if event.key in [pygame.K_SPACE, pygame.K_r] and self.game_state == "GAME OVER":
                    self.restart_game()
                if event.key in [pygame.K_SPACE]:
                    if not self.game_paused:
                        self.game_paused = True
                if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                    self.quit_game()
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_w, pygame.K_UP]:
                    self.speed = self.speed - 5
            if event.type == pygame.VIDEORESIZE:
                self.SCREEN_WIDTH, self.SCREEN_HEIGHT = event.w, event.h
                self.SCREEN = pygame.display.set_mode(
                    (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE
                )

                # Update lane positions
                self.road_w = int(self.SCREEN_WIDTH / 1.6)
                self.right_lane = self.SCREEN_WIDTH / 2 + self.road_w / 4
                self.left_lane = self.SCREEN_WIDTH / 2 - self.road_w / 4

                # Rescale the car images using the original images
                self.car = pygame.transform.scale(
                    self.original_car,
                    (
                        int(self.original_car.get_width() * (self.SCREEN_WIDTH / 800)),
                        int(
                            self.original_car.get_height() * (self.SCREEN_HEIGHT / 600)
                        ),
                    ),
                )
                self.car2 = pygame.transform.scale(
                    self.original_car2,
                    (
                        int(self.original_car2.get_width() * (self.SCREEN_WIDTH / 800)),
                        int(
                            self.original_car2.get_height() * (self.SCREEN_HEIGHT / 600)
                        ),
                    ),
                )

                # Update car rectangle positions based
                # on the updated lane positions
                if self.car_lane == "R":
                    self.car_loc = self.car.get_rect(
                        center=(self.right_lane, self.SCREEN_HEIGHT * 0.8)
                    )
                else:
                    self.car_loc = self.car.get_rect(
                        center=(self.left_lane, self.SCREEN_HEIGHT * 0.8)
                    )

                if self.car2_lane == "R":
                    self.car2_loc = self.car2.get_rect(
                        center=(self.right_lane, self.car2_loc.center[1])
                    )
                else:
                    self.car2_loc = self.car2.get_rect(
                        center=(self.left_lane, self.car2_loc.center[1])
                    )

    def draw(self, event_updater_counter):
        """
        This is a function that draws the background of the game and is
        used to update the background when resized
        For moving the yellow dashed line on the road, several rect are drawn
        and then moved with the event_updater_counter variable.
        Once the event_update_counter reaches 30, the rects are reset to their
        original positions and the process is repeated.
        """

        # drawing the dark road on the center of green screen
        self.SCREEN.fill(self.GRASS_COLOR)

        pygame.draw.rect(
            self.SCREEN,
            self.DARK_ROAD_COLOR,
            (
                self.SCREEN_WIDTH / 2 - self.road_w / 2,
                0,
                self.road_w,
                self.SCREEN_HEIGHT,
            ),
        )

        # drawing the yellow dashed line on the center of dark road
        num_yellow_lines = 11 # 10 + 1 moving in the borders of the screen
        # event_updater_counter is used to move the yellow dashed line
        line_positions = [
            (
                self.SCREEN_WIDTH / 2 - self.roadmark_w / 2,
                # be careful changing this values, it may cause the lines
                # to not be drawn correctly
                # line speed is 75% of car2 speed
                int(
                    (self.SCREEN_HEIGHT / 20
                    + 2 * self.SCREEN_HEIGHT / 20 * num_line
                    + self.speed * self.speed_factor * event_updater_counter * 0.75)
                    % self.SCREEN_HEIGHT / 10 * 11
                    - self.SCREEN_HEIGHT / 20
                ),
                self.roadmark_w,
                self.SCREEN_HEIGHT / 20,
            )
            for num_line in range(num_yellow_lines)
        ]

        for line_position in line_positions:
            pygame.draw.rect(
                self.SCREEN,
                self.YELLOW_LINE_COLOR,
                line_position,
            )

        # drawing a white line on the left side of road
        pygame.draw.rect(
            self.SCREEN,
            self.WHITE_LINE_COLOR,
            (
                self.SCREEN_WIDTH / 2 - self.road_w / 2 + self.roadmark_w * 2,
                0,
                self.roadmark_w,
                self.SCREEN_HEIGHT,
            ),
        )
        # drawing a white line on the right side of road
        pygame.draw.rect(
            self.SCREEN,
            (255, 255, 255),
            (
                self.SCREEN_WIDTH / 2 + self.road_w / 2 - self.roadmark_w * 3,
                0,
                self.roadmark_w,
                self.SCREEN_HEIGHT,
            ),
        )

        # load the vehicles on road
        self.SCREEN.blit(self.car, self.car_loc)
        self.SCREEN.blit(self.car2, self.car2_loc)
        self.SCREEN.blit(self.truck, self.truck_loc)

    def display_score(self):
        self.message_display(
            "SCORE ",
            self.score_font,
            (255, 50, 50),
            self.right_lane + self.road_w / 2.5,
            20,
        )
        self.message_display(
            self.score,
            self.score_font,
            (255, 50, 50),
            self.right_lane + self.road_w / 2.5,
            55,
        )

    def game_over_draw(self):
        self.SCREEN.fill((200, 200, 200))
        self.message_display(
            "GAME OVER!", self.game_over_font, (40, 40, 40), self.SCREEN_WIDTH / 2, 330
        )
        self.message_display(
            "FINAL SCORE ",
            self.score_font,
            (80, 80, 80),
            self.SCREEN_WIDTH / 2 - 50,
            230,
        )
        self.message_display(
            self.score, self.score_font, (80, 80, 80), self.SCREEN_WIDTH / 2 + 150, 230
        )

        if not self.has_update_scores:
            # Read high_scores from txt file, which are in the form of space separated numbers
            with open("high_scores.txt", "r") as hs_file:
                high_scores = hs_file.read()
                hs_file.close()

            # Convert the high score string data into list of numbers and add new score to the data
            self.scores = [int(i) for i in high_scores.split()]
            self.scores.append(self.score)

            # Sort in descending order, then keep only the top 5 scores by deleting the extra score if present
            self.scores.sort()
            self.scores.reverse()

            if len(self.scores) > 5:
                self.scores = self.scores[:5]

            #formatting the scores
            self.scores = self.pad_scores(self.scores)

            # Rewrites the high_scores file with the updated high scores
            with open("high_scores.txt", "w") as hs_file:
                hs_file.write(" ".join([str(i) for i in self.scores]))

            self.has_update_scores = True

            # Printing top 5 high scores
        self.message_display(
            "HIGH SCORES", self.score_font, (100, 100, 100), self.SCREEN_WIDTH / 2, 410
        )

        for idx, score in enumerate(self.scores):
            self.message_display(
                f"{idx + 1}. {score}",
                self.score_font,
                (100, 100, 100),
                self.SCREEN_WIDTH / 2,
                410 + ((idx + 1) * 30),
            )
        
        self.message_display(
            "(Space to restart)", self.score_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 600
        )

    def game_paused_draw(self):
        self.message_display(
            "PAUSED", self.game_over_font, (0, 0, 100), self.SCREEN_WIDTH / 2, 200
        )

    def game_info_draw(self):
        pygame.draw.rect(self.SCREEN, (0, 0, 0), [self.SCREEN_WIDTH/4 - 3, self.SCREEN_HEIGHT/4 + 65 - 3, self.SCREEN_WIDTH/2 + 6, 300 + 6])
        pygame.draw.rect(self.SCREEN, (200, 200, 200), [self.SCREEN_WIDTH/4, self.SCREEN_HEIGHT/4 + 65, self.SCREEN_WIDTH/2, 300])
        self.message_display(
            "Controls", self.game_info_font, (40, 40, 40), self.SCREEN_WIDTH / 2, 250
        )
        self.message_display(
            "Left:                 A or \u2190", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 300,
        )
        self.message_display(
            "Right:              D or \u2192", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 350,
        )
        self.message_display(
            "Speed Up:         W or \u2191", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 400,
        )
        self.message_display(
            "Pause:        Space Bar", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 450,
        )
        self.message_display(
            "Exit:              Q or ESC", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 500,
        )

    def restart_game(self):
        self.score = 0
        self.level = 0
        self.speed = 3
        self.event_updater_counter = 0
        self.game_state = "MAIN GAME"
        self.has_update_scores = False
        self.scores = []
        self.current_enemy = None  # Reset current enemy
        self.car_loc.center = (
            self.right_lane,
            self.SCREEN_HEIGHT - self.car_loc.height * 0.5,
        )
        self.car2_loc = self.car2.get_rect()
        self.car2_loc.center = (self.left_lane, -1000)  # Start off-screen
        self.truck_loc = self.truck.get_rect()
        self.truck_loc.center = (self.right_lane, -self.truck_loc.height - 1000)  # Start off-screen
        self.car_lane = "R"
        print("Restart!")

    @staticmethod
    def quit_game():
        sys_exit()
        quit()

    def message_display(self, text, font, text_col, x, y, center=True):
        """
        This is a function which displays text with the desired specifications

        param: text: This is the Text to display
        type: str

        param: font: The font that will be used
        type: Font

        param: text_col: The color that the text will be in (R, G, B) format
        type: tuple

        param: x: The x coordinate of the text
        type: int

        param: y: The y coordinate of the text
        type: int

        param: center: Determines if the text is centered
        type: bool
        """
        img = font.render(str(text), True, text_col)
        img = img.convert_alpha()

        if center:
            # Adjust x and y to center the text
            x -= img.get_width() / 2
            y -= img.get_height() / 2

        self.SCREEN.blit(img, (x, y))

    # padding zeroes for high scores to have same digits for alignment
    @staticmethod
    def pad_scores(scores):
        """
        :param: scores : high scores in descending order
        :type: list

        :return: high scores in padded format
        :type: list
        """
        length_of_highest_score = len(str(scores[0]))
        scores_padded = [str(score).zfill(length_of_highest_score) for score in scores]
        return scores_padded

if __name__ == "__main__":
    game = Game()
    game.main_loop()
