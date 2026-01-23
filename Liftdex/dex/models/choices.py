from django.db import models

class Difficulty(models.IntegerChoices):
    VERY_EASY = 1, "とても易しい"
    EASY = 2, "易しい"
    NOMAL = 3, "普通"
    HARD = 4, "難しい"
    VERY_HARD = 5, "とても難しい"

class Equipment(models.TextChoices):
    BARBELL = "barbell", "バーベル"
    DUMBBELL = "dumbbell", "ダンベル"
    SMITH = "smith", "スミスマシン"
    MACHINE = "machine", "マシン"
    PLATE_LOADED = "plate_loaded", "プレートロード"
    CABLE = "cable", "ケーブル"
    BODYWEIGHT = "bodyweight", "自重"
    OTHER = "other", "その他"

class ExerciseType(models.TextChoices):
    COMPOUND = "compound", "コンパウンド"
    ISOLATION = "isolation", "アイソレーション"