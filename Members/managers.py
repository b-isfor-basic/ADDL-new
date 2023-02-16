from django.db import models
from django.db.models import Case, Count, F, Max, Min, Q, Sum, Value, When
from django.db.models.functions import Ln, Round
from django.db.models.lookups import LessThan, LessThanOrEqual


class PlayerStatsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().prefetch_related("playerscoresummary_set", "")


class TeamStatsManager(models.Manager):            
            
    def get_queryset(self):
        qs = super().get_queryset().prefetch_related("teamscoresummary_set", "scoresummary_set")
        return qs.values('teamscoresummary__team_id').annotate(
                total_darts_thrown=(Sum("teamscoresummary__darts_thrown1") + Sum("teamscoresummary__darts_thrown2")),
                total_score_left=(Sum("teamscoresummary__score_left1") + Sum("teamscoresummary__score_left2")),
                games_included=(Count("teamscoresummary__id", distinct=True) * 2.0),
                avg_doubles_ppd=(
                    ((501.0 * F("games_included")) - F("total_score_left"))
                    / F("total_darts_thrown")
                ),
                best_501_game=Case(
                    When(
                        LessThanOrEqual(
                            Min("teamscoresummary__darts_thrown1", filter=Q(teamscoresummary__score_left1=0)),
                            Min("teamscoresummary__darts_thrown2", filter=Q(teamscoresummary__score_left2=0)),
                        ),
                        then=Min("teamscoresummary__darts_thrown1", filter=Q(teamscoresummary__score_left1=0)),
                    ),
                    When(
                        LessThan(
                            Min("teamscoresummary__darts_thrown2", filter=Q(teamscoresummary__score_left2=0)),
                            Min("teamscoresummary__darts_thrown1", filter=Q(teamscoresummary__score_left1=0)),
                        ),
                        then=Min("teamscoresummary__darts_thrown2", filter=Q(teamscoresummary__score_left2=0)),
                    ),
                    default=None,
                ),
                total_points=Sum("scoresummary__singles_points") + Sum("scoresummary__doubles_points"),
        )