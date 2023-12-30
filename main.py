from flask import Flask, jsonify, request
import ipl

website = Flask(__name__)


@website.route('/')
def page_1():
    return 'Jai Sri Krishna'


@website.route('/api/teams')
def page_2():
    teams = ipl.All_teams_API()
    return jsonify(teams)


@website.route('/api/team_record')
def page_3():
    team1 = request.args.get('team')
    response = ipl.team_record_API(team1)
    return jsonify(response)


@website.route('/api/batsmen')
def page_4():
    batsmen = ipl.All_batsmen_API()
    return jsonify(batsmen)


@website.route('/api/batsman_record')
def page_5():
    batter1 = request.args.get('batter')
    response = ipl.batsman_record(batter1)
    return jsonify(response)


@website.route('/api/POM_names')
def page_6():
    pomnames = ipl.POM_names()
    return jsonify(pomnames)

@website.route('/api/POM_record')
def page_7():
    pom_name = request.args.get('pom')
    response = ipl.player_of_match_record(pom_name)
    return jsonify(response)


@website.route('/api/batsman_against_record')
def page_8():
    batter_name = request.args.get('batter')
    response = ipl.batsman_against_record(batter_name)
    return jsonify(response)

@website.route('/api/bowlers')
def page_9():
    bowler_name = ipl.bowlers_name_list()
    return jsonify(bowler_name)

@website.route('/api/bowling_rec')
def page_10():
    bowler1 = request.args.get('bowler')
    response = ipl.bowling_rec(bowler1)
    return jsonify(response)

@website.route('/api/aga_bowling_rec')
def page_11():
    bowler1 = request.args.get('bowl')
    response = ipl.aga_bowling_rec(bowler1)
    return jsonify(response)




if __name__ == '__main__':

    website.run(debug=True, port=5002)
