from otree.api import *


doc = """
パート1: 確実性同等値（CE）測定 (MPL)
ストッピングルール適用版
"""


class C(BaseConstants):
    NAME_IN_URL = 'part1_ce'
    PLAYERS_PER_GROUP = None
    PAYOFF_LIST = [
        0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500,
        550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050
    ]
    NUM_ROUNDS = len(PAYOFF_LIST)
    LOTTERY_HIGH = 2000  # くじの当たり額: 2000円
    LOTTERY_LOW = 0


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    choice = models.StringField(
        choices=[
            ['lottery', 'くじを引く'],
            ['sure_payoff', '確定額を受け取る'],
        ],
        widget=widgets.RadioSelect
    )
    switching_point = models.CurrencyField(blank=True)


# --- PAGES ---

class Decision(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True

        # 過去のラウンドの「選択肢(choice)」をチェック
        # DBの数値フィールドではなく文字列フィールドを参照するため100%エラーになりません
        for r in range(1, player.round_number):
            prev_player = player.in_round(r)
            if prev_player.choice == 'sure_payoff':
                return False  # 過去に確定額を選んでいたら以降のラウンドをスキップ

        return True

    @staticmethod
    def vars_for_template(player: Player):
        sure_payoff = C.PAYOFF_LIST[player.round_number - 1]
        return {
            'sure_payoff': sure_payoff,
            'lottery_high': C.LOTTERY_HIGH,
            'lottery_low': C.LOTTERY_LOW,
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.choice == 'sure_payoff':
            player.switching_point = C.PAYOFF_LIST[player.round_number - 1]


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        switching_val = None

        # 確定額を選んだ最初のラウンドを探して金額を特定
        for r in range(1, C.NUM_ROUNDS + 1):
            p = player.in_round(r)
            if p.choice == 'sure_payoff':
                switching_val = C.PAYOFF_LIST[r - 1]
                break

        return {
            'switching_val': switching_val,
        }


page_sequence = [Decision, Results]
