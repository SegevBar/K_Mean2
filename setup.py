from setuptools import setup, find_packages, Extension
setup(
    name='mykmeanssp',
    version='0.1.0',
    author='Bar Pakula & Bar Segev',
    author_email="",
    description="k-means algorithm",
    install_requires=['invoke'],
    packages=find_packages(),

    license='GPL-2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: Hebrew',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',

    ],
    ext_modules=[
        Extension(
            'mykmeanssp',
            ['kmeans.c'],
        ),
    ]

)
