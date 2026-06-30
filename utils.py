
from datetime import datetime, timezone


def checktime(games, max_time):
    """
    Checks whether cached match data should be refreshed.

    This function compares the current UTC time with the `last_updated`
    timestamp of the first match object in the games list.
    essential for maintaining up-to-date match information,caching and helping to stay within API rate limits.

    Args:
        games (list):
            A list of objects containing at least:
            - last_updated (str)

            Expected format:
                "YYYY-MM-DD HH:MM:SS"

            Example:
                [
                    Match(last_updated="2026-06-29 18:30:00")
                ]

        max_time (int | bool):
            Maximum cache age in seconds.

            Examples:
                60 → refresh after 60 seconds
                300 → refresh after 5 minutes
                False → disable refresh checks
                0 → disable refresh checks

    Returns:
        bool:
            True  → refresh data
            False → keep current cached data

    Example:
        >>> checktime([], 60)
        True

        >>> checktime([match], 60)
        False

        >>> checktime([old_match], 60)
        True
    """

    # If refresh system is disabled, do not refresh
    if max_time is False or max_time == 0:
        return False

    # If no games exist, data must be fetched
    if len(games) == 0:
        return True

    # Get current UTC time
    utc_now = datetime.now(timezone.utc)

    # Convert stored timestamp into datetime object
    last = datetime.strptime(games[0].last_updated, "%Y-%m-%d %H:%M:%S")

    # Set timezone explicitly as UTC
    last = last.replace(tzinfo=timezone.utc)

    # Calculate how old the cached data is
    age = (utc_now - last).total_seconds()

    # Return True if data is older than allowed cache time
    return age > max_time


if __name__ == "__main__":
    """
    Test block for checktime().

    Runs 3 test cases:
        1. Empty list
        2. Fresh timestamp
        3. Old timestamp
    """

    from datetime import datetime, timezone

    class FakeMatch:
        """
        Mock match object for testing.

        Attributes:
            last_updated (str):
                Timestamp in format:
                YYYY-MM-DD HH:MM:SS
        """

        def __init__(self, last_updated):
            """
            Creates a fake match object.

            Args:
                last_updated (str): Timestamp string
            """
            self.last_updated = last_updated

    # Test 1: Empty list should trigger refresh
    result = checktime([], 60)
    print(f"Empty list test: {result}")  # Expected: True

    # Test 2: Current timestamp should NOT trigger refresh
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    fake_match = FakeMatch(now)
    result = checktime([fake_match], 60)
    print(f"Recent data test: {result}")  # Expected: False

    # Test 3: Very old timestamp should trigger refresh
    old_time = "2020-01-01 00:00:00"
    old_match = FakeMatch(old_time)
    result = checktime([old_match], 60)
    print(f"Old data test: {result}")  # Expected: True
