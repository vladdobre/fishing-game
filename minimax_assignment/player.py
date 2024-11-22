#!/usr/bin/env python3
import math
import random
import time
from cmath import inf

from fishing_game_core.game_tree import Node, State
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR

ARENA_WIDTH = 20
TIME_LIMIT = 75 * 1e-3  # 75*1e-3
MOVE_ORDER = [2, 4, 1, 0, 3]
class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and send
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):
    start_time = None

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        :return:
        """

        # Generate first message (Do not remove this line!)
        first_msg = self.receiver()

        while True:
            msg = self.receiver()

            # Create the root node of the game tree
            node = Node(message=msg, player=0)

            # Possible next moves: "stay", "left", "right", "up", "down"
            best_move = self.search_best_next_move(initial_tree_node=node)

            # Execute next action
            self.sender({"action": best_move, "search_time": None})

    def search_best_next_move(self, initial_tree_node):
        """
        Use minimax (and extensions) to find best possible next move for player 0 (green boat)
        :param initial_tree_node: Initial game tree node
        :type initial_tree_node: game_tree.Node
            (see the Node class in game_tree.py for more information!)
        :return: either "stay", "left", "right", "up" or "down"
        :rtype: str
        """

        # EDIT THIS METHOD TO RETURN BEST NEXT POSSIBLE MODE USING MINIMAX ###

        # NOTE: Don't forget to initialize the children of the current node
        #       with its compute_and_get_children() method!

        # random_move = random.randrange(5)
        # return ACTION_TO_STR[random_move]

        state = initial_tree_node.state
        # hook_p1 = state.get_hook_positions()[0]
        # hook_p2 = state.get_hook_positions()[1]
        # player_index = state.get_player()
        # score_p1 = state.get_player_scores()[0]
        # score_p2 = state.get_player_scores()[1]
        # fish_scores = state.get_fish_scores()
        # fish_positions = state.get_fish_positions()
        # fish_caught_p1 = state.get_caught()[0]
        # fish_caught_p2 = state.get_caught()[1]

        if state.get_caught()[0] is not None:
            # print("CAUGHT FISH - REELING!!!")
            return ACTION_TO_STR[1]  # If caught a fish, reel it in.

        alpha = float(-inf)
        beta = float(inf)

        # print("Alpha: {}   Beta: {}".format(alpha, beta))

        # bestAction = None
        # bestValue = -inf
        # self.start_time = time.time()
        # for child in initial_tree_node.compute_and_get_children():
        #     value = self.ab_minimax(child, 0, alpha, beta)
        #     if value > bestValue:
        #         bestValue = value
        #         bestAction = child.move


        bestAction = None
        bestValue = -inf
        self.start_time = time.time()
        children = initial_tree_node.compute_and_get_children()

        if len(children) == 1:
            #print("SMALL LEN: "+str(len(children)))
            # for child in children:
            #     value = self.ab_minimax(child, 0, alpha, beta)
            #     if value > bestValue:
            #         bestValue = value
            #         bestAction = child.move
            bestAction = 1
        else:
            #print("Normal len: "+str(len(children)))
            for action in MOVE_ORDER:
                value = self.ab_minimax(children[action], 0, alpha, beta)
                if value > bestValue:
                    bestValue = value
                    bestAction = action

        # print("BEST ACTION: " + str(bestAction) + "VALUE: " + str(bestValue))
        return ACTION_TO_STR[bestAction]

    depth_limit = 2

    def ab_minimax(self, node, depth, alpha, beta):
        if depth > self.depth_limit or self.is_terminal(node):
            return self.heuristic(node)
        children = node.compute_and_get_children()

        if node.state.get_player() == 0:
            output = -inf
            if len(children) == 1:
                output = max(output, self.ab_minimax(children[0], depth + 1, alpha, beta))
            else:
                for move in MOVE_ORDER:
                    output = max(output, self.ab_minimax(children[move], depth + 1, alpha, beta))
                    alpha = max(alpha, output)
                    if beta <= alpha:  ##BETA PRUNE!!
                        # print("BETA PRUNE")
                        break
        else:  # OPPONENT :(
            output = +inf
            if len(children) == 1:
                output = min(output, self.ab_minimax(children[0], depth + 1, alpha, beta))
            else:
                for move in MOVE_ORDER:
                    output = min(output, self.ab_minimax(children[move], depth + 1, alpha, beta))
                    beta = min(output, beta)
                    if beta <= alpha:  # ALPHA PRUNE
                        # print("Alpha PRUNE")
                        break
        return output

    def heuristic(self, node):
        scores = node.state.get_player_scores()

        return scores[0] - scores[1] + self.get_caught_diff(node) + self.get_min_dist_diff(node)


    # def get_min_fish_dist_just_me(self, node):
    #     fish_pos = node.state.get_fish_positions()
    #     hooks = node.state.get_hook_positions()
    #     min_dist = 30
    #     for fish in fish_pos:
    #         dist = self.get_hook_fish_distance(hooks[0], hooks[1], fish_pos[fish])
    #         if dist < min_dist:
    #             min_dist = dist
    #     #print("DIST: "+str(min_dist/ARENA_WIDTH))
    #     return min_dist/ARENA_WIDTH

    # def get_min_fish_dist_both(self, node):
    #     fish_pos = node.state.get_fish_positions()
    #     player = node.state.get_player()
    #     hooks = node.state.get_hook_positions()
    #     min_dist = 30
    #     for fish in fish_pos:
    #         dist = self.get_hook_fish_distance(hooks[player], hooks[not player], fish_pos[fish])
    #         if dist < min_dist:
    #             min_dist = dist
    #     #print("DIST: "+str(min_dist/ARENA_WIDTH))
    #     return min_dist/ARENA_WIDTH


    def get_min_dist_diff(self, node):
        fish_pos = node.state.get_fish_positions()
        player = node.state.get_player()
        hooks = node.state.get_hook_positions()
        min_dist_A = 30
        min_dist_B = 30
        for fish in fish_pos:
            dist_A = self.get_hook_fish_distance(hooks[0], hooks[1], fish_pos[fish])
            dist_B = self.get_hook_fish_distance(hooks[1], hooks[0], fish_pos[fish])
            if dist_A < min_dist_A:
                min_dist_A = dist_A
            if dist_B < min_dist_B:
                min_dist_B = dist_B
        return (min_dist_B - min_dist_A) / ARENA_WIDTH

    def get_hook_fish_distance(self, hook_0, hook_1, fish):
        if not self.is_opponent_between(hook_0, hook_1, fish):
            return math.sqrt((hook_0[0] - fish[0]) ** 2 + (hook_0[1] - fish[1]) ** 2)
        else:
            return math.sqrt((hook_0[0] + (ARENA_WIDTH - fish[0])) ** 2 + (hook_0[1] - fish[1]) ** 2)

    def is_opponent_between(self, hook_green, hook_red, fish):
        if (hook_green[0] < hook_red[0] and fish[0] < hook_red[0]) \
                or (hook_green[0] > hook_red[0] and fish[0] > hook_red[0]):
            return False
        return True

    def get_score_diff(self, node):
        return node.state.get_player_scores()[0] - node.state.get_player_scores()[1]


    def get_caught_diff(self, node):
        caught = node.state.get_caught()
        fish_scores = node.state.get_fish_scores()
        if caught[0] is None and caught[1] is None:
            return 0
        if caught[0] is None:
            return -fish_scores[caught[1]]
        if caught[1] is None:
            return fish_scores[caught[0]]
        return fish_scores[caught[0]] - fish_scores[caught[1]]


    def is_terminal(self, node):  # if the game is over
        # print("GAME NOT OVER!")
        # print("CAUGHT FISH 0: ", node.state.get_caught()[0])
        # print("CAUGHT FISH 1: ", node.state.get_caught()[1])
        return len(node.state.get_fish_positions()) == 0