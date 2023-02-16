from itertools import groupby, chain

from django.db import models
from django.db.models import Case, Count, F, Max, Min, Q, Sum, Value, When
from django.db.models.functions import Ln
from django.db.models.lookups import LessThan, LessThanOrEqual, GreaterThanOrEqual


class PlayerScoreSummaryManager(models.Manager):

    def get_queryset(self, *args, **kwargs):

        """
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
            - total_wins: total wins (singles + doubles)
            - singles_wins: total singles wins
            - doubles_wins: total doubles wins
            - stars: total stars
            - perfects: total perfects
            - max_high_in: highest high in
            - max_high_out: highest high out
            - average_ppd: average points per dart
            - win_percentage: win percentage
            - avg_stars_per_game: average stars per game
            - rating: player rating calculated as 
                ((Ln(average_ppd) * 3.5) + (win_percentage * 8) + (avg_stars_per_game * 5)
            - best_week_singles_ppd: best week's average ppd in singles
            - best_501_game: lowest darts thrown to win a singles 501 game
        """

        qs = super().get_queryset()
        return (
            qs.annotate(
                weekly_ppd=(
                    ((501.0*2) - (F("score_left1")+F("score_left2")))
                    / (F("darts_thrown1") + F("darts_thrown2"))
                )
            ).values(
                "player", "player__first_name", "player__last_name", "team__division"
            ).annotate(
                # Get total_darts_thrown, total_score_left, games_included to calculate average ppd
                total_darts_thrown=(Sum("darts_thrown1") + Sum("darts_thrown2")),
                total_score_left=(Sum("score_left1") + Sum("score_left2")),
                games_included=(Count("id", distinct=True) * 2),
                max_weekly_ppd=(Max("weekly_ppd")),
            ).annotate(
                # Points stats
                singles_wins=Sum("singles_points", default=0),
                doubles_wins=Sum("doubles_points", default=0),
                total_wins=(
                    Sum("singles_points", default=0) + Sum("doubles_points", default=0)
                ),
                games_played=(Count("id", distinct=True) * 10),
                win_percentage=(F("total_wins") / (Count("id", distinct=True) * 10.0)),

                # Stars stats
                stars=Sum("total_stars", default=0),
                perfects=Sum("total_perfects", default=0),
                avg_stars_per_game=(Sum("total_stars") / (Count("id", distinct=True) * 10.0)),
                
                # '01 stats
                max_high_in=Max("high_in", default=0),
                max_high_out=Max("high_out", default=0),
                avg_ppd=(
                    ((501.0 * F("games_included")) - F("total_score_left"))
                    / F("total_darts_thrown")
                ),
                best_501_game=Case(
                    When(
                        LessThanOrEqual(
                            Min("darts_thrown1", filter=Q(score_left1=0)),
                            Min("darts_thrown2", filter=Q(score_left2=0)),
                        ),
                        then=Min("darts_thrown1", filter=Q(score_left1=0)),
                    ),
                    When(
                        LessThan(
                            Min("darts_thrown2", filter=Q(score_left2=0)),
                            Min("darts_thrown1", filter=Q(score_left1=0)),
                        ),
                        then=Min("darts_thrown2", filter=Q(score_left2=0)),
                    ),
                    default=1000,
                ),
                best_week_singles_ppd=F("max_weekly_ppd"),

                # Rating stats
                rating_score=(
                   (Ln(F("avg_ppd")) * 3.5)
                    + (F("win_percentage") * 8.0)
                    + (F("avg_stars_per_game") * 5.0)
                ),
                rating=Case(
                    When(
                        LessThanOrEqual(F("rating_score"), 10.50),
                        then=Value("E")
                    ),
                    When(
                        LessThan(F("rating_score"), 12.20),
                        then=Value("D")
                    ),
                    When(
                        LessThan(F("rating_score"), 15.40),
                        then=Value("C")
                    ),
                    When(
                        LessThan(F("rating_score"), 18.80),
                        then=Value("B")
                    ),
                    When(
                        LessThan(F("rating_score"), 22.50),
                        then=Value("A")
                    ),
                    When(
                        GreaterThanOrEqual(F("rating_score"), 22.50),
                        then=Value('AA')
                    )
                ),   
            )
        )


class TeamScoreSummaryManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset().select_related("team", "match", "match__week", "team__division")
        return (
            qs.annotate(
                weekly_doubles_ppd=(
                    ((501.0 * 2) - (F("score_left1") + F("score_left2")))
                    / (F("darts_thrown1") + F("darts_thrown2"))
                )
            )
            .values("team", "team__division")
            .annotate(
                total_darts_thrown=(Sum("darts_thrown1") + Sum("darts_thrown2")),
                total_score_left=(Sum("score_left1") + Sum("score_left2")),
                games_included=(Count("id", distinct=True) * 2.0),
                avg_doubles_ppd=(
                    ((501.0 * F("games_included")) - F("total_score_left"))
                    / F("total_darts_thrown")
                ),
                best_501_game=Case(
                    When(
                        LessThanOrEqual(
                            Min("darts_thrown1", filter=Q(score_left1=0)),
                            Min("darts_thrown2", filter=Q(score_left2=0)),
                        ),
                        then=Min("darts_thrown1", filter=Q(score_left1=0)),
                    ),
                    When(
                        LessThan(
                            Min("darts_thrown2", filter=Q(score_left2=0)),
                            Min("darts_thrown1", filter=Q(score_left1=0)),
                        ),
                        then=Min("darts_thrown2", filter=Q(score_left2=0)),
                    ),
                    default=1000,
                ),
                best_week_doubles_ppd=Max(F("weekly_doubles_ppd")),
            )
        )


    def with_names(self, *args, **kwargs):
        
        from Members.models import Team
        
        qs = self.get_queryset().filter(*args, **kwargs)
        for team in qs:
            team_name = [player.last_name for player in Team.objects.get(id=team['team']).players.all()]
            team_name = '/'.join(team_name)
            team['name'] = team_name
        return qs


    def all_stats(self, *args, **kwargs):

        from .models import ScoreSummary
        additional = ScoreSummary.stats.filter(*args, **kwargs
            ).values('team', 'rating_score').annotate(
                total_points=Sum('singles_points') + Sum('doubles_points'),
                team_rating=Case(
                    When(
                        LessThanOrEqual(F("rating_score"), 10.50),
                        then=Value("E")
                    ),
                    When(
                        LessThan(F("rating_score"), 12.20),
                        then=Value("D")
                    ),
                    When(
                        LessThan(F("rating_score"), 15.40),
                        then=Value("C")
                    ),
                    When(
                        LessThan(F("rating_score"), 18.80),
                        then=Value("B")
                    ),
                    When(
                        LessThan(F("rating_score"), 22.50),
                        then=Value("A")
                    ),
                    When(
                        GreaterThanOrEqual(F("rating_score"), 22.50),
                        then=Value('AA')
                    )
                ),
            )
        original = self.with_names(*args, **kwargs)
        for team in original:
            # add the extra stats to the original queryset
            team.update(additional.get(team=team['team']).items())
        return original





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
        if player in match.week.season.team_set.filter(id=team.id).players.all():
            sub = False
        else:
            sub = True
        scoreset = self.create(match=match, team=team, player=player, is_sub=sub)
        return scoreset

