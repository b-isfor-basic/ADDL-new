from django.db import models
from django.db.models.aggregates import Avg, Count, Max, Min, Sum
from django.db.models.functions import Cast, Ln, Round


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


class GamesManager(
    SinglesCricketGameManager,
    DoublesCricketGameManager,
    Singles501GameManager,
    Doubles501GameManager,
    Doubles301GameManager,
    models.Manager,
):
    pass


class ScoresetManager(models.Manager):
    def create_new(self, match, team, player):
        if player in match.season.team_set.filter(id=team.id).players.all():
            sub = False
        else:
            sub = True
        scoreset = self.create(match=match, team=team, player=player, is_sub=sub)
        return scoreset


class PlayerStatsManager(models.Manager):
    """
    This is a custom manager that returns a queryset of player stats.
    Primary purpose is to provide a queryset for the PlayerStatsListView.

    The queryset is annotated with the following fields:
        games_played: The number of games played by the player.
        singles_points: The number of points earned in singles games.
        doubles_points: The number of points earned in doubles games.
        total_points: The total number of points earned.
        win_percentage: The percentage of games won by the player.
        total_stars: The total number of stars earned by the player.
        avg_stars_per_game: The average number of stars earned per game.
        total_perfects: The total number of perfects earned by the player.
        best_singles_501: The fewest darts thrown in a 501 singles game.
        high_in: The highest in thrown by the player.
        high_out: The highest out thrown by the player.
        avg_ppd: The average points per dart thrown in 501 singles games.
    """

    def get_queryset(self, **kwargs):
        return (
            super()
            .get_queryset(**kwargs)
            .prefetch_related("gamescore_set", "player")
            .values("player_id", "player__first_name", "player__last_name")
            .annotate(
                games_played=(Count("match_id", distinct=True) * 10),
                singles_points=Sum(
                    "gamescore__game_point", filter=models.Q(gamescore__format="SN")
                ),
                doubles_points=Sum(
                    "gamescore__game_point", filter=models.Q(gamescore__format="DB")
                ),
                total_points=Sum("gamescore__game_point"),
                win_percentage=Round(
                    Cast(
                        (
                            Sum("gamescore__game_point")
                            / (Count("match_id", distinct=True) * 10.00)
                            * 100.00
                        ),
                        models.FloatField(),
                    ),
                    2,
                ),
                total_stars=Sum("gamescore__stars"),
                avg_stars_per_game=Round(
                    Cast(Avg("gamescore__stars"), models.FloatField()), 2
                ),
                total_perfects=Sum("gamescore__perfects"),
                best_singles_501=Min(
                    "gamescore__darts_thrown",
                    filter=models.Q(
                        gamescore__format="SN",
                        gamescore__game="501",
                        gamescore__game_point=1,
                    ),
                ),
                high_in=Max("gamescore__in_thrown"),
                high_out=Max("gamescore__out_thrown"),
                avg_ppd=Round(
                    Cast(
                        (
                            (
                                501.0
                                * Count(
                                    "gamescore",
                                    distinct=True,
                                    filter=models.Q(
                                        gamescore__format="SN", gamescore__game="501"
                                    ),
                                )
                                - Sum(
                                    "gamescore__score_left",
                                    filter=models.Q(
                                        gamescore__format="SN", gamescore__game="501"
                                    ),
                                )
                            )
                            / Sum(
                                "gamescore__darts_thrown",
                                filter=models.Q(
                                    gamescore__format="SN", gamescore__game="501"
                                ),
                            )
                        ),
                        models.FloatField(),
                    ),
                    4,
                ),
                rating=Round(
                    (Ln(models.F("avg_ppd")) * 3.5)
                    + ((models.F("win_percentage") / 100) * 8)
                    + (models.F("avg_stars_per_game") * 5),
                    4,
                ),
            )
        )


class TeamStatsManager(models.Manager):
    def get_queryset(self, **kwargs):
        return (
            super()
            .get_queryset(**kwargs)
            .prefetch_related("gamescore_set", "team")
            .values("team")
            .annotate(
                total_wins=Sum("gamescore__game_point"),
                total_losses=Count(
                    "gamescore__game_point",
                    filter=models.Q(gamescore__game_point=0),
                    distinct=True,
                ),
                win_percentage=Round(
                    Cast(
                        (
                            Sum("gamescore__game_point")
                            / (Count("match_id", distinct=True) * 20.00)
                            * 100.00
                        ),
                        models.FloatField(),
                    ),
                    2,
                ),
                best_doubles_501=Min(
                    "gamescore__darts_thrown",
                    filter=models.Q(
                        gamescore__format="DB",
                        gamescore__game="501",
                        gamescore__game_point=1,
                    ),
                ),
                avg_doubles_ppd=Round(
                    Cast(
                        (
                            501.0
                            * Count(
                                "gamescore",
                                distinct=True,
                                filter=models.Q(
                                    gamescore__format="DB", gamescore__game="501"
                                ),
                            )
                            - Sum(
                                "gamescore__score_left",
                                filter=models.Q(
                                    gamescore__format="DB", gamescore__game="501"
                                ),
                                distinct=True,
                            )
                        )
                        / Sum(
                            "gamescore__darts_thrown",
                            filter=models.Q(
                                gamescore__format="DB", gamescore__game="501"
                            ),
                            distinct=True,
                        ),
                        models.FloatField(),
                    ),
                    4,
                ),
            )
        )
