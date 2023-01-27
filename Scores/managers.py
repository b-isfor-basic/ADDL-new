from django.db import models
from django.db.models import Count, Max, Min, Sum, F, Q, Case, When, Avg
from django.db.models.functions import Ln, Round
from django.db.models.lookups import LessThanOrEqual


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
    pass
#     """
#     This is a custom manager that returns a queryset of player stats.
#     Primary purpose is to provide a queryset for the PlayerStatsListView.

#     The queryset is annotated with the following fields:
#         games_played: The number of games played by the player.
#         singles_points: The number of points earned in singles games.
#         doubles_points: The number of points earned in doubles games.
#         total_points: The total number of points earned.
#         win_percentage: The percentage of games won by the player.
#         total_stars: The total number of stars earned by the player.
#         avg_stars_per_game: The average number of stars earned per game.
#         total_perfects: The total number of perfects earned by the player.
#         best_singles_501: The fewest darts thrown in a 501 singles game.
#         high_in: The highest in thrown by the player.
#         high_out: The highest out thrown by the player.
#         avg_ppd: The average points per dart thrown in 501 singles games.
#     """

#     def get_queryset(self, **kwargs):
#         return (
#             super()
#             .get_queryset(**kwargs)
#             .prefetch_related("gamescore_set", "player")
#             .values("player_id", "player__first_name", "player__last_name")
#             .annotate(
#                 games_played=(Count("match_id", distinct=True) * 10),
#                 singles_points=Sum(
#                     "gamescore__game_point", filter=models.Q(gamescore__format="SN")
#                 ),
#                 doubles_points=Sum(
#                     "gamescore__game_point", filter=models.Q(gamescore__format="DB")
#                 ),
#                 total_points=Sum("gamescore__game_point"),
#                 win_percentage=Round(
#                     Cast(
#                         (
#                             Sum("gamescore__game_point")
#                             / (Count("match_id", distinct=True) * 10.00)
#                             * 100.00
#                         ),
#                         models.FloatField(),
#                     ),
#                     2,
#                 ),
#                 total_stars=Sum("gamescore__stars"),
#                 avg_stars_per_game=Round(
#                     Cast(Avg("gamescore__stars"), models.FloatField()), 2
#                 ),
#                 total_perfects=Sum("gamescore__perfects"),
#                 best_singles_501=Min(
#                     "gamescore__darts_thrown",
#                     filter=models.Q(
#                         gamescore__format="SN",
#                         gamescore__game="501",
#                         gamescore__game_point=1,
#                     ),
#                 ),
#                 high_in=Max("gamescore__in_thrown"),
#                 high_out=Max("gamescore__out_thrown"),
#                 avg_ppd=Round(
#                     Cast(
#                         (
#                             (
#                                 501.0
#                                 * Count(
#                                     "gamescore",
#                                     distinct=True,
#                                     filter=models.Q(
#                                         gamescore__format="SN", gamescore__game="501"
#                                     ),
#                                 )
#                                 - Sum(
#                                     "gamescore__score_left",
#                                     filter=models.Q(
#                                         gamescore__format="SN", gamescore__game="501"
#                                     ),
#                                 )
#                             )
#                             / Sum(
#                                 "gamescore__darts_thrown",
#                                 filter=models.Q(
#                                     gamescore__format="SN", gamescore__game="501"
#                                 ),
#                             )
#                         ),
#                         models.FloatField(),
#                     ),
#                     4,
#                 ),
#                 rating=Round(
#                     (Ln(models.F("avg_ppd")) * 3.5)
#                     + ((models.F("win_percentage") / 100) * 8)
#                     + (models.F("avg_stars_per_game") * 5),
#                     4,
#                 ),
#             )
#         )


class TeamStatsManager(models.Manager):
    pass
