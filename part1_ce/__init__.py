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

        # getattr を使い、未設定(None)の場合でもエラーを起こさずに取得
        for r in range(1, player.round_number):
            prev_player = player.in_round(r)
            val = getattr(prev_player, 'switching_point', None)
            if val is not None:
                return False

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

        # 全ラウンドを通して最初に設定された switching_point を検索
        for r in range(1, C.NUM_ROUNDS + 1):
            val = getattr(player.in_round(r), 'switching_point', None)
            if val is not None:
                switching_val = val
                break

        return {
            'switching_val': switching_val,
        }


page_sequence = [Decision, Results]
