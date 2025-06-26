from rest_framework.throttling import UserRateThrottle

class ReviewcreateThrottle(UserRateThrottle):
    scope='review-create'
    
    
class ReviewListThrottle(UserRateThrottle):
    scope='review-list'
    