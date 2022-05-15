#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =======================================================


import os
import platform

import setuptools
import sphinx.ext.apidoc
from sphinx.setup_command import BuildDoc


class BuildDocApiDoc(BuildDoc, object):
    # inherit from object to enable 'super'
    user_options = []
    description = 'sphinx'

    def run(self):
        # metadata contains information supplied in setup()
        metadata = self.distribution.metadata

        # package_dir may be None, in that case use the current directory.
        src_dir = (self.distribution.package_dir or {'': ''})['']
        src_dir = os.path.join(os.getcwd(), src_dir, 'docs')
        print(src_dir)

        # Run sphinx by calling the main method, '--full' also adds a conf.py
        cmd_line = ['-f', '-H', metadata.name, '-A', metadata.author,
                    '-V', metadata.version, '-R', metadata.version, '-T',
                    '-o', os.path.join('docs', '_build'), src_dir]

        print(cmd_line)
        sphinx.ext.apidoc.main(cmd_line)

        super(BuildDocApiDoc, self).run()


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
version = '1.1.1'
release = '1.1.1'

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
            'chromedriver_autoinstaller',
            'geckodriver_autoinstaller',
            'fake_useragent',
            'lxml',
            'requests[socks]',
            'selenium',
            'selenium_requests',
            'pickle-mixin',
            'sphinx'
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
            'License :: OSI Approved :: MIT License',
        ],
        data_files=get_data_files(),
        cmdclass={'build_sphinx': BuildDocApiDoc},
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
