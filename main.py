from datetime import datetime, timezone
import requests
from utils import checktime
"""
last updated: 2026-06-30
credits: @think (https://github.com/thinkdev123)
based of the work of Joseph Wilson(pseudo-r)(https://github.com/pseudo-r)
This module contains the SoccerClient class, which serves as the main API
client for retrieving football/soccer match data from ESPN API. 
-in the current state of the client the client only fetches from https://site.api.espn.com/apis/site/v2/sports/soccer/slug/scoreboard
-as of right now the client only extracts:
    - match_id
    - date
    - short_name
    - state
    - detail
    - venue_name
    - venue_city
    - venue_country
    - home_name
    - away_name
    - home_score
    - away_score
    - home_abbreviation
    - away_abbreviation
    - home_logo
    - away_logo
    - home_form
    - away_form

-rest of the atributes have been found to either be dependent on the slug/legue or give out inconsistent data, so they have been left out for now.
- parsing the form atribute has not been implemented yet but can be done manually by using instance.home_form and instance.away_form for a match instance.(for the games list simply iterate through and then use before mentioned attributes to get the form for each match)
- home_logo,away_logo only return a url, retriving a logo image has not been verified or implemented yet.
-uses/applications has been described in the readme file.
"""

class SoccerClient:
    """
    Attributes:
        sport (str): Sport type (default: soccer)
        slug (str): Competition slug (example: fifa.world)
        url (str): Full API endpoint URL
        games (list): Stores Match objects

    """
    def __init__(self, slug='fifa.world'):
        """

        Args:
            slug (str): Competition slug

        """
        self.sport = 'soccer'
        self.slug = slug
        self.url = f"https://site.api.espn.com/apis/site/v2/sports/{self.sport}/{self.slug}/scoreboard"
        self.games = []

    def get_info(self, date=None, date_range=None, limit=100):
        """
        Fetches all available match data from ESPN API.

        Args:
            date (str, optional): Specific date in YYYYMMDD format.
            date_range (tuple, optional): Tuple of (start, end) in YYYYMMDD format.
            limit (int, optional): Maximum number of events to return. Defaults to 100.

        Returns:
            list[Match]: List of Match objects.
        """

        # Only cache default "today" requests
        use_cache = date is None and date_range is None and limit == 100

        params = {}

        if limit != 100:
            params["limit"] = limit

        if date_range:
            params["dates"] = f"{date_range[0]}-{date_range[1]}"
        elif date:
            params["dates"] = date

        response = requests.get(self.url, params=params)
        response.raise_for_status()
        data = response.json()

        events = data.get("events", [])
        utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        fetched_games = []

        for event in events:
            if "id" in event:
                match_id = event["id"]
            else:
                match_id = ""

            if "date" in event:
                match_date = event["date"]
            else:
                match_date = ""

            if "shortName" in event:
                short_name = event["shortName"]
            elif "name" in event:
                short_name = event["name"]
            else:
                short_name = "Unknown match"

            if "competitions" in event and len(event["competitions"]) > 0:
                competition = event["competitions"][0]
            else:
                competition = {}

            if "venue" in competition:
                venue = competition["venue"]
            else:
                venue = {}

            venue_name = venue.get("fullName", "")

            if "address" in venue:
                venue_city = venue["address"].get("city", "")
                venue_country = venue["address"].get("country", "")
            else:
                venue_city = ""
                venue_country = ""

            if "status" in competition:
                status = competition["status"]
            else:
                status = {}

            if "type" in status:
                status_type = status["type"]
            else:
                status_type = {}

            state = status_type.get("state", "unknown")
            detail = status_type.get("detail", "")

            if "competitors" in competition:
                competitors = competition["competitors"]
            else:
                competitors = []

            home_name, home_score, home_abbreviation, home_logo, home_form = "Home", "-", "", "", ""
            away_name, away_score, away_abbreviation, away_logo, away_form = "Away", "-", "", "", ""

            for c in competitors:
                if "team" in c:
                    team = c["team"]
                    team_name = team.get("displayName", "?")
                    team_abbr = team.get("abbreviation", "")
                    team_logo = ""

                    if "links" in team and len(team["links"]) > 0:
                        team_logo = team.get("logo", "")
                    elif "logo" in team:
                        team_logo = team["logo"]
                else:
                    team_name, team_abbr, team_logo = "?", "", ""

                score = c.get("score", "-")
                form = c.get("form", "")

                if "homeAway" in c and c["homeAway"] == "home":
                    home_name = team_name
                    home_score = score
                    home_abbreviation = team_abbr
                    home_logo = team_logo
                    home_form = form

                elif "homeAway" in c and c["homeAway"] == "away":
                    away_name = team_name
                    away_score = score
                    away_abbreviation = team_abbr
                    away_logo = team_logo
                    away_form = form

            matchinfo = {
                "match_id": match_id,
                "date": match_date,
                "short_name": short_name,
                "state": state,
                "detail": detail,
                "venue_name": venue_name,
                "venue_city": venue_city,
                "venue_country": venue_country,
                "home_name": home_name,
                "away_name": away_name,
                "home_score": home_score,
                "away_score": away_score,
                "home_abbreviation": home_abbreviation,
                "away_abbreviation": away_abbreviation,
                "home_logo": home_logo,
                "away_logo": away_logo,
                "home_form": home_form,
                "away_form": away_form,
                "last_updated": utc_now
            }

            inst = Match(matchinfo)
            fetched_games.append(inst)

        if use_cache:
                self.games = fetched_games

        return fetched_games

    def ongoing(self, max_time=60):
        """
        Returns all live matches.

        Output:
            list[Match]

        Example:
            [Brazil 1 - 0 Germany]
        """
        if checktime(self.games,max_time):
            self.get_info()
        return [i for i in self.games if i.is_live]

    def finished(self, max_time=60):
        """
        Returns all completed matches.

        Output:
            list[Match]
        """
        if checktime(self.games,max_time):
            self.get_info()

        return [i for i in self.games if i.is_finished]

    def upcoming(self, max_time=60):
        """
        Returns all scheduled/upcoming matches.

        Output:
            list[Match]
        """
        if checktime(self.games,max_time):
            self.get_info()

        return [i for i in self.games if i.is_upcoming]

    def venues(self, max_time=60):
        """
        Returns venue details for all matches.

        Output:
            [
                {
                    "venue": "...",
                    "city": "...",
                    "country": "..."
                }
            ]
        """
        venue_list = []
        if checktime(self.games,max_time):
            self.get_info()
        for i in self.games:
            venue_list.append({"venue": i.venue_name, "city": i.venue_city, "country": i.venue_country})

        return venue_list

    def scores(self,max_time=60):
        """
        Returns score summary for all matches.

        Output:
            [
                {
                    "home": "Brazil",
                    "home_score": "2",
                    "away_score": "1",
                    "away": "Argentina"
                }
            ]
        """
        score_list = []
        if checktime(self.games,max_time):
            self.get_info()
        for i in self.games:
            score_list.append({"home": i.home_name, "home_score": i.home_score, "away_score": i.away_score, "away": i.away_name})
        return score_list

    def get_ids(self,max_time=60):
        """
        Returns all match IDs mapped to short names.

        Output:
            {
                "BRA vs ARG": "12345"
            }
        """
        id_dict = {}
        if checktime(self.games,max_time):
            self.get_info()
        for i in self.games:
            id_dict[f"{i.short_name}"] = i.match_id
        return id_dict

    def get_id(self,match_short,max_time=60):
        """
        Gets a specific match ID using short name.

        Args:
            match_short (str)

        Output:
            str or None
        """
        if checktime(self.games,max_time):
            self.get_info()
        for i in self.games:
            if i.short_name == match_short:
                return i.match_id
        return None


