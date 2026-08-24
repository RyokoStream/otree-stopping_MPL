from otree.api import *
import random

doc = """
パート1：順次提示型MPL（くじ vs 確定額）
確定額を選んだ時点で以降の質問を自動スキップします。
"""

class C(BaseConstants):
    NAME_IN_URL = 'part1_ce'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 22  # 50円〜1100円の22段階
    
    # 各ラウンドの確定額リスト (50円〜1100円)
    AMOUNT_LIST = [50 * i for i in range(1, 23)]
    
    # くじの仕様
    LOTTERY_HIGH = 2000
    LOTTERY_LOW = 0

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # 各ラウンドでの選択 ('lottery' or 'sure')
    choice = models.StringField(
        choices=[
            ['lottery', 'くじA（50%で2000円 / 50%で0円）'],
            ['sure', '現金をもらう']
        ],
        widget=widgets.RadioSelect
    )
    # 切り替わった（確定額を選んだ）金額を記録
    switching_point = models.IntegerField()


# --- Paging & Logic ---

class Decision(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def is_displayed(player: Player):
        # ラウンド1は必ず表示
        if player.round_number == 1:
            return True
        # 直前ラウンドまでの選択を確認し、すでに「sure（現金）」を選んでいたらスキップ
        prev_player = player.in_round(player.round_number - 1)
        if prev_player.field_maybe_none('switching_point') is not None:
            return False
        return True

    @staticmethod
    def vars_for_template(player: Player):
        # 現在のラウンドに応じた確実な金額を取得
        current_sure_amount = C.AMOUNT_LIST[player.round_number - 1]
        return {
            'round_num': player.round_number,
            'sure_amount': current_sure_amount,
            'lottery_high': C.LOTTERY_HIGH,
            'lottery_low': C.LOTTERY_LOW,
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        current_sure_amount = C.AMOUNT_LIST[player.round_number - 1]
        
        if player.choice == 'sure':
            # 「現金」を選んだ場合、切り替えポイントとして現在の金額を保存
            player.switching_point = current_sure_amount
        else:
            player.switching_point = None

        # 最終ラウンド（第22問）で一度も「現金」を選ばなかった場合の処理
        if player.round_number == C.NUM_ROUNDS and player.switching_point is None:
            # 切り替えなし（常にくじを選択）として記録
            player.switching_point = 9999 


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        # 最終ラウンドのみ結果画面を表示
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        # 被験者の切り替えポイント（確定額を選んだ最小の金額）を全ラウンドから探す
        switching_val = None
        for r in range(1, C.NUM_ROUNDS + 1):
            val = player.in_round(r).switching_point
            if val is not None:
                switching_val = val
                break

        # 謝礼決定ロジック（BDM方式 / ランダム選出）
        # 22個の質問の中から1つをランダムに決定
        selected_round = random.randint(1, C.NUM_ROUNDS)
        selected_sure_amount = C.AMOUNT_LIST[selected_round - 1]
        
        lottery_drawn = False
        lottery_win = False
        payoff_amount = 0

        if switching_val is not None and selected_sure_amount >= switching_val:
            # 選ばれた質問の提示額が切り替えポイント以上なら「確定額」を獲得
            payoff_amount = selected_sure_amount
        else:
            # 切り替えポイント未満なら「くじ」を実行（50%の確率で2000円）
            lottery_drawn = True
            if random.random() < 0.5:
                payoff_amount = C.LOTTERY_HIGH
                lottery_win = True
            else:
                payoff_amount = C.LOTTERY_LOW
                lottery_win = False

        # oTree標準の支払額フィールドに保存
        player.payoff = payoff_amount

        # パート間でデータを引き継ぐ場合、participant.varsに保存しておきます
        player.participant.vars['part1_payoff'] = payoff_amount

        return {
            'switching_val': switching_val if switching_val != 9999 else "なし（常にくじを選択）",
            'selected_round': selected_round,
            'selected_sure_amount': selected_sure_amount,
            'lottery_drawn': lottery_drawn,
            'lottery_win': lottery_win,
            'payoff_amount': payoff_amount,
        }

page_sequence = [Decision, Results]
