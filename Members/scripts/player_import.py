import re

from Members.models import Player

teams = {}

with open("Members/scripts/season41.txt") as f:
    f_lines = f.read().splitlines()
    f.close()
    
area = ''
for line in f_lines:
    if re.match(r"^Area \d", line):
        area = re.match(r"^Area \d+", line).group()
        teams[area] = []
    elif re.match(r"^\d. ", line):
        teams.get(area).append(line[3:])
    else:
        continue

players = []
for k, v in teams.items():
    for team in v:
        names = team.split(' / ')
        for name in names:
            players.append({'first_name': name.split(' ')[0], 'last_name': ' '.join(name.split(' ')[1:])})

print(teams)
print(players)

for player in players:
    username = player.get('first_name') + '.' + ''.join(player.get('last_name').split(' '))
    new = Player.objects.create(username=username, first_name=player.get('first_name'), last_name=player.get('last_name'))
    new.save()

