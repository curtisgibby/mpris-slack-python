# MPRIS / Slack Integration

## Why does this exist?

I wanted to be able to push my now-listening status (including album art) to my company's Slack.

## Sounds cool. What do I need to do?

### 1. Create your `config.json` file

```
cp config.default.json config.json
```

### 2. Update your `config.json` file

#### Update `slack-token` _(required)_

Open the Slack customization page, e.g. `subdomain.slack.com/customize`. Open the console (F12) and paste:

```javascript
window.prompt("Your API token is: ", TS.boot_data.api_token)
```

Copy the API token from the popup and replace `YOUR_SLACK_TOKEN` with your actual token.

#### Update `emoji-name` _(optional)_

Replace `my-album-art` with your desired Slack emoji name

### 3. Start your MPRIS-enabled media player

This integration has been tested on the following players:

- [Google Play Music Desktop Player](https://www.googleplaymusicdesktopplayer.com/)
- [Spotify](https://www.spotify.com) (Linux client)
- [Pithos](https://pithos.github.io/) (Linux [Pandora](https://www.pandora.com/) client)

You need to be playing your media _before_ moving on to step 4.

### 4. Run the Python script

```
python mpris-track-change-to-slack.py
```

The script will let you know which media player it found. For example, I see this when I start Google Play Music:

```
Currently playing: Google Play Music Desktop Player
```

You can either wait until the current track finishes playing on its own, or if you're feeling impatient, skip to the next track to manually trigger the "track change" functionality. The script will attempt to:
   - save your album art as a Slack emoji and
   - set your status to the now-playing text including the artist and title and the album-art emoji

```
Attempting to set status: Now Playing: INXS - Devil Inside
Success
```

If the script is unable to create the album-art emoji (because of a bad token, no local album art, whatever), it will try to set the status using a standard emoji instead, randomly picking one of the following:

- :cd: (`:cd:`)
- :headphones: (`:headphones:`)
- :musical_note: (`:musical_note:`)
- :notes: (`:notes:`)
- :radio: (`:radio:`)

## Whom should I thank?

Thanks to Jack Ellenberger (@jackellenberger) for his [":slack_on_fire:" article](https://medium.com/@jack.a.ellenberger/slack-on-fire-part-two-please-stop-rotating-my-user-token-replay-attacking-slack-for-emoji-fun-c87da4e54b03) and his emojime library (particularly [`emoji-add.js`](https://github.com/jackellenberger/emojme/blob/e076b58bbe310da154013b51f77d3e1047938983/lib/emoji-add.js#L79-L82)) for helping me figure out how to push an emoji to Slack's [undocumented `/api/emoji.add` endpoint](https://webapps.stackexchange.com/a/126154/35105).
