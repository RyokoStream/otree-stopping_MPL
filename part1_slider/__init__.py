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

    # 50円〜1100円の50円刻み（全22問）
    SURE_PAYOFFS = [50 * i for i in range(1, 23)]
    NUM_QUESTIONS = len(SURE_PAYOFFS)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # スライダーの値を保存（0: 全問確実な金額 〜 22: 全問くじ）
    switching_point = models.IntegerField(
        min=0,
        max=Constants.NUM_QUESTIONS,
        doc="くじを選んだ最後の問題番号（0〜22）"
    )

    # 謝礼決定用の記録フィールド
    selected_question = models.IntegerField(doc="抽選で選ばれた問題番号（1〜22）")
    lottery_outcome = models.IntegerField(doc="くじの結果（2000または0）", initial=0)
    payoff_choice = models.StringField(doc="選ばれていた選択肢（'くじ' または '確実な金額'）")

    # 全22問の回答結果領域（True = くじ, False = 確実な金額）
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


# PAGES
class Decision(Page):
    form_model = 'player'
    form_fields = ['switching_point'] + [f'q{i}' for i in range(1, 23)]

    def vars_for_template(player: Player):
        # 画面描画用の問ごとのデータ作成
        questions = []
        for i, sure_payoff in enumerate(Constants.SURE_PAYOFFS, start=1):
            questions.append({
                'num': i,
                'sure_payoff': sure_payoff,
                'high': Constants.LOTTERY_HIGH,
                'low': Constants.LOTTERY_LOW,
            })
        return {
            'questions': questions,
            'num_questions': Constants.NUM_QUESTIONS,
        }

    def before_next_page(player: Player, timeout_happened):
        # 1〜22問から1つをランダム選択
        selected_q = random.randint(1, Constants.NUM_QUESTIONS)
        player.selected_question = selected_q

        # 選択された問題の回答を取得
        chosen_lottery = getattr(player, f'q{selected_q}')

        if chosen_lottery:
            player.payoff_choice = 'くじ'
            # 50%の確率で当たりの判定
            if random.random() < 0.5:
                player.lottery_outcome = Constants.LOTTERY_HIGH
                player.payoff = Constants.LOTTERY_HIGH
            else:
                player.lottery_outcome = Constants.LOTTERY_LOW
                player.payoff = Constants.LOTTERY_LOW
        else:
            player.payoff_choice = '確実な金額'
            player.payoff = Constants.SURE_PAYOFFS[selected_q - 1]


class Results(Page):
    def vars_for_template(player: Player):
        selected_sure = Constants.SURE_PAYOFFS[player.selected_question - 1]
        return {
            'selected_sure': selected_sure,
        }


page_sequence = [Decision, Results]
