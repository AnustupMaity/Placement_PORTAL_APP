"""DB MODEL   ALL MODEL HERE IMPORT FROM THE OTHER DIFF MODELS  CREATE DB ALL MODELS CALLED HERE AT ONCE ,  
WHEN RUN CREATE DB COMMAND
"""

from models.user import User
from models.company import CompanyProfile
from models.student import StudentProfile
from models.drive import PlacementDrive
from models.application import Application
from models.placement import Placement
from models.notification import Notification

__all__ = [
    'User',
    'CompanyProfile',
    'StudentProfile',
    'PlacementDrive',
    'Application',
    'Placement',
    'Notification',
]