class Match:
    """
    Stores individual match information.
    home_form and away_form are strings representing the last 5 match results for each team, where:
        W = Win
        D = Draw
        L = Loss
    example: "W-W-D-L-W" means the team won 3, drew 1, and lost 1 of their last 5 matches.
    Attributes:
    matchinfo (dict): Dictionary containing match details.

    """

    def __init__(self,matchinfo):
        """Initializes Match object from matchinfo dictionary."""
        self.match_id = matchinfo["match_id"] 
        self.date = matchinfo["date"] # Match date in ISO format
        self.short_name = matchinfo["short_name"] 
        self.venue_name = matchinfo["venue_name"] 
        self.venue_city = matchinfo["venue_city"] 
        self.venue_country = matchinfo["venue_country"] 
        self.home_abbreviation = matchinfo["home_abbreviation"] 
        self.away_abbreviation = matchinfo["away_abbreviation"] 
        self.home_logo = matchinfo["home_logo"] 
        self.away_logo = matchinfo["away_logo"] 
        self.home_form = matchinfo["home_form"] # Home team form
        self.away_form = matchinfo["away_form"] # Away team form
        self.state =matchinfo["state"] 
        self.detail= matchinfo["detail"] 
        self.home_name= matchinfo["home_name"] 
        self.home_score= matchinfo["home_score"]
        self.away_name= matchinfo["away_name"] 
        self.away_score= matchinfo["away_score"] 
        self.last_updated= matchinfo["last_updated"] # Last updated timestamp(produced by the client using the datetime module)

    def __repr__(self):
        """
        String representation of match.
        when a object of this class is printed it will return a string in the following format:
        {home_name} {home_score} - {away_score} {away_name} | {state} | {detail} , Venue: {venue_name}, {venue_city}, {venue_country} | Last Updated: {last_updated} | Home Abbr: {home_abbreviation} | Away Abbr: {away_abbreviation}  | Home Form: {home_form} | Away Form: {away_form}   

        Output example:
        Brazil 2 - 1 Argentina | post | FT
        """
        return f"{self.home_name} {self.home_score} - {self.away_score} {self.away_name} | {self.state} | {self.detail} , Venue: {self.venue_name}, {self.venue_city}, {self.venue_country} | Last Updated: {self.last_updated} | Home Abbr: {self.home_abbreviation} | Away Abbr: {self.away_abbreviation}  | Home Form: {self.home_form} | Away Form: {self.away_form}"

    @property
    def is_live(self):
        """Returns True if match is live."""
        if self.state == "in":
            return True
        else:
            return False

    @property
    def is_finished(self):
        """Returns True if match has ended."""
        if self.state == "post":
            return True
        else:
            return False

    @property
    def is_upcoming(self):
        """Returns True if match hasn't started."""
        if self.state == "pre":
            return True
        else:
            return False

    @property
    def venue(self):
        """
        Returns venue info. for a singular match instance

        Output:
        {
            "venue": "...",
            "city": "...",
            "country": "..."
        }
        """
        return {"venue": self.venue_name, "city": self.venue_city, "country": self.venue_country}

    @property
    def score(self):
        """
        Returns score dictionary. for a singular match instance

        Output:
        {
            "home": "...",
            "home_score": "...",
            "away_score": "...",
            "away": "..."
        }
        """
        return {"home": self.home_name, "home_score": self.home_score, "away_score": self.away_score, "away": self.away_name}


