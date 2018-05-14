
from setuptools import setup, find_packages

setup (
name= 'deltasherlock',

version= '0.1.1',

description= 'Application Identification',

author='BU PEACLab',

classifiers = [
	'Development Status :: 3 - Alpha',
	'Programming Language :: Python :: 3'
],

packages= find_packages(),

include_package_data = True,

# package_data =  {'sos_anomaly_detection': ['config.yaml', 'voltrino-config.yaml']},

# install_requires=['numpy', 'pandas', 'sklearn', 'pyyaml', 'tqdm', 'scipy'],

# entry_points= {'console_scripts': ['demo-script=sos_anomaly_detection.main:main','train-classifier=sos_anomaly_detection.main:train', 'test-classifier=sos_anomaly_detection.main:test'],}


)
