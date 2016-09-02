import cPickle as pickle
import os
import sys
from Gif.Neutron.ParticleClass import Particle

scriptdir = os.path.dirname(__file__)
relpath = './particles.pickle'
sys.stderr.write('\033[32mUnpickling...\033[m\n')
parts = pickle.load(open(os.path.join(scriptdir, relpath), 'rb'))
sys.stderr.write('\033[32mCompleted.\033[m\n')