if __name__ == "__main__":
    """
    Testing block.
    Tests all major functionality:
    - Basic get_info() with default params
    - Date filtering
    - Date range filtering
    - All filter methods (ongoing, finished, upcoming)
    - Venue and score extraction
    - Match ID retrieval
    """

    print("=" * 60)
    print("TEST 1: Basic fetch (today's matches)")
    print("=" * 60)
    instance1 = SoccerClient('fifa.world')
    live = instance1.get_info()
    print(f"Total matches found: {len(live)}")
    print(live)
    print("\n")

    print("=" * 60)
    print("TEST 2: Specific date fetch")
    print("=" * 60)
    instance2 = SoccerClient('fifa.world')
    specific_date = instance2.get_info(date="20260628")
    print(f"Matches on 2026-06-28: {len(specific_date)}")
    print(specific_date)
    print("\n")

    print("=" * 60)
    print("TEST 3: Date range fetch")
    print("=" * 60)
    instance3 = SoccerClient('fifa.world')
    date_range_matches = instance3.get_info(date_range=("20260615", "20260620"))
    print(f"Matches between 2026-06-15 and 2026-06-20: {len(date_range_matches)}")
    print(date_range_matches)
    print("\n")

    print("=" * 60)
    print("TEST 4: Filter - Ongoing matches")
    print("=" * 60)
    instance4 = SoccerClient('fifa.world')
    ongoing_matches = instance4.ongoing()
    print(f"Live matches: {len(ongoing_matches)}")
    print(ongoing_matches)
    print("\n")

    print("=" * 60)
    print("TEST 5: Filter - Finished matches")
    print("=" * 60)
    instance5 = SoccerClient('fifa.world')
    finished_matches = instance5.finished()
    print(f"Finished matches: {len(finished_matches)}")
    print(finished_matches)
    print("\n")

    print("=" * 60)
    print("TEST 6: Filter - Upcoming matches")
    print("=" * 60)
    instance6 = SoccerClient('fifa.world')
    upcoming_matches = instance6.upcoming()
    print(f"Upcoming matches: {len(upcoming_matches)}")
    print(upcoming_matches)
    print("\n")

    print("=" * 60)
    print("TEST 7: Venues extraction")
    print("=" * 60)
    instance7 = SoccerClient('fifa.world')
    venues = instance7.venues()
    print(f"Total venues: {len(venues)}")
    print(venues)
    print("\n")

    print("=" * 60)
    print("TEST 8: Scores extraction")
    print("=" * 60)
    instance8 = SoccerClient('fifa.world')
    scores = instance8.scores()
    print(f"Total scores: {len(scores)}")
    print(scores)
    print("\n")

    print("=" * 60)
    print("TEST 9: Match IDs extraction")
    print("=" * 60)
    instance9 = SoccerClient('fifa.world')
    match_ids = instance9.get_ids()
    print(f"Total match IDs: {len(match_ids)}")
    print(match_ids)
    print("\n")

    print("=" * 60)
    print("TEST 10: Get specific match ID by short name")
    print("=" * 60)
    instance10 = SoccerClient('fifa.world')
    instance10.get_info()
    if len(instance10.games) > 0:
        test_short_name = instance10.games[0].short_name
        match_id = instance10.get_id(test_short_name)
        print(f"Short name: {test_short_name}")
        print(f"Match ID: {match_id}")
    else:
        print("No matches available to test get_id()")
    print("\n")

    print("=" * 60)
    print("TEST 11: Match object properties")
    print("=" * 60)
    instance11 = SoccerClient('fifa.world')
    instance11.get_info()
    if len(instance11.games) > 0:
        test_match = instance11.games[0]
        print(f"Match: {test_match.short_name}")
        print(f"Is Live: {test_match.is_live}")
        print(f"Is Finished: {test_match.is_finished}")
        print(f"Is Upcoming: {test_match.is_upcoming}")
        print(f"Venue: {test_match.venue}")
        print(f"Score: {test_match.score}")
    else:
        print("No matches available to test properties")
    print("\n")

    print("=" * 60)
    print("TEST 12: Custom limit parameter")
    print("=" * 60)
    instance12 = SoccerClient('fifa.world')
    limited = instance12.get_info(limit=5)
    print(f"Matches with limit=5: {len(limited)}")
    print(limited)
    print("\n")

    print("=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)