import random
from otree.api import *

doc = """
スライダー形式の確定等価性（CE）測定タスク
"""


class Constants(BaseConstants):
    name_in_url = 'part1_slider'
    players_per_group = None
    num_rounds = 1  # 1画面完結

    LOTTERY_HIGH = 2000
    LOTTERY_LOW = 0

    # 確定額のリスト（問1〜22）
    SURE_PAYOFFS = [
        0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500,
        600, 700, 800, 900, 1000, 1100, 1200, 1400, 1600, 1800, 2000
    ]
    NUM_QUESTIONS = len(SURE_PAYOFFS)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # スライダーの値を保存（0: 全問確定額 〜 22: 全問くじ）
    switching_point = models.IntegerField(
        min=0,
        max=Constants.NUM_QUESTIONS,
        doc="くじを選んだ最後の問題番号（0〜22）"
    )

    # 謝礼決定用の記録フィールド
    selected_question = models.IntegerField(doc="抽選で選ばれた問題番号（1〜22）")
    lottery_outcome = models.IntegerField(doc="くじの結果（2000または0）", initial=0)
    payoff_choice = models.StringField(doc="選ばれていた選択肢（'くじ' または '確定額'）")

    # 全22問の回答結果領域
    q1 = models.BooleanField()
    q2 = models.BooleanField()
    q3 = models.BooleanField()
    q4 = models.BooleanField()
    q5 = models.BooleanField()
    q6 = models.BooleanField()
    q7 = models.BooleanField()
    q8 = models.BooleanField()
    q9 = models.BooleanField()
    q10 = models.BooleanField()
    q11 = models.BooleanField()
    q12 = models.BooleanField()
    q13 = models.BooleanField()
    q14 = models.BooleanField()
    q15 = models.BooleanField()
    q16 = models.BooleanField()
    q17 = models.BooleanField()
    q18 = models.BooleanField()
    q19 = models.BooleanField()
    q20 = models.BooleanField()
    q21 = models.BooleanField()
    q22 = models.BooleanField()


class Decision(Page):
    form_model = 'player'
    form_fields = ['switching_point']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # 1. スライダーの値に基づき q1 〜 q22 を自動決定（False: くじ, True: 確定額）
        sp = player.switching_point
        for i in range(1, Constants.NUM_QUESTIONS + 1):
            is_sure = (i > sp)
            setattr(player, f'q{i}', is_sure)

        # 2. 謝礼金のランダム決定処理
        q_num = random.randint(1, Constants.NUM_QUESTIONS)
        player.selected_question = q_num
        
        sure_payoff = Constants.SURE_PAYOFFS[q_num - 1]
        chosen_sure = getattr(player, f'q{q_num}')
        
        if chosen_sure:
            player.payoff_choice = '確定額'
            player.payoff = sure_payoff
        else:
            player.payoff_choice = 'くじ'
            outcome = random.choice([Constants.LOTTERY_HIGH, Constants.LOTTERY_LOW])
            player.lottery_outcome = outcome
            player.payoff = outcome


class Results(Page):
    pass


page_sequence = [Decision, Results]

