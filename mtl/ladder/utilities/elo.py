K_FACTOR = 32


def get_updated_rating(rating_a, rating_b, result):
    """ result = 1 if A won, 0 if B won
        https://metinmediamath.wordpress.com/2013/11/27/how-to-calculate-the-elo-rating-including-example/
    """
    transformed_rating_a = 10**(rating_a/400)
    transformed_rating_b = 10**(rating_b/400)

    expected_score_a = transformed_rating_a / (transformed_rating_a + transformed_rating_b)
    expected_score_b = transformed_rating_b / (transformed_rating_a + transformed_rating_b)

    score_a = result
    score_b = 1 - result

    elo_rating_a = rating_a + K_FACTOR * (score_a - expected_score_a)
    elo_rating_b = rating_b + K_FACTOR * (score_b - expected_score_b)

    return elo_rating_a, elo_rating_b
