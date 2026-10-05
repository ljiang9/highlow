#!/usr/bin/env python3
"""highlow: 终端高低牌猜大小游戏。纯标准库。"""

import argparse
import random
import secrets
import sys

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANKS)}  # A=14, 最大
SUITS = ["♠", "♥", "♦", "♣"]
SUIT_NAME = {"♠": "黑桃", "♥": "红桃", "♦": "方块", "♣": "梅花"}


def new_deck(rng):
    deck = [(r, s) for s in SUITS for r in RANKS]
    rng.shuffle(deck)
    return deck


def card_name(card):
    r, s = card
    return f"{SUIT_NAME[s]}{r}"


def judge(current, nxt, guess):
    """返回 'win' / 'lose' / 'push'。同点算 push(平局,不计胜负)。"""
    cv, nv = RANK_VALUE[current[0]], RANK_VALUE[nxt[0]]
    if nv == cv:
        return "push"
    if guess == "h":
        return "win" if nv > cv else "lose"
    return "win" if nv < cv else "lose"


def median_guess(card):
    """最优策略:按中位数猜。A=14 全牌共13点,
    点数<8 猜大,>8 猜小,=8 无所谓(期望胜率相同)。"""
    v = RANK_VALUE[card[0]]
    return "h" if v < 8 else "l"


class Game:
    def __init__(self, rng, rounds=None):
        self.rng = rng
        self.rounds = rounds
        self.deck = new_deck(rng)
        self.current = self.deck.pop()
        self.streak = 0
        self.best = 0
        self.wins = 0
        self.losses = 0
        self.pushes = 0
        self.played = 0

    def next_card(self):
        if not self.deck:
            self.deck = new_deck(self.rng)
        return self.deck.pop()

    def play_round(self, guess):
        nxt = self.next_card()
        result = judge(self.current, nxt, guess)
        self.played += 1
        if result == "win":
            self.streak += 1
            self.best = max(self.best, self.streak)
            self.wins += 1
        elif result == "lose":
            self.streak = 0
            self.losses += 1
        else:
            self.pushes += 1
        prev, self.current = self.current, nxt
        return prev, nxt, result


def play_interactive(rounds, seed):
    rng = random.Random(seed) if seed is not None else secrets.SystemRandom()
    game = Game(rng, rounds)
    print("High-Low 猜大小 | A 最大(14)。猜下一张比当前大(h)还是小(l)。")
    print("同点算平局(push),连胜不清零。输入 q 退出。\n")
    while True:
        print(f"当前: {card_name(game.current)}  | 连胜: {game.streak} (最佳 {game.best})")
        if rounds is not None and game.played >= rounds:
            break
        try:
            raw = input("猜 (h=大 / l=小 / q=退出): ").strip().lower()
        except EOFError:
            print()
            break
        if raw == "q":
            break
        if raw not in ("h", "l", "higher", "lower", "大", "小"):
            print("请输入 h(大)、l(小) 或 q。")
            continue
        guess = "h" if raw in ("h", "higher", "大") else "l"
        prev, nxt, result = game.play_round(guess)
        msg = {"win": "✔ 猜对了!", "lose": "✘ 猜错了。", "push": "＝ 同点,平局。"}[result]
        print(f"{msg} 下一张是 {card_name(nxt)}\n")
    decided = game.wins + game.losses
    rate = game.wins / decided * 100 if decided else 0.0
    print(f"结束: 共 {game.played} 局, 胜 {game.wins} 负 {game.losses} "
          f"平 {game.pushes}, 胜率 {rate:.1f}%, 最佳连胜 {game.best}。")
    return 0


def play_auto(n, seed):
    rng = random.Random(seed)
    game = Game(rng)
    for _ in range(n):
        game.play_round(median_guess(game.current))
    decided = game.wins + game.losses
    rate = game.wins / decided if decided else 0.0
    print(f"--auto {n} 局(中位数策略): 胜 {game.wins} 负 {game.losses} "
          f"平 {game.pushes}, 胜率 {rate * 100:.2f}%")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="High-Low 猜大小:猜下一张牌比当前大还是小。")
    ap.add_argument("--rounds", type=int, default=None, help="猜多少局后结束(默认一直玩到 q)")
    ap.add_argument("--auto", type=int, default=None, metavar="N",
                    help="自动演示 N 局(中位数最优策略)")
    ap.add_argument("--seed", type=int, default=None, help="随机种子(可复现)")
    args = ap.parse_args(argv)
    if args.rounds is not None and args.rounds <= 0:
        print("error: --rounds 需要正整数", file=sys.stderr)
        return 2
    if args.auto is not None:
        if args.auto <= 0:
            print("error: --auto 需要正整数", file=sys.stderr)
            return 2
        return play_auto(args.auto, args.seed)
    return play_interactive(args.rounds, args.seed)


if __name__ == "__main__":
    raise SystemExit(main())
