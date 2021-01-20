from riotwatcher import LolWatcher, ApiError
import serial
import sys
import time

# Enable Serial
SERIAL = True
serial_port = 'COM3'

# API related
# Change API to YOUR API
api_key = '########'
watcher = LolWatcher(api_key)

# Change these values to YOUR values
my_region = 'euw1'
my_summonername = 'Embedded'

## Try to connect to Riot API
try:
    me = watcher.summoner.by_name(my_region, my_summonername)
except ApiError as err:
    if err.me.status_code == 429:
        print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
        print('this retry-after is handled by default by the RiotWatcher library')
        print('future requests wait until the retry-after time passes')
    elif err.me.status_code == 404:
        print('Summoner with that ridiculous name not found.')

print(me)

# Try to open Serial
if SERIAL == True:
    ser = serial.Serial(serial_port)
    s = ser.read_all()

while True:

    _match_all = watcher.match.matchlist_by_account(my_region, me['accountId'])
    print(_match_all['matches'][0]['gameId'])

    # last game ever made
    try:
        _last_game_id = watcher.match.by_id(my_region, _match_all['matches'][0]['gameId'])
    except ApiError as err:
        if err._last_game_id.status_code == 404:
            print('No match with such an ID')
        elif err._last_game_id.status_code == 504:
            print('Gateway error 504')
            time.sleep(10)

    for x in range(0, len(_last_game_id['participantIdentities']), 1):

        if me['accountId'] == _last_game_id['participantIdentities'][x]['player']['accountId']:

            print("My summoner's name: " + _last_game_id['participantIdentities'][x]['player']['summonerName'])
            _game_result = _last_game_id['participants'][x]['stats']['win']
            print("Game Result: " + str(_game_result))
            _game_duration = _last_game_id['gameDuration']
            print("Game Duration: " + str(_game_duration / 60))

            _game_duration_min = str(_game_duration / 60)

            ## Send to Serial 
            # You took X minutes to lose - you noob!
            # You took only Y minutes to kick their ass!

            if SERIAL == True:
                if _game_result == True:
                    ser.write(b'You took '+ _game_duration_min.encode() + b' minutes to win - Faker is that you? \n') 
                else:
                    ser.write(b'You took '+ _game_duration_min.encode() + b' minutes to lose - you NOOB! \n') 

    
    time.sleep(30)        
