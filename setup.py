import os
from flutrack_backend import populateDB

os.environ['SECRET_KEY'] = 'm%nec7j8_r1yr3bkc=-(&qf91m17bfk35v5ct$ub-7n9=oscwd'
populateDB.populate_from_txt("/prediction/data/dummypopulation.csv")
populateDB.populate_from_flutrack_api()
