from otree.api import *


doc = """
パート1: 確実性同等値（CE）測定 (MPL)
ストッピングルール適用版
"""


class C(BaseConstants):
    NAME_IN_URL = 'part1_ce'
    PLAYERS_PER_GROUP = None
    # 例: 22ラウンド設定
    PAYOFF_LIST = [
        0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500,
        550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050
    ]
    NUM_ROUNDS = len(PAYOFF_LIST)
    LOTTERY_HIGH = 1000
    LOTTERY_LOW = 0


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # 被験者の選択 (例: 'lottery' か 'sure_payoff')
    choice = models.StringField(
        choices=[
            ['lottery', 'くじを引く'],
            ['sure_payoff', '確定額を受け取る'],
        ],
        widget=widgets.RadioSelect
    )
    # 切り替えポイントの確定額を保持（未決定時は None）
    switching_point = models.CurrencyField(blank=True)


# --- PAGES ---

class MainChoice(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def is_displayed(player: Player):
        # 第1ラウンドは必ず表示
        if player.round_number == 1:
            return True

        # 過去のラウンドで「確定額（sure_payoff）」を選んで switching_point がセットされているか確認
        # oTreeの安全な値取得関数 field_maybe_none を使用
        for r in range(1, player.round_number):
            prev_player = player.in_round(r)
            if field_maybe_none(prev_player, 'switching_point') is not None:
                # 既に切り替え済みの場合は以降のラウンドをスキップ
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
        # 「確定額を受け取る」を選んだ瞬間にその額を switching_point として保存
        if player.choice == 'sure_payoff':
            player.switching_point = C.PAYOFF_LIST[player.round_number - 1]


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        # 最終ラウンドのみ表示
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        switching_val = None

        # 全ラウンドを走査して最初（最小）の switching_point を探す
        for r in range(1, C.NUM_ROUNDS + 1):
            val = field_maybe_none(player.in_round(r), 'switching_point')
            if val is not None:
                switching_val = val
                break

        return {
            'switching_val': switching_val,
        }
class Decision(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def vars_for_template(player: Player):
        # HTML側の {{ sure_payoff }} や {{ lottery_high }} 等に値を渡す設定
        sure_payoff = C.PAYOFF_LIST[player.round_number - 1]
        return dict(
            sure_payoff=sure_payoff,
            lottery_high=C.LOTTERY_HIGH,
            lottery_low=C.LOTTERY_LOW,
        )

page_sequence = [Decision]

page_sequence = [MainChoice, Results]
