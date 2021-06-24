# Licensed under the GNU General Public License v3.0. See footer for details.
import setuptools

setuptools.setup(
    name="kaen",
    version="1.0.1.4",
    author="CounterFactual.AI LLC",
    author_email="kaen@counterfactual.ai",
    description="kaen is an open source toolkit to help you train and deploy deep learning models in public clouds",
    url="https://github.com/CounterFactualAI/kaenai",
    license="GPL v3.0",
    install_requires=[
      'torch',
      'fsspec',
      'pandas',
      's3fs',
      'gcsfs',
'click', 
			'python-dotenv', 
			'docker', 
			'mlflow',
    ],
		extras_require={
			"optuna":  ["optuna", "sklearn", "plotly", "kaleido"],			
    },
    include_package_data=True,
		py_modules=['kaen.main'],
    
    # package_dir = {'': 'src/py'},
    packages=setuptools.find_packages(
      # where = 'src/py',
      exclude=["src/py/test", "test", "**/.DS_Store"],
    ),
    # data_files=[('src/py/setup.py')],    
    python_requires=">=3.6",
)
# Copyright 2021 CounterFactual.AI LLC. All Rights Reserved.
#
# Licensed under the GNU General Public License, Version 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://github.com/CounterFactualAI/kaenai/blob/main/LICENSE
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
