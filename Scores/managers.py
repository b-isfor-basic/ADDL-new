from django.db import models
from django.db.models import F
from django.db.models.aggregates import Count, Max, Min, Sum, Avg


class SinglesCricketGameManager(models.Manager):
    def sngl_ckt_create(self, **kwargs):
        format = "SN"
        game = "CKT"
        return super().create(format=format, game=game, **kwargs)


class DoublesCricketGameManager(models.Manager):
    def dbls_ckt_create(self, **kwargs):
        format = "DB"
        game = "CKT"
        return super().create(format=format, game=game, **kwargs)


class Singles501GameManager(models.Manager):
    def sngl_501_create(self, **kwargs):
        format = "SN"
        game = "501"
        return super().create(format=format, game=game, **kwargs)


class Doubles501GameManager(models.Manager):
    def dbls_501_create(self, **kwargs):
        format = "DB"
        game = "501"
        return super().create(format=format, game=game, **kwargs)


class Doubles301GameManager(models.Manager):
    def dbls_301_create(self, **kwargs):
        format = "DB"
        game = "301"
        return super().create(format=format, game=game, **kwargs)


class GameQuerySet(models.QuerySet):
    def doubles(self, **kwargs):
        return super(GameQuerySet, self).filter(format="DB", **kwargs)

    def singles(self, **kwargs):
        return super(GameQuerySet, self).filter(format="SN", **kwargs)

    def five01_singles(self, **kwargs):
        return super(GameQuerySet, self).filter(format="SN", game="501", **kwargs)

    def five01_doubles(self, **kwargs):
        return super(GameQuerySet, self).filter(format="DB", game="501", **kwargs)

    def wins(self, **kwargs):
        return super(GameQuerySet, self).filter(game_point=1, **kwargs)


class GamesManager(SinglesCricketGameManager, DoublesCricketGameManager, Singles501GameManager, Doubles501GameManager, Doubles301GameManager, models.Manager):
    pass


class ScoresetManager(models.Manager):
    """
    Provides methods for calculating scoreset stats.
    ::
    get_wins
        Returns a queryset with total win points annotated.
    get_stars
        Returns a queryset with total stars annotated.
    get_perfects
        Returns a queryset with total perfects annotated.
    get_in_thrown
        Returns a queryset with high in thrown annotated.
    get_out_thrown
        Returns a queryset with high out thrown annotated.
    get_best_week_501
        Returns a queryset with low darts thrown annotated.
    get_ppd
        Returns a queryset with average PPD annotated.
    """
    def get_queryset(self):
        return (
            super(ScoresetManager, self)
            .get_queryset()
            .select_related("match", "match__season", "team", "player")
            .prefetch_related("gamescore_set")
        )

    def get_wins(self):
        return (
            super(ScoresetManager, self)
            .get_queryset()
            .annotate(Sum("gamescore__game_point"))
        )

    def get_stars(self):
        return (
            super(ScoresetManager, self)
            .get_queryset()
            .annotate(Sum("gamescore__stars"))
        )

    def get_perfects(self):
        return (
            super(ScoresetManager, self)
            .get_queryset()
            .annotate(Sum("gamescore__perfects"))
        )

    def get_ppd(self):
        return (
            super(ScoresetManager, self)
            .get_queryset()
            .annotate(
                Avg(
                    F((501 * Count("gamescore__id")) - Sum("gamescore__score_left"))
                    / F(Sum("gamescore__darts_thrown"))
                )
            )
        )

    def get_best_week_501(self):
        return (
            super(ScoresetManager, self)
            .get_queryset()
            .filter(gamescore__score_left=0)
            .annotate(Min("gamescore__darts_thrown"))
        )

    def get_high_in(self):
        return (
            super(ScoresetManager, self)
            .get_queryset()
            .filter(gamescore__in_thrown__isnull=False)
            .annotate(Max("gamescore__in_thrown"))
        )

    def get_high_out(self):
        return (
            super(ScoresetManager, self)
            .get_queryset()
            .filter(gamescore__out_thrown__isnull=False)
            .annotate(Max("gamescore__out_thrown"))
        )

    def create_new(self, match, team, player):
        if player in match.season.team_set.filter(id=team.id).players.all():
            sub = False
        else:
            sub = True
        scoreset = self.create(match=match, team=team, player=player, is_sub=sub)
        return scoreset