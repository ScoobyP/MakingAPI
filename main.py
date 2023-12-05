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


if __name__ == '__main__':

    website.run(debug=True, port=5002)
