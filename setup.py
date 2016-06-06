import os
import sys
os.environ['SECRET_KEY'] = 'm%nec7j8_r1yr3bkc=-(&qf91m17bfk35v5ct$ub-7n9=oscwd'
os.environ['MONGOLAB_URI'] = 'mongodb://localhost:27017'
os.environ['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("Added ")
