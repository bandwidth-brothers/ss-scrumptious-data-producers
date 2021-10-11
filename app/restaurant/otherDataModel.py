from app.db.database import Database


class OtherRestaurantData:
    def __init__(self, restaurant_id: str, reviews: list):
        self.restaurant_id = restaurant_id
        self.reviews = reviews

    def save(self, database: Database):
        return True

    def __str__(self):
        review_str = ""
        for review in self.reviews:
            review_str += f"  {review.user_id} ({review.rating}) - {review.description}\n"

        return f"Restaurant ID: {self.restaurant_id}. Reviews: \n{review_str}"
