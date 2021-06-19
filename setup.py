# Licensed under the GNU General Public License v3.0. See footer for details.
import setuptools

setuptools.setup(
    name="kaen",
    version="1.0.1",
    author="CounterFactual.AI LLC",
    author_email="kaen@counterfactual.ai",
    description="Kaen, a framework for deep learning",
    url="https://github.com/CounterFactualAI/kaenai",
    license="GPL v3.0",
    install_requires=[
      'torch',
      'fsspec',
      'pandas',
      's3fs',
      'gcsfs'
    ],
    packages=setuptools.find_packages()
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