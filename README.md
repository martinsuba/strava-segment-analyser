# strava-segment-analyser

Simple command line tool for analysing [Strava](https://strava.com)'s segment efforts without premium subscription written in Python using the Strava API.

## Usage

```
py strava_analyser.py
```

### Arguments

All are optional.

- `id` - Activity to print efforts for (Default: last activity)
- `all` - prints all segment efforts (Default: prints best efforts)
- `update` - fetches new activities

```
py strava_analyser.py 4728381269 all update
```