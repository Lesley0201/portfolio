import urllib.request, urllib.error, urllib.parse, json
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)

from secrets import CLIENT_ID, CLIENT_SECRET

GRANT_TYPE = 'authorization_code'


app.secret_key = CLIENT_SECRET


def spotifyurlfetch(url, access_token, params=None):
    headers = {'Authorization': 'Bearer ' + access_token}
    req = urllib.request.Request(
        url=url,
        data=params,
        headers=headers
    )
    print(req)
    response = urllib.request.urlopen(req)
    return response.read()


@app.route("/")
def index():
    if 'user_id' in session:
        app.logger.info("In MainHandler")
    return render_template('weather and mood.html', user=session, page_title="Songs")


@app.route("/weather&mood")
def weather_mood():
    weather = request.args.get('weather')
    app.logger.info(weather)
    mood = request.args.get('mood')
    app.logger.info(mood)
    print(weather)
    print(mood)
    if mood == 'Anxiety':
        if weather == 'Sunny':
            cate = 'chill'
        else:
            cate = 'summer'
    elif mood == 'Angry':
        if weather == 'Foggy' or weather == 'Cloudy':
            cate = 'wellness'
        elif weather == 'Sunny':
            cate = 'funk'
        else:
            cate = 'jazz'
    elif mood == 'Happy':
        cate = 'pop'
    elif mood == 'Sad':
        if weather == 'Sunny' or weather == 'Cloudy':
            cate = 'country'
        else:
            cate = 'blues'
    elif mood == 'Excited':
        if weather == 'Sunny':
            cate = 'kpop'
        else:
            cate = 'classical'
    app.logger.info(cate)
    url = "https://api.spotify.com/v1/browse/categories/" + cate + "/playlists"
    response = json.loads(spotifyurlfetch(url, session['access_token']))
    api_url = response['playlists']['href']
    playlists = response['playlists']['items']
    html = render_template('playlists.html', playlist_name=cate, playlists=playlists, api_url=api_url)
    return html


@app.route("/auth/login")
def login_handler():
    args = {}
    args['client_id'] = CLIENT_ID

    verification_code = request.args.get("code")
    if verification_code:
        args["client_secret"] = CLIENT_SECRET
        args["grant_type"] = GRANT_TYPE
        args["code"] = verification_code
        args['redirect_uri'] = request.base_url
        data = urllib.parse.urlencode(args).encode("utf-8")
        url = "https://accounts.spotify.com/api/token"
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req, data=data)
        response_dict = json.loads(response.read())
        access_token = response_dict["access_token"]
        refresh_token = response_dict["refresh_token"]
        profile = json.loads(spotifyurlfetch('https://api.spotify.com/v1/me',
                                             access_token))
        session['user_id'] = profile["id"]
        session['displayname'] = profile["display_name"]
        session['access_token'] = access_token
        session['profile_url'] = profile["external_urls"]["spotify"]
        session['api_url'] = profile["href"]
        session['refresh_token'] = refresh_token
        if profile.get('images') is not None:
            session['img'] = profile["images"][0]["url"]
        return redirect(url_for('index'))
    else:
        args['redirect_uri'] = request.base_url
        print(request.base_url)
        args['response_type'] = "code"
        args['scope'] = "user-library-modify playlist-modify-private playlist-modify-public playlist-read-collaborative playlist-read-private"

        url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(args)
        return redirect(url)


@app.route("/auth/logout")
def logout_handler():
    for key in list(session.keys()):
        session.pop(key)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)