#     def get_queryset(self, **kwargs):
#         return (
#             super()
#             .get_queryset(**kwargs)
#             .prefetch_related("gamescore_set", "team")
#             .values("team")
#             .annotate(
#                 total_wins=Sum("gamescore__game_point"),
#                 total_losses=Count(
#                     "gamescore__game_point",
#                     filter=models.Q(gamescore__game_point=0),
#                     distinct=True,
#                 ),
#                 win_percentage=Round(
#                     Cast(
#                         (
#                             Sum("gamescore__game_point")
#                             / (Count("match_id", distinct=True) * 20.00)
#                             * 100.00
#                         ),
#                         models.FloatField(),
#                     ),
#                     2,
#                 ),
#                 best_doubles_501=Min(
#                     "gamescore__darts_thrown",
#                     filter=models.Q(
#                         gamescore__format="DB",
#                         gamescore__game="501",
#                         gamescore__game_point=1,
#                     ),
#                 ),
#                 avg_doubles_ppd=Round(
#                     Cast(
#                         (
#                             501.0
#                             * Count(
#                                 "gamescore",
#                                 distinct=True,
#                                 filter=models.Q(
#                                     gamescore__format="DB", gamescore__game="501"
#                                 ),
#                             )
#                             - Sum(
#                                 "gamescore__score_left",
#                                 filter=models.Q(
#                                     gamescore__format="DB", gamescore__game="501"
#                                 ),
#                                 distinct=True,
#                             )
#                         )
#                         / Sum(
#                             "gamescore__darts_thrown",
#                             filter=models.Q(
#                                 gamescore__format="DB", gamescore__game="501"
#                             ),
#                             distinct=True,
#                         ),
#                         models.FloatField(),
#                     ),
#                     4,
#                 ),
#             )
#         )



class PlayerScoreSummaryManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        '''
        Accepts a queryset and returns an aggregated queryset of 
        ScoreSummary objects grouped by player with annotations
        for all stats.
        For Average PPD calculation:
            - total_darts_thrown: total darts thrown in all games
            - total_score_left: total score left in all games
            - games_included: total games included in calculation (2 singles 501 games per match)
        For Win Percentage calculation:
            - games_played: total games played (10 games per match)
        Reported Stats:

        '''
        qs = super().get_queryset()
        return qs.annotate(
                weekly_ppd=Round(
                    (1001.0-(F('score_left1')+F('score_left2'))) 
                    /(F('darts_thrown1')+F('darts_thrown2'))
                    , 4
                )
            ).values("player", "player__first_name", "player__last_name", "team__division").annotate(
            # Get total_darts_thrown, total_score_left, games_included to calculate average ppd
            total_darts_thrown=(Sum("darts_thrown1")+Sum("darts_thrown2")),
            total_score_left=(Sum("score_left1")+Sum("score_left2")),
            games_included=(Count("id", distinct=True)*2),
            # Get total games_played to calculate win percentage
            games_played=(Count("id", distinct=True)*10),
            total_wins=(Sum("singles_points") + Sum("doubles_points")),
            singles_wins=Sum("singles_points"),
            doubles_wins=Sum("doubles_points"),
            stars=Sum("total_stars"),
            perfects=Sum("total_perfects"),
            max_high_in=Max("high_in", default=0),
            max_high_out=Max("high_out", default=0),
            avg_ppd=Round((501.0*F("games_included")-F("total_score_left"))/F("total_darts_thrown"), 4),
            avg_ppd2=Avg("weekly_ppd"),
            win_percentage=(F("total_wins")/(Count("id")*10.0)),
            avg_stars_per_game=Round((Sum("total_stars")/(Count("id")*10.0)), 2, output_field=models.FloatField()),
            rating=Round(
                (Ln(F("avg_ppd"))*3.5) 
                +((F("win_percentage"))*8.0) 
                +((F("avg_stars_per_game"))*5.0)
                ,4
            ),
            best_501_game=Case(
                When(
                    LessThanOrEqual(
                        Min('darts_thrown1', filter=Q(score_left1=0)),
                        Min('darts_thrown2', filter=Q(score_left2=0))
                    ), then=Min('darts_thrown1', filter=Q(score_left1=0))
                ), default=Min('darts_thrown2', filter=Q(score_left2=0))
            ),
            best_week_singles_ppd=Max('weekly_ppd')
        )


class TeamScoreSummaryManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()        
        return qs.annotate(weekly_ppd=Round(
                (1001.0-(F('score_left1')+F('score_left2')))
                /(F('darts_thrown1')+F('darts_thrown2')), 4
            )).values("team", "team__division").annotate(
            total_darts_thrown=(Sum("darts_thrown1")+Sum("darts_thrown2")),
            total_score_left=(Sum("score_left1")+Sum("score_left2")),
            games_included=(Count("id", distinct=True)*2.0),
            avg_doubles_ppd=Round((501.0*F("games_included")-F("total_score_left"))/F("total_darts_thrown"), 4),
            best_501_game=Case(
                When(
                    LessThanOrEqual(
                        Min('darts_thrown1', filter=Q(score_left1=0)),
                        Min('darts_thrown2', filter=Q(score_left2=0))
                    ), then=Min('darts_thrown1', filter=Q(score_left1=0))
                ), default=Min('darts_thrown2', filter=Q(score_left2=0))
            ),
            best_week_doubles_ppd=Max('weekly_ppd')
        )