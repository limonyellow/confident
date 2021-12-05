import setuptools

setuptools.setup(
      name='confident',
      version='0.0.1',
      description='Loading configurations from multiple sources into a data model.',
      long_description=open('README.md').read(),
      url='http://github.com/',
      author='limonyellow',
      author_email='lemon@example.com',
      license='MIT',
      zip_safe=False,
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      packages=['confident'],
      install_requires=[
            'pydantic',
            'pyyaml',
            'python-dotenv',
      ],
      # package_dir={"": "src"},
      # packages=setuptools.find_packages(where="src"),
      python_requires=">=3.6",
)
