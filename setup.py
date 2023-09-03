#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2023 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================


import os
import platform

import setuptools

cmdclass = {}
try:
    from sphinx.setup_command import BuildDoc
    cmdclass = {'build_sphinx': BuildDoc}
except ImportError:
    pass

try:
    with open('README.rst') as f:
        readme = f.read()
except IOError:
    readme = ''


# 補完ファイルインストール用関数
def get_data_files():

    # 補完ファイルのインストール先を取得する関数
    def get_completefile_install_location(shell):
        # pathのprefixを定義
        prefix = ''

        # osの種類を取得
        uname = platform.uname()[0]

        # 実行ユーザがrootかどうかでprefixを変更
        if os.geteuid() == 0:
            ''' システムインストール時の挙動 '''
            if uname == 'Linux' and shell == 'bash':
                prefix = '/'
            elif uname == 'Linux' and shell == 'zsh':
                prefix = '/usr/local'
            elif uname == 'Darwin' and shell == 'bash':
                prefix = '/'
            elif uname == 'Darwin' and shell == 'zsh':
                prefix = '/usr'

        # shellの種類に応じてインストール先のlocationを変更
        if shell == 'bash':
            location = os.path.join(prefix, 'etc/bash_completion.d')
        elif shell == 'zsh':
            location = os.path.join(prefix, 'share/zsh/site-functions')
        else:
            raise ValueError('unsupported shell: {0}'.format(shell))

        # locationを返す
        return location

    # locationをdict形式で取得する
    loc = {
        'bash': get_completefile_install_location('bash'),
        'zsh': get_completefile_install_location('zsh')
    }

    # 対象となるファイルをdict形式で指定
    files = dict(
        bash=['completion/pydork-completion.bash'],
        zsh=[
            'completion/pydork-completion.bash',
            'completion/_pydork'
        ]
    )

    # data_files形式でreturn
    data_files = []
    data_files.append((loc['bash'], files['bash']))
    data_files.append((loc['zsh'], files['zsh']))
    return data_files


name = 'pydork'
version = '1.1.6'
release = '1.1.6'

if __name__ == "__main__":
    setuptools.setup(
        name=name,
        version=version,
        author='blacknon',
        author_email='blacknon@orebibou.com',
        maintainer='blacknon',
        maintainer_email='blacknon@orebibou.com',
        description='Scraping and listing text and image searches on Google, Bing, DuckDuckGo, Baidu, Yahoo japan.',
        long_description=readme,
        license='MIT License',
        install_requires=[
            'bs4',
            'get-chrome-driver',
            'get-gecko-driver',
            'chromedriver_autoinstaller',
            'geckodriver_autoinstaller',
            'fake_useragent',
            'lxml',
            'requests[socks]',
            'selenium==4.7.2',
            'selenium_requests',
            'pickle-mixin',
            'sphinx',
            'sphinx-rtd-theme',
            'sphinx-autobuild'
        ],
        url='https://github.com/blacknon/pydork',
        packages=setuptools.find_packages(),
        py_modules=['pydork'],
        entry_points={
            'console_scripts': [
                'pydork = pydork:main',
            ],
        },
        classifiers=[
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'License :: OSI Approved :: MIT License',
        ],
        data_files=get_data_files(),
        cmdclass=cmdclass,
        command_options={
            'build_sphinx': {
                'project': ('setup.py', name),
                'version': ('setup.py', version),
                'release': ('setup.py', release)}},
        setup_requires=[
            "sphinx",
            "sphinx-rtd-theme",
            "sphinx-autobuild",
        ],
    )
